#!/usr/bin/env python3
import json
import html
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA = os.path.join(ROOT, 'data.json')
OUT_DIR = os.path.join(ROOT, 'archive')
OUT_FILE = os.path.join(OUT_DIR, 'index.html')

with open(DATA, 'r', encoding='utf-8') as f:
    tweets = json.load(f)

os.makedirs(OUT_DIR, exist_ok=True)

def truncate(text, n=70):
    if len(text) <= n:
        return text
    return text[:n].rstrip() + '…'

def tidy(text):
    if text is None:
        return ''
    # collapse whitespace and remove newlines
    s = ' '.join(text.split())
    return s

head = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>archive</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-" crossorigin="anonymous">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <div class="container py-4">
    <div class="row">
      <div class="col-12 text-white">
        <h1 class="display-6">archive</h1>
        <div class="small d-flex flex-wrap" id="archive-list">
'''

foot = '''
        </div>
      </div>
    </div>
  </div>
</body>
</html>
'''

with open(OUT_FILE, 'w', encoding='utf-8') as out:
    out.write(head)
    for t in tweets:
        tid = t.get('id')
        if not tid:
            continue
        alt = tidy(t.get('alt', ''))
        alt_trunc = html.escape(truncate(alt, 70))
        # absolute path so it works from /archive/
        href = f"/tweet/{html.escape(tid)}"
        out.write(f'          <a href="{href}" class="text-white text-decoration-none small me-2 mb-1">{html.escape(tid)}: {alt_trunc}</a>\n')
    out.write(foot)

print(f'Wrote {OUT_FILE}')
