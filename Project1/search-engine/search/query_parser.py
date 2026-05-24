class QueryParser:
    def parse(self, raw_query: str) -> dict | None:
        path_terms = []
        content_terms = []
        general_terms = []
        color_terms = []

        tokens = raw_query.strip().split()

        if not tokens:
            return None

        for token in tokens:
            if token.startswith("path:"):
                value = token[5:]
                if value:
                    path_terms.append(value)
            elif token.startswith("content:"):
                value = token[8:]
                if value:
                    content_terms.append(value)
            elif token.startswith("color:"):
                value = token[6:]
                if value:
                    color_terms.append(value)
            else:
                general_terms.append(token)

        return {
            "path": path_terms,
            "content": content_terms,
            "general": general_terms,
            "color": color_terms
        }