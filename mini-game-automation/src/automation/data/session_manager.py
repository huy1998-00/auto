"""
Date-based session folder management.

Creates and manages session folders in format:
data/sessions/YYYY-MM-DD_HH-MM-SS/
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

from ..utils.logger import get_logger, TIMESTAMP_FORMAT

logger = get_logger("session_manager")


class SessionManager:
    """
    Manages date-based session folders for data persistence.

    Creates session folders in format: data/sessions/YYYY-MM-DD_HH-MM-SS/
    with per-table JSON files and session configuration.
    """

    # Session folder structure
    DEFAULT_BASE_PATH = "data/sessions"
    SESSION_CONFIG_FILE = "session_config.json"
    TABLE_FILE_PATTERN = "table_{table_id}.json"

    def __init__(
        self,
        base_path: Optional[str] = None,
        max_tables: int = 6,
    ):
        """
        Initialize session manager.

        Args:
            base_path: Base path for sessions directory
            max_tables: Maximum number of tables (default: 6)
        """
        self.base_path = Path(base_path or self.DEFAULT_BASE_PATH)
        self.max_tables = max_tables

        self._current_session_path: Optional[Path] = None
        self._session_start: Optional[str] = None
        self._active_tables: List[int] = []

    @property
    def session_path(self) -> Optional[Path]:
        """Get current session path."""
        return self._current_session_path

    @property
    def session_start(self) -> Optional[str]:
        """Get session start timestamp."""
        return self._session_start

    def create_session(self) -> Path:
        """
        Create a new session folder.

        Creates: data/sessions/YYYY-MM-DD_HH-MM-SS/

        Returns:
            Path to the created session folder
        """
        self._session_start = datetime.now().strftime(TIMESTAMP_FORMAT)
        session_folder = self.base_path / self._session_start

        # Create directory structure
        session_folder.mkdir(parents=True, exist_ok=True)

        self._current_session_path = session_folder
        self._active_tables = []

        logger.info(f"Created session: {session_folder}")

        # Create initial session config
        self._write_session_config()

        return session_folder

    def _write_session_config(self) -> None:
        """Write session configuration file."""
        if not self._current_session_path:
            return

        config = {
            "session_start": self._session_start,
            "session_end": None,
            "tables_active": self._active_tables,
            "max_tables": self.max_tables,
            "settings": {
                "screenshot_interval_fast": 100,
                "screenshot_interval_normal": 200,
            },
        }

        config_path = self._current_session_path / self.SESSION_CONFIG_FILE

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def get_table_file_path(self, table_id: int) -> Optional[Path]:
        """
        Get the JSON file path for a table.

        Args:
            table_id: Table ID (1-6)

        Returns:
            Path to table JSON file, or None if no session
        """
        if not self._current_session_path:
            return None

        return self._current_session_path / self.TABLE_FILE_PATTERN.format(table_id=table_id)

    def register_table(self, table_id: int) -> Path:
        """
        Register a table for the current session.

        Creates the table JSON file if it doesn't exist.

        Args:
            table_id: Table ID to register

        Returns:
            Path to the table JSON file

        Raises:
            RuntimeError: If no session is active
        """
        if not self._current_session_path:
            raise RuntimeError("No active session. Call create_session() first.")

        if table_id not in self._active_tables:
            self._active_tables.append(table_id)
            self._write_session_config()

        table_path = self.get_table_file_path(table_id)

        # Create initial table file if it doesn't exist
        if not table_path.exists():
            initial_data = {
                "table_id": table_id,
                "session_start": self._session_start,
                "patterns": "",
                "rounds": [],
                "statistics": {
                    "total_rounds": 0,
                    "correct_decisions": 0,
                    "accuracy": 0.0,
                },
            }

            with open(table_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

            logger.info(f"Registered table {table_id} for session")

        return table_path

    def unregister_table(self, table_id: int) -> None:
        """
        Unregister a table from the session.

        Args:
            table_id: Table ID to unregister
        """
        if table_id in self._active_tables:
            self._active_tables.remove(table_id)
            self._write_session_config()
            logger.info(f"Unregistered table {table_id}")

    def end_session(self) -> None:
        """
        End the current session.

        Updates session_config.json with end timestamp.
        """
        if not self._current_session_path:
            return

        # Update session config with end time
        config_path = self._current_session_path / self.SESSION_CONFIG_FILE

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            config["session_end"] = datetime.now().strftime(TIMESTAMP_FORMAT)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Session ended: {self._current_session_path}")

        except Exception as e:
            logger.error(f"Failed to update session config: {e}")

        self._current_session_path = None
        self._session_start = None
        self._active_tables = []

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions.

        Returns:
            List of session info dictionaries
        """
        sessions = []

        if not self.base_path.exists():
            return sessions

        for session_dir in sorted(self.base_path.iterdir(), reverse=True):
            if session_dir.is_dir():
                config_path = session_dir / self.SESSION_CONFIG_FILE

                session_info = {
                    "path": str(session_dir),
                    "name": session_dir.name,
                }

                if config_path.exists():
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                        session_info.update(config)
                    except Exception:
                        pass

                sessions.append(session_info)

        return sessions

    def load_session(self, session_path: str) -> bool:
        """
        Load an existing session.

        Args:
            session_path: Path to session folder

        Returns:
            True if loaded successfully, False otherwise
        """
        session_dir = Path(session_path)

        if not session_dir.exists():
            logger.error(f"Session not found: {session_path}")
            return False

        config_path = session_dir / self.SESSION_CONFIG_FILE

        if not config_path.exists():
            logger.error(f"Session config not found: {config_path}")
            return False

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            self._current_session_path = session_dir
            self._session_start = config.get("session_start")
            self._active_tables = config.get("tables_active", [])

            logger.info(f"Loaded session: {session_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False

    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about current session.

        Returns:
            Dictionary with session info, or None if no active session
        """
        if not self._current_session_path:
            return None

        return {
            "path": str(self._current_session_path),
            "session_start": self._session_start,
            "active_tables": self._active_tables.copy(),
            "max_tables": self.max_tables,
        }

    def cleanup_old_sessions(
        self,
        keep_count: int = 10,
    ) -> int:
        """
        Remove old sessions, keeping only the most recent ones.

        Args:
            keep_count: Number of recent sessions to keep

        Returns:
            Number of sessions removed
        """
        import shutil

        sessions = self.list_sessions()

        if len(sessions) <= keep_count:
            return 0

        removed = 0
        sessions_to_remove = sessions[keep_count:]

        for session in sessions_to_remove:
            try:
                shutil.rmtree(session["path"])
                removed += 1
                logger.info(f"Removed old session: {session['name']}")
            except Exception as e:
                logger.error(f"Failed to remove session: {e}")

        return removed
