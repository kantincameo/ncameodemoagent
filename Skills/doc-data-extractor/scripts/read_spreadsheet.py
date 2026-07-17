#!/usr/bin/env python3
"""
read_spreadsheet.py

Reads a CSV/TSV/XLSX/XLS file and dumps its rows as JSON so the model
can scan them for name/email/phone-like columns. This is a reading
helper only -- it does NOT produce the final schema output itself,
it just gets raw row data into an easy-to-scan JSON form.

Usage:
    python3 read_spreadsheet.py <path-to-file> [--sheet SHEET_NAME]

Requires: pandas, openpyxl (for .xlsx)
    pip install pandas openpyxl --break-system-packages
"""

import sys
import os
import json
import argparse


def read_file(path: str, sheet: str | None = None) -> dict:
    import pandas as pd

    ext = os.path.splitext(path.lower())[1]

    if ext in (".csv",):
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    elif ext in (".tsv",):
        df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    elif ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path, sheet_name=sheet if sheet else 0, dtype=str)
        df = df.fillna("")
    else:
        raise ValueError(f"Unsupported spreadsheet extension: {ext}")

    return {
        "path": path,
        "columns": list(df.columns),
        "row_count": len(df),
        "rows": df.to_dict(orient="records"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the spreadsheet file")
    parser.add_argument("--sheet", default=None, help="Sheet name (xlsx only)")
    args = parser.parse_args()

    try:
        result = read_file(args.path, args.sheet)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
