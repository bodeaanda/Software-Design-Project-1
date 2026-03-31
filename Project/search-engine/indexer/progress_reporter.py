from datetime import datetime

class ProgressReporter:
    def __init__(self):
        self._found = 0
        self._indexed = 0
        self._skipped = 0
        self._errors = []
        self._start_time = None

    def start(self):
        self._start_time = datetime.now()
        print(f"Indexing started at {self._start_time.strftime('%H:%M:%S')}")

    def increment_found(self):
        self._found += 1

    def increment_indexed(self):
        self._indexed += 1

    def increment_skipped(self):
        self._skipped += 1

    def log_error(self, path, error):
        self._errors.append((str(path), str(error)))
        print(f"[ERROR] {path}: {error}")

    def report(self):
        duration = (datetime.now() - self._start_time).seconds
        print("\n===== Indexing Report =====")
        print(f"Duration      : {duration}s")
        print(f"Files found   : {self._found}")
        print(f"Files indexed : {self._indexed}")
        print(f"Files skipped : {self._skipped}")
        print(f"Errors        : {len(self._errors)}")
        if self._errors:
            print("\nErrors detail:")
            for path, err in self._errors:
                print(f"  - {path}: {err}")
        print("===========================\n")