from shared.app_config import AppConfig
from indexer.file_scanner import FileScanner
from indexer.file_filter import FileFilter
from indexer.metadata_extractor import MetadataExtractor

config = AppConfig.load()
scanner = FileScanner(config)
file_filter = FileFilter(config)
extractor = MetadataExtractor()

for path in scanner.scan():
    if file_filter.should_index(path):
        metadata = extractor.extract(path)
        print(metadata)
        break  # just test on the first file for now