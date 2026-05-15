from abc import ABC, abstractmethod

import duckdb
from pydantic import BaseModel

from .file_sources import BaseFileSource
from .sql_destinations import BaseSQLDestination


class BaseIngestor(ABC, BaseModel):
    source: BaseFileSource
    sql_dest: BaseSQLDestination

    @abstractmethod
    def reader_function(self):
        """Logic for moving data between specific configs."""
        pass

    @abstractmethod
    def run_ingestion(self, file_path: str | None):
        """Logic for moving data between specific configs."""
        pass


class BaseDuckIngestor(BaseIngestor):
    @property
    def reader_function(self) -> str:
        """Determines the DuckDB function based on format."""
        mapping = {
            "csv": "read_csv_auto",
            "parquet": "read_parquet",
            "json": "read_json_auto",
        }
        return mapping.get(self.source.format.lower(), "read_csv_auto")

    def run_ingestion(self, file_path: str | None):
        target_path = file_path if file_path else self.source.read_path
        # This logic NEVER has to change, no matter how many DB types you add.
        con = duckdb.connect()
        con.execute(f"INSTALL {self.sql_dest.dialect}; LOAD {self.sql_dest.dialect};")
        con.execute(
            f"ATTACH '{self.sql_dest.conn_str}' AS remote_db (TYPE {self.sql_dest.dialect});"
        )

        options = ""
        if self.source.format.lower() == "csv" and self.source.null_str:
            options = f", nullstr='{self.source.null_str}'"

        # Clear the table before loading to ensure a 1:1 reflection of the CSV
        con.execute(f"DELETE FROM {self.sql_dest.full_target_path};")

        con.execute(
            f"INSERT INTO {self.sql_dest.full_target_path} SELECT * FROM {self.reader_function}('{target_path}'{options});"
        )
        print(f"🚀 Executed SQL: INSERT INTO {self.sql_dest.full_target_path} SELECT * FROM {self.reader_function}('{target_path}'{options});")
        print("Ingestion Successful")


INGESTOR_REGISTRY = {"duckdb": BaseDuckIngestor}
