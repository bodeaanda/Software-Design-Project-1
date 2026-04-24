class QueryParser:
    def parse(self, raw_query: str) -> dict:
        path_terms = []
        content_terms = []
        general_terms = []

        tokens = raw_query.strip().split()

        for token in tokens:
            if token.startswith("path:"):
                path_terms.append(token[5:])
            elif token.startswith("content:"):
                content_terms.append(token[8:])
            else:
                general_terms.append(token)

        return {
            "path": path_terms,
            "content": content_terms,
            "general": general_terms
        }