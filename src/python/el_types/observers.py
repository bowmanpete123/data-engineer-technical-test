from abc import ABC, abstractmethod

from pydantic import BaseModel, ValidationError
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from .file_sources import BaseFileSource
from .ingestors import BaseIngestor


# NOTE: I feel this is more necessary than its ingestor counterpart, because the source data you're watching could change based on the environment you're in, for this I'd think that once you'd deployed you'd need it to look at an S3 bucket or a SQS message queue etc. Also this class has terrible logs! I need to do something about this or it will be a monster to observe and debug
class BaseFileObserver(ABC, BaseModel):
    source_location: BaseFileSource
    ingestor: BaseIngestor

    @abstractmethod
    def observe(self):
        pass

    def handle_raw_event(self, event_type: str):
        """
        Because its pertinent to validate the file if it has been changed we must run the validate file again just to check
        """
        try:
            self.source_location.validate_connection()
            self.ingestor.run_ingestion()
        except ValueError, ValidationError:
            return


class WatchDogObserver(BaseFileObserver):
    def observe(self):
        """
        The main loop that starts the background thread.
        """
        # 1. Setup the Handler with our logic
        event_handler = PatternMatchingEventHandler(
            patterns=[self.source_location.read_path],
            ignore_directories=True,
            case_sensitive=False,
        )
        event_handler.on_created = self._handle_file_event  # type: ignore
        event_handler.on_modified = self._handle_file_event  # type: ignore
        # Start the OS thread
        observer = Observer()
        observer.schedule(
            event_handler, str(self.source_location.read_path), recursive=False
        )
        observer.start()
        print(f"📡 Monitoring: {self.source_location.read_path}")

        try:
            while observer.is_alive():
                observer.join(1)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            observer.stop()
            observer.join()

    def _handle_file_event(self, event: FileSystemEvent) -> None:
        self.handle_raw_event(event.event_type)


OBSERVER_REGISTRY = {"watchdog": WatchDogObserver}
