"""文献元数据 → 证据账本 测试（离线，不访问网络）。"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ingest_literature.py"
spec = importlib.util.spec_from_file_location("ingest_literature", SCRIPT)
ingest_literature = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(ingest_literature)


def _write(path: Path, data) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_ingest_and_dedupe(tmp_path):
    openalex = _write(tmp_path / "openalex.json", {
        "source": "openalex", "query": "LLM compliance", "retrieved_at": "2026-11-20T01:00:00+08:00",
        "results": [
            {"source": "openalex", "title": "A Survey of LLM Compliance", "authors": ["Alice Chen"],
             "year": 2024, "doi": "https://doi.org/10.1000/x1", "venue": "JAI", "cited_by_count": 10,
             "oa_url": "https://example.org/x1", "landing_page": "https://doi.org/10.1000/x1"},
            {"source": "openalex", "title": "", "year": 2024},
        ],
    })
    arxiv = _write(tmp_path / "arxiv.json", {
        "source": "arxiv", "query": "LLM compliance", "retrieved_at": "2026-11-20T01:01:00+08:00",
        "results": [
            {"source": "arxiv", "title": "Auditable LLM Systems", "authors": ["Bob Li"],
             "year": 2024, "doi": "", "venue": "arXiv", "pdf_url": "https://arxiv.org/pdf/1",
             "landing_page": "http://arxiv.org/abs/1"},
        ],
    })
    verify = _write(tmp_path / "verify.json", {"doi": "https://doi.org/10.1000/x1",
                                               "status": "match", "checked_at": "2026-11-20"})
    ledger = tmp_path / "data" / "literature_ledger.jsonl"
    result = ingest_literature.ingest([openalex, arxiv], [verify], ledger=ledger)
    assert result["appended"] == 2 and result["duplicates"] == 0 and result["skipped"] == 1
    assert result["by_source"] == {"openalex": 1, "arxiv": 1}
    assert result["by_verification"] == {"match": 1, "unverified": 1}
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
    assert [row["id"] for row in rows] == ["LIT-0001", "LIT-0002"]
    assert rows[0]["evidence_level"] == "L3_METADATA"
    assert rows[0]["verification"] == "match"
    assert rows[1]["source_db"] == "arxiv"

    # 再跑一次：全部重复
    rerun = ingest_literature.ingest([openalex, arxiv], [verify], ledger=ledger)
    assert rerun["appended"] == 0 and rerun["duplicates"] == 2


def test_dry_run_does_not_write(tmp_path):
    source = _write(tmp_path / "openalex.json", {
        "source": "openalex", "query": "q", "results": [
            {"source": "openalex", "title": "Paper", "doi": "10.1/abc", "year": 2024},
        ],
    })
    ledger = tmp_path / "ledger.jsonl"
    result = ingest_literature.ingest([source], [], ledger=ledger, dry_run=True)
    assert result["appended"] == 1 and result["dry_run"] is True
    assert not ledger.exists()


def test_invalid_input(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"foo": 1}', encoding="utf-8")
    with pytest.raises(ValueError):
        ingest_literature.ingest([bad], [], ledger=tmp_path / "ledger.jsonl")
