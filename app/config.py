import os
import re

from pydantic import BaseModel


_DEFAULT_DATABASE_URL = "mysql+pymysql://root@localhost:3306/things_in_leeds"


def derive_read_only_database_url(database_url: str) -> str:
    """Derive a separate database name when no read-only URL is configured."""
    match = re.search(r"(?<!/)/(?!/)([^/?]+)(?:\?[^/]*)?$", database_url)
    if match:
        database_name = match.group(1)
        if not database_name.endswith("_read_only"):
            return database_url[:match.start(1)] + database_name + "_read_only" + database_url[match.end(1):]
    return database_url


DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_DATABASE_URL)


class Settings(BaseModel):
    database_url: str = DATABASE_URL
    read_only_database_url: str = os.getenv(
        "READ_ONLY_DATABASE_URL",
        derive_read_only_database_url(DATABASE_URL),
    )
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


settings = Settings()
