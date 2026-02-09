import argparse
import json
import os
import html
from pathlib import Path
import sys


def load_json(path):
  try:
    with open(path, 'r', encoding='utf-8') as f:
      return json.load(f)
  except Exception as e:
    print(f"Failed to load JSON from {path}: {e}")
    return None

# Tweet page template with placeholders
blueprint = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="description" content="{safe_alt_110}">
    <meta property="og:title" content="{page_title}">
    <meta property="og:image:alt" content="{safe_alt_full}">
    <meta property="og:description" content="{safe_alt_full}">
    <meta property="og:image" content="/img/{id}.webp">
    <link rel="icon" type="image/png" href="/favicon.png">
    <meta name="google" content="notranslate">
    <title>{page_title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/styles.css" rel="stylesheet">
    <script type="application/ld+json">
    {json_ld}
    </script>
  </head>
  <body>
    <main class="container py-3" role="main">
      <div id="tweet-container">
        <div class="row tweet-row">
          <div class="col-12 col-md-6 img-col">
            <img src="/img/{id}.webp" class="img-fluid rounded" alt="{safe_alt_full}">
          </div>
          <div class="col-12 col-md-6">
            <h4><span class="name-text">{name}</span> <span class="handle-text fs-6 d-block d-md-inline">@{handle}</span></h4>
            <p>{alt_with_br}</p>
            <a href="/" onclick="if(history.length > 1){{ event.preventDefault(); history.back(); }}" class="btn btn-sm btn-link">Back</a>
            <button id="random-btn" class="btn btn-sm btn-outline-secondary ms-2">Random</button>
          </div>
        </div>
      </div>
    </main>

    <script>
      fetch('/data.min.json').then(r => r.json()).then(data => {{
        document.getElementById('random-btn').addEventListener('click', () => {{
          let idx = Math.floor(Math.random() * data.length);
          window.location.href = `/tweet/${{data[idx].id}}/`;
        }});
      }});

      document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') window.location.href = '/';
      }});
    </script>
  </body>
</html>
"""

def bake():
  parser = argparse.ArgumentParser(description='Bake static tweet pages from JSON')
  parser.add_argument('--input', '-i', default=None, help='Path to input JSON file (defaults to repo root data.json)')
  parser.add_argument('--ids', help="Comma-separated ids to process or 'all' (default: all)")
  parser.add_argument('--limit', type=int, help='Limit number of tweets processed')
  parser.add_argument('--log', default=None, help='Path to log file (defaults to root/logs/bake.log)')
  args = parser.parse_args()

  script_root = Path(__file__).resolve().parent.parent
  default_input = script_root / 'data.json'
  input_path = Path(args.input) if args.input else default_input

  tweets = load_json(input_path)
  if tweets is None:
    print('No tweets loaded, aborting.')
    sys.exit(1)

  # Prepare log
  logs_dir = script_root / 'logs'
  logs_dir.mkdir(exist_ok=True)
  log_file = Path(args.log) if args.log else logs_dir / 'bake.log'

  out_root = script_root / 'tweet'
  out_root.mkdir(exist_ok=True)

  # Determine IDs to process
  ids_arg = args.ids
  if ids_arg and ids_arg.lower() != 'all':
    wanted_ids = set(s.strip() for s in ids_arg.split(','))
    tweets = [t for t in tweets if str(t.get('id')) in wanted_ids]

  if args.limit:
    tweets = tweets[: args.limit]

  created = 0
  with open(log_file, 'a', encoding='utf-8') as logf:
    for t in tweets:
      try:
        raw_id = t.get('id')
        if raw_id is None:
          logf.write(f"MISSING_ID\tFAIL\tmissing id\n")
          continue
        tw_id = str(raw_id)

        name = t.get('name', '')
        handle = t.get('handle', '')
        raw_alt = t.get('alt', '')

        # Normalize new lines, strip, decode HTML
        raw_alt = raw_alt.replace('\r\n', '\n').replace('\r', '\n').strip()
        raw_alt = html.unescape(raw_alt)

        # process and escape
        escaped = html.escape(raw_alt, quote=True)
        safe_alt_full = escaped
        safe_alt_110 = safe_alt_full[:110] + '...' if len(safe_alt_full) > 110 else safe_alt_full
        alt_with_br = escaped.replace('\n', '<br>')
        page_title = f"{raw_alt[:50]} — {name} @{handle}".strip()

        # JSON-LD (use relative paths, no hardcoded domain)
        json_ld_data = {
          "@context": "https://schema.org",
          "@graph": [
            {
              "@type": "BreadcrumbList",
              "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
                {"@type": "ListItem", "position": 2, "name": "Tweet", "item": f"/tweet/{tw_id}/"}
              ]
            },
            {
              "@type": "SocialMediaPosting",
              "identifier": tw_id,
              "headline": raw_alt[:110],
              "articleBody": raw_alt,
              "image": f"/img/{tw_id}.webp",
              "author": {"@type": "Person", "name": name, "alternateName": handle}
            }
          ]
        }

        folder = out_root / tw_id
        folder.mkdir(parents=True, exist_ok=True)

        rendered = blueprint.format(
          id=tw_id,
          name=html.escape(name),
          handle=html.escape(handle),
          safe_alt_full=safe_alt_full,
          safe_alt_110=safe_alt_110,
          alt_with_br=alt_with_br,
          page_title=html.escape(page_title),
          json_ld=json.dumps(json_ld_data, indent=2)
        )

        with open(folder / 'index.html', 'w', encoding='utf-8') as f:
          f.write(rendered)

        logf.write(f"{tw_id}\tOK\n")
        created += 1
      except Exception as e:
        try:
          logf.write(f"{t.get('id', 'UNKNOWN')}\tFAIL\t{e}\n")
        except Exception:
          logf.write(f"UNKNOWN\tFAIL\t{e}\n")

  print(f"Bake complete. Created {created} pages. Log: {log_file}")

if __name__ == "__main__":
    bake()