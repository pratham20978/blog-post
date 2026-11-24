"""Export every assets/fig-*.html to .svg and a 2x .png, and render the Mermaid figures (private).
Usage: python assets/_export.py [names...]"""
import pathlib
import re
import shutil
import subprocess
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
FONTS = ("<style>@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:"
         "wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap');</style>")
CHROME = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")


def to_svg(src):
    svg = re.search(r"<svg\b[\s\S]*?</svg>", src.read_text(encoding="utf-8")).group(0)
    if "xmlns=" not in svg.split(">", 1)[0]:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    head, rest = svg.split(">", 1)
    svg = f"{head}><defs>{FONTS}</defs>{rest}"
    out = src.with_suffix(".svg")
    out.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg + "\n", encoding="utf-8")
    return out


def main(names):
    pages = sorted(HERE.glob("fig-*.html"))
    if names:
        pages = [p for p in pages if any(n in p.name for n in names)]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        for src in pages:
            w = float(re.search(r'viewBox="[\d.\s-]+?\s([\d.]+)\s[\d.]+"', src.read_text()).group(1))
            page = browser.new_page(viewport={"width": int(w) + 80, "height": 1000}, device_scale_factor=2)
            page.goto(src.resolve().as_uri())
            page.wait_for_timeout(400)
            page.add_style_tag(content=f"svg{{width:{w}px!important;min-width:0!important}}")
            page.locator("svg").first.screenshot(path=str(src.with_suffix(".png")))
            page.close()
            to_svg(src)
            print("exported", src.stem)
        browser.close()
    mmdc = pathlib.Path.home() / "mmdc" / "node_modules" / ".bin" / "mmdc"
    for mmd in sorted(HERE.glob("fig-*.mmd")):
        if names and not any(n in mmd.name for n in names):
            continue
        base = ["-p", str(pathlib.Path.home() / "mmdc" / "puppeteer.json"), "-c", str(HERE / "mermaid-config.json"),
                "-C", str(HERE / "mermaid.css"), "-b", "#f5f5f5", "-i", str(mmd)]
        subprocess.run([str(mmdc), *base, "-o", str(mmd.with_suffix(".svg"))], check=True, capture_output=True)
        subprocess.run([str(mmdc), *base, "-s", "2", "-o", str(mmd.with_suffix(".png"))], check=True, capture_output=True)
        print("rendered", mmd.stem)


if __name__ == "__main__":
    main(sys.argv[1:])
