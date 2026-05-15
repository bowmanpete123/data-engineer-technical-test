from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict


# TODO: this is definitely overkill, I've really gone down a rabbit hole on this but to show you where my head is at I've added a (admitted vibe coded) sqlite connector too
class BaseSQLDestination(ABC, BaseModel):
    model_config = ConfigDict(frozen=True)
    table: str
    schema_name: str

    @property
    @abstractmethod
    def dialect(self) -> str:
        """Must return the DuckDB extension name (e.g., 'postgres', 'mysql')"""
        pass

    @property
    @abstractmethod
    def conn_str(self) -> str:
        """Must return the string used in the ATTACH statement"""
        pass

    @property
    def full_target_path(self) -> str:
        """
        The unified way to address the table inside DuckDB.
        Note: Some DBs like SQLite might override this if they don't use schemas.
        """
        return f"remote_db.{self.schema_name}.{self.table}"


class PostgresDestination(BaseSQLDestination):
    host: str
    database: str
    user: str
    password: str
    port: int = 5432

    @property
    def dialect(self) -> str:
        return "postgres"

    @property
    def conn_str(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"


class SQLiteDestination(BaseSQLDestination):
    db_path: str

    @property
    def dialect(self) -> str:
        return "sqlite"

    @property
    def conn_str(self) -> str:
        return self.db_path

    @property
    def full_target_path(self) -> str:
        # SQLite doesn't use 'public.' schema prefix in DuckDB ATTACH
        return f"remote_db.{self.table}"


SQL_DESTINATION_REGISTRY = {
    "postgres": PostgresDestination,
    "sqlite": SQLiteDestination,
}
