import json
from dataclasses import dataclass

@dataclass
class AppConfig:
    root_dir: str
    ignore_dirs: list[str]
    ignore_extensions: list[str]
    db_path: str
    report_format: str

    @staticmethod
    def load(path: str = "config.json") -> "AppConfig":
        with open(path, "r") as f:
            data = json.load(f)
        return AppConfig(
            root_dir=data["root_dir"],
            ignore_dirs=data["ignore_dirs"],
            ignore_extensions=data["ignore_extensions"],
            db_path=data["db_path"],
            report_format=data["report_format"]
        )