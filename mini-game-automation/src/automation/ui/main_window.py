"""
Main desktop UI window using Tkinter.

Provides game URL input, pattern editor, table configuration,
and real-time status monitoring.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, Any, Callable
import threading
import queue
import asyncio
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.env_manager import EnvManager
from .coordinate_picker import CoordinatePicker

logger = get_logger("ui.main_window")


class MainWindow:
    """
    Main application window with all UI components.

    Features:
    - Game URL configuration
    - Pattern editor with validation
    - Table coordinates configuration
    - Real-time status display
    - Control buttons (start/stop, pause/resume)
    """

    def __init__(
        self,
        on_open_browser: Optional[Callable] = None,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_pattern_update: Optional[Callable] = None,
        on_coordinates_update: Optional[Callable] = None,
    ):
        """
        Initialize main window.

        Args:
            on_open_browser: Callback when open browser button clicked (game_url)
            on_start: Callback when start button clicked
            on_stop: Callback when stop button clicked
            on_pattern_update: Callback when patterns updated (table_id, patterns)
            on_coordinates_update: Callback when coordinates updated (table_id, coords)
        """
        self.root = tk.Tk()
        self.root.title("Mini-Game Automation Tool")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Callbacks
        self.on_open_browser = on_open_browser
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_pattern_update = on_pattern_update
        self.on_coordinates_update = on_coordinates_update

        # State
        self.is_running = False
        self.browser_opened = False
        self.ui_queue = queue.Queue()
        self.table_status_vars: Dict[int, Dict[str, tk.StringVar]] = {}

        # Create UI components
        self._create_widgets()

        # Start UI update loop
        self._update_ui_loop()

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Top section: Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)

        # Game URL input - Load from .env if available
        ttk.Label(config_frame, text="Game URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        saved_url = EnvManager.load_game_url() or "https://your-game-url.com"
        self.game_url_var = tk.StringVar(value=saved_url)
        game_url_entry = ttk.Entry(config_frame, textvariable=self.game_url_var, width=50)
        game_url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Step 1: Open Browser button
        self.open_browser_button = ttk.Button(
            config_frame,
            text="1. Open Browser",
            command=self._on_open_browser_clicked,
        )
        self.open_browser_button.grid(row=0, column=2, padx=(0, 5))

        # Browser status
        self.browser_status_var = tk.StringVar(value="Browser: Not opened")
        ttk.Label(
            config_frame,
            textvariable=self.browser_status_var,
            font=("TkDefaultFont", 9),
            foreground="gray",
        ).grid(row=0, column=3, padx=(5, 0))

        # Control buttons
        control_frame = ttk.Frame(config_frame)
        control_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky=tk.W)

        ttk.Label(
            control_frame,
            text="Step 2: Configure →",
            font=("TkDefaultFont", 9),
        ).grid(row=0, column=0, padx=(0, 5))

        self.configure_tables_button = ttk.Button(
            control_frame,
            text="Configure Tables",
            command=self._open_table_config,
            state=tk.DISABLED,
        )
        self.configure_tables_button.grid(row=0, column=1, padx=(0, 5))

        ttk.Label(
            control_frame,
            text="Step 3: Start →",
            font=("TkDefaultFont", 9),
        ).grid(row=0, column=2, padx=(10, 5))

        self.start_button = ttk.Button(
            control_frame,
            text="Start Automation",
            command=self._on_start_clicked,
            state=tk.DISABLED,
        )
        self.start_button.grid(row=0, column=3, padx=(0, 5))

        self.stop_button = ttk.Button(
            control_frame,
            text="Stop Automation",
            command=self._on_stop_clicked,
            state=tk.DISABLED,
        )
        self.stop_button.grid(row=0, column=4, padx=(0, 5))

        # Left panel: Pattern Editor
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)

        pattern_frame = ttk.LabelFrame(left_panel, text="Pattern Editor", padding="10")
        pattern_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        pattern_frame.columnconfigure(0, weight=1)

        # Table selection for patterns
        ttk.Label(pattern_frame, text="Table:").grid(row=0, column=0, sticky=tk.W)
        self.pattern_table_var = tk.IntVar(value=1)
        pattern_table_combo = ttk.Combobox(
            pattern_frame,
            textvariable=self.pattern_table_var,
            values=list(range(1, 7)),
            state="readonly",
            width=10,
        )
        pattern_table_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        pattern_table_combo.bind("<<ComboboxSelected>>", self._on_pattern_table_changed)

        # Pattern input
        ttk.Label(pattern_frame, text="Patterns:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        pattern_help = ttk.Label(
            pattern_frame,
            text="Format: BBP-P;BPB-B (B=Red, P=Blue)",
            font=("TkDefaultFont", 8),
            foreground="gray",
        )
        pattern_help.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))

        self.pattern_text = scrolledtext.ScrolledText(
            pattern_frame,
            height=4,
            width=40,
            wrap=tk.WORD,
        )
        self.pattern_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.pattern_text.insert("1.0", "BBP-P;BPB-B;BBB-P")

        # Pattern buttons
        pattern_buttons = ttk.Frame(pattern_frame)
        pattern_buttons.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        ttk.Button(
            pattern_buttons,
            text="Validate",
            command=self._validate_pattern,
        ).grid(row=0, column=0, padx=(0, 5))

        ttk.Button(
            pattern_buttons,
            text="Save Pattern",
            command=self._save_pattern,
        ).grid(row=0, column=1, padx=(0, 5))

        ttk.Button(
            pattern_buttons,
            text="Help",
            command=self._show_pattern_help,
        ).grid(row=0, column=2)

        self.pattern_status_var = tk.StringVar(value="")
        ttk.Label(
            pattern_frame,
            textvariable=self.pattern_status_var,
            foreground="green",
            font=("TkDefaultFont", 9),
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # Table Status Display
        status_frame = ttk.LabelFrame(left_panel, text="Table Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)

        # Create status display for each table
        self.status_canvas = tk.Canvas(status_frame, height=400)
        self.status_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_canvas.yview)
        self.status_scrollable_frame = ttk.Frame(self.status_canvas)

        self.status_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.status_canvas.configure(scrollregion=self.status_canvas.bbox("all"))
        )

        self.status_canvas.create_window((0, 0), window=self.status_scrollable_frame, anchor="nw")
        self.status_canvas.configure(yscrollcommand=self.status_scrollbar.set)

        self.status_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        status_frame.rowconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)

        # Create status widgets for each table
        self._create_table_status_widgets()

        # Right panel: Logs and Info
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)

        # Resource Monitor
        resource_frame = ttk.LabelFrame(right_panel, text="Resource Monitor", padding="10")
        resource_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        resource_frame.columnconfigure(0, weight=1)

        self.cpu_var = tk.StringVar(value="CPU: --")
        self.memory_var = tk.StringVar(value="Memory: --")
        ttk.Label(resource_frame, textvariable=self.cpu_var, font=("TkDefaultFont", 10)).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(resource_frame, textvariable=self.memory_var, font=("TkDefaultFont", 10)).grid(row=1, column=0, sticky=tk.W)

        # Logs
        log_frame = ttk.LabelFrame(right_panel, text="Application Logs", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            width=50,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def _create_table_status_widgets(self):
        """Create status display widgets for each table."""
        for table_id in range(1, 7):
            table_frame = ttk.LabelFrame(
                self.status_scrollable_frame,
                text=f"Table {table_id}",
                padding="5",
            )
            table_frame.grid(row=table_id - 1, column=0, sticky=(tk.W, tk.E), pady=2, padx=5)
            table_frame.columnconfigure(1, weight=1)

            # Status variables
            self.table_status_vars[table_id] = {
                "status": tk.StringVar(value="⚪ Stopped"),
                "timer": tk.StringVar(value="Timer: --"),
                "rounds": tk.StringVar(value="Last 3: ---"),
                "pattern": tk.StringVar(value="Pattern: --"),
                "decision": tk.StringVar(value="Decision: --"),
            }

            # Status label
            ttk.Label(
                table_frame,
                textvariable=self.table_status_vars[table_id]["status"],
                font=("TkDefaultFont", 10, "bold"),
            ).grid(row=0, column=0, columnspan=2, sticky=tk.W)

            # Timer
            ttk.Label(
                table_frame,
                textvariable=self.table_status_vars[table_id]["timer"],
            ).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))

            # Rounds
            ttk.Label(
                table_frame,
                textvariable=self.table_status_vars[table_id]["rounds"],
            ).grid(row=1, column=1, sticky=tk.W)

            # Pattern match
            ttk.Label(
                table_frame,
                textvariable=self.table_status_vars[table_id]["pattern"],
            ).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))

            # Decision
            ttk.Label(
                table_frame,
                textvariable=self.table_status_vars[table_id]["decision"],
            ).grid(row=2, column=1, sticky=tk.W)

            # Control buttons
            button_frame = ttk.Frame(table_frame)
            button_frame.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky=tk.W)

            ttk.Button(
                button_frame,
                text="Pause",
                command=lambda tid=table_id: self._pause_table(tid),
                width=8,
            ).grid(row=0, column=0, padx=(0, 5))

            ttk.Button(
                button_frame,
                text="Resume",
                command=lambda tid=table_id: self._resume_table(tid),
                width=8,
            ).grid(row=0, column=1)

    def _on_open_browser_clicked(self):
        """Handle open browser button click."""
        url = self.game_url_var.get().strip()
        
        # URL is optional - if provided, validate format; if not, open blank page
        if url and url != "https://your-game-url.com":
            # Basic URL format validation if URL is provided
            if not url.startswith(("http://", "https://")):
                messagebox.showwarning(
                    "Invalid URL Format",
                    "Game URL must start with http:// or https://\n\n"
                    f"Current value: {url}\n\n"
                    "You can leave it empty to open a blank page, or enter a valid URL."
                )
                return
            
            # Save Game URL to .env file automatically if valid URL provided
            if EnvManager.save_game_url(url):
                self.log(f"Saved Game URL to .env file")
            self.log(f"Opening browser to: {url}")
        else:
            # No URL provided - open blank page
            url = None
            self.log("Opening browser (blank page - navigate manually)")

        self.open_browser_button.config(state=tk.DISABLED)
        self.browser_status_var.set("Browser: Opening...")

        if self.on_open_browser:
            # Call callback in background thread
            def open_thread():
                try:
                    self.on_open_browser(url)
                    self.root.after(0, lambda: self._on_browser_opened())
                except Exception as e:
                    self.root.after(0, lambda: self._on_browser_error(str(e)))

            threading.Thread(target=open_thread, daemon=True).start()

    def _on_browser_opened(self):
        """Handle browser opened successfully."""
        self.browser_opened = True
        self.browser_status_var.set("Browser: ✓ Opened")
        self.open_browser_button.config(state=tk.NORMAL, text="Browser Opened")
        self.configure_tables_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)  # Enable start button after browser opens
        self.log("Browser opened successfully.")
        messagebox.showinfo(
            "Browser Opened",
            "Browser opened successfully!\n\n"
            "IMPORTANT - Manual Setup Required:\n"
            "1. Navigate to your game page manually\n"
            "2. Log in if required\n"
            "3. Set up the page as needed\n"
            "4. Make sure the game is loaded\n\n"
            "After manual setup:\n"
            "1. Configure table coordinates (click 'Configure Tables')\n"
            "2. Set betting patterns for each table\n"
            "3. Click 'Start Automation' when ready\n\n"
            "Note: Game URL field is optional - you can navigate manually!"
        )

    def _on_browser_error(self, error: str):
        """Handle browser open error."""
        self.browser_opened = False
        self.browser_status_var.set("Browser: ✗ Error")
        self.open_browser_button.config(state=tk.NORMAL)
        self.log(f"Browser open error: {error}")
        messagebox.showerror("Error", f"Failed to open browser:\n{error}")

    def _on_start_clicked(self):
        """Handle start button click."""
        if not self.browser_opened:
            messagebox.showwarning(
                "Warning",
                "Please open browser first!\n\n"
                "1. Enter Game URL\n"
                "2. Click 'Open Browser'\n"
                "3. Manually navigate, login, and set up the page\n"
                "4. Configure tables and patterns\n"
                "5. Then start automation"
            )
            return

        # Confirm user has completed manual setup
        response = messagebox.askyesno(
            "Ready to Start Automation?",
            "Before starting, please confirm:\n\n"
            "✓ You have navigated to the game page\n"
            "✓ You have logged in (if required)\n"
            "✓ The game page is fully loaded\n"
            "✓ Tables are visible on the page\n\n"
            "Have you completed the manual setup?"
        )
        if not response:
            return

        # Check if tables are configured
        if not self._check_tables_configured():
            response = messagebox.askyesno(
                "No Tables Configured",
                "No tables are configured yet.\n\n"
                "Do you want to start anyway?\n"
                "(You can add tables later)"
            )
            if not response:
                return

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.open_browser_button.config(state=tk.DISABLED)
        self.configure_tables_button.config(state=tk.DISABLED)
        self.log("Starting automation...")

        if self.on_start:
            self.on_start()

    def _check_tables_configured(self) -> bool:
        """Check if any tables are configured."""
        # This would check with the main app if tables exist
        # For now, return True to allow starting
        return True

    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.open_browser_button.config(state=tk.NORMAL)
        self.configure_tables_button.config(state=tk.NORMAL)
        self.log("Stopping automation...")

        if self.on_stop:
            self.on_stop()

    def _validate_pattern(self):
        """Validate pattern format."""
        pattern = self.pattern_text.get("1.0", tk.END).strip()
        if not pattern:
            self.pattern_status_var.set("Error: Pattern cannot be empty")
            return

        from ..pattern_matching.pattern_validator import PatternValidator
        validator = PatternValidator()
        is_valid, error = validator.validate(pattern)

        if is_valid:
            self.pattern_status_var.set("✓ Pattern is valid")
        else:
            self.pattern_status_var.set(f"✗ {error}")
            messagebox.showerror("Invalid Pattern", error)

    def _save_pattern(self):
        """Save pattern for selected table."""
        pattern = self.pattern_text.get("1.0", tk.END).strip()
        table_id = self.pattern_table_var.get()

        # Validate first
        from ..pattern_matching.pattern_validator import PatternValidator
        validator = PatternValidator()
        is_valid, error = validator.validate(pattern)

        if not is_valid:
            messagebox.showerror("Invalid Pattern", error)
            return

        if self.on_pattern_update:
            self.on_pattern_update(table_id, pattern)

        self.pattern_status_var.set(f"✓ Pattern saved for Table {table_id}")
        self.log(f"Pattern saved for Table {table_id}: {pattern}")

    def _on_pattern_table_changed(self, event=None):
        """Handle pattern table selection change."""
        # In a real implementation, load existing patterns for the selected table
        pass

    def _show_pattern_help(self):
        """Show pattern format help."""
        help_text = """
