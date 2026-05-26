from __future__ import annotations

from csv import writer
from importlib.resources import readers
import threading
import queue
from pathlib import Path

from indexer.metadata_extractor import MetadataExtractor
from indexer.file_scorer import FileScorer
from indexer.progress_reporter import ProgressReporter
from shared.db_wrapper import DatabaseWrapper

_DONE = object()


class ParallelIndexer:

    def __init__(
        self,
        db: DatabaseWrapper,
        extractor: MetadataExtractor,
        reporter: ProgressReporter,
        num_readers: int = 4,
        queue_size: int = 64,
    ):
        self._db = db
        self._extractor = extractor
        self._reporter = reporter
        self._scorer = FileScorer()
        self._num_readers = num_readers
        self._queue: queue.Queue = queue.Queue(maxsize=queue_size)

    def index_all(self, paths: list[Path]) -> None:
        chunks = self._split(paths, self._num_readers)

        readers = []
        for chunk in chunks:
            t = threading.Thread(target=self._reader_worker, args=(chunk,), daemon=True)
            t.start()
            readers.append(t)

        writer = threading.Thread(target=self._writer_worker, daemon=True)
        writer.start()

        for t in readers:
            t.join()

        for _ in readers:
            self._queue.put(_DONE)

        writer.join()

    def _reader_worker(self, paths: list[Path]) -> None:
        for path in paths:
            try:
                current_mtime = path.stat().st_mtime
                stored_mtime = self._db.get_mtime(str(path))

                if stored_mtime is not None and stored_mtime == current_mtime:
                    self._reporter.increment_skipped()
                    continue

                metadata = self._extractor.extract(path)
                score = self._scorer.score(path, metadata["size"], metadata["mtime"])
                self._queue.put({
                    "path":           metadata["path"],
                    "extension":      metadata["extension"],
                    "size":           metadata["size"],
                    "mtime":          metadata["mtime"],
                    "preview":        metadata["preview"],
                    "score":          score,
                    "dominant_color": metadata["dominant_color"],
                    "file_type":      metadata["file_type"],
                })
            except Exception as e:
                self._reporter.log_error(path, e)

    def _writer_worker(self) -> None:
        active_readers = self._num_readers

        while True:
            item = self._queue.get()

            if item is _DONE:
                active_readers -= 1
                if active_readers == 0:
                    break
                continue

            try:
                self._db.upsert_file(**item)
                self._reporter.increment_indexed()
            except Exception as e:
                self._reporter.log_error(Path(item.get("path", "?")), e)

    @staticmethod
    def _split(lst: list, n: int) -> list[list]:
        if not lst:
            return [[] for _ in range(n)]
        size = max(1, len(lst) // n)
        chunks = [lst[i:i + size] for i in range(0, len(lst), size)]
        while len(chunks) > n:
            chunks[-2].extend(chunks[-1])
            chunks.pop()
        return chunks