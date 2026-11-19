# 中美 AI 对比研究（cn-us-ai-compare）

一套**可回溯、可证伪、可迭代**的中美 AI 产业对比研究：分层框架 L1–L5、美国 12 家科技/芯片公司、中国 A 股 23 家 AI 与算力公司、跨市场比率与证伪账本。

> DOI: [10.5281/zenodo.24374262](https://doi.org/10.5281/zenodo.24374262) ｜ Zenodo: https://zenodo.org/records/24373672
> 公开版报告 v1.5.2（2026-11-20）：A 股 2026 三季报/半年报原文 23/23 已核；美国 2026Q3 财报季。
> 研究材料，不构成投资建议。

## 目录

| 路径 | 内容 |
|---|---|
| `papers/` | 两篇工作论文（论文 1：AI 投资竞赛实证；论文 2：可审计跨市场对比方法论） |
| `reports/` | 公开版报告（Markdown + PDF）与图表（美国 capex/营收、A 股纯度×风险、研究体系架构） |
| `methodology/` | 方法论、底层架构与数据通道说明（六环节 + 反馈回路） |
| `data/` | 可回溯数据：197 条 key_claims、48 条证伪假设、美国 12 家财务、单季 capex、A 股 23 家 Q3/H1 摘要（CSV） |
| `scripts/` | 数据抓取与校验示例：SEC companyfacts、巨潮公告 PDF、JSONL schema 校验 |

## 快速开始

```bash
# 校验数据完整性
python scripts/validate_claims.py data/key_claims.jsonl --schema key_claims
python scripts/validate_claims.py data/falsification_ledger.jsonl --schema ledger

# 下载 SEC companyfacts（示例：微软）
python scripts/fetch_sec_companyfacts.py --cik 0000789019 --out data/sec/MSFT.json

# 下载巨潮公告 PDF（示例：协创数据 2026 三季报；orgId 可在巨潮公告页查询）
python scripts/fetch_cninfo.py --code 300857 --org 9900039793 --title 2026年三季度报告 --out data/cn/
```

## Working papers

- **Paper 1** (v0.3, 14 pp.): *The AI investment race: revenue, capital expenditure, and financing structures in US and Chinese listed firms (2026)*.
- **Paper 2** (v0.2, 18 pp.): *Making Cross-Market Industry Comparisons Auditable: An Evidence-Graded, Falsifiable Framework*.

PDFs are in [`papers/`](papers/). Working papers, not peer reviewed.

## 核心结论（摘要）

1. 美国强在"能力+资本+生态+变现"，中国强在"工程+成本+场景+速度"；没有总分，只有分层差距。
2. 美国云 AI 收入加速（Azure +48%、Google Cloud +103%、AWS +39.3%），但 capex 增速整体更高；谷歌最接近投入产出平衡。
3. A 股已出现真实算力收入（协创 2026 前三季营收 196.10 亿、归母 30.62 亿），但普遍伴随高杠杆（协创负债率 85.8%）。
4. 2026–2027 关键：谁能把 AI 投入变成可核验的现金流。

完整判断（12 条，含置信度与可证伪条件）见报告"判断汇总"一节。

## 数据来源与证据分级

- **L1 一手原文**：公司公告/定期报告、SEC EDGAR、中国海关总署、业绩公告；
- **L2**：由原文计算或扫描（需回原文核对）；
- **L3**：媒体/研报线索（只作方向，不作定量结论）。
- 第三方数据（AAII/QuestMobile/IDC 等）只做结论级引用，不在仓库保存原始数据。

## 许可

- 代码（`scripts/`）：MIT（见 `LICENSE`）。
- 报告文本与数据摘要：CC BY 4.0（见 `LICENSE-REPORT-DATA`），引用请注明来源。
- 公司公告原文版权归各公司，本仓库仅保存数字摘要、不转载 PDF 全文。

## 引用

见 `CITATION.cff`；或：`yin-kang83. 中美 AI 对比研究（公开版 v1.5.2）. 2026. https://gitee.com/yin-kang83/cn-us-ai-compare`

## 更新节奏

- A 股：2026 年报/2027 一季报（2027-01 至 2027-04）；公告哨兵每周一。
- 美国：季度财报（capex/云收入/FCF）。
- 版本变更见 `CHANGELOG.md`。

## 免责声明

见 `DISCLAIMER.md`：研究参考，不构成投资建议；数据可能滞后或被修订，以公司公告与监管文件为准。


## 归档与引用（v1.4）

- 报告 DOI：[10.5281/zenodo.24374262](https://doi.org/10.5281/zenodo.24374262)（记录 24373672）；
- 代码/可复现包 DOI：[10.5281/zenodo.24374263](https://doi.org/10.5281/zenodo.24374263)（记录 24373980，software）；
- **两条记录相互匹配**：同一 git tag v1.4、同一归档包 `cn-us-ai-compare-v1.4.zip`，
  sha256 `c22fd0da99ee…` / md5 `ee31cd3afae30230a73dd435c2021095`；详见 `ARCHIVE.md`。


## 下载入口（无需 Gitee/GitHub 账号）

Zenodo 归档包**自包含**：报告 PDF/代码/数据/论文/一致性脚本都在同一个 zip 内，下载即完整，无需打开 Gitee/GitHub。

- 报告+完整包（v1.4）：[cn-us-ai-compare-v1.4.zip](https://zenodo.org/records/24373672/files/cn-us-ai-compare-v1.4.zip?download=1)（记录 [24373672](https://zenodo.org/records/24373672)，DOI `10.5281/zenodo.24374262`）
- 代码/可复现包（software，v1.4）：https://zenodo.org/records/24373980（DOI `10.5281/zenodo.24374263`）
- Gitee/GitHub 仅作代码镜像与更新源；GitHub 读者也可不登录直接下载 Release 附件。

> 两条 Zenodo 记录**相互匹配**：同一 v1.4 归档包、同一 sha256/md5；详见 `ARCHIVE.md`。


## 延伸阅读

- [《AI 学习的四种路径与可验证性标准》](methodology/AI学习的四种路径与可验证性标准-20261119.md)：四种学习路径、可验证性四问、用本研究的 197 条 claim / 48 条证伪假设做案例，附 6 个月路径。
