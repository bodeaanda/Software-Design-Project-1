from search.query_parser import QueryParser
from search.ranking_strategy import RankingStrategy, ScoreRanking
from shared.db_wrapper import DatabaseWrapper

class ResultController:
    def __init__(self, db: DatabaseWrapper, parser: QueryParser, ranking: RankingStrategy = None):
        self._db = db
        self._parser = parser
        self._ranking = ranking or ScoreRanking()

    def set_ranking(self, ranking: RankingStrategy):
        self._ranking = ranking

    def search(self, raw_query: str) -> list[dict]:
        parsed = self._parser.parse(raw_query)
        if not parsed:
            return []
        try:
            results = self._db.search(parsed)
            return self._ranking.rank(results)
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []