from pathlib import Path

class MetadataExtractor:
    def extract(self, path: Path) -> dict:
        stat = path.stat()
        preview = self._get_preview(path)
        return {
            "path": str(path),
            "extension": path.suffix.lower(),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "preview": preview
        }

    def _get_preview(self, path: Path) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 3:
                        break
                    lines.append(line.strip())
            return " | ".join(lines)
        except Exception:
            return ""