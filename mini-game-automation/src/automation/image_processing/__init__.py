"""
Image processing module using OpenCV and EasyOCR.

Handles template matching for timer/score extraction
and OCR fallback for error recovery.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "TemplateMatcher":
        from .template_matcher import TemplateMatcher
        return TemplateMatcher
    elif name == "ImageExtractor":
        from .image_extractor import ImageExtractor
        return ImageExtractor
    elif name == "OCRFallback":
        from .ocr_fallback import OCRFallback
        return OCRFallback
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "TemplateMatcher",
    "ImageExtractor",
    "OCRFallback",
]
