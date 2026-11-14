#!/usr/bin/env python3
"""Locate the bundled offline GVF page and optionally request a browser open."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import webbrowser


def framework_path() -> Path:
    return Path(__file__).resolve().parents[1] / "offline" / "gvf" / "index.html"


def open_page(path: Path) -> bool:
    if sys.platform == "win32":
        os.startfile(str(path))
        return True
    return webbrowser.open(path.as_uri(), new=2)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="打开技能内置的 GVF 离线网页；不联网、不启动服务。")
    parser.add_argument("--print-path", action="store_true", help="只输出绝对路径与 file_url，供宿主浏览器打开")
    args = parser.parse_args(argv)
    path = framework_path()
    result = {"path": str(path), "file_url": path.as_uri(), "status": "located"}
    code = 0
    if not path.is_file():
        result.update(status="error", error="missing_offline_page")
        code = 1
    elif not args.print_path:
        try:
            if open_page(path):
                result["status"] = "open_requested"
            else:
                result.update(status="error", error="browser_open_failed")
                code = 1
        except (OSError, webbrowser.Error) as exc:
            result.update(status="error", error="browser_open_failed", reason=type(exc).__name__)
            code = 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
