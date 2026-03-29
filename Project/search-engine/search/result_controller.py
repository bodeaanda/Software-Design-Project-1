from search.query_parser import QueryParser
from shared.db_wrapper import DatabaseWrapper

class ResultController:
    def __init__(self, db: DatabaseWrapper, parser: QueryParser):
        self._db = db
        self._parser = parser

    def search(self, raw_query: str) -> list[dict]:
        if not raw_query.strip():
            return []
        query = self._parser.parse(raw_query)
        try:
            return self._db.search(query)
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []