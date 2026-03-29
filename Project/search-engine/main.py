from shared.app_config import AppConfig
from indexer.file_scanner import FileScanner

config = AppConfig.load()
scanner = FileScanner(config)

for path in scanner.scan():
    print(path)