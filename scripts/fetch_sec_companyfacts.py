# -*- coding: utf-8 -*-
"""下载 SEC companyfacts 并可选提取单季 capex。

用法: python fetch_sec_companyfacts.py --cik 0000789019 --out data/sec/MSFT.json
"""
import argparse, gzip, json, sys, urllib.request

UA = {"User-Agent": "cn-us-ai-compare research (contact via Gitee issues)", "Accept-Encoding": "gzip, deflate"}

def fetch(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cik", required=True, help="SEC CIK, 10 digits")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = fetch(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{args.cik.zfill(10)}.json")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print("saved", args.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
