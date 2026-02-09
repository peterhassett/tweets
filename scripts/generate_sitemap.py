#!/usr/bin/env python3
"""
Generate sitemap.xml for homepage and tweet pages.

Usage:
    python3 scripts/generate_sitemap.py --input data.json --base-url https://bestoftwitter.com --output sitemap.xml

The script reads JSON or JSONL and extracts tweet IDs from common keys (`id`, `id_str`, `tweet_id`).
It writes a standard sitemap at the specified output path.

Updated from using querystring params to static paths.
"""
import argparse
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


def parse_args():
    p = argparse.ArgumentParser(description="Generate sitemap.xml including tweet?id={id} pages")
    p.add_argument("--input", "-i", default="data.json", help="Input JSON or JSONL file containing tweets")
    p.add_argument("--output", "-o", default="sitemap.xml", help="Output sitemap file")
    p.add_argument("--base-url", "-b", required=True, help="Base URL (e.g. https://bestoftwitter.com)")
    return p.parse_args()


def load_json_candidates(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except Exception:
        objs = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                objs.append(json.loads(line))
            except Exception:
                continue
        if objs:
            return objs
        raise


def extract_ids(data):
    ids = set()

    def maybe_add(val):
        if val is None:
            return
        if isinstance(val, int):
            ids.add(str(val))
        elif isinstance(val, str) and val.strip():
            ids.add(val.strip())

    if isinstance(data, dict):
        keys_all_numeric = all((k.isdigit() for k in data.keys())) if data.keys() else False
        if keys_all_numeric:
            for k in data.keys():
                ids.add(k)
            return ids

        for key, val in data.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                for item in val:
                    for k in ("id", "id_str", "tweet_id", "tweetId", "tweetID"):
                        if k in item:
                            maybe_add(item.get(k))
                if ids:
                    return ids
        for v in data.values():
            if isinstance(v, dict):
                for k in ("id", "id_str", "tweet_id", "tweetId", "tweetID"):
                    if k in v:
                        maybe_add(v.get(k))

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k in ("id", "id_str", "tweet_id", "tweetId", "tweetID"):
                    if k in item:
                        maybe_add(item.get(k))
            elif isinstance(item, (str, int)):
                maybe_add(item)

    return ids


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level + 1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def build_sitemap(base_url: str, ids):
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace('', ns)
    urlset = ET.Element(ET.QName(ns, "urlset"))

    def add_loc(path):
        url = ET.SubElement(urlset, ET.QName(ns, "url"))
        loc = ET.SubElement(url, ET.QName(ns, "loc"))
        loc.text = path

    base = base_url.rstrip("/")
    add_loc(base + "/")
    for id_ in sorted(ids, key=lambda s: s):
        add_loc(f"{base}/tweet/{id_}")

    indent(urlset)
    return urlset


def main():
    args = parse_args()
    p = Path(args.input)
    if not p.exists():
        print(f"Input file not found: {p}", file=sys.stderr)
        sys.exit(2)

    try:
        data = load_json_candidates(p)
    except Exception as e:
        print(f"Failed to parse input file: {e}", file=sys.stderr)
        sys.exit(3)

    ids = extract_ids(data)
    if not ids:
        print("No tweet ids found in input file; sitemap will only include homepage.")

    urlset = build_sitemap(args.base_url, ids)
    tree = ET.ElementTree(urlset)
    outp = Path(args.output)
    tree.write(outp, encoding="utf-8", xml_declaration=True)
    print(f"Wrote sitemap with {1 + len(ids)} urls to {outp}")


if __name__ == "__main__":
    main()
