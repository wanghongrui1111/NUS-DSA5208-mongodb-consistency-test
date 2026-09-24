"""Verify that every stored result was checked after collection."""

import json
import sys
from pathlib import Path


def main(root):
    files = sorted(Path(root).glob("*/**/results.json"))
    if not files:
        raise SystemExit("no results.json files found")
    total = 0
    for path in files:
        records = json.loads(path.read_text(encoding="utf-8"))
        if not records or any("check" not in record or "ops" not in record for record in records):
            raise SystemExit(f"unchecked or empty result: {path}")
        total += len(records)
    print(f"verified {total} checked cells across {len(files)} result files")


if __name__ == "__main__":
    main(sys.argv[1])