Pattern Format Help:

Format: [history]-[decision]
- History: 3 characters representing the last 3 round results
- Decision: 1 character representing the bet decision

Characters:
- B = Red team (Banker)
- P = Blue team (Player)

Examples:
- "BBP-P" = If last 3 rounds were Red, Red, Blue, then bet Blue
- "BPB-B" = If last 3 rounds were Red, Blue, Red, then bet Red
- "PPP-B" = If last 3 rounds were Blue, Blue, Blue, then bet Red

Multiple patterns are separated by semicolons:
- "BBP-P;BPB-B;PPP-B"

Patterns are matched in order (first match wins).
        """
        messagebox.showinfo("Pattern Format Help", help_text.strip())

    def _open_table_config(self):
        """Open table coordinates configuration window."""
        if not self.browser_opened:
            messagebox.showwarning(
                "Browser Not Open",
                "Please open browser first!\n\n"
                "1. Enter Game URL\n"
                "2. Click 'Open Browser'\n"
                "3. Then configure tables"
            )
            return

        # Get browser page from main app
        browser_page = None
        if hasattr(self, 'get_browser_page'):
            browser_page = self.get_browser_page()
        
        # Get browser event loop accessor from main app
        get_browser_event_loop = None
        if hasattr(self, 'get_browser_event_loop'):
            get_browser_event_loop = self.get_browser_event_loop

        TableConfigWindow(
            self.root,
            self.on_coordinates_update,
            self.browser_opened,
            browser_page,
            get_browser_event_loop=get_browser_event_loop
        )

    def _pause_table(self, table_id: int):
        """Pause a specific table."""
        self.log(f"Pausing Table {table_id}")
        # Callback would be implemented by main application

    def _resume_table(self, table_id: int):
        """Resume a specific table."""
        self.log(f"Resuming Table {table_id}")
        # Callback would be implemented by main application

    def update_table_status(self, table_id: int, status_data: Dict[str, Any]):
        """Update status display for a table."""
        if table_id not in self.table_status_vars:
            return

        vars = self.table_status_vars[table_id]

        # Status
        status_map = {
            "active": "🟢 Active",
            "learning": "🟡 Learning",
            "paused": "🔴 Paused",
            "stuck": "⚪ Stuck",
            "stopped": "⚪ Stopped",
        }
        status = status_data.get("status", "stopped")
        vars["status"].set(status_map.get(status, "⚪ Unknown"))

        # Timer
        timer = status_data.get("timer")
        vars["timer"].set(f"Timer: {timer if timer is not None else '--'}")

        # Last 3 rounds
        rounds = status_data.get("last_3_rounds")
        vars["rounds"].set(f"Last 3: {rounds if rounds else '---'}")

        # Pattern match
        pattern = status_data.get("pattern_match")
        vars["pattern"].set(f"Pattern: {pattern if pattern else '--'}")

        # Decision
        decision = status_data.get("decision")
        vars["decision"].set(f"Decision: {decision if decision else '--'}")

    def update_resources(self, cpu_percent: float, memory_percent: float):
        """Update resource monitor display."""
        self.cpu_var.set(f"CPU: {cpu_percent:.1f}%")
        self.memory_var.set(f"Memory: {memory_percent:.1f}%")

    def log(self, message: str):
        """Add message to log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def process_ui_queue(self):
        """Process messages from UI queue."""
        try:
            while True:
                update = self.ui_queue.get_nowait()
                if update.type == "status_update":
                    self.update_table_status(update.table_id, update.data)
                elif update.type == "error":
                    self.log(f"Table {update.table_id} Error: {update.data.get('error', 'Unknown error')}")
        except queue.Empty:
            pass

    def _update_ui_loop(self):
        """Update UI every 500ms."""
        self.process_ui_queue()
        self.root.after(500, self._update_ui_loop)

    def get_game_url(self) -> str:
        """Get current game URL."""
        return self.game_url_var.get().strip()

    def on_closing(self):
        """Handle window closing."""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Automation is running. Stop and quit?"):
                self._on_stop_clicked()
                self.root.quit()
        else:
            self.root.quit()

    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()


