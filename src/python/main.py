import os
from pathlib import Path

from .el_types.eler import ElerConfig, ElerFactory

# --- Configuring the pipeline
ingestor = os.getenv("ETL_ENGINE", "duckdb")
observer = os.getenv("ETL_WATCHER", "watchdog")
dest = ElerConfig(
    "postgres",
    {
        "host": os.getenv("PG_HOST", "localhost"),
        "database": os.getenv("PG_DATABASE", "postgres"),
        "user": os.getenv("PG_USER", "admin"),
        "password": os.getenv("PG_PASSWORD", "secret"),
        "port": int(os.getenv("PG_PORT", 5432)),  # Note the int conversion
        "table": os.getenv("PG_TABLE", "bets"),
        "schema_name": os.getenv("PG_SCHEMA", "public"),
    },
)
src = ElerConfig(
    "local",
    {
        "format": "csv",
        "path": Path(os.getenv("LANDED_FOLDER", "../landed_files/*.csv")),
        "null_str": os.getenv("NULL_STR", "NULL"),
    },
)
pipeline = ElerFactory(
    ingestor_config=ingestor,
    observer_config=observer,
    sql_destination_config=dest,
    source_file_config=src,
)
pipeline.run()
# ----------
