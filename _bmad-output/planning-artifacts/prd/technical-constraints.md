# Technical Constraints

### Technology Stack

- **Browser Automation:** Playwright (Python)
- **Image Processing:** OpenCV + PIL
- **OCR Fallback:** Tesseract (pytesseract) or EasyOCR
- **UI Framework:** Tkinter (built-in) or PyQt5/PySide6 for advanced features
- **Data Storage:** JSON files (Python json module)
- **Threading:** Python threading or asyncio

### Platform Requirements

- Cross-platform desktop application (Windows, macOS, Linux)
- Python 3.8+ runtime
- Playwright browser binaries
- OpenCV and PIL libraries
- Optional: Tesseract OCR or EasyOCR

### Performance Constraints

- Maximum 6 tables (hard limit)
- Single browser instance
- Region-only screenshots (not full page)
- Adaptive screenshot frequency based on game phase
- CPU-based auto-throttling

### Data Constraints

- Date-based session folders
- Per-table JSON files (table_1.json through table_6.json)
- Continuous writing until tool closes
- Thread-safe file operations
- In-memory cache with periodic flushing
