from search.query_parser import QueryParser
from search.ranking_strategy import RankingStrategy, ScoreRanking
from search.observer import SearchObserver
from shared.db_wrapper import DatabaseWrapper

class ResultController:
    def __init__(self, db: DatabaseWrapper, parser: QueryParser, ranking: RankingStrategy = None):
        self._db = db
        self._parser = parser
        self._ranking = ranking or ScoreRanking()
        self._observers: list[SearchObserver] = []

    #replaces the current ranking strategy
    def set_ranking(self, ranking: RankingStrategy):
        self._ranking = ranking

    #obs get notified whenever a search runs
    def add_observer(self, observer: SearchObserver):
        self._observers.append(observer)

    #calls on_search 
    def _notify_observers(self, query: str, results: list[dict]):
        for observer in self._observers:
            observer.on_search(query, results)

    def search(self, raw_query: str) -> list[dict]:
        parsed = self._parser.parse(raw_query)
        if not parsed:
            return []
        try:
            results = self._db.search(parsed)
            ranked = self._ranking.rank(results)
            self._notify_observers(raw_query, ranked)
            return ranked
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []