"""
Thread-safe JSON file writing using portalocker.

Ensures safe concurrent writes from multiple table threads.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import portalocker

from ..utils.logger import get_logger

logger = get_logger("json_writer")


class JSONWriter:
    """
    Thread-safe JSON file writer using portalocker.

    Uses file locking to ensure safe concurrent writes
    from multiple table threads.
    """

    # Lock timeout in seconds
    DEFAULT_TIMEOUT = 5.0

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize JSON writer.

        Args:
            timeout: Lock acquisition timeout in seconds
        """
        self.timeout = timeout

    def write(
        self,
        filepath: Path,
        data: Dict[str, Any],
        table_id: Optional[int] = None,
    ) -> bool:
        """
        Write data to JSON file with file locking.

        Args:
            filepath: Path to JSON file
            data: Dictionary data to write
            table_id: Table ID for logging

        Returns:
            True if write successful, False otherwise
        """
        filepath = Path(filepath)

        try:
            # Ensure parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Open file with exclusive lock
            with portalocker.Lock(
                str(filepath),
                mode="w",
                timeout=self.timeout,
                flags=portalocker.LOCK_EX,
            ) as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(
                f"Wrote JSON to {filepath}",
                extra={"table_id": table_id} if table_id else {},
            )
            return True

        except portalocker.LockException as e:
            logger.error(
                f"Failed to acquire lock for {filepath}: {e}",
                extra={"table_id": table_id} if table_id else {},
            )
            return False

        except Exception as e:
            logger.error(
                f"Failed to write JSON to {filepath}: {e}",
                extra={"table_id": table_id} if table_id else {},
            )
            return False

    def read(
        self,
        filepath: Path,
        table_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Read data from JSON file with file locking.

        Args:
            filepath: Path to JSON file
            table_id: Table ID for logging

        Returns:
            Dictionary data or None if read failed
        """
        filepath = Path(filepath)

        if not filepath.exists():
            logger.warning(
                f"JSON file not found: {filepath}",
                extra={"table_id": table_id} if table_id else {},
            )
            return None

        try:
            # Open file with shared lock (multiple readers allowed)
            with portalocker.Lock(
                str(filepath),
                mode="r",
                timeout=self.timeout,
                flags=portalocker.LOCK_SH,
            ) as f:
                data = json.load(f)

            return data

        except portalocker.LockException as e:
            logger.error(
                f"Failed to acquire lock for {filepath}: {e}",
                extra={"table_id": table_id} if table_id else {},
            )
            return None

        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON in {filepath}: {e}",
                extra={"table_id": table_id} if table_id else {},
            )
            return None

        except Exception as e:
            logger.error(
                f"Failed to read JSON from {filepath}: {e}",
                extra={"table_id": table_id} if table_id else {},
            )
            return None

    def update(
        self,
        filepath: Path,
        update_func,
        table_id: Optional[int] = None,
    ) -> bool:
        """
        Read, update, and write JSON file atomically.

        Args:
            filepath: Path to JSON file
            update_func: Function that takes data dict and returns updated dict
            table_id: Table ID for logging

        Returns:
            True if update successful, False otherwise
        """
        filepath = Path(filepath)

        try:
            # Open file with exclusive lock for read-modify-write
            with portalocker.Lock(
                str(filepath),
                mode="r+",
                timeout=self.timeout,
                flags=portalocker.LOCK_EX,
            ) as f:
                # Read current data
                data = json.load(f)

                # Apply update function
                updated_data = update_func(data)

                # Seek to beginning and truncate
                f.seek(0)
                f.truncate()

                # Write updated data
                json.dump(updated_data, f, indent=2, ensure_ascii=False)

            logger.debug(
                f"Updated JSON at {filepath}",
                extra={"table_id": table_id} if table_id else {},
            )
            return True

        except FileNotFoundError:
            logger.warning(
                f"JSON file not found for update: {filepath}",
                extra={"table_id": table_id} if table_id else {},
            )
            return False

        except portalocker.LockException as e:
            logger.error(
                f"Failed to acquire lock for update {filepath}: {e}",
                extra={"table_id": table_id} if table_id else {},
            )
            return False

        except Exception as e:
            logger.error(
                f"Failed to update JSON at {filepath}: {e}",
                extra={"table_id": table_id} if table_id else {},
            )
            return False

    def append_round(
        self,
        filepath: Path,
        round_data: Dict[str, Any],
        table_id: Optional[int] = None,
    ) -> bool:
        """
        Append a round to the rounds array in a table JSON file.

        Args:
            filepath: Path to table JSON file
            round_data: Round data dictionary
            table_id: Table ID for logging

        Returns:
            True if append successful, False otherwise
        """
        def update_func(data: Dict[str, Any]) -> Dict[str, Any]:
            if "rounds" not in data:
                data["rounds"] = []
            data["rounds"].append(round_data)

            # Update statistics
            if "statistics" not in data:
                data["statistics"] = {}

            data["statistics"]["total_rounds"] = len(data["rounds"])

            # Count correct decisions
            correct = sum(
                1 for r in data["rounds"]
                if r.get("result") == "correct"
            )
            total_decisions = sum(
                1 for r in data["rounds"]
                if r.get("decision_made") is not None
            )

            data["statistics"]["correct_decisions"] = correct
            data["statistics"]["accuracy"] = (
                round(correct / total_decisions * 100, 2)
                if total_decisions > 0 else 0.0
            )

            return data

        return self.update(filepath, update_func, table_id)

    def update_patterns(
        self,
        filepath: Path,
        patterns: str,
        table_id: Optional[int] = None,
    ) -> bool:
        """
        Update patterns in a table JSON file.

        Args:
            filepath: Path to table JSON file
            patterns: Pattern string
            table_id: Table ID for logging

        Returns:
            True if update successful, False otherwise
        """
        def update_func(data: Dict[str, Any]) -> Dict[str, Any]:
            data["patterns"] = patterns
            return data

        return self.update(filepath, update_func, table_id)
