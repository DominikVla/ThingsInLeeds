import re
from collections.abc import Iterator

from sqlalchemy import bindparam, create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.config import settings
from app.schemas import VenueFilters


_ALLOWED_READ_STATEMENTS = re.compile(
    r"^(SELECT|WITH|SHOW|DESCRIBE|DESC|EXPLAIN|PRAGMA|VALUES)\b",
    re.IGNORECASE,
)
_FORBIDDEN_READ_ONLY_WRITE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|REPLACE|MERGE|CREATE|ALTER|DROP|TRUNCATE|RENAME|CALL|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def is_read_only_statement(statement: str) -> bool:
    cleaned = re.sub(r"^\s*(?:/\*.*?\*/|--[^\n]*\n)*", "", statement, flags=re.DOTALL)
    return bool(_ALLOWED_READ_STATEMENTS.match(cleaned)) and not bool(
        _FORBIDDEN_READ_ONLY_WRITE.search(cleaned)
    )


def configure_read_only_engine(database_url: str) -> Engine:
    engine = create_engine(database_url, pool_pre_ping=True)

    @event.listens_for(engine, "before_cursor_execute")
    def reject_writes(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemultiple,
    ) -> None:
        if not is_read_only_statement(statement):
            raise RuntimeError("Only read-only SQL is allowed on the LLM database copy")

    if engine.dialect.name == "mysql":
        @event.listens_for(engine, "connect")
        def set_read_only(dbapi_connection, connection_record) -> None:
            with dbapi_connection.cursor() as cursor:
                cursor.execute("SET SESSION TRANSACTION READ ONLY")

    return engine


# The application, including any LLM-facing database access, only receives
# this read-only copy. A separate DATABASE_URL remains the write-capable source.
read_only_engine: Engine = configure_read_only_engine(settings.read_only_database_url)
# Backwards-compatible names used by existing integrations.
llm_engine: Engine = read_only_engine
engine: Engine = read_only_engine


def get_read_only_db() -> Iterator[Session]:
    with Session(read_only_engine) as session:
        yield session


def get_db() -> Iterator[Session]:
    yield from get_read_only_db()


def search_venues(db: Session, filters: VenueFilters) -> list[dict]:
    conditions = ["1 = 1"]
    params: dict = {}

    if filters.venue_types:
        conditions.append("v.venue_type IN :venue_types")
        params["venue_types"] = [item.value for item in filters.venue_types]
    if filters.neighbourhoods:
        conditions.append("v.neighbourhood IN :neighbourhoods")
        params["neighbourhoods"] = filters.neighbourhoods
    if filters.max_price_tier is not None:
        conditions.append("v.price_tier <= :max_price_tier")
        params["max_price_tier"] = filters.max_price_tier
    if filters.max_budget_gbp is not None:
        conditions.append(
            "(v.venue_type != 'accommodation' OR "
            "ad.avg_nightly_rate_gbp <= :max_budget_gbp)"
        )
        params["max_budget_gbp"] = filters.max_budget_gbp
    if filters.is_free_entry is True:
        conditions.append("atd.is_free = 1")
    if filters.categories:
        conditions.append(
            "EXISTS (SELECT 1 FROM venue_categories vc "
            "JOIN categories c ON c.id = vc.category_id "
            "WHERE vc.venue_id = v.id AND c.name IN :categories)"
        )
        params["categories"] = filters.categories
    if filters.open_at_time is not None:
        time_value = filters.open_at_time.isoformat(timespec="minutes")
        conditions.append(
            "EXISTS (SELECT 1 FROM opening_hours oh "
            "WHERE oh.venue_id = v.id AND "
            "(CASE WHEN oh.close_time >= oh.open_time "
            "THEN :open_at_time BETWEEN oh.open_time AND oh.close_time "
            "ELSE :open_at_time >= oh.open_time OR :open_at_time <= oh.close_time END))"
        )
        params["open_at_time"] = time_value

    sql = text(
        "SELECT DISTINCT v.id, v.name, v.venue_type, v.description, "
        "v.neighbourhood, v.address, v.postcode, v.price_tier, v.website_url "
        "FROM venues v "
        "LEFT JOIN accommodation_details ad ON ad.venue_id = v.id "
        "LEFT JOIN attraction_details atd ON atd.venue_id = v.id "
        "WHERE " + " AND ".join(conditions) + " LIMIT 100"
    )
    bound_params = {
        name: bindparam(name, expanding=True)
        if name in {"venue_types", "neighbourhoods", "categories"}
        else bindparam(name)
        for name in params
    }
    sql = sql.bindparams(**bound_params)
    rows = db.execute(sql, params).mappings().all()
    return [dict(row) for row in rows]
