"""
In-memory cache with write-through strategy.

Maintains in-memory cache of table data for fast access,
with immediate persistence to JSON files.
"""

import threading
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

from .json_writer import JSONWriter
from .session_manager import SessionManager
from ..utils.logger import get_logger, TIMESTAMP_FORMAT

logger = get_logger("cache_manager")


@dataclass
class TableCache:
    """Cache for a single table's data."""

    table_id: int
    data: Dict[str, Any] = field(default_factory=dict)
    dirty: bool = False
    last_sync: Optional[str] = None


class CacheManager:
    """
    In-memory cache manager with write-through strategy.

    Provides fast access to table data while ensuring
    immediate persistence to JSON files (zero data loss).
    """

    def __init__(
        self,
        session_manager: SessionManager,
        json_writer: Optional[JSONWriter] = None,
    ):
        """
        Initialize cache manager.

        Args:
            session_manager: Session manager instance
            json_writer: JSON writer instance
        """
        self.session_manager = session_manager
        self.json_writer = json_writer or JSONWriter()

        # Per-table caches
        self._caches: Dict[int, TableCache] = {}

        # Lock for thread-safe cache access
        self._lock = threading.Lock()

    def initialize_table(self, table_id: int) -> bool:
        """
        Initialize cache for a table.

        Loads existing data from JSON if available.

        Args:
            table_id: Table ID to initialize

        Returns:
            True if initialized successfully
        """
        with self._lock:
            # Register table with session manager
            filepath = self.session_manager.register_table(table_id)

            # Load existing data
            data = self.json_writer.read(filepath, table_id)

            if data is None:
                # Create initial data structure
                data = {
                    "table_id": table_id,
                    "session_start": self.session_manager.session_start,
                    "patterns": "",
                    "rounds": [],
                    "statistics": {
                        "total_rounds": 0,
                        "correct_decisions": 0,
                        "accuracy": 0.0,
                    },
                }

            # Create cache entry
            self._caches[table_id] = TableCache(
                table_id=table_id,
                data=data,
                dirty=False,
                last_sync=datetime.now().strftime(TIMESTAMP_FORMAT),
            )

            logger.info(f"Cache initialized for table {table_id}")
            return True

    def get_table_data(self, table_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached data for a table.

        Args:
            table_id: Table ID

        Returns:
            Table data dictionary or None if not cached
        """
        with self._lock:
            cache = self._caches.get(table_id)
            if cache:
                return cache.data.copy()
            return None

    def update_table_data(
        self,
        table_id: int,
        data: Dict[str, Any],
        flush: bool = True,
    ) -> bool:
        """
        Update cached data for a table.

        Uses write-through strategy: cache updated and
        immediately flushed to JSON.

        Args:
            table_id: Table ID
            data: New data dictionary
            flush: Whether to flush to JSON immediately

        Returns:
            True if update successful
        """
        with self._lock:
            cache = self._caches.get(table_id)
            if not cache:
                logger.warning(f"Table {table_id} not initialized in cache")
                return False

            cache.data = data
            cache.dirty = True

        # Flush to JSON (outside lock to avoid blocking)
        if flush:
            return self.flush_table(table_id)

        return True

    def append_round(
        self,
        table_id: int,
        round_data: Dict[str, Any],
    ) -> bool:
        """
        Append a round to a table's cache and persist.

        Write-through: Updates cache and immediately writes to JSON.

        Args:
            table_id: Table ID
            round_data: Round data dictionary

        Returns:
            True if successful
        """
        filepath = self.session_manager.get_table_file_path(table_id)
        if not filepath:
            logger.error(f"No file path for table {table_id}")
            return False

        # Update cache first
        with self._lock:
            cache = self._caches.get(table_id)
            if cache:
                if "rounds" not in cache.data:
                    cache.data["rounds"] = []
                cache.data["rounds"].append(round_data)
                self._update_statistics(cache.data)
                cache.dirty = True

        # Write to JSON (write-through)
        success = self.json_writer.append_round(filepath, round_data, table_id)

        if success:
            with self._lock:
                cache = self._caches.get(table_id)
                if cache:
                    cache.dirty = False
                    cache.last_sync = datetime.now().strftime(TIMESTAMP_FORMAT)

            logger.debug(
                f"Round appended and persisted for table {table_id}",
                extra={"table_id": table_id},
            )

        return success

    def update_patterns(
        self,
        table_id: int,
        patterns: str,
    ) -> bool:
        """
        Update patterns for a table.

        Args:
            table_id: Table ID
            patterns: Pattern string

        Returns:
            True if successful
        """
        filepath = self.session_manager.get_table_file_path(table_id)
        if not filepath:
            return False

        # Update cache
        with self._lock:
            cache = self._caches.get(table_id)
            if cache:
                cache.data["patterns"] = patterns
                cache.dirty = True

        # Write to JSON
        success = self.json_writer.update_patterns(filepath, patterns, table_id)

        if success:
            with self._lock:
                cache = self._caches.get(table_id)
                if cache:
                    cache.dirty = False
                    cache.last_sync = datetime.now().strftime(TIMESTAMP_FORMAT)

        return success

    def _update_statistics(self, data: Dict[str, Any]) -> None:
        """Update statistics in data dict."""
        rounds = data.get("rounds", [])

        if "statistics" not in data:
            data["statistics"] = {}

        data["statistics"]["total_rounds"] = len(rounds)

        correct = sum(
            1 for r in rounds
            if r.get("result") == "correct"
        )
        total_decisions = sum(
            1 for r in rounds
            if r.get("decision_made") is not None
        )

        data["statistics"]["correct_decisions"] = correct
        data["statistics"]["accuracy"] = (
            round(correct / total_decisions * 100, 2)
            if total_decisions > 0 else 0.0
        )

    def flush_table(self, table_id: int) -> bool:
        """
        Flush table cache to JSON file.

        Args:
            table_id: Table ID to flush

        Returns:
            True if flush successful
        """
        filepath = self.session_manager.get_table_file_path(table_id)
        if not filepath:
            return False

        with self._lock:
            cache = self._caches.get(table_id)
            if not cache:
                return False
            data = cache.data.copy()

        success = self.json_writer.write(filepath, data, table_id)

        if success:
            with self._lock:
                cache = self._caches.get(table_id)
                if cache:
                    cache.dirty = False
                    cache.last_sync = datetime.now().strftime(TIMESTAMP_FORMAT)

        return success

    def flush_all(self) -> int:
        """
        Flush all dirty caches to JSON files.

        Returns:
            Number of tables successfully flushed
        """
        flushed = 0

        with self._lock:
            table_ids = list(self._caches.keys())

        for table_id in table_ids:
            with self._lock:
                cache = self._caches.get(table_id)
                is_dirty = cache.dirty if cache else False

            if is_dirty:
                if self.flush_table(table_id):
                    flushed += 1

        if flushed > 0:
            logger.info(f"Flushed {flushed} table caches")

        return flushed

    def get_rounds(self, table_id: int) -> List[Dict[str, Any]]:
        """
        Get rounds for a table from cache.

        Args:
            table_id: Table ID

        Returns:
            List of round dictionaries
        """
        with self._lock:
            cache = self._caches.get(table_id)
            if cache:
                return cache.data.get("rounds", []).copy()
        return []

    def get_statistics(self, table_id: int) -> Dict[str, Any]:
        """
        Get statistics for a table from cache.

        Args:
            table_id: Table ID

        Returns:
            Statistics dictionary
        """
        with self._lock:
            cache = self._caches.get(table_id)
            if cache:
                return cache.data.get("statistics", {}).copy()
        return {}

    def get_all_table_ids(self) -> List[int]:
        """
        Get all cached table IDs.

        Returns:
            List of table IDs
        """
        with self._lock:
            return list(self._caches.keys())

    def remove_table(self, table_id: int) -> None:
        """
        Remove a table from cache.

        Flushes any dirty data before removal.

        Args:
            table_id: Table ID to remove
        """
        # Flush first
        self.flush_table(table_id)

        with self._lock:
            if table_id in self._caches:
                del self._caches[table_id]
                logger.info(f"Removed table {table_id} from cache")

    def clear(self) -> None:
        """Clear all caches after flushing."""
        self.flush_all()

        with self._lock:
            self._caches.clear()
            logger.info("All caches cleared")
