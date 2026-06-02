#!/usr/bin/env python3
"""Build the GitHub Pages artifact for the JWST/NIRSpec IFU report."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "report_formal.md"
SOURCE_FIGURES = ROOT / "source" / "figures"
STATIC_PDF = ROOT / "static" / "report_formal.pdf"
PDF_HEADER = ROOT / "pdf_table_style.tex"


def html_markdown(source: str) -> str:
    """Prepare Markdown for HTML without changing the downloadable source."""

    pattern = re.compile(r"\[([^\n]+?)\]\(<\/Users\/[^>]+>\)")
    cleaned = pattern.sub(
        lambda match: (
            f'<span class="paper-unavailable">{html.escape(match.group(1))}'
            ' <span class="availability-note">local PDF unavailable online</span></span>'
        ),
        source,
    )
    return cleaned.replace("](figures/", "](assets/figures/")


def sync_public_assets(output: Path) -> None:
    """Copy repository sources into the publish artifact."""

    assets = output / "assets"
    figures = assets / "figures"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, assets / "report_formal.md")
    shutil.copy2(STATIC_PDF, assets / "report_formal.pdf")
    shutil.copytree(SOURCE_FIGURES, figures, dirs_exist_ok=True)
    shutil.copy2(ROOT / "styles.css", output / "styles.css")
    shutil.copy2(ROOT / "script.js", output / "script.js")
    (output / ".nojekyll").touch()


def build_chart(chart: Path) -> None:
    gratings = [
        ("PRISM/CLEAR", 0.60, 5.30, "#2f6b7c"),
        ("G140/F100LP", 0.97, 1.89, "#c26b47"),
        ("G235/F170LP", 1.66, 3.17, "#789447"),
        ("G395/F290LP", 2.87, 5.27, "#885f8d"),
    ]
    lines = [
        ("[OII] 3727", 0.3727),
        ("[NeIII] 3869", 0.3869),
        ("[OIII] 4363", 0.4363),
        ("Hbeta", 0.4861),
        ("[OIII] 5007", 0.5007),
        ("Halpha", 0.6563),
        ("[NII] 6584", 0.6584),
        ("[SII] 6720", 0.6720),
    ]
    line_colors = {
        "[OII] 3727": "#226f74",
        "[NeIII] 3869": "#bd7b2f",
        "[OIII] 4363": "#6f4d90",
        "Hbeta": "#2f7d4b",
        "[OIII] 5007": "#6f4d90",
        "Halpha": "#b45144",
        "[NII] 6584": "#9b5c25",
        "[SII] 6720": "#7b715d",
    }

    fig, (ax_top, ax_bottom) = plt.subplots(
        2, 1, figsize=(12.5, 7.2), gridspec_kw={"height_ratios": [1, 1.65]}
    )
    fig.patch.set_facecolor("#fbfbf8")
    for ax in (ax_top, ax_bottom):
        ax.set_facecolor("#fbfbf8")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="x", color="#d7dad6", linewidth=0.7, alpha=0.8)

    for row, (label, start, end, color) in enumerate(gratings[::-1]):
        ax_top.add_patch(Rectangle((start, row - 0.3), end - start, 0.6, color=color, alpha=0.9))
        ax_top.text(
            start + 0.04,
            row,
            f"{label}  {start:.2f}-{end:.2f} um",
            va="center",
            ha="left",
            fontsize=10,
            color="white",
            weight="bold",
        )
    ax_top.set_xlim(0.45, 5.45)
    ax_top.set_ylim(-0.7, 3.7)
    ax_top.set_yticks([])
    ax_top.set_xlabel("Observed wavelength (micron)")
    ax_top.set_title("NIRSpec IFU grating/filter wavelength coverage", loc="left", weight="bold")

    redshifts = [2, 3, 4, 5, 6, 7, 8]
    for label, rest in lines:
        observed = [rest * (1 + z) for z in redshifts]
        ax_bottom.plot(
            redshifts,
            observed,
            marker="o",
            markersize=4,
            linewidth=1.9,
            label=label,
            color=line_colors[label],
        )
    for label, start, end, color in gratings[1:]:
        ax_bottom.axhspan(start, end, color=color, alpha=0.055)
        ax_bottom.text(8.12, (start + end) / 2, label.split("/")[0], color=color, va="center", fontsize=8)
    ax_bottom.set_xlim(1.9, 8.55)
    ax_bottom.set_ylim(0.85, 5.5)
    ax_bottom.set_xlabel("Redshift")
    ax_bottom.set_ylabel("Observed wavelength (micron)")
    ax_bottom.set_title("Rest-optical diagnostic lines across redshift", loc="left", weight="bold")
    ax_bottom.legend(ncol=4, frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(pad=2.0)
    fig.savefig(chart, dpi=170, bbox_inches="tight")
    plt.close(fig)


def pandoc_fragment(markdown: str) -> str:
    cmd = [
        "pandoc",
        "--from",
        "markdown+lists_without_preceding_blankline+raw_html",
        "--to",
        "html5",
        "--mathjax",
        "--section-divs",
    ]
    return subprocess.run(cmd, input=markdown, check=True, capture_output=True, text=True).stdout


def site_shell(article: str) -> str:
    chart_figure = """
<figure class="coverage-figure">
  <img src="assets/nirspec-ifu-coverage.png" alt="NIRSpec IFU wavelength coverage and diagnostic line visibility across redshift">
  <figcaption>NIRSpec IFU wavelength coverage and the observed wavelengths of key rest-optical diagnostic lines.</figcaption>
</figure>
"""
    marker = '<section id="single-line-redshift-coverage"'
    if marker in article:
        article = article.replace(marker, chart_figure + "\n" + marker, 1)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="JWST/NIRSpec IFU metallicity-gradient candidate program report">
  <title>JWST/NIRSpec IFU 金属梯度候选项目</title>
  <link rel="stylesheet" href="styles.css">
  <script>
    window.MathJax = {{
      tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] }},
      svg: {{ fontCache: 'global' }}
    }};
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
  <script defer src="script.js"></script>
</head>
<body>
  <header class="site-header">
    <div>
      <p class="eyebrow">JWST / NIRSpec IFU</p>
      <h1>金属梯度候选项目正式汇总</h1>
      <p class="subtitle">Resolved metallicity indicators, wavelength coverage, published results, and candidate programs.</p>
    </div>
    <div class="header-actions">
      <a class="download-button" href="assets/report_formal.pdf" download>Download PDF</a>
      <a class="download-button secondary" href="assets/report_formal.md" download>Download Markdown</a>
    </div>
  </header>
  <div class="page-shell">
    <aside class="sidebar">
      <label class="search-label" for="site-search">Search report</label>
      <input id="site-search" type="search" placeholder="Program ID, target, paper title">
      <p id="search-status" class="search-status" aria-live="polite">33 programs</p>
      <nav id="table-of-contents" aria-label="Report sections"></nav>
    </aside>
    <main id="report-content" class="report-content">
      {article}
    </main>
  </div>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    sync_public_assets(output)
    build_chart(output / "assets" / "nirspec-ifu-coverage.png")
    fragment = pandoc_fragment(html_markdown(SOURCE.read_text(encoding="utf-8")))
    (output / "index.html").write_text(site_shell(fragment), encoding="utf-8")
    print(f"Built static site: {output}")


if __name__ == "__main__":
    main()
