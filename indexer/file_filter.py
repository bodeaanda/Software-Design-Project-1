from pathlib import Path
from shared.app_config import AppConfig

class FileFilter:
    def __init__(self, config: AppConfig):
        self._ignore_dirs = config.ignore_dirs
        self._ignore_extensions = config.ignore_extensions

    def should_skip_dir(self, path: Path) -> bool:
        return path.name in self._ignore_dirs

    def should_index(self, path: Path) -> bool:
        return path.suffix not in self._ignore_extensions