class TableConfigWindow:
    """Window for configuring table coordinates with guide."""

    def __init__(
        self,
        parent,
        on_save: Optional[Callable] = None,
        browser_opened: bool = False,
        browser_page=None,
        get_browser_event_loop: Optional[Callable] = None,
    ):
        """
        Initialize table configuration window.

        Args:
            parent: Parent window
            on_save: Callback when coordinates are saved (table_id, coords_dict)
            browser_opened: Whether browser is already opened
            browser_page: Playwright Page instance for coordinate picking
            get_browser_event_loop: Function to get browser event loop for coordinate picker
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Table Coordinates Configuration")
        self.window.geometry("900x700")
        self.on_save = on_save
        self.browser_opened = browser_opened
        self.browser_page = browser_page
        self.get_browser_event_loop = get_browser_event_loop

        self._create_widgets()

    def _create_widgets(self):
        """Create configuration widgets."""
        # Notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Configuration Guide
        guide_frame = ttk.Frame(notebook, padding="10")
        notebook.add(guide_frame, text="Guide")

        guide_text = scrolledtext.ScrolledText(guide_frame, wrap=tk.WORD, height=25)
        guide_text.pack(fill=tk.BOTH, expand=True)

        guide_content = """
TABLE COORDINATES CONFIGURATION GUIDE
=====================================

