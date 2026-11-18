# -*- coding: utf-8 -*-
"""从巨潮资讯网下载 A 股定期报告 PDF（示例脚本，需自行遵守网站条款与频率限制）。

用法: python fetch_cninfo.py --code 300857 --org 9900039793 --title 2026年三季度报告 --out data/cn/
"""
import argparse, json, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0", "Referer": "http://www.cninfo.com.cn/"}

def query(code: str, org: str, page: int = 1) -> list:
    data = urllib.parse.urlencode({
        "pageNum": page, "pageSize": 30, "column": "szse", "tabName": "fulltext",
        "plate": "", "stock": f"{code},{org}", "searchkey": "", "secDate": "", "category": "",
    }).encode()
    req = urllib.request.Request("http://www.cninfo.com.cn/new/hisAnnouncement/query", data=data,
                                 headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8")).get("announcements") or []

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", required=True)
    ap.add_argument("--org", required=True, help="巨潮 orgId（可在公告页 URL 或接口查询）")
    ap.add_argument("--title", required=True, help="公告标题，如 2026年三季度报告")
    ap.add_argument("--out", required=True, help="输出目录")
    args = ap.parse_args()
    import os
    os.makedirs(args.out, exist_ok=True)
    for page in range(1, 6):
        anns = query(args.code, args.org, page)
        if not anns:
            break
        for a in anns:
            if (a.get("announcementTitle") or "").strip() == args.title:
                url = "http://static.cninfo.com.cn/" + a["adjunctUrl"]
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=120) as r:
                    pdf = r.read()
                path = os.path.join(args.out, f"{args.code}-{args.title}.pdf")
                open(path, "wb").write(pdf)
                print("saved", path, len(pdf), "bytes")
                return 0
        time.sleep(0.5)
    print("not found")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
