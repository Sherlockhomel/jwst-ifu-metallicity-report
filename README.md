# JWST/NIRSpec IFU Metallicity-gradient Report

Advisor-facing GitHub Pages site generated from a repository-local mirror of
the formal Markdown report.

## Update the report mirror

The editable report lives in `../report/`. Regenerate its PDF with the same
Markdown list semantics used by the website:

```bash
pandoc ../report/report_formal.md \
  -o ../report/report_formal.pdf \
  --from markdown+lists_without_preceding_blankline+raw_html \
  --resource-path=../report \
  --pdf-engine=xelatex \
  -H ../report/pdf_table_style.tex \
  -V mainfont='Hiragino Sans GB' \
  -V CJKmainfont='Hiragino Sans GB' \
  -V geometry:margin=0.55in
```

Then sync the Markdown, checked PDF, and figures into this repository:

```bash
python3 sync_report.py --report-dir ../report
```

## Build locally

Install Pandoc and the Python dependency first:

```bash
python3 -m pip install -r requirements.txt
```

Then build and serve the static artifact:

```bash
python3 build_site.py --output _site
python3 -m http.server 8765 --directory _site
```

Then open `http://localhost:8765`.

## Publish

Push the repository to `main`. The GitHub Pages workflow builds `_site/` from
the mirrored sources and publishes it automatically. Set the repository Pages
source to **GitHub Actions**.

The downloadable PDF is synced from the locally checked formal report instead
of being rebuilt on the Linux runner.
