#!/usr/bin/env bash
# Portfolio auto-updater — run by Claude Code after project changes
# Usage: bash update.sh
set -e
PORTFOLIO_DIR="$(cd "$(dirname "$0")" && pwd)"
# Windows-compatible path for Python
export PORTFOLIO_DIR_WIN="$(cygpath -w "$PORTFOLIO_DIR" 2>/dev/null || echo "$PORTFOLIO_DIR")"
cd "$PORTFOLIO_DIR"

echo "[portfolio] Copying Graphify graphs..."
mkdir -p graphs
for entry in \
  "/c/Users/Till/Projects/imperium/graphify-out/graph.html:imperium" \
  "/c/Users/Till/Documents/WarlordBritannia/graphify-out/graph.html:britannia" \
  "/c/Users/Till/Desktop/GynToolRepo/graphify-out/graph.html:gyntools" \
  "/c/Users/Till/Projects/intensivtools/graphify-out/graph.html:intensivtools" \
  "/c/Users/Till/gynteach/graphify-out/graph.html:gynteach"; do
  src="${entry%%:*}"
  name="${entry##*:}"
  if [ -f "$src" ]; then
    cp "$src" "graphs/${name}.html"
    echo "  + $name"
  fi
done

echo "[portfolio] Collecting stats and updating HTML..."
PYTHONIOENCODING=utf-8 python -c "
import json, subprocess, os, re
from pathlib import Path

projects = [
    {'id': 'imperium',      'path': 'C:/Users/Till/Projects/imperium',         'graph': 'C:/Users/Till/Projects/imperium/graphify-out/graph.json'},
    {'id': 'britannia',     'path': 'C:/Users/Till/Documents/WarlordBritannia','graph': 'C:/Users/Till/Documents/WarlordBritannia/graphify-out/graph.json'},
    {'id': 'gynteach',      'path': 'C:/Users/Till/gynteach',                  'graph': 'C:/Users/Till/gynteach/graphify-out/graph.json'},
    {'id': 'intensivtools', 'path': 'C:/Users/Till/Projects/intensivtools',    'graph': 'C:/Users/Till/Projects/intensivtools/graphify-out/graph.json'},
    {'id': 'gyntools',      'path': 'C:/Users/Till/Desktop/GynToolRepo',       'graph': 'C:/Users/Till/Desktop/GynToolRepo/graphify-out/graph.json'},
]

stats = {}
for p in projects:
    info = {}

    # Git stats
    try:
        os.chdir(p['path'])
        r = subprocess.run(['git', 'log', '-1', '--format=%s'], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            info['last_commit'] = r.stdout.strip()
        r = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            info['commits'] = int(r.stdout.strip())
    except Exception:
        pass

    # Graphify stats (no networkx needed)
    gp = Path(p['graph']) if p['graph'] else None
    if gp and gp.exists():
        try:
            data = json.loads(gp.read_text(encoding='utf-8'))
            nodes = data.get('nodes', [])
            info['nodes'] = len(nodes)
            info['edges'] = len(data.get('links', []))
            info['communities'] = len(set(
                n.get('community') for n in nodes if n.get('community') is not None
            ))
        except Exception:
            pass

    stats[p['id']] = info

# Read and update index.html
html_path = Path(os.environ.get('PORTFOLIO_DIR_WIN', '$PORTFOLIO_DIR') + '/index.html')
html = html_path.read_text(encoding='utf-8')

for pid, s in stats.items():
    # Find the card for this project
    card_pattern = f'data-project=\"{pid}\"'
    card_start = html.find(card_pattern)
    if card_start == -1:
        continue

    # Find the end of this card (next card or end of projects div)
    next_card = html.find('data-project=', card_start + len(card_pattern))
    if next_card == -1:
        next_card = len(html)
    card_html = html[card_start:next_card]

    # Update last-commit
    if 'last_commit' in s:
        card_html = re.sub(
            r'(data-stat=\"last-commit\">)[^<]*(</span>)',
            lambda m: m.group(1) + s['last_commit'] + m.group(2),
            card_html
        )

    # Update commits count
    if 'commits' in s:
        card_html = re.sub(
            r'(data-stat=\"commits\">)[^<]*(</span>)',
            lambda m: m.group(1) + f\"{s['commits']} Commits\" + m.group(2),
            card_html
        )

    # Update nodes
    if 'nodes' in s:
        card_html = re.sub(
            r'(data-stat=\"nodes\">).*?(Nodes</span>)',
            lambda m: m.group(1) + f\"<span class=\\\"label\\\">Graphify:</span> {s['nodes']:,} \".replace(',', '.') + m.group(2),
            card_html
        )

    # Update edges
    if 'edges' in s:
        card_html = re.sub(
            r'(data-stat=\"edges\">)[^<]*(</span>)',
            lambda m: m.group(1) + f\"{s['edges']:,} Edges\".replace(',', '.') + m.group(2),
            card_html
        )

    # Update communities
    if 'communities' in s:
        card_html = re.sub(
            r'(data-stat=\"communities\">)[^<]*(</span>)',
            lambda m: m.group(1) + f\"{s['communities']} Communities\" + m.group(2),
            card_html
        )

    html = html[:card_start] + card_html + html[next_card:]

Path(os.environ.get('PORTFOLIO_DIR_WIN', '$PORTFOLIO_DIR') + '/index.html').write_text(html, encoding='utf-8')

# Summary
for pid, s in stats.items():
    parts = [pid]
    if 'commits' in s: parts.append(f\"{s['commits']} commits\")
    if 'nodes' in s: parts.append(f\"{s['nodes']}n/{s['edges']}e\")
    if 'last_commit' in s: parts.append(s['last_commit'][:50])
    print(f\"  {' | '.join(parts)}\")
"

echo "[portfolio] Deploying to Cloudflare..."
npx wrangler pages deploy . --project-name portfolio --commit-dirty=true 2>&1 | tail -2

echo "[portfolio] Done"
