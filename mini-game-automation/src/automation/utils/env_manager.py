"""
Environment variable manager for .env file.

Handles loading and saving GAME_URL and other settings.
"""

import os
from pathlib import Path
from typing import Optional, Dict
import re

from .logger import get_logger

logger = get_logger("env_manager")


class EnvManager:
    """Manages .env file for application settings."""

    ENV_FILE = ".env"

    @classmethod
    def load_env(cls, env_file: Optional[str] = None) -> Dict[str, str]:
        """
        Load environment variables from .env file.

        Args:
            env_file: Path to .env file (default: .env in current directory)

        Returns:
            Dictionary of environment variables
        """
        env_file = Path(env_file or cls.ENV_FILE)
        env_vars = {}

        if not env_file.exists():
            logger.debug(f".env file not found: {env_file}")
            return env_vars

        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Parse KEY=VALUE format
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        env_vars[key] = value

            logger.debug(f"Loaded {len(env_vars)} variables from {env_file}")
            return env_vars

        except Exception as e:
            logger.error(f"Failed to load .env file: {e}")
            return env_vars

    @classmethod
    def get(cls, key: str, default: Optional[str] = None, env_file: Optional[str] = None) -> Optional[str]:
        """
        Get an environment variable from .env file or system environment.

        Args:
            key: Environment variable key
            default: Default value if not found
            env_file: Path to .env file

        Returns:
            Value of the environment variable or default
        """
        # First check system environment
        value = os.getenv(key)
        if value:
            return value

        # Then check .env file
        env_vars = cls.load_env(env_file)
        return env_vars.get(key, default)

    @classmethod
    def set(cls, key: str, value: str, env_file: Optional[str] = None) -> bool:
        """
        Set an environment variable in .env file.

        Args:
            key: Environment variable key
            value: Value to set
            env_file: Path to .env file

        Returns:
            True if saved successfully, False otherwise
        """
        env_file = Path(env_file or cls.ENV_FILE)

        try:
            # Load existing variables
            env_vars = cls.load_env(env_file) if env_file.exists() else {}

            # Update the variable
            env_vars[key] = value

            # Write back to file
            with open(env_file, "w", encoding="utf-8") as f:
                # Write header comment
                f.write("# Mini-Game Automation Configuration\n")
                f.write("# Auto-generated - Edit via UI or manually\n\n")

                # Write variables
                for k, v in env_vars.items():
                    # Escape special characters in value
                    if " " in v or "#" in v or "=" in v:
                        v = f'"{v}"'
                    f.write(f"{k}={v}\n")

            logger.info(f"Saved {key} to {env_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save {key} to .env file: {e}")
            return False

    @classmethod
    def load_game_url(cls) -> Optional[str]:
        """Load GAME_URL from .env file or environment."""
        return cls.get("GAME_URL")

    @classmethod
    def save_game_url(cls, url: str) -> bool:
        """Save GAME_URL to .env file."""
        return cls.set("GAME_URL", url)
