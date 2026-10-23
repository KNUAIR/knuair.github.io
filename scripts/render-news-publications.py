#!/usr/bin/env python3
"""Compatibility entry point: generate Publications and News together."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("render-publications.py")), run_name="__main__")
