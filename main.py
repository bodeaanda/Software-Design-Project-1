from shared.app_config import AppConfig
from shared.db_wrapper import DatabaseWrapper
from indexer.file_scanner import FileScanner
from indexer.file_filter import FileFilter
from indexer.metadata_extractor import MetadataExtractor
from indexer.index_manager import IndexManager
from indexer.progress_reporter import ProgressReporter
from search.query_parser import QueryParser
from search.result_controller import ResultController
from search.ranking_strategy import ScoreRanking, AlphabeticalRanking, DateRanking
from search.search_history import SearchHistory
from search.gui import SearchGUI

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
print("Done!")
reporter.report()

parser = QueryParser()
controller = ResultController(db, parser)

history = SearchHistory(db)
controller.add_observer(history)

gui = SearchGUI(controller, history)
gui.run()

db.close()