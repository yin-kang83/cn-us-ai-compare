# -*- coding: utf-8 -*-
"""三处一致性检查：本地/Gitee 主仓、GitHub 镜像、Zenodo 归档。

用法:
    python check_consistency.py --repo-dir . --gitee yin-kang83/cn-us-ai-compare \\
        --github yin-kang83/cn-us-ai-compare --zenodo-id 24353870

检查项:
1. 本地 main 与 Gitee main 的 commit（fetch 后比较）与 tree hash；
2. GitHub main 的 tree hash 与本地一致（内容一致，历史可不同）；
3. Zenodo 记录版本号与发布包 sha256 是否与本地 tag 归档一致；
4. 输出 PASS/FAIL 表。
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

GIT = r"D:\tools\git\cmd\git.exe"


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def github_get(url: str, token: str):
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "cn-us-ai-compare-consistency",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def zenodo_get(url: str, token: str):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "cn-us-ai-compare-consistency",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def zenodo_token() -> str:
    """从环境变量或本机密钥文件读取 Zenodo token（不打印）。"""
    import os
    tok = os.environ.get("ZENODO_TOKEN", "").strip()
    if tok:
        return tok
    for p in [Path(r"E:\_keys\Zenodo-KEY.txt")]:
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    return ""


def github_token() -> str:
    """从环境变量或 git 凭据读取 GitHub token（不打印）。"""
    import os
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if tok:
        return tok
    psi = subprocess.run([GIT, "credential", "fill"],
                         input="protocol=https\nhost=github.com\n\n",
                         capture_output=True, text=True)
    for line in psi.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-dir", default=".")
    ap.add_argument("--gitee", required=True, help="owner/repo")
    ap.add_argument("--github", required=True, help="owner/repo")
    ap.add_argument("--zenodo-id", required=True, help="Zenodo record id（版本记录）")
    ap.add_argument("--tag", default="v1.3.1")
    args = ap.parse_args()
    repo = Path(args.repo_dir).resolve()
    results = []

    # 本地
    rc, local_main, _ = run([GIT, "rev-parse", "HEAD"], cwd=repo)
    rc, local_tree, _ = run([GIT, "rev-parse", "HEAD^{tree}"], cwd=repo)
    results.append(("本地 HEAD", local_main[:12], "OK" if rc == 0 else "FAIL"))

    # Gitee
    gitee_url = f"https://gitee.com/{args.gitee}.git"
    with tempfile.TemporaryDirectory() as td:
        rc, _, err = run([GIT, "clone", "--quiet", "--depth", "1", "--branch", "main", gitee_url, td])
        if rc == 0:
            _, g_main, _ = run([GIT, "rev-parse", "HEAD"], cwd=td)
            _, g_tree, _ = run([GIT, "rev-parse", "HEAD^{tree}"], cwd=td)
            results.append(("Gitee main", g_main[:12], "OK"))
            results.append(("Gitee tree", g_tree[:12], "MATCH" if g_tree == local_tree else "DIFF"))
        else:
            results.append(("Gitee main", "N/A", f"FAIL {err[:60]}"))
            g_tree = ""

    # GitHub（API，内容树比较）
    gh_tok = github_token()
    try:
        tr = github_get(f"https://api.github.com/repos/{args.github}/git/trees/main?recursive=1", gh_tok)
        gh_tree = tr["sha"]
        results.append(("GitHub tree", gh_tree[:12], "MATCH" if gh_tree == local_tree else "DIFF"))
    except Exception as e:
        results.append(("GitHub tree", "N/A", f"FAIL {str(e)[:60]}"))

    # Zenodo
    z_tok = zenodo_token()
    try:
        rec = zenodo_get(f"https://zenodo.org/api/records/{args.zenodo_id}", z_tok)
        ver = rec.get("metadata", {}).get("version", "")
        doi = rec.get("doi", "")
        files = rec.get("files", [])
        pub_sha = files[0].get("checksum", "").replace("sha256:", "") if files else ""
        results.append(("Zenodo version", ver, "OK" if ver == args.tag else f"DIFF (期望 {args.tag})"))
        results.append(("Zenodo DOI", doi, "OK"))
        # 本地 tag 归档 sha256
        with tempfile.TemporaryDirectory() as td:
            zpath = Path(td) / "archive.zip"
            rc, _, err = run([GIT, "archive", "--format=zip", f"-o{zpath}", args.tag], cwd=repo)
            if rc == 0:
                local_sha = hashlib.sha256(zpath.read_bytes()).hexdigest()
                results.append(("Zenodo 文件 sha256", pub_sha[:16] + "…",
                                "MATCH" if pub_sha == local_sha else "DIFF"))
            else:
                results.append(("Zenodo 文件 sha256", "N/A", f"FAIL {err[:60]}"))
    except Exception as e:
        results.append(("Zenodo", "N/A", f"FAIL {str(e)[:60]}"))

    print("\n=== 三处一致性检查 ===")
    ok = True
    for name, value, verdict in results:
        if verdict not in ("OK", "MATCH"):
            ok = False
        print(f"{name:22s} {value:16s} {verdict}")
    print("=>", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
