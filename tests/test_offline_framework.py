"""Offline release integrity and portable launch behavior; no network or browser."""
from contextlib import redirect_stdout
import hashlib
from html.parser import HTMLParser
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OFFLINE = ROOT / "offline"
WEB = OFFLINE / "gvf"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend((tag, key, value) for key, value in attrs
                         if key in {"href", "src", "poster", "action"} and value)


class OfflineFrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (WEB / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<script id="framework-data" type="application/json">(.*?)</script>', cls.html, re.S)
        cls.data = json.loads(match[1])

    def test_release_manifest_covers_exact_files_and_original_bytes(self):
        manifest = json.loads((OFFLINE / "manifest.json").read_text(encoding="utf-8"))
        actual = {p.relative_to(OFFLINE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in WEB.rglob("*") if p.is_file()}
        self.assertEqual(actual, manifest["files"])
        self.assertEqual(manifest["framework_version"], "0.2.0")
        self.assertEqual(len(actual), 45)
        for filename in ("parameters", "glossary"):
            self.assertEqual((WEB / "data" / (filename + ".json")).read_bytes(),
                             (ROOT / "references" / ("gvf-" + filename + ".json")).read_bytes())

    def test_page_and_embedded_documents_have_no_missing_local_links_or_runtime_cdn(self):
        def check(base, url):
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path:
                return
            path = (base / unquote(parsed.path)).resolve()
            self.assertTrue(path.is_relative_to(WEB), url)
            self.assertTrue(path.is_file(), f"{base}: {url}")

        for path in WEB.rglob("*"):
            if path.suffix not in {".html", ".md", ".svg"}:
                continue
            text = path.read_text(encoding="utf-8-sig")
            if path.suffix == ".md":
                text = re.sub(r"```.*?```", "", text, flags=re.S)
                for url in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                    check(path.parent, url.strip("<>"))
            else:
                parser = Links(); parser.feed(text)
                for tag, key, url in parser.urls:
                    check(path.parent, url)
                    if tag in {"script", "img", "iframe", "link"}:
                        self.assertFalse(urlsplit(url).scheme in {"http", "https"}, url)
        for group in ("docs", "notes", "caseDocs"):
            for doc in self.data[group]:
                parser = Links(); parser.feed(doc["html"])
                for _, _, url in parser.urls:
                    check(WEB, url)
        for profile in self.data["profiles"]:
            check(WEB, profile["_path"])
        for case in self.data["cases"]:
            check(WEB, "cases/observations/" + case["id"] + ".json")
            for image in case["images"]:
                check(WEB, image["local_path"])
        self.assertEqual(len(self.data["cases"]), 4)
        self.assertEqual(sum(len(c["images"]) for c in self.data["cases"]), 12)

    def test_locator_survives_relocation_spaces_and_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "中文 skill with spaces"
            (root / "scripts").mkdir(parents=True)
            (root / "offline/gvf").mkdir(parents=True)
            shutil.copyfile(ROOT / "scripts/open_framework.py", root / "scripts/open_framework.py")
            page = root / "offline/gvf/index.html"
            page.write_text("<!doctype html><title>fixture</title>", encoding="utf-8")
            command = [sys.executable, "-B", str(root / "scripts/open_framework.py"), "--print-path"]
            result = subprocess.run(command, cwd=temp, capture_output=True, encoding="utf-8", check=True)
            value = json.loads(result.stdout)
            self.assertEqual(Path(value["path"]), page)
            self.assertEqual(value["file_url"], page.as_uri())
            self.assertEqual(value["status"], "located")
            page.unlink()
            result = subprocess.run(command, cwd=temp, capture_output=True, encoding="utf-8")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["error"], "missing_offline_page")

    def test_launch_result_distinguishes_request_from_failure_and_locate_does_not_open(self):
        spec = importlib.util.spec_from_file_location("open_framework", ROOT / "scripts/open_framework.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        for args, outcome, code, status in [(["--print-path"], True, 0, "located"),
                                            ([], True, 0, "open_requested"),
                                            ([], False, 1, "error")]:
            with patch.object(module, "open_page", return_value=outcome) as opener, redirect_stdout(io.StringIO()) as output:
                self.assertEqual(module.main(args), code)
                self.assertEqual(json.loads(output.getvalue())["status"], status)
                self.assertEqual(opener.call_count, 0 if args else 1)


if __name__ == "__main__":
    unittest.main()
