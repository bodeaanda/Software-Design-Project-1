from shared.app_config import AppConfig
from shared.db_wrapper import DatabaseWrapper
from indexer.file_scanner import FileScanner
from indexer.file_filter import FileFilter
from indexer.metadata_extractor import MetadataExtractor
from indexer.index_manager import IndexManager
from indexer.progress_reporter import ProgressReporter
from search.query_parser import QueryParser
from search.result_controller import ResultController
from search.preview_formatter import PreviewFormatter

config = AppConfig.load()
db = DatabaseWrapper(config)

reporter = ProgressReporter()
scanner = FileScanner(config, reporter)
file_filter = FileFilter(config)
extractor = MetadataExtractor()
index_manager = IndexManager(db, extractor, reporter)

reporter.start()
for path in scanner.scan():
    if file_filter.should_index(path):
        index_manager.process(path)
print(f"Done!")
reporter.report()

parser = QueryParser()
controller = ResultController(db, parser)
formatter = PreviewFormatter()

print("Search ready. Type a query or 'quit' to exit.")
while True:
    query = input("> ")
    if query.lower() == "quit":
        break
    results = controller.search(query)
    print(formatter.format(results))

db.close()