import time
from pathlib import Path

class FileScorer:
    # important extentsions
    PRIORITY_EXTENSIONS = {
        ".txt": 1.5,
        ".pdf": 1.4,
        ".doc": 1.3,
        ".docx": 1.3,
        ".py": 1.2,
        ".java": 1.2,
        ".md": 1.1,
    }

    def score(self, path: Path, size: int, mtime: float) -> float:
        total_score = 1.0

        # shorter paths 
        path_length = len(path.parts)
        total_score += max(0, 10 - path_length) * 0.1

        # priority extensions
        ext = path.suffix.lower()
        total_score += self.PRIORITY_EXTENSIONS.get(ext, 0)

        # recent files 
        age_days = (time.time() - mtime) / 86400
        if age_days < 7:
            total_score += 1.0
        elif age_days < 30:
            total_score += 0.5
        elif age_days < 90:
            total_score += 0.2

        # file size
        if 100 < size < 100000:
            total_score += 0.3

        return round(total_score, 4)