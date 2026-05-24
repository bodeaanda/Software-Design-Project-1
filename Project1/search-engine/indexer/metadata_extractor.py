from pathlib import Path
from indexer.file_processor import FileProcessor, TextFileProcessor, ImageFileProcessor

class MetadataExtractor:
    def __init__(self):
        self._processors: list[FileProcessor] = [
            TextFileProcessor(),
            ImageFileProcessor(),
        ]

    def extract(self, path: Path) -> dict:
        stat = path.stat()
        processor = self._get_processor(path)

        try:
            result = processor.process(path)
        except Exception:
            result = {
                "type": "unknown",
                "preview": "",
                "dominant_color": None
            }

        return {
            "path": str(path),
            "extension": path.suffix.lower(),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "preview": result.get("preview", ""),
            "dominant_color": result.get("dominant_color", None),
            "file_type": result.get("type", "text")
        }

    def _get_processor(self, path: Path) -> FileProcessor:
        for processor in self._processors:
            if processor.can_process(path):
                return processor
        return TextFileProcessor()