import atexit
from loguru import logger
import time
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
import sys

from dash_simulation.patched_loader import PatchedAconityLoader


logger.remove()
logger.add(sys.stderr, colorize=True)


class LayerHandler(FileSystemEventHandler):
    def __init__(self, loader, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_files = set()
        self.loader = loader

    def on_closed(self, event: FileSystemEvent) -> None:
        logger.info(event)
        if (f := event.src_path) not in self.cached_files:
            self.cached_files.add(f)
            logger.info(f"Reading {f}")
            self.loader.read_layer(f)
        else:
            logger.info(f"Skipping {f} (already loaded)")


def main():
    logger.info("Initialising application...")
    loader = PatchedAconityLoader()
    event_handler = LayerHandler(loader)
    observer = Observer()
    observer.schedule(event_handler, "./layers/", recursive=False)
    observer.start()
    atexit.register(observer.stop)
    atexit.register(observer.join)
    logger.success("Watcher ready!")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
