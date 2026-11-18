# 维护说明（如何更新与镜像）

## 日常更新（以 Gitee 为主仓）

```bash
# 1) 更新报告/数据/脚本后
git add -A
git commit -m "v1.x: 说明本次变更"
git push origin main

# 2) 打版本标签
git tag -a v1.x -m "公开版 v1.x"
git push origin v1.x
```

## GitHub 镜像（本机 github.com:443 被阻断时的替代方案）

优先方案：Gitee 仓库设置 →「仓库镜像管理」→ 添加 GitHub 镜像（需 GitHub 授权），可自动同步。

备选方案（API 方式，已在本仓库验证可行）：

```bash
set GITHUB_TOKEN=ghp_xxx
python scripts/mirror_to_github_api.py --owner yin-kang83 --repo cn-us-ai-compare --branch main
```

说明：脚本通过 GitHub Git Data API 创建 blobs/tree/commit 并更新分支，适合网络无法直连 github.com 的环境；token 只从环境变量读取，不写入仓库。

## 发布检查清单

1. 报告/数据/图表更新完成，数字回原文核对；
2. `python scripts/validate_claims.py data/key_claims.jsonl --schema key_claims` PASS；
3. `python scripts/validate_claims.py data/falsification_ledger.jsonl --schema ledger` PASS；
4. 公开内容脱敏（路径/密钥/个人信息）；
5. 更新 CHANGELOG，打 tag，推送 Gitee，镜像 GitHub。

## 许可提醒

- 代码 MIT；报告与数据摘要 CC BY 4.0；公司公告原文版权归各公司，仓库不转载 PDF 全文。
