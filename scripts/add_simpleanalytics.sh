#!/bin/bash
set -euo pipefail

# Insert SimpleAnalytics script tag before </body> in all .html files that don't already contain it
SCRIPT_LINE='    <script async src="https://scripts.simpleanalyticscdn.com/latest.js"></script>'

find . -type f -name "*.html" -print0 | while IFS= read -r -d '' f; do
  # skip files already containing the script
  if grep -q "scripts.simpleanalyticscdn.com/latest.js" "$f"; then
    continue
  fi
  # insert script before the last </body>
  perl -0777 -pe "s|</body>|${SCRIPT_LINE}\n</body>|i" -i "$f"
  echo "Updated: $f"
done