This guide will help you configure table region coordinates for screenshot capture.

IMPORTANT: Browser must be opened first!
Use the "Open Browser" button in the main window before configuring tables.

STEP 1: Browser is Already Open
---------------------------------
✓ Browser should be open and showing your game
✓ Browser window is set to 1920x1080 resolution
✓ Game page is loaded with all tables visible

STEP 2: Use Visual Coordinate Picker (EASIEST METHOD!)
------------------------------------------------------
🎯 NO NEED TO USE DEVTOOLS! Just click the "Pick" buttons!

For Table Region:
1. Click "📐 Pick Table Region" button
2. A visual overlay will appear on the browser
3. Drag your mouse to select the entire table area
4. Release mouse - coordinates are automatically captured!

For Button Positions:
1. Click the button picker (e.g., "🔵 Pick Blue")
2. Click directly on the button in the browser
3. A red marker appears - coordinates are captured!

For Timer/Score Regions:
1. Click the region picker (e.g., "⏱️ Pick Timer")
2. Drag to select the timer/score display area
3. Release mouse - coordinates are captured!

STEP 3: Review and Adjust
---------------------------
1. Check the captured coordinates in the form fields
2. Adjust manually if needed
3. Click "Validate" to check for errors
4. Click "Save" to save configuration

STEP 4: Repeat for All Tables
-------------------------------
1. Select next table from dropdown
2. Use picker buttons to capture coordinates
3. Save each table configuration

