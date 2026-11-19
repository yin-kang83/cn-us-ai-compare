"""把文献检索结果（OpenAlex/Crossref/arXiv）写入证据账本（元数据层，L3）。

原则：
- 只入**元数据**，不入全文、不下载 PDF；OA 链接仅作线索；
- 入账即标注 `evidence_level = L3_METADATA`，**不得直接当作事实结论**；
- 去重：优先 DOI，其次 landing_page/id，最后标题+年份；
- 追加写 JSONL，不覆盖已有记录；`--dry-run` 只预览。

用法：
    python scripts/ingest_literature.py \
        --input openalex.json --input arxiv.json --verify verify.json \
        --ledger data/literature_ledger.jsonl
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

VALID_VERIFICATION = {"match", "partial", "mismatch", "not_found", "unverified"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        results = data.get("results")
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]
        if "doi" in data:  # verify_metadata 单条输出
            return [data]
    raise ValueError(f"无法识别的 JSON 结构：{type(data).__name__}")


def _normalize_doi(doi: Any) -> str:
    value = str(doi or "").strip().lower()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value)
    return value


def _dedupe_key(record: dict[str, Any]) -> str:
    doi = _normalize_doi(record.get("doi"))
    if doi:
        return "doi:" + doi
    for key in ("landing_page",):
        value = str(record.get(key) or "").strip()
        if value:
            return "url:" + value.lower()
    title = " ".join(str(record.get("title") or "").lower().split())
    year = str(record.get("year") or "")
    return "title:" + title + "|" + year


def _normalize_record(record: dict[str, Any], *, query: str | None,
                      retrieved_at: str | None, verification: str) -> dict[str, Any] | None:
    title = " ".join(str(record.get("title") or "").split())
    if not title:
        return None
    source_db = str(record.get("source") or "unknown")
    return {
        "source_db": source_db,
        "title": title,
        "authors": [str(author) for author in (record.get("authors") or []) if str(author).strip()],
        "year": record.get("year"),
        "doi": str(record.get("doi") or ""),
        "venue": str(record.get("venue") or ""),
        "type": str(record.get("type") or ""),
        "cited_by_count": record.get("cited_by_count"),
        "oa_url": str(record.get("oa_url") or ""),
        "pdf_url": str(record.get("pdf_url") or ""),
        "landing_page": str(record.get("landing_page") or ""),
        "query": query or "",
        "retrieved_at": retrieved_at or "",
        "verification": verification if verification in VALID_VERIFICATION else "unverified",
        "evidence_level": "L3_METADATA",
        "note": "文献元数据（未读原文），只能作为线索；不得直接作为事实结论。",
    }


def _existing_keys(path: Path) -> tuple[set[str], int]:
    keys: set[str] = set()
    next_id = 1
    if not path.exists():
        return keys, next_id
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        keys.add(_dedupe_key(record))
        match = re.match(r"LIT-(\d+)$", str(record.get("id") or ""))
        if match:
            next_id = max(next_id, int(match.group(1)) + 1)
    return keys, next_id


def ingest(input_paths: Iterable[Path], verify_paths: Iterable[Path], *,
           ledger: Path, dry_run: bool = False) -> dict[str, Any]:
    verification: dict[str, str] = {}
    for path in verify_paths:
        for item in _records(_load_json(path)):
            doi = _normalize_doi(item.get("doi"))
            status = str(item.get("status") or "unverified")
            if doi:
                verification[doi] = status if status in VALID_VERIFICATION else "unverified"

    existing_keys, next_id = _existing_keys(ledger)
    to_append: list[dict[str, Any]] = []
    duplicates = 0
    skipped = 0
    by_source: dict[str, int] = {}
    by_verification: dict[str, int] = {}
    for path in input_paths:
        data = _load_json(path)
        query = str(data.get("query") or "") if isinstance(data, dict) else ""
        retrieved_at = str(data.get("retrieved_at") or "") if isinstance(data, dict) else ""
        for raw in _records(data):
            doi_key = _normalize_doi(raw.get("doi"))
            status = verification.get(doi_key, "unverified")
            normalized = _normalize_record(raw, query=query, retrieved_at=retrieved_at,
                                           verification=status)
            if normalized is None:
                skipped += 1
                continue
            key = _dedupe_key(normalized)
            if key in existing_keys:
                duplicates += 1
                continue
            existing_keys.add(key)
            normalized["id"] = f"LIT-{next_id:04d}"
            normalized["ingested_at"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
            to_append.append(normalized)
            next_id += 1
            by_source[normalized["source_db"]] = by_source.get(normalized["source_db"], 0) + 1
            by_verification[normalized["verification"]] = by_verification.get(normalized["verification"], 0) + 1

    if not dry_run and to_append:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8", newline="\n") as handle:
            for record in to_append:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return {"ledger": str(ledger), "appended": len(to_append), "duplicates": duplicates,
            "skipped": skipped, "by_source": by_source, "by_verification": by_verification,
            "dry_run": dry_run}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="文献元数据 → 证据账本（L3，只入元数据）")
    parser.add_argument("--input", action="append", required=True, help="检索结果 JSON，可多次传入")
    parser.add_argument("--verify", action="append", default=[], help="verify_metadata.py 输出，可多次传入")
    parser.add_argument("--ledger", default="data/literature_ledger.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = ingest([Path(item) for item in args.input],
                        [Path(item) for item in args.verify],
                        ledger=Path(args.ledger), dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001
        print(f"入库失败：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
