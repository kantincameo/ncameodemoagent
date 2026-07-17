#!/usr/bin/env python3
"""
fetch_source.py

Resolves a URL (direct file link, Google Drive/Dropbox/OneDrive share
link) to a local downloaded file, so it can then be read with the
normal type-specific tools (pdf/docx/xlsx skills, vision for images).

NOTE: This script requires network access. In sandboxed environments
without internet access, use the web_fetch tool instead (see
references/source_resolution.md) rather than this script.

Usage:
    python3 fetch_source.py <url> [--out /tmp/downloaded_source]

Behavior:
    - Detects Google Drive / Dropbox / OneDrive share links and
      rewrites them to a direct-download URL.
    - Downloads the (possibly rewritten) URL to a local file.
    - Prints the local path and detected extension as JSON.
"""

import sys
import os
import re
import argparse
import json
import urllib.request
from urllib.parse import urlparse, parse_qs


def rewrite_share_link(url: str) -> str:
    """Convert common cloud-storage share links to direct-download URLs."""

    # Google Drive: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    m = re.search(r"drive\.google\.com/file/d/([^/]+)/", url)
    if m:
        file_id = m.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    # Google Drive: already in open?id=FILE_ID or uc?id=FILE_ID form
    if "drive.google.com" in url:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "id" in qs:
            file_id = qs["id"][0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"

    # Dropbox: ...?dl=0  ->  ...?dl=1
    if "dropbox.com" in url:
        if "dl=0" in url:
            return url.replace("dl=0", "dl=1")
        if "?" not in url:
            return url + "?dl=1"
        if "dl=1" not in url:
            return url + "&dl=1"

    # OneDrive: append download=1 if not present
    if "1drv.ms" in url or "onedrive.live.com" in url:
        if "download=1" not in url:
            sep = "&" if "?" in url else "?"
            return url + f"{sep}download=1"

    return url


def guess_extension(url: str, content_type: str = "") -> str:
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    if ext:
        return ext

    mapping = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "text/csv": ".csv",
        "image/jpeg": ".jpg",
        "image/png": ".png",
    }
    return mapping.get(content_type.split(";")[0].strip(), "")


def fetch(url: str, out_prefix: str) -> dict:
    resolved_url = rewrite_share_link(url)

    req = urllib.request.Request(resolved_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()

    ext = guess_extension(resolved_url, content_type) or ".bin"
    out_path = out_prefix + ext

    with open(out_path, "wb") as f:
        f.write(data)

    return {
        "original_url": url,
        "resolved_url": resolved_url,
        "local_path": out_path,
        "content_type": content_type,
        "size_bytes": len(data),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to fetch (direct file link or cloud share link)")
    parser.add_argument("--out", default="/tmp/downloaded_source",
                         help="Output path prefix (extension auto-detected and appended)")
    args = parser.parse_args()

    try:
        result = fetch(args.url, args.out)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "url": args.url}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
