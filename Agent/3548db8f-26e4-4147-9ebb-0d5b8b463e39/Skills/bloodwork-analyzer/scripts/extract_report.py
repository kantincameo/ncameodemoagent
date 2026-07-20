#!/usr/bin/env python3
"""
extract_report.py — Reliable text extraction from a blood report PDF.

Usage:
    python3 extract_report.py path/to/report.pdf

Prints the extracted raw text to stdout, using `pdftotext -layout` so
numeric columns / marker-value alignment survives. This is the mandatory
first step before matching any marker — never eyeball a PDF for numbers.

For screenshots or image files, DO NOT use this script — view the image
directly (native vision) and transcribe every marker name, value, and
flag (H/L/normal) verbatim before proceeding to matching.

No internet access is used or required here.
"""
import sys
import subprocess
import shutil
import os


def extract_pdf_text(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"ERROR: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if shutil.which("pdftotext") is None:
        print("ERROR: pdftotext not found. Install poppler-utils (apt-get install poppler-utils).",
              file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: pdftotext failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return result.stdout


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 extract_report.py path/to/report.pdf", file=sys.stderr)
        sys.exit(1)

    text = extract_pdf_text(sys.argv[1])
    print(text)
    print(f"\n--- Extracted {len(text)} characters. ---", file=sys.stderr)
    print("Next: grep -i this output for each candidate marker name from read_markers.py "
          "before trusting a match. Wrap matched substrings in repr() to catch invisible "
          "Unicode/whitespace mismatches.", file=sys.stderr)
