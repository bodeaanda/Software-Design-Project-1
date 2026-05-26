from __future__ import annotations
from abc import ABC, abstractmethod


class QueryBuilder(ABC):
    @abstractmethod
    def build(self, raw_query: str) -> str:
        pass


class BaseQueryBuilder(QueryBuilder):
    """Baza pipeline-ului — returneaza query-ul neschimbat."""
    def build(self, raw_query: str) -> str:
        return raw_query


class QueryDecorator(QueryBuilder, ABC):
    """Decorator de baza — wrapeaza un alt QueryBuilder."""
    def __init__(self, wrapped: QueryBuilder):
        self._wrapped = wrapped

    def build(self, raw_query: str) -> str:
        return self._wrapped.build(raw_query)


class SanitizationDecorator(QueryDecorator):
    """Sterge caracterele speciale care ar putea sparge sintaxa FTS5."""
    _SPECIAL_CHARS = set('"\';()[]{}\\')

    def build(self, raw_query: str) -> str:
        cleaned = super().build(raw_query)
        cleaned = ''.join(ch for ch in cleaned if ch not in self._SPECIAL_CHARS)
        cleaned = ' '.join(cleaned.split())  # normalizeaza spatiile
        return cleaned


class SynonymDecorator(QueryDecorator):
    """Expandeaza termeni la sinonime standard."""
    SYNONYMS: dict[str, list[str]] = {
        "img":   ["img", "image", "photo"],
        "pic":   ["pic", "image", "photo"],
        "photo": ["photo", "image", "img"],
        "image": ["image", "img", "photo"],
        "doc":   ["doc", "document"],
        "vid":   ["vid", "video"],
    }

    def build(self, raw_query: str) -> str:
        query = super().build(raw_query)
        tokens = query.split()
        expanded = []
        for token in tokens:
            # nu atinge qualifier-ele (path:, content:, color:)
            if ':' in token:
                expanded.append(token)
            else:
                lower = token.lower()
                if lower in self.SYNONYMS:
                    expanded.append(' OR '.join(self.SYNONYMS[lower]))
                else:
                    expanded.append(token)
        return ' '.join(expanded)


class LogicDecorator(QueryDecorator):
    """Adauga wildcard (*) la termeni generali pentru prefix matching."""
    def build(self, raw_query: str) -> str:
        query = super().build(raw_query)
        tokens = query.split()
        result = []
        for token in tokens:
            # nu atinge qualifier-ele sau termenii OR deja expandati
            if ':' in token or ' OR ' in token or token.endswith('*'):
                result.append(token)
            else:
                result.append(token + '*')
        return ' '.join(result)


def build_default_pipeline() -> QueryBuilder:
    """Construieste pipeline-ul default: Sanitize -> Synonym -> Logic."""
    base = BaseQueryBuilder()
    sanitized = SanitizationDecorator(base)
    synonymed = SynonymDecorator(sanitized)
    logic = LogicDecorator(synonymed)
    return logic