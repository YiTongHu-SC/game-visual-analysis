"""Offline contracts for the bundled GVF snapshot and existing catalogue queries."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "query_catalog.py"
CATALOGS = {
    "gvf-parameters.json": "parameters",
    "gvf-glossary.json": "terms",
    "gvf-evidence.json": "sources",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree(root):
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            path = Path(directory) / name
            result[path.relative_to(root).as_posix()] = "directory"
        for name in files:
            path = Path(directory) / name
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="gvf-snapshot-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.skill = self.root / "skill"
        self.references = self.skill / "references"
        self.references.mkdir(parents=True)
        self.script = self.skill / "scripts" / "query_catalog.py"
        self.script.parent.mkdir()
        shutil.copyfile(SCRIPT, self.script)
        self.cwd = self.root / "unrelated-project"
        self.cwd.mkdir()
        self.documents = {
            "gvf-parameters.json": {
                "framework_version": "0.2.0", "catalog_version": "0.2.0",
                "domains": [{"id": "shape", "zh": "形态"}, {"id": "color", "zh": "色彩"}],
                "parameters": [{"id": "shape.silhouette", "zh": "轮廓", "domain": "shape", "note": "Visual silhouette"},
                               {"id": "color.value", "zh": "明度", "domain": "color", "note": "Visual value"}],
            },
            "gvf-glossary.json": {"version": "0.2.0", "terms": [{"id": "value", "zh": "明度", "en": "Value"}]},
            "gvf-evidence.json": {"framework_version": "0.2.0", "sources": [{"id": "sample", "title": "Synthetic local source", "publisher": "Fixture"}]},
        }
        for filename, data in self.documents.items():
            self.write_json(filename, data)
        self.manifest = {
            "framework_version": "0.2.0", "packaged_on": "2000-01-01",
            "parameters": 2, "terms": 1, "sources": 1,
            "files": [{"file": filename, "source": "synthetic/" + filename,
                       "sha256": digest(self.references / filename)} for filename in CATALOGS],
        }
        self.save_manifest()

    def write_json(self, filename, data):
        (self.references / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def save_manifest(self):
        self.write_json("snapshot.json", self.manifest)

    def update_document_hash(self, filename):
        for entry in self.manifest["files"]:
            if entry["file"] == filename:
                entry["sha256"] = digest(self.references / filename)
        self.save_manifest()

    def run_cli(self, arguments, *, real_package=False):
        script = SCRIPT if real_package else self.script
        package = SKILL if real_package else self.skill
        before_package, before_temp = tree(package), tree(self.root)
        environment = {key: value for key, value in os.environ.items()
                       if not any(part in key.upper() for part in ("TOKEN", "API_KEY", "ELEVEN"))
                       and key.upper() not in ("PYTHONPATH", "PYTHONSTARTUP", "PYTHONINSPECT")}
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONUTF8"] = "1"
        for key in ("HOME", "USERPROFILE", "LOCALAPPDATA"):
            environment[key] = str(self.root / "unused-user-root")
        process = subprocess.run([sys.executable, "-B", str(script), *arguments], cwd=self.cwd,
                                 env=environment, capture_output=True, encoding="utf-8", timeout=15)
        self.assertNotIn("Traceback", process.stderr)
        self.assertEqual(tree(package), before_package, "Query changed its skill package")
        self.assertEqual(tree(self.root), before_temp, "Query wrote files or bytecode")
        return process

    def check_result(self, *, expected=0, code=None):
        process = self.run_cli(["--check-snapshot"])
        self.assertEqual(process.returncode, expected, process.stdout + process.stderr)
        self.assertEqual(process.stderr, "")
        result = json.loads(process.stdout)
        self.assertEqual(result["status"], "ok" if expected == 0 else "error")
        self.assertEqual(result["scope"], "internal-snapshot-consistency")
        self.assertIsInstance(result["checked_files"], int)
        self.assertIsInstance(result["files"], list)
        self.assertIsInstance(result["issues"], list)
        if expected:
            self.assertTrue(result["issues"])
            for issue in result["issues"]:
                self.assertIsInstance(issue["code"], str)
                self.assertTrue(issue["code"])
                self.assertIn(issue["file"], {"snapshot.json", *CATALOGS})
        else:
            self.assertEqual(result["issues"], [])
            self.assertEqual(result["checked_files"], 4)
            self.assertEqual(result["framework_version"], "0.2.0")
        if code:
            self.assertIn(code, {issue["code"] for issue in result["issues"]})
        return result

    def load_checker(self):
        namespace = {"__name__": "gvf_fixture", "__file__": str(self.script)}
        exec(compile(self.script.read_text(encoding="utf-8"), str(self.script), "exec"), namespace)
        return namespace["check_snapshot"]

    def test_real_bundled_snapshot_passes_from_unrelated_cwd_without_writes(self):
        process = self.run_cli(["--check-snapshot"], real_package=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["framework_version"], read_json(SKILL / "references/snapshot.json")["framework_version"])
        self.assertEqual(result["checked_files"], 4)
        self.assertEqual(result["issues"], [])

    def test_small_self_contained_snapshot_passes_without_source_repository(self):
        result = self.check_result()
        self.assertEqual({item["file"] for item in result["files"]}, {"snapshot.json", *CATALOGS})
        self.assertTrue(all(item["status"] == "ok" for item in result["files"]))

    def test_changed_file_bytes_fail_even_when_json_meaning_is_unchanged(self):
        path = self.references / "gvf-parameters.json"
        path.write_bytes(path.read_bytes() + b" \n")
        self.check_result(expected=1, code="sha256_mismatch")

    def test_each_missing_catalog_is_reported_without_traceback(self):
        for filename in CATALOGS:
            with self.subTest(filename=filename):
                path = self.references / filename
                original = path.read_bytes()
                path.unlink()
                self.check_result(expected=1, code="missing_file")
                path.write_bytes(original)

    def test_catalog_bad_json_and_non_object_shape_fail_even_with_matching_hash(self):
        for payload in (b"{broken", b"[]", b"null", b"\xff\xfe"):
            with self.subTest(payload=payload):
                (self.references / "gvf-evidence.json").write_bytes(payload)
                self.update_document_hash("gvf-evidence.json")
                self.check_result(expected=1, code="invalid_document" if payload in (b"[]", b"null") else "invalid_json")

    def test_matching_hash_does_not_hide_framework_or_glossary_version_drift(self):
        for filename, field in (("gvf-parameters.json", "framework_version"),
                                ("gvf-glossary.json", "version"),
                                ("gvf-evidence.json", "framework_version")):
            with self.subTest(filename=filename):
                changed = dict(self.documents[filename])
                changed[field] = "999.0.0"
                self.write_json(filename, changed)
                self.update_document_hash(filename)
                self.check_result(expected=1, code="version_mismatch")
                self.write_json(filename, self.documents[filename])
                self.update_document_hash(filename)

    def test_count_mismatch_in_each_collection_is_rejected(self):
        for key in ("parameters", "terms", "sources"):
            with self.subTest(key=key):
                previous = self.manifest[key]
                self.manifest[key] = previous + 1
                self.save_manifest()
                self.check_result(expected=1, code="count_mismatch")
                self.manifest[key] = previous
                self.save_manifest()

    def test_boolean_count_cannot_masquerade_as_integer_one(self):
        for key in ("parameters", "terms", "sources"):
            with self.subTest(key=key):
                previous = self.manifest[key]
                self.manifest[key] = True
                self.save_manifest()
                self.check_result(expected=1, code="invalid_count")
                self.manifest[key] = previous
                self.save_manifest()

    def test_duplicate_manifest_entry_is_rejected(self):
        self.manifest["files"].append(dict(self.manifest["files"][0]))
        self.save_manifest()
        self.check_result(expected=1, code="duplicate_file")

    def test_missing_manifest_entry_is_rejected(self):
        self.manifest["files"].pop()
        self.save_manifest()
        self.check_result(expected=1, code="invalid_file_set")

    def test_manifest_paths_cannot_escape_or_expand_the_fixed_read_set(self):
        for unsafe in ("../outside.json", "sub/../../outside.json", "/absolute.json",
                       r"C:\outside.json", r"\\server\share\outside.json", "extra.json"):
            with self.subTest(unsafe=unsafe):
                self.manifest["files"][0]["file"] = unsafe
                self.save_manifest()
                result = self.check_result(expected=1, code="invalid_file_set")
                rendered = json.dumps(result)
                self.assertNotIn(unsafe, rendered)
                self.assertLessEqual(result["checked_files"], 4)

    def test_invalid_sha256_is_rejected_before_file_hash_can_be_trusted(self):
        for value in ("", "a" * 63, "g" * 64, True, None, 123):
            with self.subTest(value=value):
                self.manifest["files"][0]["sha256"] = value
                self.save_manifest()
                self.check_result(expected=1, code="invalid_sha256")

    def test_missing_manifest_is_structured_error_with_exit_one(self):
        (self.references / "snapshot.json").unlink()
        result = self.check_result(expected=1, code="missing_file")
        self.assertEqual(result["checked_files"], 1)

    def test_empty_invalid_and_non_object_manifests_fail_without_traceback(self):
        for payload in (b"", b"{broken", b"[]", b"null", b"\xff\xfe", b"{}"):
            with self.subTest(payload=payload):
                (self.references / "snapshot.json").write_bytes(payload)
                self.check_result(expected=1)

    def test_invalid_manifest_file_list_and_entry_shapes_fail_without_traceback(self):
        for value in (None, {}, [], [None], ["gvf-parameters.json"], [{}]):
            with self.subTest(value=value):
                self.manifest["files"] = value
                self.save_manifest()
                self.check_result(expected=1)

    def test_catalog_and_ancestor_reparse_points_are_rejected_before_read(self):
        checker = self.load_checker()
        for target in (self.references / "gvf-parameters.json", self.references, self.skill):
            with self.subTest(target=target):
                original_lstat, original_read = Path.lstat, Path.read_bytes
                reads = []
                def lstat(path, *args, **kwargs):
                    actual = original_lstat(path, *args, **kwargs)
                    if path == target:
                        return SimpleNamespace(st_mode=actual.st_mode, st_file_attributes=0x400)
                    return actual
                def guarded_read(path, *args, **kwargs):
                    reads.append(path)
                    if path == target or target in path.parents:
                        raise AssertionError("Checker read through an injected reparse point")
                    return original_read(path, *args, **kwargs)
                before = tree(self.skill)
                with patch.object(Path, "lstat", lstat), patch.object(Path, "read_bytes", guarded_read):
                    result = checker(self.references)
                self.assertEqual(result["status"], "error")
                self.assertTrue(result["issues"])
                self.assertIn("unsafe_path", {issue["code"] for issue in result["issues"]})
                self.assertEqual(tree(self.skill), before)

    def test_malicious_manifest_never_reads_an_existing_outside_file(self):
        outside = self.root / "outside.json"
        outside.write_text('{"do_not_read":"synthetic sentinel"}', encoding="utf-8")
        self.manifest["files"][0]["file"] = str(outside)
        self.save_manifest()
        checker, reads, original = self.load_checker(), [], Path.read_bytes
        def observed_read(path, *args, **kwargs):
            reads.append(path)
            if path == outside:
                raise AssertionError("Manifest expanded the fixed file read set")
            return original(path, *args, **kwargs)
        with patch.object(Path, "read_bytes", observed_read):
            result = checker(self.references)
        self.assertEqual(result["status"], "error")
        self.assertEqual(reads, [self.references / "snapshot.json"])

    def test_duplicate_json_keys_and_invalid_record_shapes_are_structured_failures(self):
        path = self.references / "gvf-glossary.json"
        path.write_text('{"version":"0.2.0","version":"0.2.0","terms":[]}', encoding="utf-8")
        self.update_document_hash(path.name)
        self.check_result(expected=1, code="duplicate_key")
        for records in ({}, [None], ["not-an-object"]):
            with self.subTest(records=records):
                self.write_json(path.name, {"version": "0.2.0", "terms": records})
                self.update_document_hash(path.name)
                self.check_result(expected=1, code="invalid_records")

    def test_snapshot_mode_rejects_every_query_option_even_explicit_default_kind(self):
        for arguments in (("--kind", "parameters"), ("--kind", "terms"), ("--id", "shape.silhouette"),
                          ("--search", "Visual"), ("--domain", "shape"), ("--list-domains",)):
            with self.subTest(arguments=arguments):
                result = self.run_cli(["--check-snapshot", *arguments])
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("--check-snapshot", result.stderr)

    def test_existing_index_id_search_domain_and_terms_queries_are_unchanged(self):
        cases = [
            ([], 0, "parameters", "index", 2),
            (["--id", "shape.silhouette"], 0, "parameters", "records", 1),
            (["--search", "VISUAL"], 0, "parameters", "records", 2),
            (["--search", "no-such-synthetic-term"], 0, "parameters", "records", 0),
            (["--domain", "color"], 0, "parameters", "records", 1),
            (["--id", "shape.silhouette", "--domain", "color"], 1, "parameters", "records", 0),
            (["--kind", "terms", "--id", "value"], 0, "terms", "records", 1),
            (["--kind", "evidence", "--search", "synthetic"], 0, "evidence", "records", 1),
        ]
        for arguments, exit_code, kind, mode, count in cases:
            with self.subTest(arguments=arguments):
                process = self.run_cli(arguments)
                self.assertEqual(process.returncode, exit_code, process.stderr)
                data = json.loads(process.stdout)
                self.assertEqual((data["kind"], data["mode"], data["count"]), (kind, mode, count))
                self.assertEqual(data["framework_version"], "0.2.0")
                if arguments == ["--id", "shape.silhouette"]:
                    self.assertEqual(data["results"], [self.documents["gvf-parameters.json"]["parameters"][0]])
        process = self.run_cli(["--list-domains"])
        self.assertEqual(process.returncode, 0, process.stderr)
        data = json.loads(process.stdout)
        self.assertEqual(data["domains"], self.documents["gvf-parameters.json"]["domains"])
        self.assertEqual(data["count"], 2)


if __name__ == "__main__":
    unittest.main()
