# Assumptions and Dependencies

### Assumptions

1. Game website structure remains stable (canvas element, button positions, score displays)
2. Table region coordinates can be manually configured during development
3. Pattern format (`BBP-P;BPB-B`) accurately represents user decision logic
4. Timer and score extraction via template matching is reliable for game graphics
5. Page refreshes are infrequent and recoverable
6. Network connectivity is generally stable
7. User has basic understanding of pattern format and game mechanics

### Dependencies

1. Playwright browser automation library
2. OpenCV image processing library
3. PIL/Pillow image manipulation library
4. Tesseract OCR or EasyOCR (for fallback)
5. Python desktop UI framework (Tkinter or PyQt5/PySide6)
6. Game website availability and accessibility
7. Stable browser environment (Chromium)
