from search.observer import SearchObserver
from shared.db_wrapper import DatabaseWrapper

class SearchHistory(SearchObserver):
    def __init__(self, db: DatabaseWrapper):
        self._db = db

    def on_search(self, query: str):
        self._db.save_search(query)

    def get_suggestions(self, prefix: str) -> list[str]:
        return self._db.get_suggestions(prefix)