from abc import ABC, abstractmethod
from pathlib import Path
from sys import path

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
    COLOR_MAP = [
        ("red",    (200, 0,   0),   (255, 80,  80)),
        ("green",  (0,   150, 0),   (80,  255, 80)),
        ("blue",   (0,   0,   150), (80,  80,  255)),
        ("yellow", (200, 200, 0),   (255, 255, 80)),
        ("orange", (200, 100, 0),   (255, 180, 80)),
        ("purple", (100, 0,   150), (180, 80,  255)),
        ("pink",   (200, 0,   150), (255, 80,  200)),
        ("brown",  (100, 50,  0),   (180, 120, 80)),
        ("white",  (200, 200, 200), (255, 255, 255)),
        ("black",  (0,   0,   0),   (80,  80,  80)),
        ("gray",   (80,  80,  80),  (200, 200, 200)),
    ]

    def can_process(self, path: Path) -> bool:
        return path.suffix.lower() in self.IMAGE_EXTENSIONS

    def process(self, path: Path) -> dict:
        color = self._extract_dominant_color(path)
        return {
            "type": "image",
            "preview": f"Dominant color: {color}",
            "dominant_color": color
        }

    def _extract_dominant_color(self, path: Path) -> str:
        try:
            from PIL import Image
            img = Image.open(path).convert("RGB")
            img = img.resize((50, 50))  

            pixels = list(img.getdata())
            
            r = sum(p[0] for p in pixels) // len(pixels)
            g = sum(p[1] for p in pixels) // len(pixels)
            b = sum(p[2] for p in pixels) // len(pixels)

            return self._rgb_to_color_name(r, g, b)
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