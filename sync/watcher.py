import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sync.sender import send_file

class FileWatcher:
    def __init__(self, folder_to_watch, config):
        self.folder_to_watch = folder_to_watch
        self.config = config
        self.observer = Observer()

    def start(self):
        event_handler = SyncHandler(self.config)
        self.observer.schedule(event_handler, self.folder_to_watch, recursive=True)
        print(f"Watching folder: {self.folder_to_watch}")
        self.observer.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.observer.stop()
        self.observer.join()

class SyncHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config

    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            send_file(event.src_path, self.config)

    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            send_file(event.src_path, self.config)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")
            # Optionally handle deletion synchronization here
