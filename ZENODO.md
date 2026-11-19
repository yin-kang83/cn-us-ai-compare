# 发布到 Zenodo（拿 DOI）

> ✅ **已发布（v1.5.2，2026-11-20）**：DOI **[10.5281/zenodo.24374262](https://doi.org/10.5281/zenodo.24374262)** ｜ 记录页 https://zenodo.org/records/24374262 ｜ 概念 DOI 10.5281/zenodo.24353869


## 方式 A：GitHub–Zenodo 自动集成（推荐，一次配置长期有效）

1. 用 GitHub 账号登录 https://zenodo.org （Settings → GitHub）。
2. 在 "GitHub repositories" 列表里找到 `yin-kang83/cn-us-ai-compare`，打开开关。
3. 到 GitHub 仓库创建 **新 release**（如 `v1.3.2`）——Zenodo 只归档"开启集成之后"创建的 release。
4. 发布后 Zenodo 自动生成 DOI，并写入 release 页面；可在 Zenodo 记录里改标题/作者/关键词（或用本仓库 `.zenodo.json` 预填）。
5. 把 DOI 回填到 README 与引用信息（`CITATION.cff`）。

> 若此前已有 `v1.3` release：开启集成后需再建一个 release（例如 `v1.3.2`）才会归档。

## 方式 B：手动上传（无需 GitHub 网络）

1. 打开 https://zenodo.org/uploads/new。
2. 上传本仓库发布包 `cn-us-ai-compare-v1.3.1.zip`（见下）。
3. 按 `ZENODO.md` 下方"元数据填写"逐项填入（或参考 `.zenodo.json`）。
4. 保存草稿 → 检查预览 → Publish → 得到 DOI。

## 方式 C：API 投递（需要 Zenodo access token）

```bash
# 1) 创建 deposition
curl -X POST "https://zenodo.org/api/deposit/depositions" \
  -H "Authorization: Bearer $ZENODO_TOKEN" -H "Content-Type: application/json" -d '{}'
# 2) 上传文件（bucket URL 来自上一步返回的 links.bucket）
curl -X PUT "$BUCKET/cn-us-ai-compare-v1.3.1.zip" \
  -H "Authorization: Bearer $ZENODO_TOKEN" --data-binary @cn-us-ai-compare-v1.3.1.zip
# 3) 填元数据（用 .zenodo.json 的内容）
curl -X PUT "https://zenodo.org/api/deposit/depositions/$ID" \
  -H "Authorization: Bearer $ZENODO_TOKEN" -H "Content-Type: application/json" \
  -d '{"metadata":{...}}'
# 4) 发布（拿 DOI）
curl -X POST "https://zenodo.org/api/deposit/depositions/$ID/actions/publish" \
  -H "Authorization: Bearer $ZENODO_TOKEN"
```

## 元数据填写（手动上传时照抄）

- Title: 中美 AI 对比研究：分层框架、美国 12 家与 A 股 23 家（公开版 v1.3.1）
- Creators: Yin, Kang（Independent Researcher）
- Resource type: Publication / Report
- License: CC BY 4.0（代码 scripts/ 为 MIT，请在描述注明）
- Version: v1.3.1
- Language: Chinese
- Keywords: 中美AI对比; AI infrastructure; capex; 分层框架; 证伪账本; A股; China-US AI comparison
- Related: Gitee / GitHub 仓库链接（isSupplementedBy）

## 发布包

- 文件：`cn-us-ai-compare-v1.3.1.zip`（由 tag v1.3.1 的 `git archive` 生成，SHA256 见发布目目录 `SHA256SUMS.txt`）
- 内容：报告（MD/PDF/图）、方法论、数据摘要、脚本、许可与风险控制清单；不含公告 PDF 全文与内部路径。


## 代码记录（software，v1.4）

- Zenodo 记录 **24374263**：https://zenodo.org/records/24374263 ｜ DOI `10.5281/zenodo.24374263`；
- 与报告记录 **24374262**（`10.5281/zenodo.24374262`）**相互匹配**：同一版本 v1.4、同一归档包、同一 sha256/md5，
  代码记录 metadata 声明 `isSupplementTo → 10.5281/zenodo.24374262`；详见 `ARCHIVE.md`。


## 下载入口（面向读者，无需登录）

- 直接下载完整包：https://zenodo.org/records/24374262/files/cn-us-ai-compare-v1.4.zip?download=1
- 报告记录：https://zenodo.org/records/24374262 ｜ 代码记录：https://zenodo.org/records/24374263
- 归档包自包含（报告 PDF + 代码 + 数据 + 论文），无需访问 Gitee/GitHub。
