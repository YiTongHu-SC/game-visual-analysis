#!/usr/bin/env python3
"""Read the bundled GVF definitions; never inspect or measure user images."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from datetime import date
import hashlib
import json
import re
import stat
from pathlib import Path


REFERENCE_DIR = Path(__file__).absolute().parent.parent / "references"
CATALOGS = {
    "parameters": ("gvf-parameters.json", "parameters", ("id", "zh", "domain")),
    "terms": ("gvf-glossary.json", "terms", ("id", "zh", "en")),
    "evidence": ("gvf-evidence.json", "sources", ("id", "title", "publisher")),
}
SNAPSHOT_FILES = {
    "gvf-parameters.json": ("framework_version", "parameters", "parameters"),
    "gvf-glossary.json": ("version", "terms", "terms"),
    "gvf-evidence.json": ("framework_version", "sources", "sources"),
}
VERSION = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


class SnapshotError(Exception):
    pass


def snapshot_bytes(path: Path) -> bytes:
    # Inspect ancestors before the file so a junction cannot cause even the
    # target's metadata to be read before the linked parent is rejected.
    path = path.absolute()
    try:
        for part in [*reversed(path.parents), path]:
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise SnapshotError("unsafe_path")
            if part != path and not stat.S_ISDIR(info.st_mode):
                raise SnapshotError("unsafe_path")
        if not stat.S_ISREG(info.st_mode):
            raise SnapshotError("not_regular_file")
        return path.read_bytes()
    except FileNotFoundError:
        raise SnapshotError("missing_file") from None
    except OSError:
        raise SnapshotError("read_error") from None


def snapshot_json(raw: bytes) -> object:
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise SnapshotError("duplicate_key")
            result[key] = value
        return result
    def invalid_constant(_value):
        raise SnapshotError("invalid_json")
    try:
        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_keys,
                          parse_constant=invalid_constant)
    except (UnicodeError, ValueError, RecursionError):
        raise SnapshotError("invalid_json") from None


def check_snapshot(reference_dir: Path = REFERENCE_DIR) -> dict:
    result = {"status": "error", "framework_version": None, "checked_files": 0,
              "files": [], "issues": [], "scope": "internal-snapshot-consistency"}
    def row(filename):
        item = {"file": filename, "status": "ok", "issues": []}
        result["files"].append(item)
        result["checked_files"] += 1
        return item
    def issue(item, code, field=None):
        item["status"] = "error"
        item["issues"].append(code)
        detail = {"file": item["file"], "code": code}
        if field is not None:
            detail["field"] = field
        result["issues"].append(detail)
    manifest_row = row("snapshot.json")
    try:
        manifest = snapshot_json(snapshot_bytes(Path(reference_dir) / "snapshot.json"))
    except SnapshotError as error:
        issue(manifest_row, str(error))
        return result
    fields = {"framework_version", "packaged_on", "parameters", "terms", "sources", "files"}
    if not isinstance(manifest, dict) or set(manifest) != fields:
        issue(manifest_row, "invalid_manifest")
        return result
    version = manifest["framework_version"]
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        issue(manifest_row, "invalid_version", "framework_version")
    else:
        result["framework_version"] = version
    try:
        if not isinstance(manifest["packaged_on"], str) or date.fromisoformat(manifest["packaged_on"]).isoformat() != manifest["packaged_on"]:
            raise ValueError()
    except ValueError:
        issue(manifest_row, "invalid_manifest", "packaged_on")
    for key in ("parameters", "terms", "sources"):
        if type(manifest[key]) is not int or manifest[key] < 0:
            issue(manifest_row, "invalid_count", key)
    entries = manifest["files"]
    selected = {}
    if not isinstance(entries, list):
        issue(manifest_row, "invalid_file_set", "files")
    else:
        for index, entry in enumerate(entries):
            prefix = f"files[{index}]"
            if not isinstance(entry, dict) or set(entry) != {"file", "source", "sha256"}:
                issue(manifest_row, "invalid_manifest", prefix)
                continue
            filename = entry["file"]
            if not isinstance(filename, str) or filename not in SNAPSHOT_FILES:
                issue(manifest_row, "invalid_file_set", prefix + ".file")
                continue
            if filename in selected:
                issue(manifest_row, "duplicate_file", prefix + ".file")
            selected[filename] = entry
            if not isinstance(entry["sha256"], str) or not SHA256.fullmatch(entry["sha256"]):
                issue(manifest_row, "invalid_sha256", prefix + ".sha256")
            source = entry["source"]
            if (not isinstance(source, str) or not source.strip() or "\\" in source or ":" in source
                    or any(part in {"", ".", ".."} for part in source.split("/"))
                    or any(ord(char) < 32 for char in source)):
                issue(manifest_row, "invalid_source", prefix + ".source")
        if len(entries) != len(SNAPSHOT_FILES) or set(selected) != set(SNAPSHOT_FILES):
            issue(manifest_row, "invalid_file_set", "files")
    if manifest_row["issues"]:
        return result
    for filename, (version_key, records_key, count_key) in SNAPSHOT_FILES.items():
        item = row(filename)
        try:
            raw = snapshot_bytes(Path(reference_dir) / filename)
        except SnapshotError as error:
            issue(item, str(error))
            continue
        item["sha256"] = hashlib.sha256(raw).hexdigest()
        if item["sha256"] != selected[filename]["sha256"].lower():
            issue(item, "sha256_mismatch")
        try:
            document = snapshot_json(raw)
        except SnapshotError as error:
            issue(item, str(error))
            continue
        if not isinstance(document, dict):
            issue(item, "invalid_document")
            continue
        if document.get(version_key) != version:
            issue(item, "version_mismatch", version_key)
        records = document.get(records_key)
        if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
            issue(item, "invalid_records", records_key)
        else:
            item["count"] = len(records)
            item["expected_count"] = manifest[count_key]
            if len(records) != manifest[count_key]:
                issue(item, "count_mismatch", records_key)
    result["status"] = "error" if result["issues"] else "ok"
    return result


def emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="查询技能内置 GVF 目录；不带筛选时仅输出索引。",
        epilog="--id、--domain、--search 同时使用时取交集；--id 区分大小写。",
    )
    parser.add_argument("--kind", choices=CATALOGS)
    parser.add_argument("--check-snapshot", action="store_true", help="独立核对内置快照的原字节、版本和计数")
    parser.add_argument("--list-domains", action="store_true", help="列出 12 个视觉域")
    parser.add_argument("--domain", help="按视觉域 ID 筛选参数")
    parser.add_argument("--id", help="精确记录 ID；未命中时退出码为 1")
    parser.add_argument("--search", help="在记录全部字段中搜索中文、英文或 ID（不区分大小写）")
    args = parser.parse_args()

    if args.check_snapshot:
        if args.kind is not None or args.list_domains or any(value is not None for value in (args.domain, args.id, args.search)):
            parser.error("--check-snapshot 不能与查询参数组合")
        result = check_snapshot()
        emit(result)
        return 0 if result["status"] == "ok" else 1
    args.kind = args.kind or "parameters"

    if (args.domain or args.list_domains) and args.kind != "parameters":
        parser.error("--domain 和 --list-domains 只适用于 --kind parameters")
    if args.list_domains and any((args.domain, args.id, args.search)):
        parser.error("--list-domains 不能与筛选条件组合")
    if args.search is not None and not args.search.strip():
        parser.error("--search 不能为空白")

    filename, records_key, index_keys = CATALOGS[args.kind]
    try:
        document = json.loads((REFERENCE_DIR / filename).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"无法读取内置目录 {filename}: {exc}\n")

    version = document.get("framework_version", document.get("version"))
    if args.list_domains:
        emit({"framework_version": version, "count": len(document["domains"]),
              "domains": document["domains"]})
        return 0
    if args.domain and args.domain not in {item["id"] for item in document["domains"]}:
        parser.error(f"未知视觉域 {args.domain!r}；用 --list-domains 查看合法 ID")

    records = document[records_key]
    if args.id is not None:
        records = [record for record in records if record["id"] == args.id]
    if args.domain:
        records = [record for record in records if record.get("domain") == args.domain]
    if args.search:
        query = args.search.strip().casefold()
        records = [record for record in records
                   if query in json.dumps(record, ensure_ascii=False).casefold()]

    filtered = any((args.id is not None, args.domain, args.search))
    result = {
        "framework_version": version,
        "kind": args.kind,
        "mode": "records" if filtered else "index",
        "count": len(records),
        "results": records if filtered else [
            {key: record[key] for key in index_keys if key in record} for record in records
        ],
    }
    if not records:
        result["message"] = "没有匹配记录；检查 ID、关键词或交集筛选条件。"
    emit(result)
    return 1 if args.id is not None and not records else 0


if __name__ == "__main__":
    raise SystemExit(main())
