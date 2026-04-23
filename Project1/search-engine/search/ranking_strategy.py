from abc import ABC, abstractmethod

class RankingStrategy(ABC):
    @abstractmethod
    def rank(self, results: list[dict]) -> list[dict]:
        pass

class ScoreRanking(RankingStrategy):
    def rank(self, results: list[dict]) -> list[dict]:
        return sorted(results, key=lambda r: r.get("score", 0), reverse=True)

class AlphabeticalRanking(RankingStrategy):
    def rank(self, results: list[dict]) -> list[dict]:
        return sorted(results, key=lambda r: r["path"].lower())

class DateRanking(RankingStrategy):
    def rank(self, results: list[dict]) -> list[dict]:
        return sorted(results, key=lambda r: r.get("mtime", 0), reverse=True)