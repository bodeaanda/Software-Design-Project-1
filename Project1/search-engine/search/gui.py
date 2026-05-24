import tkinter as tk
from tkinter import ttk
from search.result_controller import ResultController
from search.search_history import SearchHistory
from search.ranking_strategy import ScoreRanking, AlphabeticalRanking, DateRanking
from search.widgets import WidgetManager

BG_DARK = "#1a1a2e"
BG_MEDIUM = "#16213e"
BG_LIGHT = "#0f3460"
C_YELLOW = "#DBD56E"
C_GREEN = "#88AB75"
C_BLUE = "#2D93AD"
C_GRAY = "#7D7C84"
C_ORANGE = "#DE8F6E"

class SearchGUI:
    def __init__(self, controller: ResultController, history: SearchHistory, widget_manager: WidgetManager):
        self._controller = controller
        self._history = history
        self._widget_manager = widget_manager

        self._window = tk.Tk()
        self._window.title("Local Search Engine")
        self._window.geometry("900x600")
        self._window.configure(bg=BG_DARK)

        self._build_ui()

    def _build_ui(self):
        # title
        title = tk.Label(self._window, text="Local Search Engine",
                        font=("Georgia", 22, "bold"),
                        bg=BG_DARK, fg=C_YELLOW)
        title.pack(pady=10)

        # search bar frame
        search_frame = tk.Frame(self._window, bg=BG_MEDIUM)
        search_frame.pack(fill=tk.X, padx=20)

        self._search_var = tk.StringVar()
        self._search_var.trace("w", self._on_type)

        search_entry = tk.Entry(search_frame, textvariable=self._search_var,
                               font=("Georgia", 14),
                               bg=BG_MEDIUM, fg=C_GREEN,
                               insertbackground=C_YELLOW,
                               relief=tk.FLAT, bd=10)
        search_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        search_entry.focus()

        # ranking dropdown
        self._ranking_var = tk.StringVar(value="Score")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                       fieldbackground=BG_LIGHT,
                       background=BG_LIGHT,
                       foreground=C_YELLOW,
                       selectbackground=BG_LIGHT,
                       selectforeground=C_YELLOW)
        ranking_menu = ttk.Combobox(search_frame,
                                   textvariable=self._ranking_var,
                                   font=("Georgia", 12),
                                   values=["Score", "Alphabetical", "Date"],
                                   width=15, state="readonly")
        ranking_menu.pack(side=tk.LEFT, padx=10)
        ranking_menu.bind("<<ComboboxSelected>>", self._on_ranking_change)

        # suggestions label
        self._suggestions_var = tk.StringVar()
        suggestions_label = tk.Label(self._window,
                                    textvariable=self._suggestions_var,
                                    font=("Georgia", 10, "italic"),
                                    bg=BG_DARK, fg=C_GRAY)
        suggestions_label.pack(anchor=tk.W, padx=20)

        # results count
        self._count_var = tk.StringVar(value="")
        count_label = tk.Label(self._window,
                              textvariable=self._count_var,
                              font=("Georgia", 10),
                              bg=BG_DARK, fg=C_GRAY)
        count_label.pack(anchor=tk.W, padx=20)

        # action widgets for context-aware suggestions
        self._widget_frame = tk.Frame(self._window, bg=BG_DARK)
        self._widget_frame.pack(fill=tk.X, padx=20, pady=(5, 0))

        # results list
        results_frame = tk.Frame(self._window, bg=BG_DARK)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._results_list = tk.Text(results_frame,
                                    font=("Georgia", 11),
                                    bg=BG_MEDIUM, fg=C_GREEN,
                                    relief=tk.FLAT,
                                    yscrollcommand=scrollbar.set,
                                    state=tk.DISABLED)
        self._results_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._results_list.yview)

        # tags for coloring
        self._results_list.tag_config("path", foreground=C_BLUE)
        self._results_list.tag_config("type", foreground=C_GREEN)
        self._results_list.tag_config("preview", foreground=C_ORANGE)
        self._results_list.tag_config("score", foreground=C_YELLOW)
        self._results_list.tag_config("date", foreground=C_GRAY)

    def _on_type(self, *args):
        query = self._search_var.get().strip()

        if not query:
            self._clear_results()
            self._suggestions_var.set("")
            self._count_var.set("")
            return

        suggestions = self._history.get_suggestions(query)
        if suggestions:
            self._suggestions_var.set(f"Suggestions: {', '.join(suggestions)}")
        else:
            self._suggestions_var.set("")

        results = self._controller.search(query)
        self._count_var.set(f"{len(results)} results found")
        self._display_results(results)

    def _on_ranking_change(self, *args):
        choice = self._ranking_var.get()
        if choice == "Score":
            self._controller.set_ranking(ScoreRanking())
        elif choice == "Alphabetical":
            self._controller.set_ranking(AlphabeticalRanking())
        elif choice == "Date":
            self._controller.set_ranking(DateRanking())
        self._on_type()

    def _display_results(self, results: list[dict]):
        self._results_list.config(state=tk.NORMAL)
        self._results_list.delete(1.0, tk.END)

        for i, r in enumerate(results, 1):
            from datetime import datetime
            mtime = r.get("mtime", 0)
            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M") if mtime else "N/A"

            self._results_list.insert(tk.END, f"{i}. ", "path")
            self._results_list.insert(tk.END, f"{r['path']}\n", "path")
            self._results_list.insert(tk.END, f"   Type: {r['extension']}\n", "type")
            self._results_list.insert(tk.END, f"   Preview: {r.get('preview', '')}\n", "preview")
            self._results_list.insert(tk.END, f"   Score: {r.get('score', 0)}\n", "score")
            self._results_list.insert(tk.END, f"   Last Modified: {date_str}\n\n", "date")

        self._results_list.config(state=tk.DISABLED)
        self._update_widgets(results)

    def _update_widgets(self, results: list[dict]):
        for child in self._widget_frame.winfo_children():
            child.destroy()

        active_widgets = self._widget_manager.get_active_widgets()
        print(f"[GUI] _update_widgets -> found {len(active_widgets)} active widgets")
        if not active_widgets:
            return

        context = self._widget_manager.get_context()
        if not context:
            return

        label = tk.Label(self._widget_frame,
                         text="Suggested actions:",
                         font=("Georgia", 10, "bold"),
                         bg=BG_DARK,
                         fg=C_YELLOW)
        label.pack(anchor=tk.W)

        try:
            names = ", ".join([w.name for w in active_widgets])
            debug_label = tk.Label(self._widget_frame, text=f"Active: {names}", font=("Georgia", 9), bg=BG_DARK, fg=C_GRAY)
            debug_label.pack(anchor=tk.W)
        except Exception:
            pass

        action_frame = tk.Frame(self._widget_frame, bg=BG_DARK)
        action_frame.pack(anchor=tk.W, pady=(5, 0))

        for widget in active_widgets:
            button = widget.build_button(action_frame, context)
            button.pack(side=tk.LEFT, padx=5)

    def _clear_results(self):
        self._results_list.config(state=tk.NORMAL)
        self._results_list.delete(1.0, tk.END)
        self._results_list.config(state=tk.DISABLED)

        for child in self._widget_frame.winfo_children():
            child.destroy()

    def run(self):
        self._window.mainloop()