from __future__ import annotations
from abc import ABC, abstractmethod


class QueryBuilder(ABC):
    @abstractmethod
    def build(self, raw_query: str) -> str:
        pass


class BaseQueryBuilder(QueryBuilder):
    def build(self, raw_query: str) -> str:
        return raw_query


class QueryDecorator(QueryBuilder, ABC):
    def __init__(self, wrapped: QueryBuilder):
        self._wrapped = wrapped

    def build(self, raw_query: str) -> str:
        return self._wrapped.build(raw_query)


class SanitizationDecorator(QueryDecorator):
    _SPECIAL_CHARS = set('"\';()[]{}\\')

    def build(self, raw_query: str) -> str:
        cleaned = super().build(raw_query)
        cleaned = ''.join(ch for ch in cleaned if ch not in self._SPECIAL_CHARS)
        cleaned = ' '.join(cleaned.split())  
        return cleaned


class SynonymDecorator(QueryDecorator):
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
    def build(self, raw_query: str) -> str:
        query = super().build(raw_query)
        tokens = query.split()
        result = []
        for token in tokens:
            if ':' in token or ' OR ' in token or token.endswith('*'):
                result.append(token)
            else:
                result.append(token + '*')
        return ' '.join(result)


def build_default_pipeline() -> QueryBuilder:
    base = BaseQueryBuilder()
    sanitized = SanitizationDecorator(base)
    synonymed = SynonymDecorator(sanitized)
    logic = LogicDecorator(synonymed)
    return logic