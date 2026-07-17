#!/usr/bin/env python3
"""
detect_filetype.py

Detects the type of an uploaded document and tells the caller which
reading strategy to use. This is a lightweight router, not a parser --
actual content reading is still done via the appropriate skill/tool
(pdf, docx, xlsx, vision-for-images, etc.) as described in SKILL.md.

Usage:
    python3 detect_filetype.py <path-to-file>

Output (stdout, JSON):
    {
        "path": "/mnt/user-data/uploads/example.pdf",
        "extension": ".pdf",
        "category": "pdf",
        "suggested_strategy": "Use the pdf/pdf-reading skill to extract text."
    }
"""

import sys
import os
import json

# Map file extensions -> (category, suggested strategy string)
EXTENSION_MAP = {
    ".pdf": ("pdf", "Use the pdf or pdf-reading skill to extract text (handles text + scanned/OCR PDFs)."),
    ".docx": ("word", "Use the docx skill to read document content."),
    ".doc": ("word", "Use the docx skill (may need conversion) to read document content."),
    ".xlsx": ("spreadsheet", "Use the xlsx skill or pandas/openpyxl to read rows."),
    ".xlsm": ("spreadsheet", "Use the xlsx skill or pandas/openpyxl to read rows."),
    ".xls": ("spreadsheet", "Use the xlsx skill or pandas to read rows."),
    ".csv": ("spreadsheet", "Read directly with pandas or csv module."),
    ".tsv": ("spreadsheet", "Read directly with pandas (sep='\\t') or csv module."),
    ".txt": ("text", "Read the file directly as plain text."),
    ".md": ("text", "Read the file directly as plain text/markdown."),
    ".json": ("text", "Read the file directly and parse as JSON."),
    ".jpg": ("image", "View the image directly and read text visually (vision)."),
    ".jpeg": ("image", "View the image directly and read text visually (vision)."),
    ".png": ("image", "View the image directly and read text visually (vision)."),
    ".webp": ("image", "View the image directly and read text visually (vision)."),
    ".gif": ("image", "View the image directly and read text visually (vision)."),
    ".bmp": ("image", "View the image directly and read text visually (vision)."),
    ".tiff": ("image", "View the image directly and read text visually (vision)."),
    ".pptx": ("presentation", "Use the pptx skill to extract slide text."),
    ".ppt": ("presentation", "Use the pptx skill (may need conversion) to extract slide text."),
}


def detect(path: str) -> dict:
    if not os.path.exists(path):
        return {
            "path": path,
            "error": f"File not found: {path}",
        }

    _, ext = os.path.splitext(path.lower())
    category, strategy = EXTENSION_MAP.get(
        ext, ("unknown", "Use the file-reading skill as a router to determine the right approach.")
    )

    return {
        "path": path,
        "extension": ext or "(none)",
        "category": category,
        "suggested_strategy": strategy,
        "size_bytes": os.path.getsize(path),
    }


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python3 detect_filetype.py <path-to-file>"}))
        sys.exit(1)

    result = detect(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
