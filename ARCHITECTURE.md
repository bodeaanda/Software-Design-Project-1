# Software Architecture: Local Search Engine

## Overview
This document outlines the architecture for a local file search system designed to index documents, media, and binaries with high responsiveness. The design follows the **C4 model**—System Context, Containers, and Components and Classes (or Code) to ensure clear boundaries and minimize the cost of future changes.

---

## 1. Level 1: System Context
The System Context diagram provides a "big picture" view of the system's landscape, focusing on people and software systems rather than technical protocols.

* **User**: Interacts with the search bar to find local files and view contextual previews.
* **Search Engine (This System)**: Indexes local content and provides fast, responsive information retrieval.
* **Local File System**: The external source of data (documents, media, binaries) that the system crawls.

![System Context Diagram](.\Assignment1\c4-Context.drawio.png)

---

## 2. Level 2: Containers
This level illustrates the high-level technology choices and how responsibilities are distributed across separately deployable units.

* **Search CLI/GUI (Desktop App)**: The entry point that captures queries as the user types and displays results.
* **Indexer (Console App)**: A background unit that crawls the file system recursively and filters unwanted data.
* **Database (DBMS)**: A relational or NoSQL database used to store file metadata, content, and the search index.
* **File System (External)**: The local storage where raw files reside.

![Container Diagram](.\Assignment1\c4-Container.drawio.png)

---

## 3. Level 3: Components
This level zooms into the internal structural building blocks of the containers.

### Indexer Components
* **File Traverser**: Recursively walks directories and handles edge cases like symlink loops or permission issues.
* **File Filter**: Excludes unwanted data based on runtime ignore rules or file types.
* **Incremental Manager**: Tracks file changes to update only modified records instead of rebuilding the entire index.
* **Content Extractor**: Reads file content and prepares the first 3 lines for mandatory previews.
* **DB Client**: Maps extracted metadata and content into the database schema.

### Search CLI/GUI Components
* **Query Parser**: Converts user input into optimized SQL or Full-Text Search (FTS) queries.
* **Result Controller**: An asynchronous coordinator that fetches data from the database as the user types.
* **Preview Formatter**: Formats the raw data and contextual snippets into a user-friendly view.
* **Configuration Manager**: Allows runtime configuration of ignore rules and root directories.

![Component Diagram](.\Assignment1\c4-Components.drawio.png)

---
## 4. Level 4: Code (Class Diagram)
This level zooms in on the **Indexer** component to show how the classes interact to handle file discovery, metadata extraction, and incremental updates.

### Key Classes
* **`FileScanner`**: Implements the recursive traversal logic. It interacts with the OS to list files and manages the "ignore" list to skip binaries or hidden folders.
* **`MetadataExtractor`**: A class dedicated to pulling specific info from files, such as `mtime` (last modified), file extension, and the first 3 lines of text for the preview.
* **`IndexManager`**: The core logic for incremental indexing. It compares the current file's state against the database record to decide if an update is needed.
* **`DatabaseWrapper`**: An abstraction layer (likely using an ORM or direct SQL) that handles the `INSERT` and `UPDATE` operations into the DBMS.

### Class Relationships
1.  The `FileScanner` identifies a file and passes the path to the `IndexManager`.
2.  The `IndexManager` queries the `DatabaseWrapper` to check if the file is already known.
3.  If the file is new or modified, the `MetadataExtractor` is called to parse the content.
4.  The final data object is passed back to the `DatabaseWrapper` to be persisted.