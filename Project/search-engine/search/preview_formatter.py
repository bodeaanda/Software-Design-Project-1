class PreviewFormatter:
    def format(self, results: list[dict]) -> str:
        if not results:
            return "No results found."
        
        output = []
        for i, r in enumerate(results, 1):
            output.append(f"{i}. {r['path']}")
            output.append(f"   Type: {r['extension']}")
            output.append(f"   Preview: {r['preview']}")
            output.append("")
        return "\n".join(output)