MANUAL ENTRY (Alternative Method):
-----------------------------------
If you prefer manual entry or need to adjust:
- Enter x, y, width, height values directly
- Coordinates are relative to canvas (#layaCanvas)
- Button coordinates are relative to table region
- Canvas has a 17px horizontal offset (automatically handled)

IMPORTANT NOTES:
- All coordinates are relative to the canvas element (#layaCanvas)
- Button coordinates are relative to the table region
- Canvas has a 17px horizontal offset (automatically handled)
- Make sure coordinates don't overlap between tables
- Test with one table first before configuring all 6

TROUBLESHOOTING:
- If picker doesn't appear: Make sure browser is opened first
- If coordinates seem wrong: Try picking again or adjust manually
- If screenshots are wrong: Check table region coordinates
- If clicks miss: Check button coordinates
- If timer/score extraction fails: Check region coordinates
- Make sure browser is at 1920x1080 resolution

TIP: Use the visual picker - it's much easier than DevTools!

For more help, see INSTALLATION_GUIDE.md
        """
        guide_text.insert("1.0", guide_content.strip())
        guide_text.config(state=tk.DISABLED)

        # Tab 2: Configuration Editor
        # Create scrollable frame
        canvas = tk.Canvas(config_frame := ttk.Frame(notebook), highlightthickness=0)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        notebook.add(config_frame, text="Configuration")

        # Initialize coordinate variables BEFORE creating inputs
        self.coord_vars = {}

        # Table selection
        ttk.Label(scrollable_frame, text="Select Table:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10), padx=10)
        self.config_table_var = tk.IntVar(value=1)
        table_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.config_table_var,
            values=list(range(1, 7)),
            state="readonly",
            width=10,
        )
        table_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 10), pady=(0, 10))
        table_combo.bind("<<ComboboxSelected>>", self._load_table_config)

        # Pick button for table region - Put it OUTSIDE region_frame so it's ALWAYS visible!
        def _on_pick_table_btn_clicked():
            """Wrapper to debug button click."""
            print("DEBUG: Button 'Pick Table Region' clicked!")
            logger.info("DEBUG: Button 'Pick Table Region' clicked!")
            try:
                self._pick_table_region()
            except Exception as e:
                print(f"DEBUG: Exception in button handler: {e}")
                logger.error(f"DEBUG: Exception in button handler: {e}", exc_info=True)
                raise
        
        pick_table_btn = ttk.Button(
            scrollable_frame,
            text="📐 Pick Table Region",
            command=_on_pick_table_btn_clicked,
            width=50,
        )
        pick_table_btn.grid(row=1, column=0, columnspan=2, pady=(0, 10), padx=10, sticky=(tk.W, tk.E))

        # Table Region
        region_frame = ttk.LabelFrame(scrollable_frame, text="Table Region", padding="10")
        region_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10), padx=10)
        region_frame.columnconfigure(1, weight=1)
        
        self._create_coord_inputs(region_frame, "x", "y", "width", "height", 0)

        # Buttons
        buttons_frame = ttk.LabelFrame(scrollable_frame, text="Button Coordinates", padding="10")
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10), padx=10)
        buttons_frame.columnconfigure(1, weight=1)

        self._create_coord_inputs(buttons_frame, "blue_x", "blue_y", "red_x", "red_y", 0)
        self._create_coord_inputs(buttons_frame, "confirm_x", "confirm_y", "cancel_x", "cancel_y", 1)
        
        # Pick buttons for button positions
        button_pick_frame = ttk.Frame(buttons_frame)
        button_pick_frame.grid(row=2, column=0, columnspan=8, pady=(5, 0), sticky=tk.W)
        
        ttk.Button(
            button_pick_frame,
            text="🔵 Pick Blue",
            command=lambda: self._pick_button("blue"),
        ).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(
            button_pick_frame,
            text="🔴 Pick Red",
            command=lambda: self._pick_button("red"),
        ).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(
            button_pick_frame,
            text="✓ Pick Confirm",
            command=lambda: self._pick_button("confirm"),
        ).grid(row=0, column=2, padx=(0, 5))
        
        ttk.Button(
            button_pick_frame,
            text="✗ Pick Cancel",
            command=lambda: self._pick_button("cancel"),
        ).grid(row=0, column=3)

        # Timer and Score Regions
        regions_frame = ttk.LabelFrame(scrollable_frame, text="Timer & Score Regions", padding="10")
        regions_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10), padx=10)
        regions_frame.columnconfigure(1, weight=1)

        self._create_coord_inputs(regions_frame, "timer_x", "timer_y", "timer_w", "timer_h", 0)
        self._create_coord_inputs(regions_frame, "blue_score_x", "blue_score_y", "blue_score_w", "blue_score_h", 1)
        self._create_coord_inputs(regions_frame, "red_score_x", "red_score_y", "red_score_w", "red_score_h", 2)
        
        # Pick buttons for regions
        region_pick_frame = ttk.Frame(regions_frame)
        region_pick_frame.grid(row=3, column=0, columnspan=8, pady=(5, 0), sticky=tk.W)
        
        ttk.Button(
            region_pick_frame,
            text="⏱️ Pick Timer",
            command=lambda: self._pick_region("timer"),
        ).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(
            region_pick_frame,
            text="🔵 Pick Blue Score",
            command=lambda: self._pick_region("blue_score"),
        ).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(
            region_pick_frame,
            text="🔴 Pick Red Score",
            command=lambda: self._pick_region("red_score"),
        ).grid(row=0, column=2)

        # Action buttons
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0), padx=10)

        ttk.Button(
            action_frame,
            text="Validate",
            command=self._validate_coordinates,
        ).grid(row=0, column=0, padx=(0, 5))

        ttk.Button(
            action_frame,
            text="Save",
            command=self._save_coordinates,
        ).grid(row=0, column=1, padx=(0, 5))

        ttk.Button(
            action_frame,
            text="Load from Config",
            command=self._load_from_config_file,
        ).grid(row=0, column=2, padx=(0, 5))

        ttk.Button(
            action_frame,
            text="Close",
            command=self.window.destroy,
        ).grid(row=0, column=3)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            scrollable_frame,
            textvariable=self.status_var,
            foreground="green",
        ).grid(row=6, column=0, columnspan=2, pady=(10, 0), padx=10)
        
        # Update scroll region when window is resized
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", update_scroll_region)

    def _create_coord_inputs(self, parent, label1, label2, label3, label4, row):
        """Create coordinate input fields."""
        ttk.Label(parent, text=f"{label1}:").grid(row=row, column=0, sticky=tk.W, padx=(0, 5))
        var1 = tk.StringVar()
        ttk.Entry(parent, textvariable=var1, width=10).grid(row=row, column=1, sticky=tk.W, padx=(0, 10))
        self.coord_vars[label1] = var1

        ttk.Label(parent, text=f"{label2}:").grid(row=row, column=2, sticky=tk.W, padx=(0, 5))
        var2 = tk.StringVar()
        ttk.Entry(parent, textvariable=var2, width=10).grid(row=row, column=3, sticky=tk.W, padx=(0, 10))
        self.coord_vars[label2] = var2

        ttk.Label(parent, text=f"{label3}:").grid(row=row, column=4, sticky=tk.W, padx=(0, 5))
        var3 = tk.StringVar()
        ttk.Entry(parent, textvariable=var3, width=10).grid(row=row, column=5, sticky=tk.W, padx=(0, 10))
        self.coord_vars[label3] = var3

        ttk.Label(parent, text=f"{label4}:").grid(row=row, column=6, sticky=tk.W, padx=(0, 5))
        var4 = tk.StringVar()
        ttk.Entry(parent, textvariable=var4, width=10).grid(row=row, column=7, sticky=tk.W)
        self.coord_vars[label4] = var4

    def _load_table_config(self, event=None):
        """Load configuration for selected table."""
        # In real implementation, load from config file
        pass

    def _validate_coordinates(self):
        """Validate coordinate values."""
        table_id = self.config_table_var.get()
        errors = []

        # Validate table region
        try:
            x = int(self.coord_vars["x"].get())
            y = int(self.coord_vars["y"].get())
            w = int(self.coord_vars["width"].get())
            h = int(self.coord_vars["height"].get())

            if x < 0 or y < 0 or w <= 0 or h <= 0:
                errors.append("Table region: All values must be positive")
            if x + w > 1920:
                errors.append("Table region: x + width exceeds canvas width (1920)")
            if y + h > 1080:
                errors.append("Table region: y + height exceeds canvas height (1080)")
        except ValueError:
            errors.append("Table region: Invalid numeric values")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            self.status_var.set("✗ Validation failed")
        else:
            self.status_var.set("✓ Coordinates are valid")
            messagebox.showinfo("Success", "Coordinates are valid!")

    def _save_coordinates(self):
        """Save coordinates for selected table."""
        table_id = self.config_table_var.get()

        coords = {
            "x": int(self.coord_vars["x"].get() or 0),
            "y": int(self.coord_vars["y"].get() or 0),
            "width": int(self.coord_vars["width"].get() or 0),
            "height": int(self.coord_vars["height"].get() or 0),
            "buttons": {
                "blue": {
                    "x": int(self.coord_vars["blue_x"].get() or 0),
                    "y": int(self.coord_vars["blue_y"].get() or 0),
                },
                "red": {
                    "x": int(self.coord_vars["red_x"].get() or 0),
                    "y": int(self.coord_vars["red_y"].get() or 0),
                },
                "confirm": {
                    "x": int(self.coord_vars["confirm_x"].get() or 0),
                    "y": int(self.coord_vars["confirm_y"].get() or 0),
                },
                "cancel": {
                    "x": int(self.coord_vars["cancel_x"].get() or 0),
                    "y": int(self.coord_vars["cancel_y"].get() or 0),
                },
            },
            "timer": {
                "x": int(self.coord_vars["timer_x"].get() or 0),
                "y": int(self.coord_vars["timer_y"].get() or 0),
                "width": int(self.coord_vars["timer_w"].get() or 0),
                "height": int(self.coord_vars["timer_h"].get() or 0),
            },
            "blue_score": {
                "x": int(self.coord_vars["blue_score_x"].get() or 0),
                "y": int(self.coord_vars["blue_score_y"].get() or 0),
                "width": int(self.coord_vars["blue_score_w"].get() or 0),
                "height": int(self.coord_vars["blue_score_h"].get() or 0),
            },
            "red_score": {
                "x": int(self.coord_vars["red_score_x"].get() or 0),
                "y": int(self.coord_vars["red_score_y"].get() or 0),
                "width": int(self.coord_vars["red_score_w"].get() or 0),
                "height": int(self.coord_vars["red_score_h"].get() or 0),
            },
        }

        if self.on_save:
            self.on_save(table_id, coords)

        self.status_var.set(f"✓ Coordinates saved for Table {table_id}")
        messagebox.showinfo("Success", f"Coordinates saved for Table {table_id}")

    def _load_from_config_file(self):
        """Load coordinates from config file."""
        import yaml
        from pathlib import Path

        config_path = Path("config/table_regions.yaml")
        if not config_path.exists():
            messagebox.showerror("Error", f"Config file not found: {config_path}")
            return

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            table_id = self.config_table_var.get()
            table_config = config.get("tables", {}).get(table_id)

            if not table_config:
                messagebox.showwarning("Warning", f"No configuration found for Table {table_id}")
                return

            # Load values into form
            self.coord_vars["x"].set(str(table_config.get("x", 0)))
            self.coord_vars["y"].set(str(table_config.get("y", 0)))
            self.coord_vars["width"].set(str(table_config.get("width", 0)))
            self.coord_vars["height"].set(str(table_config.get("height", 0)))

            buttons = table_config.get("buttons", {})
            if buttons:
                self.coord_vars["blue_x"].set(str(buttons.get("blue", {}).get("x", 0)))
                self.coord_vars["blue_y"].set(str(buttons.get("blue", {}).get("y", 0)))
                self.coord_vars["red_x"].set(str(buttons.get("red", {}).get("x", 0)))
                self.coord_vars["red_y"].set(str(buttons.get("red", {}).get("y", 0)))
                self.coord_vars["confirm_x"].set(str(buttons.get("confirm", {}).get("x", 0)))
                self.coord_vars["confirm_y"].set(str(buttons.get("confirm", {}).get("y", 0)))
                self.coord_vars["cancel_x"].set(str(buttons.get("cancel", {}).get("x", 0)))
                self.coord_vars["cancel_y"].set(str(buttons.get("cancel", {}).get("y", 0)))

            timer = table_config.get("timer", {})
            if timer:
                self.coord_vars["timer_x"].set(str(timer.get("x", 0)))
                self.coord_vars["timer_y"].set(str(timer.get("y", 0)))
                self.coord_vars["timer_w"].set(str(timer.get("width", 0)))
                self.coord_vars["timer_h"].set(str(timer.get("height", 0)))

            blue_score = table_config.get("blue_score", {})
            if blue_score:
                self.coord_vars["blue_score_x"].set(str(blue_score.get("x", 0)))
                self.coord_vars["blue_score_y"].set(str(blue_score.get("y", 0)))
                self.coord_vars["blue_score_w"].set(str(blue_score.get("width", 0)))
                self.coord_vars["blue_score_h"].set(str(blue_score.get("height", 0)))

            red_score = table_config.get("red_score", {})
            if red_score:
                self.coord_vars["red_score_x"].set(str(red_score.get("x", 0)))
                self.coord_vars["red_score_y"].set(str(red_score.get("y", 0)))
                self.coord_vars["red_score_w"].set(str(red_score.get("width", 0)))
                self.coord_vars["red_score_h"].set(str(red_score.get("height", 0)))

            self.status_var.set("✓ Configuration loaded from file")
            messagebox.showinfo("Success", "Configuration loaded from file")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")

    def _pick_table_region(self):
        """Pick table region using visual picker."""
        # DEBUG: Confirm method is being called
        print("DEBUG: _pick_table_region() called!")
        logger.info("DEBUG: _pick_table_region() method called")
        print(f"DEBUG: self.browser_page = {self.browser_page}")
        print(f"DEBUG: self.browser_page is None? {self.browser_page is None}")
        
        if not self.browser_page:
            print("DEBUG: browser_page is None - showing warning")
            logger.warning("DEBUG: browser_page is None - attempting to show warning dialog")
            logger.warning("Browser page not available for coordinate picking")
            messagebox.showwarning(
                "Browser Not Available",
                "Browser page not available.\n\n"
                "Please:\n"
                "1. Click 'Open Browser' in the main window\n"
                "2. Navigate to your game page\n"
                "3. Then try picking coordinates again"
            )
            return

        logger.info("Browser page available, showing coordinate picker info dialog")
        
        # Show info message
        self.window.after(0, lambda: messagebox.showinfo(
            "Coordinate Picker",
            "Coordinate picker will appear in the browser window.\n\n"
            "Instructions:\n"
            "1. Look at the browser window\n"
            "2. You'll see a green overlay\n"
            "3. Drag to select the table region\n"
            "4. Release mouse to capture coordinates\n\n"
            "Press ESC to cancel."
        ))

        def pick_thread():
            """
            Thread function to run coordinate picker using the original browser event loop.
            
            Uses run_coroutine_threadsafe to schedule the coroutine in the browser's
            event loop instead of creating a new one, which prevents deadlocks with
            Playwright Page objects.
            """
            logger.info("Coordinate picker thread started")
            
            # Get the original event loop instead of creating new one
            original_loop = None
            if hasattr(self, 'get_browser_event_loop') and callable(self.get_browser_event_loop):
                original_loop = self.get_browser_event_loop()
                logger.debug(f"Retrieved browser event loop: {original_loop}")
            else:
                logger.warning("get_browser_event_loop method not available or not callable")
            
            if not original_loop:
                logger.error("Browser event loop not available - browser may not be fully initialized")
                self.window.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Browser event loop not available. Please ensure browser is fully opened before using coordinate picker."
                ))
                return
            
            if not self.browser_page:
                logger.error("Browser page not available")
                self.window.after(0, lambda: messagebox.showwarning(
                    "Browser Not Available",
                    "Browser page not available.\n\n"
                    "Please:\n"
                    "1. Click 'Open Browser' in the main window\n"
                    "2. Navigate to your game page\n"
                    "3. Then try picking coordinates again"
                ))
                return
            
            try:
                logger.info("Using original event loop for coordinate picker")
                
                # Create picker instance
                picker = CoordinatePicker(self.browser_page)
                
                # Use run_coroutine_threadsafe to run in original loop
                logger.info("Calling picker.pick_table_region() via run_coroutine_threadsafe")
                future = asyncio.run_coroutine_threadsafe(
                    picker.pick_table_region(),
                    original_loop
                )
                
                # Wait for result (blocking call, but in separate thread)
                result = future.result(timeout=60.0)  # 60 second timeout
                
                logger.info(f"Picker returned result: {result}")
                
                if result:
                    self.window.after(0, lambda: self._apply_table_region(result))
                else:
                    self.window.after(0, lambda: messagebox.showinfo(
                        "Cancelled",
                        "Coordinate picking cancelled"
                    ))
                    
            except asyncio.TimeoutError:
                logger.error("Coordinate picking timed out")
                self.window.after(0, lambda: messagebox.showerror(
                    "Timeout",
                    "Coordinate picking timed out after 60 seconds."
                ))
            except Exception as e:
                import traceback
                error_msg = f"Failed to pick coordinates:\n{str(e)}\n\n{traceback.format_exc()}"
                logger.error(error_msg)
                self.window.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Failed to pick coordinates:\n{str(e)}\n\n"
                    "Check logs for details. Make sure browser is open and on a valid page."
                ))

        threading.Thread(target=pick_thread, daemon=True).start()

    def _apply_table_region(self, result: Dict[str, int]):
        """Apply picked table region to form."""
        self.coord_vars["x"].set(str(result.get("x", 0)))
        self.coord_vars["y"].set(str(result.get("y", 0)))
        self.coord_vars["width"].set(str(result.get("width", 0)))
        self.coord_vars["height"].set(str(result.get("height", 0)))
        self.status_var.set("✓ Table region captured")
        messagebox.showinfo("Success", "Table region captured! Review and save if correct.")

    def _pick_button(self, button_type: str):
        """
        Pick button position using visual picker.
        
        Args:
            button_type: Type of button to pick (e.g., 'start', 'stop')
        """
        if not self.browser_page:
            messagebox.showwarning(
                "Browser Not Available",
                "Browser page not available. Please ensure browser is opened."
            )
            return

        def pick_thread():
            """
            Thread function to run button coordinate picker using the original browser event loop.
            """
            logger.info(f"Button picker thread started for button type: {button_type}")
            
            # Get the original event loop instead of creating new one
            original_loop = None
            if hasattr(self, 'get_browser_event_loop') and callable(self.get_browser_event_loop):
                original_loop = self.get_browser_event_loop()
                logger.debug(f"Retrieved browser event loop: {original_loop}")
            else:
                logger.warning("get_browser_event_loop method not available or not callable")
            
            if not original_loop:
                logger.error("Browser event loop not available - browser may not be fully initialized")
                self.window.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Browser event loop not available. Please ensure browser is fully opened before using coordinate picker."
                ))
                return
            
            try:
                # Create picker instance
                picker = CoordinatePicker(self.browser_page)
                
                # Use run_coroutine_threadsafe to run in original loop
                logger.info("Calling picker.pick_button_position() via run_coroutine_threadsafe")
                future = asyncio.run_coroutine_threadsafe(
                    picker.pick_button_position(),
                    original_loop
                )
                
                # Wait for result (blocking call, but in separate thread)
                result = future.result(timeout=60.0)  # 60 second timeout
                
                logger.info(f"Button picker returned result: {result}")
                
                if result:
                    self.window.after(0, lambda: self._apply_button_position(button_type, result))
                else:
                    self.window.after(0, lambda: messagebox.showinfo(
                        "Cancelled",
                        "Coordinate picking cancelled"
                    ))
                    
            except asyncio.TimeoutError:
                logger.error("Button coordinate picking timed out")
                self.window.after(0, lambda: messagebox.showerror(
                    "Timeout",
                    "Coordinate picking timed out after 60 seconds."
                ))
            except Exception as e:
                import traceback
                error_msg = f"Failed to pick button coordinates: {str(e)}\n\n{traceback.format_exc()}"
                logger.error(error_msg)
                self.window.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Failed to pick coordinates: {str(e)}\n\n"
                    "Check logs for details. Make sure browser is open and on a valid page."
                ))

        threading.Thread(target=pick_thread, daemon=True).start()

    def _apply_button_position(self, button_type: str, result: Dict[str, int]):
        """Apply picked button position to form."""
        x_key = f"{button_type}_x"
        y_key = f"{button_type}_y"
        
        if x_key in self.coord_vars and y_key in self.coord_vars:
            self.coord_vars[x_key].set(str(result.get("x", 0)))
            self.coord_vars[y_key].set(str(result.get("y", 0)))
            self.status_var.set(f"✓ {button_type.capitalize()} button captured")
            messagebox.showinfo("Success", f"{button_type.capitalize()} button position captured!")
        else:
            messagebox.showerror("Error", f"Unknown button type: {button_type}")

    def _pick_region(self, region_type: str):
        """
        Pick region (timer or score) using visual picker.
        
        Args:
            region_type: Type of region to pick ('timer', 'blue_score', or 'red_score')
        """
        if not self.browser_page:
            messagebox.showwarning(
                "Browser Not Available",
                "Browser page not available. Please ensure browser is opened."
            )
            return

        mode_map = {
            "timer": "timer",
            "blue_score": "score",
            "red_score": "score",
        }
        mode = mode_map.get(region_type, "score")

        def pick_thread():
            """
            Thread function to run region coordinate picker using the original browser event loop.
            
            Uses run_coroutine_threadsafe to schedule the coroutine in the browser's
            event loop instead of creating a new one, which prevents deadlocks with
            Playwright Page objects.
            """
            logger.info(f"Region picker thread started for region type: {region_type}")
            
            # Get the original event loop instead of creating new one
            original_loop = None
            if hasattr(self, 'get_browser_event_loop') and callable(self.get_browser_event_loop):
                original_loop = self.get_browser_event_loop()
                logger.debug(f"Retrieved browser event loop: {original_loop}")
            else:
                logger.warning("get_browser_event_loop method not available or not callable")
            
            if not original_loop:
                logger.error("Browser event loop not available - browser may not be fully initialized")
                self.window.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Browser event loop not available. Please ensure browser is fully opened before using coordinate picker."
                ))
                return
            
            if not self.browser_page:
                logger.error("Browser page not available")
                self.window.after(0, lambda: messagebox.showwarning(
                    "Browser Not Available",
                    "Browser page not available.\n\n"
                    "Please:\n"
                    "1. Click 'Open Browser' in the main window\n"
                    "2. Navigate to your game page\n"
                    "3. Then try picking coordinates again"
                ))
                return
            
            try:
                logger.info(f"Using original event loop for region picker (mode: {mode})")
                
                # Create picker instance
                picker = CoordinatePicker(self.browser_page)
                
                # Use run_coroutine_threadsafe to run in original loop
                if mode == "timer":
                    logger.info("Calling picker.pick_timer_region() via run_coroutine_threadsafe")
                    future = asyncio.run_coroutine_threadsafe(
                        picker.pick_timer_region(),
                        original_loop
                    )
                else:
                    logger.info("Calling picker.pick_score_region() via run_coroutine_threadsafe")
                    future = asyncio.run_coroutine_threadsafe(
                        picker.pick_score_region(),
                        original_loop
                    )
                
                # Wait for result (blocking call, but in separate thread)
                result = future.result(timeout=60.0)  # 60 second timeout
                
                logger.info(f"Region picker returned result: {result}")
                
                if result:
                    self.window.after(0, lambda: self._apply_region(region_type, result))
                else:
                    self.window.after(0, lambda: messagebox.showinfo(
                        "Cancelled",
                        "Coordinate picking cancelled"
                    ))
                    
            except asyncio.TimeoutError:
                logger.error("Region coordinate picking timed out")
                self.window.after(0, lambda: messagebox.showerror(
                    "Timeout",
                    "Coordinate picking timed out after 60 seconds."
                ))
            except Exception as e:
                import traceback
                error_msg = f"Failed to pick region coordinates: {str(e)}\n\n{traceback.format_exc()}"
                logger.error(error_msg)
                self.window.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Failed to pick coordinates: {str(e)}\n\n"
                    "Check logs for details. Make sure browser is open and on a valid page."
                ))

        threading.Thread(target=pick_thread, daemon=True).start()

    def _apply_region(self, region_type: str, result: Dict[str, int]):
        """Apply picked region to form."""
        x_key = f"{region_type}_x"
        y_key = f"{region_type}_y"
        w_key = f"{region_type}_w"
        h_key = f"{region_type}_h"
        
        if x_key in self.coord_vars and y_key in self.coord_vars:
            self.coord_vars[x_key].set(str(result.get("x", 0)))
            self.coord_vars[y_key].set(str(result.get("y", 0)))
            if w_key in self.coord_vars and h_key in self.coord_vars:
                self.coord_vars[w_key].set(str(result.get("width", 0)))
                self.coord_vars[h_key].set(str(result.get("height", 0)))
            self.status_var.set(f"✓ {region_type.replace('_', ' ').title()} region captured")
            messagebox.showinfo("Success", f"{region_type.replace('_', ' ').title()} region captured!")
        else:
            messagebox.showerror("Error", f"Unknown region type: {region_type}")
