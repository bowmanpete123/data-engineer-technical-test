from typing import Any, NamedTuple

from pydantic import BaseModel, ConfigDict

from python.el_types.ingestors import INGESTOR_REGISTRY

from .file_sources import SOURCE_FILE_REGISTRY
from .observers import OBSERVER_REGISTRY, BaseFileObserver
from .sql_destinations import SQL_DESTINATION_REGISTRY

# NOTE: This is well-meaning but a bloody mess! There must be an easier way to work with these arguments, though I'm guessing I"m leaning way too hard into the type system here rather than just writing business logic, There must be a way to compose this without documentation or going through the hierarchy of like 10 inheritance classes
ElerConfig = NamedTuple("ElerConfig", [("type", str), ("kwargs", dict[str, Any])])


def _parse_config(
    config: ElerConfig | str,
    registry: dict[str, Any],
    base_class_args: dict[str, Any] = {},
):
    """Basically this exists because there are classes that we can call on that don't have any unique fields of their own and only have base class fields that only require other parts of the configuration (e.g. ingestor_configs for duckdb)"""
    if isinstance(config, ElerConfig):
        return registry[config.type](**config.kwargs, **base_class_args)
    if isinstance(config, str):
        return registry[config](base_class_args)
    # NOTE: This seems bloody pedantic but its making sure that somethign deosn't go wrong
    raise TypeError(
        f"The config you have parsed is of type: {type(config)}. Valid types are ElerConfig, and str"
    )


class ElerFactory(BaseModel):
    # Allow the model to hold complex objects that aren't basic Pydantic types
    model_config = ConfigDict(arbitrary_types_allowed=True)
    ingestor_config: ElerConfig | str
    observer_config: ElerConfig | str
    sql_destination_config: ElerConfig
    source_file_config: ElerConfig

    def compose(self) -> BaseFileObserver:
        """
        It builds the dependencies locally and returns the runnable observer.
        """
        src = _parse_config(self.source_file_config, SOURCE_FILE_REGISTRY)
        dest = _parse_config(self.sql_destination_config, SQL_DESTINATION_REGISTRY)
        ingestor = _parse_config(
            self.ingestor_config, INGESTOR_REGISTRY, {"source": src, "sql_dest": dest}
        )
        observer = _parse_config(
            self.observer_config,
            OBSERVER_REGISTRY,
            {"ingestor": ingestor, "source_location": src},
        )
        return observer

    def run(self):
        # Simply assemble and fire
        self.compose().observe()
