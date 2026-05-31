# Changelog

## [3.0.0] - May 2026

### Added
- Multimodal Search: image processor that extracts dominant color from image files
- Color query support using Strategy Pattern
- Strategy Pattern for file processing: TextFileProcessor and ImageFileProcessor
- Context-Aware Widgets: WidgetFactory activates Gallery or Analyze Logs widget based on result set
- Observer pattern integration for widget activation on search results
- Query Pre-Processor Pipeline using Decorator Pattern:
  - SanitizationDecorator: strips special characters that break FTS syntax
  - SynonymDecorator: expands terms to standard equivalents 
  - LogicDecorator: adds wildcards for prefix matching 
- Producer-Consumer indexing architecture with multiple reader threads and single writer thread
- Queue-based synchronization between readers and writer to avoid race conditions

### Fixed
- typo_search now returns file_type and dominant_color fields

## [2.0.0] - April 2026

### Added
- Query parser supporting path: and content: qualifiers
- File scoring system computed at index time based on path length, file size, and modification time
- Swappable ranking strategies toggleable without changing core engine
- Search history tracking using Observer pattern
- Query autocomplete suggestions based on search history
- Typo-tolerant search using Levenshtein distance as fallback when no exact results found

## [1.0.0] - April 2026

### Added
- Recursive file traversal with configurable root directory
- SQLite database with FTS5 virtual table for full-text search
- File metadata storage: path, extension, size, modification time
- File preview extraction 
- Incremental indexing: only re-indexes files that have changed 
- Runtime configuration via config.json (root_dir, ignore_dirs, ignore_extensions, db_path)
- Progress reporting during indexing with error logging
- Handling of permission errors and inaccessible files