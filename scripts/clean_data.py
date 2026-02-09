#!/usr/bin/env python3
# just keep adapting this
import json
import argparse
from pathlib import Path
import re
import shutil


def normalize_two_digit_year(y: int) -> int:
    return 2000 + y if y <= 50 else 1900 + y


def main():
    parser = argparse.ArgumentParser(description='Clean data.json by extracting leading dates from alt into date field')
    parser.add_argument('--input', '-i', default=None, help='Path to input JSON (defaults to repo root data.json)')
    parser.add_argument('--backup', '-b', default=None, help='Path to backup original JSON')
    parser.add_argument('--output', '-o', default=None, help='Path to write output JSON (defaults to overwrite input)')
    args = parser.parse_args()

    script_root = Path(__file__).resolve().parent.parent
    input_path = Path(args.input) if args.input else script_root / 'data.json'
    if not input_path.exists():
        print(f"Input not found: {input_path}")
        return

    backup_path = Path(args.backup) if args.backup else input_path.with_suffix('.json.bak')
    output_path = Path(args.output) if args.output else input_path

    shutil.copy2(input_path, backup_path)
    print(f"Backed up original to: {backup_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    date_re = re.compile(r'^\s*[^0-9\n]*([0-1]?\d)/([0-3]?\d)/(\d{2,4})\s*\n', re.MULTILINE)

    changed = 0
    for item in data:
        alt = item.get('alt')
        if not isinstance(alt, str) or not alt:
            continue
        m = date_re.match(alt)
        if not m:
            continue

        mm = int(m.group(1))
        dd = int(m.group(2))
        yy = m.group(3)
        if len(yy) == 4:
            year = int(yy)
        else:
            y = int(yy)
            year = normalize_two_digit_year(y)

        try:
            date_iso = f"{year:04d}-{mm:02d}-{dd:02d}"
        except Exception:
            continue

        item['date'] = date_iso

        new_alt = alt[m.end():].lstrip('\n')

        new_alt = new_alt.lstrip()
        item['alt'] = new_alt
        changed += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Processed {len(data)} items, updated {changed} records. Wrote output to {output_path}")


if __name__ == '__main__':
    main()
