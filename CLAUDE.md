# Portfolio

## Uebersicht
Persoenliches Projekt-Dashboard. Statische HTML-Seite auf Cloudflare Pages.
Zeigt alle 7 Projekt-Karten plus Portfolio-Repo-Hinweise mit Beschreibung, Status und technischen Details.

## Deploy
```bash
bash update.sh          # Komplett: Graphs kopieren + Stats aktualisieren + Deploy
# oder manuell:
npx wrangler pages deploy . --project-name portfolio --commit-dirty=true
```

## Live
https://portfolio-7wc.pages.dev

## Struktur
- `index.html` - Hauptseite mit 7 Projekt-Karten (data-project Attribute fuer automatisches Update)
- `update.sh` - Automatisierung: Graphs kopieren, Git/Graphify-Stats sammeln, in HTML injizieren, deployen
- `aquila-roadmap.html` - generierte Website-Ansicht der kanonischen Aquila-Roadmap
- `tools/render_aquila_todo.py` - rendert `C:\Users\Till\Projects\aquila-westmed\docs\TODO_AQUILA.md` zu `aquila-roadmap.html`
- `graphs/` - Kopierte Graphify HTML-Visualisierungen (aquila, imperium, britannia, postbellum, gyntools, intensivtools, gynteach)

## Wie Stats aktualisiert werden
1. update.sh liest `graph.json` aus jedem Projekt (Nodes, Edges, Communities)
2. update.sh liest `git log` aus jedem Projekt (letzter Commit, Commit-Anzahl)
3. Python injiziert Stats in `index.html` via `data-stat` Attribute
4. Deploy zu Cloudflare Pages

## Projekte (alle 8 inkl. Portfolio-Repo)
| Projekt | Pfad |
|---------|------|
| Aquila | C:\Users\Till\Projects\AquilaUnity (aktive Unity-Game-Schiene) + C:\Users\Till\Projects\aquila-westmed (Map-/Bake-Pipeline) |
| Imperium | C:\Users\Till\Projects\imperium |
| Warlord Britannia | C:\Users\Till\Documents\WarlordBritannia |
| PostBellum | C:\Users\Till\Projects\postbellum |
| GynTeach | C:\Users\Till\gynteach |
| IntensivTools | C:\Users\Till\Projects\intensivtools |
| GynTools | C:\Users\Till\Desktop\GynToolRepo |
| Portfolio | C:\Users\Till\Projects\portfolio |
