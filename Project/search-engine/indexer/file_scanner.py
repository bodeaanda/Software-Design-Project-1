from pathlib import Path
from typing import Iterator
from shared.app_config import AppConfig

class FileScanner:
    def __init__(self, config: AppConfig):
        self._root = Path(config.root_dir)
        self._ignore_dirs = config.ignore_dirs
        self._ignore_extensions = config.ignore_extensions
        self._visited_dirs: set[Path] = set()

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
        except PermissionError:
            print(f"[SKIPPED] No permission: {directory}")
            return

        for entry in entries:
            if entry.is_dir():
                if entry.name not in self._ignore_dirs:
                    yield from self._walk(entry)
            elif entry.is_file():
                if entry.suffix not in self._ignore_extensions:
                    yield entry