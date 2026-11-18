# -*- coding: utf-8 -*-
"""用 GitHub Git Data API 镜像当前仓库到 GitHub（适用于无法直连 github.com 的网络）。

用法:
    GITHUB_TOKEN=ghp_xxx python scripts/mirror_to_github_api.py \
        --owner yin-kang83 --repo cn-us-ai-compare --branch main

行为:
- 读取当前目录全部文件（排除 .git/、data/raw/）
- 创建 blobs → tree → commit（父提交为远端分支当前 head）→ 更新分支
- token 仅从环境变量 GITHUB_TOKEN 读取，不写入任何文件
"""
import argparse, base64, json, os, sys, urllib.request, urllib.error
from pathlib import Path

API = "https://api.github.com"

def req(method, url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json",
               "User-Agent": "cn-us-ai-compare-mirror", "Content-Type": "application/json"}
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.loads(resp.read().decode() or "{}")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--branch", default="main")
    ap.add_argument("--message", default="镜像同步：来自 Gitee 主仓")
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: 请设置环境变量 GITHUB_TOKEN"); return 2
    base_repo = f"{API}/repos/{args.owner}/{args.repo}"
    # 确保仓库有初始提交
    try:
        req("GET", f"{base_repo}/git/ref/heads/{args.branch}", token)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            try:
                req("PUT", f"{base_repo}/contents/README.md", token,
                    {"message": "init", "content": base64.b64encode(b"# init\n").decode()})
            except urllib.error.HTTPError as e2:
                print("init failed:", e2.code, e2.read().decode()[:200]); return 3
        else:
            print("ref check failed:", e.code); return 3
    parent = req("GET", f"{base_repo}/git/ref/heads/{args.branch}", token)["object"]["sha"]
    files = [p for p in Path(".").rglob("*")
             if p.is_file() and ".git" not in p.parts and not p.relative_to(".").as_posix().startswith("data/raw/")]
    tree = []
    for p in files:
        blob = req("POST", f"{base_repo}/git/blobs", token,
                   {"content": base64.b64encode(p.read_bytes()).decode(), "encoding": "base64"})
        tree.append({"path": p.relative_to(".").as_posix(), "mode": "100644", "type": "blob", "sha": blob["sha"]})
    tr = req("POST", f"{base_repo}/git/trees", token, {"tree": tree})
    cm = req("POST", f"{base_repo}/git/commits", token,
             {"message": args.message, "tree": tr["sha"], "parents": [parent]})
    req("PATCH", f"{base_repo}/git/refs/heads/{args.branch}", token, {"sha": cm["sha"], "force": True})
    print("mirrored", len(files), "files ->", f"https://github.com/{args.owner}/{args.repo}", cm["sha"][:8])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
