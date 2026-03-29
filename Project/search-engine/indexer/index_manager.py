from pathlib import Path
from indexer.metadata_extractor import MetadataExtractor
from shared.db_wrapper import DatabaseWrapper

class IndexManager:
    def __init__(self, db: DatabaseWrapper, extractor: MetadataExtractor):
        self._db = db
        self._extractor = extractor

    def process(self, path: Path):
        try:
            current_mtime = path.stat().st_mtime
            stored_mtime = self._db.get_mtime(str(path))

            if stored_mtime is not None and stored_mtime == current_mtime:
                return  # file unchanged, skip it

            metadata = self._extractor.extract(path)
            self._db.upsert_file(
                path=metadata["path"],
                extension=metadata["extension"],
                size=metadata["size"],
                mtime=metadata["mtime"],
                preview=metadata["preview"]
            )
        except Exception as e:
            print(f"[ERROR] Could not index {path}: {e}")