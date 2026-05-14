import os
from pathlib import Path

from .el_types.eler import ElerConfig, ElerFactory

# --- Configuring the pipeline
ingestor = os.getenv("ETL_ENGINE", "duckdb")
observer = os.getenv("ETL_WATCHER", "watchdog")
dest = ElerConfig(
    "postgres",
    {
        "HOST": os.getenv("PG_HOST", "localhost"),
        "DATABASE": os.getenv("PG_DATABASE", "postgres"),
        "USER": os.getenv("PG_USER", "admin"),
        "PASSWORD": os.getenv("PG_PASSWORD", "secret"),
        "PORT": int(os.getenv("PG_PORT", 5432)),  # Note the int conversion
        "TABLE": os.getenv("PG_TABLE", "bets"),
        "SCHEMA": os.getenv("PG_SCHEMA", "public"),
    },
)
src = ElerConfig(
    "local",
    {
        "format": "csv",
        "path": Path(os.getenv("LANDED_FILE_PATH", "../landed_files/bets.csv")),
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
