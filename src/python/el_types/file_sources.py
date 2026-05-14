from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, ConfigDict, model_validator


# NOTE: similar with the destinations I"m seeing this as for a task like this too but depending on the source this could change even between production environments (admittedly I had vibe coded help on this one)
class BaseFileSource(ABC, BaseModel):
    model_config = ConfigDict(frozen=True)
    format: str

    @property
    @abstractmethod
    def read_path(self) -> str:
        """The path string DuckDB uses (local path or URI)."""
        pass

    @abstractmethod
    def validate_connection(self) -> None:
        """This forces every subtype to validate its own existence"""
        pass

    @model_validator(mode="after")
    def run_validation(self) -> "BaseFileSource":
        """Lets make sure the file exists"""
        self.validate_connection()
        return self


class LocalFileSource(BaseFileSource):
    path: Path  # Pydantic will automatically convert strings to Path objects

    @property
    def read_path(self) -> str:
        """
        Using resolve() ensures symlinks are followed and the path is absolute.
        """
        return str(self.path.resolve())

    def validate_connection(self) -> None:
        p = self.path
        if p.name.startswith("."):
            raise ValueError(f"Nope not going to load a hidden file: {p}")
        if not p.exists():
            raise ValueError(f"File missing: {p}")
        if p.is_dir():
            raise ValueError(f"Path is a directory: {p}")
        if p.stat().st_size == 0:
            raise ValueError(f"File is empty: {p}")


class S3FileSource(BaseFileSource):
    bucket: str
    key: str

    @property
    def read_path(self) -> str:
        return f"s3://{self.bucket}/{self.key}"

    # NOTE: This is deliberately commented out, this is just to show the point of the validate connection as an abstract class rather than a sub type
    # def validate_connection(self) -> None:
    #     """Check if the S3 object exists using boto3."""
    #     s3 = boto3.client('s3')
    #     try:
    #         s3.head_object(Bucket=self.bucket, Key=self.key)
    #     except ClientError as e:
    #         raise ValueError(f"S3 Source Error: {self.bucket}/{self.key} not found or inaccessible.") from e


SOURCE_FILE_REGISTRY = {"local": LocalFileSource, "s3": S3FileSource}
