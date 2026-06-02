from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from search.observer import SearchObserver

DEBUG_WIDGETS = False

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
LOG_EXTENSIONS = {'.log'}


@dataclass
class SearchContext:
    query: str
    parsed: dict
    results: list[dict]

    @property
    def normalized_query(self) -> str:
        return self.query.lower()

    @property
    def result_count(self) -> int:
        return len(self.results)

    def image_results(self) -> list[dict]:
        return [r for r in self.results if r.get("file_type") == "image" or r.get("extension", "").lower() in IMAGE_EXTENSIONS]

    def log_results(self) -> list[dict]:
        return [r for r in self.results if r.get("extension", "").lower() in LOG_EXTENSIONS or r.get("file_type") == "log"]


class ContextAwareWidget(ABC):
    name: str
    description: str

    @abstractmethod
    def can_activate(self, context: SearchContext) -> bool:
        pass

    @abstractmethod
    def activate(self, parent, context: SearchContext):
        pass

    def build_button(self, parent, context: SearchContext):
        import tkinter as tk
        button = tk.Button(
            parent,
            text=self.name,
            command=lambda: self.activate(parent, context),
            bg="#0f3460",
            fg="#DBD56E",
            activebackground="#1a1a2e",
            activeforeground="#FFFFFF",
            relief=tk.RAISED,
            bd=1,
            padx=12,
            pady=8,
            font=("Georgia", 10, "bold")
        )
        return button


class AnalyzeLogsWidget(ContextAwareWidget):
    name = "Analyze Logs"
    description = "Summarize log results."

    def can_activate(self, context: SearchContext) -> bool:
        logs = context.log_results()
        if len(logs) < 2:
            return False
        if len(logs) >= max(1, context.result_count // 3):
            return True
        keywords = ("log", "logs", "error", "exception", "warn", "warning", "trace", "stacktrace")
        return any(term in context.normalized_query for term in keywords)

    def activate(self, parent, context: SearchContext):
        import tkinter as tk
        from tkinter import messagebox
        logs = context.log_results()
        if not logs:
            messagebox.showinfo("Analyze Logs", "No log results available for analysis.")
            return

        window = tk.Toplevel(parent)
        window.title("Log Analysis")
        window.geometry("700x400")
        window.configure(bg="#16213e")

        title = tk.Label(window, text=f"Analyzing {len(logs)} log files", font=("Georgia", 14, "bold"), bg="#16213e", fg="#DBD56E")
        title.pack(pady=10)

        summary = tk.Text(window, bg="#0f3460", fg="#88AB75", font=("Georgia", 10), relief=tk.FLAT)
        summary.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        summary.insert(tk.END, self._format_log_overview(context))
        summary.config(state=tk.DISABLED)

    def _format_log_overview(self, context: SearchContext) -> str:
        logs = context.log_results()
        lines = [f"Found {len(logs)} log entries in the result set.\n"]
        for entry in logs[:10]:
            path = entry.get("path", "Unknown")
            preview = entry.get("preview", "").strip() or "(no preview available)"
            lines.append(f"- {path}\n  Preview: {preview}\n")
        return "\n".join(lines)


class ViewGalleryWidget(ContextAwareWidget):
    name = "View as Gallery"
    description = "Open image results in a gallery-style preview."

    def can_activate(self, context: SearchContext) -> bool:
        images = context.image_results()
        if len(images) < 3:
            return False
        if len(images) >= max(1, context.result_count // 2):
            return True
        keywords = ("image", "images", "photo", "photos", "gallery", "jpg", "jpeg", "png", "gif", "bmp", "webp")
        return any(term in context.normalized_query for term in keywords)

    def activate(self, parent, context: SearchContext):
        import tkinter as tk
        from tkinter import messagebox
        from PIL import Image, ImageTk

        images = context.image_results()
        if not images:
            messagebox.showinfo("View as Gallery", "No image results available.")
            return

        window = tk.Toplevel(parent)
        window.title("Gallery View")
        window.geometry("800x500")
        window.configure(bg="#16213e")

        title = tk.Label(window, text=f"Image Gallery ({len(images)} images)",
                         font=("Georgia", 14, "bold"), bg="#16213e", fg="#DBD56E")
        title.pack(pady=10)

        container = tk.Frame(window, bg="#16213e")
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg="#16213e", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(canvas, bg="#16213e")
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        self._photo_refs = []
        COLS = 4
        THUMB_SIZE = (160, 120)

        for idx, img_data in enumerate(images[:40]):
            path = img_data.get("path", "")
            row, col = divmod(idx, COLS)

            cell = tk.Frame(inner_frame, bg="#0f3460", padx=4, pady=4)
            cell.grid(row=row, column=col, padx=6, pady=6)

            try:
                img = Image.open(path)
                img.thumbnail(THUMB_SIZE)
                photo = ImageTk.PhotoImage(img)
                self._photo_refs.append(photo)

                lbl_img = tk.Label(cell, image=photo, bg="#0f3460")
                lbl_img.pack()
            except Exception:
                lbl_img = tk.Label(cell, text="?", width=14, height=6,
                                   bg="#1a1a2e", fg="#DBD56E", font=("Georgia", 20))
                lbl_img.pack()

            fname = path.split("\\")[-1].split("/")[-1]
            lbl_name = tk.Label(cell, text=fname[:20], bg="#0f3460", fg="#88AB75",
                                font=("Georgia", 8), wraplength=160)
            lbl_name.pack()

        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

    def __repr__(self):
        return f"{self.name}({self.description})"


class WidgetFactory:
    def __init__(self):
        self._widgets = [AnalyzeLogsWidget(), ViewGalleryWidget()]

    def get_active_widgets(self, context: SearchContext) -> list[ContextAwareWidget]:
        return [widget for widget in self._widgets if widget.can_activate(context)]


class WidgetManager(SearchObserver):
    def __init__(self):
        self._factory = WidgetFactory()
        self._active_widgets: list[ContextAwareWidget] = []
        self._context: SearchContext | None = None

    def on_search(self, query: str, results: list[dict]):
        self._context = SearchContext(query=query, parsed={}, results=results)
        self._active_widgets = self._factory.get_active_widgets(self._context)
        if DEBUG_WIDGETS:
            names = [w.name for w in self._active_widgets]
            print(f"[WIDGET] on_search query={query!r} results={len(results)} active={names}")

    def get_active_widgets(self) -> list[ContextAwareWidget]:
        return self._active_widgets

    def get_context(self) -> SearchContext | None:
        return self._context