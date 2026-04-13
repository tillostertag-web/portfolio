# Portfolio

## Uebersicht
Persoenliches Projekt-Dashboard. Statische HTML-Seite auf Cloudflare Pages.
Zeigt alle 6 Projekte mit Beschreibung, Status, Graphify Knowledge Graphs und technischen Details.

## Deploy
```bash
bash update.sh          # Komplett: Graphs kopieren + Stats aktualisieren + Deploy
# oder manuell:
npx wrangler pages deploy . --project-name portfolio --commit-dirty=true
```

## Live
https://portfolio-7wc.pages.dev

## Struktur
- `index.html` — Hauptseite mit 6 Projekt-Karten (data-project Attribute fuer automatisches Update)
- `update.sh` — Automatisierung: Graphs kopieren, Git/Graphify-Stats sammeln, in HTML injizieren, deployen
- `graphs/` — Kopierte Graphify HTML-Visualisierungen (imperium, britannia, gyntools, intensivtools, gynteach)

## Wie Stats aktualisiert werden
1. update.sh liest graph.json aus jedem Projekt (Nodes, Edges, Communities)
2. update.sh liest git log aus jedem Projekt (letzter Commit, Commit-Anzahl)
3. Python injiziert Stats in index.html via data-stat Attribute
4. Deployed zu Cloudflare Pages

## Projekte (alle 6)
| Projekt | Pfad |
|---------|------|
| Imperium | C:\Users\Till\Projects\imperium |
| Warlord Britannia | C:\Users\Till\Documents\WarlordBritannia |
| GynTeach | C:\Users\Till\gynteach |
| IntensivTools | C:\Users\Till\Projects\intensivtools |
| GynTools | C:\Users\Till\Desktop\GynToolRepo |
| Portfolio | C:\Users\Till\Projects\portfolio |
