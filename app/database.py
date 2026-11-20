from collections.abc import Iterator

from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.config import settings
from app.schemas import VenueFilters

engine: Engine = create_engine(settings.database_url, pool_pre_ping=True)


def get_db() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


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
