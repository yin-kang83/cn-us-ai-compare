# -*- coding: utf-8 -*-
"""用 GitHub Git Data API 镜像当前 git 仓库到 GitHub（按 git 对象镜像，保证 tree 一致）。

用法:
    GITHUB_TOKEN=ghp_xxx python scripts/mirror_to_github_api.py \\
        --owner yin-kang83 --repo cn-us-ai-compare --branch main

特点:
- 从 `git ls-tree -r HEAD` 读取被跟踪文件，用 `git cat-file` 取原始字节上传，
  因此 GitHub 端的 tree sha 与本地 HEAD 完全一致（不受 Windows 换行影响）。
- 保留远端历史：新 commit 的 parent 为远端分支当前 head。
- token 仅从环境变量 GITHUB_TOKEN 读取，不写入任何文件。
"""
import argparse
import base64
import json
import os
import subprocess
import urllib.request
import urllib.error

GIT = os.environ.get("GIT_BIN") or (
    r"D:\tools\git\cmd\git.exe" if os.path.exists(r"D:\tools\git\cmd\git.exe") else "git")
API = "https://api.github.com"


def git(*args):
    p = subprocess.run([GIT, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[:300])
    return p.stdout


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
    repo_api = f"{API}/repos/{args.owner}/{args.repo}"

    # 1) 确保远端仓库有初始分支，取 parent sha
    try:
        parent = req("GET", f"{repo_api}/git/ref/heads/{args.branch}", token)["object"]["sha"]
    except urllib.error.HTTPError as e:
        if e.code not in (404, 409):
            print("ref check failed:", e.code, e.read().decode()[:120]); return 3
        try:
            req("PUT", f"{repo_api}/contents/README.md", token,
                {"message": "init", "content": base64.b64encode(b"# init\n").decode()})
        except urllib.error.HTTPError as e2:
            print("init failed:", e2.code, e2.read().decode()[:200]); return 3
        parent = req("GET", f"{repo_api}/git/ref/heads/{args.branch}", token)["object"]["sha"]

    # 2) 从 git 对象生成 tree（保证 tree sha 与本地一致）
    out = git("ls-tree", "-r", "-z", "HEAD").decode("utf-8", "replace")
    entries = []
    for item in out.split("\0"):
        if not item:
            continue
        meta, path = item.split("\t", 1)
        mode, objtype, sha = meta.split()
        if objtype != "blob":
            continue
        raw = git("cat-file", "blob", sha)
        blob = req("POST", f"{repo_api}/git/blobs", token,
                   {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
        entries.append({"path": path, "mode": mode, "type": "blob", "sha": blob["sha"]})

    tree = req("POST", f"{repo_api}/git/trees", token, {"tree": entries})
    local_tree = git("rev-parse", "HEAD^{tree}").decode().strip()
    same = tree["sha"] == local_tree
    print(f"files={len(entries)} local_tree={local_tree[:12]} github_tree={tree['sha'][:12]} "
          f"{'TREE_MATCH' if same else 'TREE_DIFF'}")

    commit = req("POST", f"{repo_api}/git/commits", token,
                 {"message": args.message, "tree": tree["sha"], "parents": [parent]})
    req("PATCH", f"{repo_api}/git/refs/heads/{args.branch}", token,
        {"sha": commit["sha"], "force": True})
    print("mirrored ->", f"https://github.com/{args.owner}/{args.repo}", commit["sha"][:8])
    return 0 if same else 4


if __name__ == "__main__":
    raise SystemExit(main())
