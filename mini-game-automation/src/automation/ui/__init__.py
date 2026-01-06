"""
Desktop UI module using Tkinter.

Handles main window, table status display, pattern editor,
history viewer, and resource monitoring.
"""

from .main_window import MainWindow, TableConfigWindow

__all__ = [
    "MainWindow",
    "TableConfigWindow",
]
