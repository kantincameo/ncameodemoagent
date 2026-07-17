"""
chunk_pdf_text.py
-----------------
Utility to split large PDF-extracted text into manageable chunks for QA.

Usage:
    python chunk_pdf_text.py <input.txt> [--chunk-size 3000]

Output:
    Prints numbered chunks to stdout.
"""

import argparse
import sys

def chunk_text(text: str, chunk_size: int = 3000) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    step = int(chunk_size * 0.9)  # 10% overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def main():
    parser = argparse.ArgumentParser(description="Chunk PDF text for QA")
    parser.add_argument("input", help="Path to extracted PDF text file")
    parser.add_argument("--chunk-size", type=int, default=3000,
                        help="Words per chunk (default: 3000)")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text, args.chunk_size)
    print(f"Total chunks: {len(chunks)}\n{'='*40}")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ---\n{chunk}\n")

if __name__ == "__main__":
    main()
