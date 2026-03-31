from pathlib import Path
from indexer.metadata_extractor import MetadataExtractor
from indexer.progress_reporter import ProgressReporter
from shared.db_wrapper import DatabaseWrapper

class IndexManager:
    def __init__(self, db: DatabaseWrapper, extractor: MetadataExtractor, reporter: ProgressReporter):
        self._db = db
        self._extractor = extractor
        self._reporter = reporter

    def process(self, path: Path):
        try:
            current_mtime = path.stat().st_mtime
            stored_mtime = self._db.get_mtime(str(path))

            if stored_mtime is not None and stored_mtime == current_mtime:
                self._reporter.increment_skipped()
                return

            metadata = self._extractor.extract(path)
            self._db.upsert_file(
                path=metadata["path"],
                extension=metadata["extension"],
                size=metadata["size"],
                mtime=metadata["mtime"],
                preview=metadata["preview"]
            )
            self._reporter.increment_indexed()
        except Exception as e:
            self._reporter.log_error(path, e)