class QueryParser:
    def parse(self, raw_query: str) -> str:
        terms = raw_query.strip().split()
        return " AND ".join(terms)