import atexit
from loguru import logger
import time
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
import sys


logger.remove()
logger.add(sys.stderr, colorize=True)


class LayerHandler(FileSystemEventHandler):
    def on_closed(self, event: FileSystemEvent) -> None:
        logger.info(event)


def main():
    logger.info("Initialising application...")
    event_handler = LayerHandler()
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
