"""Local OCR for uploaded image and PDF documents."""

import os

from flask import current_app


def _configure_tesseract():
    command = current_app.config.get("TESSERACT_CMD") or os.getenv("TESSERACT_CMD")
    if command:
        import pytesseract

        pytesseract.pytesseract.tesseract_cmd = command


def extract_text(filepath, mime_hint=""):
    _configure_tesseract()
    extension = os.path.splitext(filepath)[1].lower()
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return None, "OCR libraries are not installed. File stored for manual review."

    try:
        if extension == ".pdf":
            from pdf2image import convert_from_path

            options = {}
            poppler_path = current_app.config.get("POPPLER_PATH")
            if poppler_path:
                options["poppler_path"] = poppler_path
            images = convert_from_path(filepath, dpi=200, **options)
            text = "\n".join(
                pytesseract.image_to_string(image) for image in images[:8]
            ).strip()
        else:
            with Image.open(filepath) as image:
                text = pytesseract.image_to_string(image).strip()
    except Exception as error:
        return None, f"OCR could not run ({error.__class__.__name__}). File stored for manual review."

    if not text:
        return "", "OCR completed but no readable text was found. Needs manual review."
    return text, "OCR completed (prototype accuracy only)."
