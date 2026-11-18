# 三处一致性（SYNC）

本仓库有三处公开副本 + 一处源头，必须保持一致：

| 位置 | 角色 | 地址 |
|---|---|---|
| 本地仓库 | 源头（唯一编辑处） | `D:\tools\repos\cn-us-ai-compare` |
| Gitee | **主仓**（日常 push） | https://gitee.com/yin-kang83/cn-us-ai-compare |
| GitHub | 镜像（网络受限，API 同步） | https://github.com/yin-kang83/cn-us-ai-compare |
| Zenodo | **DOI 归档**（发版时） | https://doi.org/10.5281/zenodo.24353870 |

## 一致性检查（发布前必跑）

```bash
python scripts/check_consistency.py \
  --repo-dir . \
  --gitee yin-kang83/cn-us-ai-compare \
  --github yin-kang83/cn-us-ai-compare \
  --zenodo-id 24353870 \
  --tag v1.3.1 \
  --release-file ../ai-companies-analysis/zenodo/cn-us-ai-compare-v1.3.1.zip
```

期望输出（全部 OK/MATCH）：

```
本地 HEAD                <sha>            OK
Gitee main               <sha>            OK
Gitee tree               <sha>            MATCH
GitHub tree              <sha>            MATCH
Zenodo version           v1.3.1           OK
Zenodo DOI               10.5281/...      OK
Zenodo 文件 md5           <hash>           MATCH
=> PASS
```

- **tree 一致** = 三处内容完全相同（GitHub 镜像按 git 对象上传，tree sha 与本地 HEAD 一致）；
- **Zenodo 文件校验** = 归档 zip 与本地发布包同一文件（md5/sha256 按 Zenodo 返回的算法比对）；
- 任何 DIFF 都是发布阻断项。

## 日常更新流程

```bash
# 1) 本地修改（报告/数据/脚本）
# 2) 数据校验
python scripts/validate_claims.py data/key_claims.jsonl --schema key_claims
python scripts/validate_claims.py data/falsification_ledger.jsonl --schema ledger
# 3) 提交并推 Gitee
git add -A && git commit -m "v1.x: 说明" && git push origin main
# 4) 镜像 GitHub（API；token 只走环境变量）
GITHUB_TOKEN=... python scripts/mirror_to_github_api.py \
  --owner yin-kang83 --repo cn-us-ai-compare --branch main
# 5) 一致性问题修复后重跑 check_consistency.py
```

## 发版流程（含 Zenodo 新版本）

1. 更新 CHANGELOG、`CITATION.cff` 版本号与 DOI；
2. 打 tag（如 `v1.4`）并推 Gitee；
3. 生成发布包：`git archive --format=zip -o cn-us-ai-compare-v1.4.zip v1.4`；
4. 镜像 GitHub（文件 + tag/release，经 API）；
5. Zenodo 在现有记录上创建 **New version**（概念 DOI 不变），上传新 zip，改版本号/描述，发布；
6. 回填新版本 DOI 到 README/CITATION/报告，重复 1–5；
7. 跑 `check_consistency.py` 确认 PASS。

## 失败处理

- **GitHub tree DIFF**：不要手改 GitHub 网页；重跑镜像脚本（按 git 对象上传，会自动对齐 tree）。
- **Zenodo 文件校验 DIFF**：确认发布包就是上传的那个 zip（不要重新 `git archive` 后比对，zip 时间戳会变）；必要时以 Zenodo 记录中的 checksum 为准。
- **Gitee tree DIFF**：本地未 push 或有未提交改动；先提交推送再检查。
- **历史差异**：GitHub 镜像历史与 Gitee 不同（API 快照），以 **tree 一致** 为准，不要求 commit hash 一致。
