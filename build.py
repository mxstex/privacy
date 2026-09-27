"""Render the apps' privacy policies into this repository's public pages.

The text is owned by each app's repository (docs/privacy-policy.md), next to the code it
describes; this repository only publishes it. Run from the workspace that holds both:

    python build.py            # writes gravity/index.html and gravity3d/index.html
    python build.py --check    # exit 1 if a page is out of date with its source

Only the Markdown the policies use is understood: headings, paragraphs, lists, tables,
block quotes, rules, **bold**, _italic_, `code` and links. Standard library only.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = {
    "gravity": ("Gravity", HERE.parent / "gravityAndroid" / "docs" / "privacy-policy.md"),
    "gravity3d": ("Gravity 3D", HERE.parent / "gravityAndroid3d" / "docs" / "privacy-policy.md"),
}

STYLE = """
  :root { color-scheme: light dark; }
  body {
    margin: 0 auto; padding: 2.5rem 1.25rem 5rem; max-width: 44rem;
    font: 16px/1.65 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #14181f; background: #fbfcfe; overflow-wrap: break-word;
  }
  @media (prefers-color-scheme: dark) {
    body { color: #dce8ff; background: #0b1018; }
    td, th { border-color: #26364f !important; }
    code { background: #16203a !important; }
    hr { border-color: #26364f !important; }
    blockquote { border-color: #2c4470 !important; color: #a9b8d3 !important; }
    a { color: #7fb0ff !important; }
  }
  h1 { font-size: 1.9rem; margin: 0 0 .25rem; letter-spacing: -.01em; }
  h2 { font-size: 1.15rem; margin: 2.25rem 0 .6rem; }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; display: block; overflow-x: auto; }
  th, td { border: 1px solid #d7dfea; padding: .5rem .7rem; text-align: left; font-size: .95rem; }
  th { font-weight: 600; }
  code { background: #eef1f6; padding: .12em .38em; border-radius: 4px; font-size: .9em; }
  ul { padding-left: 1.3rem; }
  li { margin: .3rem 0; }
  blockquote { margin: 1.25rem 0; padding: .25rem 1rem; border-left: 3px solid #cbd9ee; color: #4a5a72; }
  hr { border: 0; border-top: 1px solid #d7dfea; margin: 3.5rem 0; }
  a { color: #2f6fd0; }
  .lang { font-size: .9rem; color: #6b7a90; margin-bottom: 2rem; }
""".strip("\n")


def inline(text: str) -> str:
    """Escape, then apply code spans, links, bold and italic - code first, so nothing inside it is touched."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        s = html.escape(part, quote=False)
        # Emphasis before links, so a closing underscore never becomes part of a bare URL.
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w/])_(.+?)_(?![\w/])", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", lambda m: f'<a href="{m[2]}">{m[1]}</a>', s)
        s = re.sub(r"&lt;(https?://[^&\s]+)&gt;", lambda m: f'<a href="{m[1]}">{m[1].split("://", 1)[1]}</a>', s)
        s = re.sub(r'(?<![">])\b(https?://[^\s<)]+[^\s<).,;:])', lambda m: f'<a href="{m[1]}">{m[1]}</a>', s)
        out.append(s)
    return "".join(out)


def render(markdown: str) -> tuple[str, str]:
    """(the first heading, the body HTML). The second top-level heading starts the Czech half (id="cs")."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    body: list[str] = []
    title = ""
    headings = 0
    i = 0
    paragraph: list[str] = []
    last_hr = False

    def flush() -> None:
        if paragraph:
            # A block of "**Field:** value" lines is a header card: one line each.
            joiner = "<br>\n" if len(paragraph) > 1 and all(line.startswith("**") for line in paragraph) else " "
            body.append(f"<p>{joiner.join(inline(line) for line in paragraph)}</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush()
            i += 1
            continue
        if stripped == "---":
            flush()
            if not last_hr:
                body.append("<hr>")
            last_hr = True
            i += 1
            continue
        last_hr = False
        if stripped.startswith("# "):
            flush()
            headings += 1
            text = stripped[2:]
            title = title or text
            if headings == 2:
                if body and body[-1] == "<hr>":
                    body[-1] = '<hr id="cs">'
                else:
                    body.append('<hr id="cs">')
                body.append(f'<h1 lang="cs">{inline(text)}</h1>')
            else:
                body.append(f"<h1>{inline(text)}</h1>")
        elif stripped.startswith("## "):
            flush()
            body.append(f"<h2>{inline(stripped[3:])}</h2>")
        elif stripped.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    rows.append(cells)
                i += 1
            table = ["<table>", "  <tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr>"]
            table += ["  <tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>" for row in rows[1:]]
            body.append("\n".join(table + ["</table>"]))
            continue
        elif stripped.startswith("- "):
            flush()
            items: list[str] = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or (lines[i].startswith("  ") and lines[i].strip())):
                if lines[i].strip().startswith("- "):
                    items.append(lines[i].strip()[2:])
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            body.append("<ul>\n" + "\n".join(f"  <li>{inline(item)}</li>" for item in items) + "\n</ul>")
            continue
        elif stripped.startswith(">"):
            flush()
            quoted = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quoted.append(lines[i].strip()[1:].strip())
                i += 1
            body.append(f"<blockquote><p>{inline(' '.join(quoted))}</p></blockquote>")
            continue
        else:
            paragraph.append(stripped)
        i += 1
    flush()
    while body and body[-1].startswith("<hr"):
        body.pop()
    return title, "\n".join(body)


def page(app: str, markdown: str) -> str:
    title, body = render(markdown)
    czech = '<p class="lang"><a href="#cs">Česky ↓</a></p>\n' if 'id="cs"' in body else ""
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{html.escape(app)} — Privacy Policy</title>\n<style>\n{STYLE}\n</style>\n</head>\n<body>\n\n"
        f"{czech}{body}\n\n</body>\n</html>\n"
    )


def main(argv: list[str]) -> int:
    check = "--check" in argv
    stale = []
    for directory, (app, source) in PAGES.items():
        text = page(app, source.read_text(encoding="utf-8"))
        target = HERE / directory / "index.html"
        if check:
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                stale.append(str(target.relative_to(HERE)))
            continue
        target.parent.mkdir(exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        print(f"{source} -> {target.relative_to(HERE)}")
    if stale:
        print("out of date: " + ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
