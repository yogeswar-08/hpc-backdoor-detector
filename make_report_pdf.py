#!/usr/bin/env python3
"""Create report.pdf from report.md using Chromium's print-to-PDF support.

This helper intentionally has no Python package dependencies. Chromium is
available in the Replit environment and can also be replaced by any browser
that supports headless PDF printing.
"""

from pathlib import Path
import html
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "report.md"
OUTPUT = ROOT / "report.pdf"


def markdown_to_html(markdown: str) -> str:
    """Convert the small, fixed report vocabulary to readable HTML."""
    blocks: list[str] = []
    paragraph: list[str] = []
    in_code = False
    code_lines: list[str] = []
    in_list = False

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(paragraph)
            text = html.escape(text)
            text = text.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
            text = text.replace("`", "<code>", 1).replace("`", "</code>", 1)
            blocks.append(f"<p>{text}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            blocks.append("</ol>")
            in_list = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line == "```":
            flush_paragraph()
            close_list()
            if in_code:
                blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line:
            flush_paragraph()
            close_list()
            continue
        if line.startswith("# "):
            flush_paragraph()
            close_list()
            blocks.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            flush_paragraph()
            close_list()
            blocks.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. ") or line.startswith("4. ") or line.startswith("5. "):
            flush_paragraph()
            if not in_list:
                blocks.append("<ol>")
                in_list = True
            item = line[3:]
            item = html.escape(item).replace("`", "<code>", 1).replace("`", "</code>", 1)
            blocks.append(f"<li>{item}</li>")
        elif line.startswith("- "):
            flush_paragraph()
            if not in_list:
                blocks.append("<ol>")
                in_list = True
            item = html.escape(line[2:]).replace("`", "<code>", 1).replace("`", "</code>", 1)
            blocks.append(f"<li>{item}</li>")
        else:
            paragraph.append(line)

    flush_paragraph()
    close_list()
    return "\n".join(blocks)


def main() -> None:
    chromium = shutil.which("chromium") or shutil.which("chromium-browser")
    if not chromium:
        raise SystemExit("Chromium is required to regenerate report.pdf.")

    body = markdown_to_html(SOURCE.read_text(encoding="utf-8"))
    document = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
@page {{ size: Letter; margin: 0.65in 0.72in; }}
* {{ box-sizing: border-box; }}
body {{ font-family: Arial, sans-serif; color: #17202a; font-size: 10.5pt;
        line-height: 1.38; }}
h1 {{ color: #123b5d; font-size: 22pt; margin: 0 0 7pt; }}
h2 {{ color: #146c94; font-size: 14pt; border-bottom: 1px solid #b8d5e3;
      padding-bottom: 2pt; margin: 13pt 0 5pt; }}
p {{ margin: 0 0 7pt; }}
ol {{ margin: 3pt 0 8pt 21pt; padding: 0; }}
li {{ margin: 0 0 3pt; }}
code {{ font-family: "Courier New", monospace; font-size: 9pt;
        background: #edf4f7; padding: 1px 3px; }}
pre {{ background: #f1f5f7; border-left: 3px solid #2b8aaf; padding: 7pt;
       font-size: 8.5pt; white-space: pre-wrap; }}
strong {{ color: #0c526e; }}
</style></head><body>{body}</body></html>"""

    with tempfile.TemporaryDirectory() as directory:
        html_path = Path(directory) / "report.html"
        html_path.write_text(document, encoding="utf-8")
        subprocess.run(
            [
                chromium,
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={OUTPUT}",
                html_path.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()