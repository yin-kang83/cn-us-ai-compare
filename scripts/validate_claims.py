# -*- coding: utf-8 -*-
"""校验 key_claims / falsification_ledger JSONL 的必需字段。

用法: python validate_claims.py data/key_claims.jsonl --schema key_claims
"""
import argparse, json, sys

SCHEMAS = {
    "key_claims": ["id", "claim", "value", "unit", "source_type", "source", "locator", "retrieved_at", "confidence", "口径"],
    "ledger": ["id", "evidence"],
}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--schema", choices=list(SCHEMAS), required=True)
    args = ap.parse_args()
    need = SCHEMAS[args.schema]
    bad = 0
    rows = 0
    with open(args.path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rows += 1
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"line {i}: JSON error: {e}")
                bad += 1
                continue
            missing = [k for k in need if k not in obj]
            if missing:
                print(f"line {i}: missing {missing}")
                bad += 1
    print(f"rows={rows} bad={bad} -> {'PASS' if bad == 0 else 'FAIL'}")
    return 0 if bad == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
