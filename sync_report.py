#!/usr/bin/env python3
"""Sync the advisor report into the self-contained GitHub Pages repository."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", type=Path, default=ROOT.parent / "report")
    return parser.parse_args()


def main() -> None:
    report_dir = parse_args().report_dir.resolve()
    source = ROOT / "source"
    static = ROOT / "static"
    source.mkdir(exist_ok=True)
    static.mkdir(exist_ok=True)

    shutil.copy2(report_dir / "report_formal.md", source / "report_formal.md")
    shutil.copy2(report_dir / "report_formal.pdf", static / "report_formal.pdf")
    shutil.copytree(report_dir / "figures", source / "figures", dirs_exist_ok=True)
    print(f"Synced report from: {report_dir}")


if __name__ == "__main__":
    main()
