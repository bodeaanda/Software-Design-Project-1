from abc import ABC, abstractmethod
from pathlib import Path


class FileProcessor(ABC):

    @abstractmethod
    def can_process(self, path: Path) -> bool:
        pass

    @abstractmethod
    def process(self, path: Path) -> dict:
        pass


class TextFileProcessor(FileProcessor):

    TEXT_EXTENSIONS = {'.txt', '.py', '.java', '.md', '.json', '.xml',
                       '.csv', '.html', '.css', '.js', '.ino', '.c', '.cpp'}

    def can_process(self, path: Path) -> bool:
        return path.suffix.lower() in self.TEXT_EXTENSIONS

    def process(self, path: Path) -> dict:
        preview = self._get_preview(path)
        return {
            "type": "text",
            "preview": preview,
            "dominant_color": None
        }

    def _get_preview(self, path: Path) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 3:
                        break
                    stripped = line.strip()
                    if len(stripped) > 100:
                        stripped = stripped[:100] + "..."
                    lines.append(stripped)
            return " | ".join(lines)
        except Exception:
            return ""


class ImageFileProcessor(FileProcessor):

    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

    def can_process(self, path: Path) -> bool:
        return path.suffix.lower() in self.IMAGE_EXTENSIONS

    def process(self, path: Path) -> dict:
        color = self._extract_dominant_color(path)
        return {
            "type": "image",
            "preview": f"[Image] dominant color: {color}",
            "dominant_color": color
        }

    def _extract_dominant_color(self, path: Path) -> str:
        try:
            from PIL import Image
            from collections import Counter

            img = Image.open(path).convert("RGBA")
            img = img.resize((50, 50))
            pixels = list(img.getdata())

            # ignora pixelii transparenti (alpha < 30)
            visible = [(r, g, b) for r, g, b, a in pixels if a > 30]
            if not visible:
                visible = [(r, g, b) for r, g, b, a in pixels]

            # cuantizeaza la 8 nivele pentru a grupa culorile similare
            quantized = [(r // 32 * 32, g // 32 * 32, b // 32 * 32) for r, g, b in visible]
            most_common = Counter(quantized).most_common(5)

            # voteaza culoarea dominanta dintre top 5
            votes: Counter = Counter()
            for (r, g, b), count in most_common:
                color = self._rgb_to_color_name(r, g, b)
                votes[color] += count

            return votes.most_common(1)[0][0]

        except Exception as e:
            print(f"[IMAGE ERROR] {path}: {e}")
            return "unknown"

    def _rgb_to_color_name(self, r: int, g: int, b: int) -> str:
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val

        if diff < 30:
            if max_val > 200:
                return "white"
            elif max_val < 80:
                return "black"
            else:
                return "gray"

        if r == max_val and r > g + 30 and r > b + 30:
            if g > 150:
                return "yellow"
            elif g > 80:
                return "orange"
            else:
                return "red"
        elif g == max_val and g > r + 30 and g > b + 30:
            return "green"
        elif b == max_val and b > r + 30 and b > g + 30:
            return "blue"
        elif r > 150 and b > 150 and g < 100:
            return "purple"
        elif r > 150 and b > 100 and g < 80:
            return "pink"

        return "mixed"