import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

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

    def post_load(self, file_path: str = None):
        """
        Triggered after a successful ingestion to run transformations and tests.
        """
        print(f"🔄 Triggering post-load transformation for: {file_path}")
        try:
            # Run dbt run
            subprocess.run(
                ["dbt", "run"],
                cwd="/opt/src/analytics",
                check=True
            )
            # Run dbt test
            subprocess.run(
                ["dbt", "test"],
                cwd="/opt/src/analytics",
                check=True
            )
            print("✅ dbt transformation and validation successful")
        except subprocess.CalledProcessError as e:
            print(f"❌ dbt failed with exit code {e.returncode}")

    def handle_raw_event(self, event_type: str, file_path: str = None):
        """
        Because its pertinent to validate the file if it has been changed we must run the validate file again just to check
        """
        try:
            self.source_location.validate_connection()
            self.ingestor.run_ingestion(file_path)
            
            # Execute post-load hooks
            self.post_load(file_path)
            
        except (ValueError, ValidationError):
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
        # Resolve the directory to watch (handles both single files and globs)
        watch_path = str(Path(self.source_location.read_path).parent)
        observer.schedule(
            event_handler, watch_path, recursive=False
        )
        observer.start()
        print(f"📡 Monitoring: {watch_path} (Filter: {self.source_location.read_path})")

        # Initial scan of existing files
        import glob
        for existing_file in glob.glob(self.source_location.read_path):
            print(f"🔍 Found existing file: {existing_file}")
            self.handle_raw_event("initial_scan", existing_file)

        try:
            while observer.is_alive():
                observer.join(1)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            observer.stop()
            observer.join()

    def _handle_file_event(self, event: FileSystemEvent) -> None:
        self.handle_raw_event(event.event_type, event.src_path)


OBSERVER_REGISTRY = {"watchdog": WatchDogObserver}
