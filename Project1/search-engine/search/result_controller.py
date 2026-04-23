from search.query_parser import QueryParser
from shared.db_wrapper import DatabaseWrapper

class ResultController:
    def __init__(self, db: DatabaseWrapper, parser: QueryParser):
        self._db = db
        self._parser = parser

    def search(self, raw_query: str) -> list[dict]:
        parsed = self._parser.parse(raw_query)
        if not parsed:
            return []
        try:
            return self._db.search(parsed)
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []