#!/usr/bin/env bash
# Portfolio auto-updater — run by Claude Code after project changes
# Usage: bash update.sh

set -e
PORTFOLIO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[portfolio] Updating graphs..."

# Copy latest Graphify graphs
for project in \
  "/c/Users/Till/Projects/imperium/graphify-out/graph.html:imperium" \
  "/c/Users/Till/Documents/WarlordBritannia/graphify-out/graph.html:britannia" \
  "/c/Users/Till/Desktop/GynToolRepo/graphify-out/graph.html:gyntools"; do
  src="${project%%:*}"
  name="${project##*:}"
  if [ -f "$src" ]; then
    cp "$src" "$PORTFOLIO_DIR/graphs/${name}.html"
    echo "  copied $name graph"
  fi
done

# Collect project stats as JSON for the site
python -c "
import json, subprocess, os
from pathlib import Path
from datetime import datetime

projects = [
    {
        'id': 'imperium',
        'path': 'C:/Users/Till/Projects/imperium',
        'graph': 'C:/Users/Till/Projects/imperium/graphify-out/graph.json',
    },
    {
        'id': 'britannia',
        'path': 'C:/Users/Till/Documents/WarlordBritannia',
        'graph': 'C:/Users/Till/Documents/WarlordBritannia/graphify-out/graph.json',
    },
    {
        'id': 'gyntools',
        'path': 'C:/Users/Till/Desktop/GynToolRepo',
        'graph': 'C:/Users/Till/Desktop/GynToolRepo/graphify-out/graph.json',
    },
    {
        'id': 'intensivtools',
        'path': 'C:/Users/Till/Projects/intensivtools',
        'graph': None,
    },
]

stats = {}
for p in projects:
    info = {'id': p['id']}

    # Git info
    try:
        os.chdir(p['path'])
        result = subprocess.run(['git', 'log', '-1', '--format=%h|%s|%aI'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            parts = result.stdout.strip().split('|', 2)
            info['last_commit_hash'] = parts[0]
            info['last_commit_msg'] = parts[1]
            info['last_commit_date'] = parts[2]

        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            info['total_commits'] = int(result.stdout.strip())
    except Exception:
        pass

    # Graphify stats
    if p['graph'] and Path(p['graph']).exists():
        try:
            from networkx.readwrite import json_graph
            import networkx as nx
            data = json.loads(Path(p['graph']).read_text(encoding='utf-8'))
            G = json_graph.node_link_graph(data, edges='links')
            info['graph_nodes'] = G.number_of_nodes()
            info['graph_edges'] = G.number_of_edges()
        except Exception:
            pass

    stats[p['id']] = info

Path('$PORTFOLIO_DIR/project-stats.json').write_text(json.dumps(stats, indent=2), encoding='utf-8')
print('[portfolio] Stats updated')
"

echo "[portfolio] Deploying to Cloudflare..."
cd "$PORTFOLIO_DIR"
npx wrangler pages deploy . --project-name portfolio --commit-dirty=true 2>&1 | tail -2

echo "[portfolio] Done"
