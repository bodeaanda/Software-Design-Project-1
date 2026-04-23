from pathlib import Path
from typing import Iterator
from shared.app_config import AppConfig
from indexer.progress_reporter import ProgressReporter

class FileScanner:
    def __init__(self, config: AppConfig, reporter: ProgressReporter):
        self._root = Path(config.root_dir)
        self._ignore_dirs = config.ignore_dirs
        self._ignore_extensions = config.ignore_extensions
        self._visited_dirs: set[Path] = set()
        self._reporter = reporter

    def scan(self) -> Iterator[Path]:
        self._visited_dirs.clear()
        yield from self._walk(self._root)

    def _walk(self, directory: Path) -> Iterator[Path]:
        real = directory.resolve()
        if real in self._visited_dirs:
            return
        self._visited_dirs.add(real)

        try:
            entries = list(directory.iterdir())
        except PermissionError as e:
            self._reporter.log_error(directory, e)
            return

        for entry in entries:
            if entry.is_dir():
                if entry.name not in self._ignore_dirs:
                    yield from self._walk(entry)
            elif entry.is_file():
                if entry.suffix not in self._ignore_extensions:
                    self._reporter.increment_found()
                    yield entry