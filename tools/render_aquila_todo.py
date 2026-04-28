from __future__ import annotations

import argparse
import html
import re
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "section"


def format_inline(text: str) -> str:
    placeholders: list[str] = []

    def stash(pattern: str, renderer) -> None:
        nonlocal text

        def repl(match: re.Match[str]) -> str:
            token = f"@@TOKEN{len(placeholders)}@@"
            placeholders.append(renderer(match))
            return token

        text = re.sub(pattern, repl, text)

    stash(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>")
    stash(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>',
    )

    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    for index, rendered in enumerate(placeholders):
        text = text.replace(f"@@TOKEN{index}@@", rendered)

    return text


def render_markdown(source: Path) -> tuple[str, list[tuple[str, str]]]:
    blocks: list[str] = []
    nav: list[tuple[str, str]] = []
    paragraph_lines: list[str] = []
    list_kind: str | None = None
    list_items: list[tuple[bool | None, str]] = []
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            text = " ".join(line.strip() for line in paragraph_lines)
            blocks.append(f"<p>{format_inline(text)}</p>")
            paragraph_lines = []

    def flush_list() -> None:
        nonlocal list_kind, list_items
        if not list_kind or not list_items:
            list_kind = None
            list_items = []
            return

        if list_kind == "check":
            blocks.append('<ul class="checklist">')
            for checked, item_text in list_items:
                state = "done" if checked else "open"
                icon = "&#10003;" if checked else "&#9633;"
                blocks.append(
                    f'<li class="{state}"><span class="check-icon">{icon}</span><span>{format_inline(item_text)}</span></li>'
                )
            blocks.append("</ul>")
        elif list_kind == "ol":
            blocks.append("<ol>")
            for _, item_text in list_items:
                blocks.append(f"<li>{format_inline(item_text)}</li>")
            blocks.append("</ol>")
        else:
            blocks.append("<ul>")
            for _, item_text in list_items:
                blocks.append(f"<li>{format_inline(item_text)}</li>")
            blocks.append("</ul>")

        list_kind = None
        list_items = []

    for raw_line in source.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                blocks.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                code_lines.append(line)
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            in_code = True
            code_lines = []
            continue

        heading_match = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            section_id = slugify(title)
            if level == 2:
                nav.append((title, section_id))
            blocks.append(f'<h{level} id="{section_id}">{format_inline(title)}</h{level}>')
            continue

        if stripped == "---":
            flush_paragraph()
            flush_list()
            blocks.append("<hr>")
            continue

        checkbox_match = re.match(r"^- \[([ xX])\]\s+(.*)$", stripped)
        if checkbox_match:
            flush_paragraph()
            if list_kind not in (None, "check"):
                flush_list()
            list_kind = "check"
            list_items.append((checkbox_match.group(1).lower() == "x", checkbox_match.group(2)))
            continue

        bullet_match = re.match(r"^- (.*)$", stripped)
        if bullet_match:
            flush_paragraph()
            if list_kind not in (None, "ul"):
                flush_list()
            list_kind = "ul"
            list_items.append((None, bullet_match.group(1)))
            continue

        ordered_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ordered_match:
            flush_paragraph()
            if list_kind not in (None, "ol"):
                flush_list()
            list_kind = "ol"
            list_items.append((None, ordered_match.group(1)))
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks), nav


def build_page(title: str, source: Path, github_url: str) -> str:
    body_html, nav = render_markdown(source)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    nav_html = "\n".join(
        f'<a href="#{section_id}">{html.escape(label)}</a>' for label, section_id in nav
    )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="Aquila Roadmap und To-do-Planung">
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#0a0a0f;color:#e2e2e8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;line-height:1.7}}
.page{{max-width:980px;margin:0 auto;padding:32px 20px 80px}}
.hero{{margin-bottom:28px;padding:24px;border:1px solid #1e1e2e;border-radius:10px;background:#12121a}}
.hero h1{{margin:0 0 10px;font-size:1.8rem}}
.hero p{{margin:0 0 14px;color:#9a9ab0}}
.meta{{display:flex;gap:14px;flex-wrap:wrap;font-size:.82rem;color:#8b8ba1}}
.meta a{{color:#7ea3ff;text-decoration:none}}
.meta a:hover{{text-decoration:underline}}
.nav{{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 24px}}
.nav a{{color:#7ea3ff;text-decoration:none;font-size:.82rem;padding:6px 10px;border:1px solid #2a4a99;border-radius:999px;background:#12121a}}
.nav a:hover{{background:#1a2240}}
.content{{padding:28px;border:1px solid #1e1e2e;border-radius:10px;background:#12121a}}
h1,h2,h3{{line-height:1.25}}
h2{{margin:32px 0 12px;font-size:1.28rem}}
h3{{margin:24px 0 10px;font-size:1.02rem;color:#f1f1f5}}
p{{margin:0 0 14px;color:#d7d7de}}
ul,ol{{margin:0 0 16px 22px;padding:0}}
li{{margin:0 0 8px}}
hr{{border:none;border-top:1px solid #23233a;margin:26px 0}}
code{{font-family:"SF Mono",Consolas,monospace;background:#0e1017;padding:2px 6px;border-radius:4px;color:#dfe7ff}}
pre{{background:#0e1017;border:1px solid #1f2436;padding:14px;border-radius:8px;overflow:auto;margin:0 0 18px}}
pre code{{background:none;padding:0}}
a{{color:#7ea3ff}}
.checklist{{list-style:none;margin-left:0}}
.checklist li{{display:flex;gap:10px;align-items:flex-start;padding:8px 10px;border:1px solid #1f2436;border-radius:8px;background:#0e1017;margin-bottom:8px}}
.checklist li.done{{border-color:#234a34;background:#101813}}
.check-icon{{width:18px;flex:0 0 18px;color:#8fe3b1}}
.footer{{margin-top:20px;font-size:.8rem;color:#8b8ba1}}
@media (max-width: 700px) {{
  .page{{padding:20px 14px 60px}}
  .content{{padding:20px}}
  .hero h1{{font-size:1.45rem}}
}}
</style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <h1>{html.escape(title)}</h1>
      <p>Automatisch aus der kanonischen Aquila-Roadmap erzeugt. Diese Seite ist die Website-Ansicht der langfristigen To-do-Planung.</p>
      <div class="meta">
        <span>Quelle: <code>{html.escape(str(source))}</code></span>
        <span>Generiert: {generated}</span>
        <a href="{html.escape(github_url, quote=True)}" target="_blank" rel="noopener">Auf GitHub ansehen</a>
        <a href="index.html">Zurueck zum Portfolio</a>
      </div>
    </section>
    <nav class="nav">
      {nav_html}
    </nav>
    <main class="content">
      {body_html}
    </main>
    <div class="footer">
      Diese Seite wird beim Portfolio-Update aus <code>docs/TODO_AQUILA.md</code> neu erzeugt.
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="Aquila Roadmap / To-do")
    parser.add_argument("--github-url", required=True)
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    output.write_text(build_page(args.title, source, args.github_url), encoding="utf-8")
    print(f"[roadmap] wrote {output}")


if __name__ == "__main__":
    main()
