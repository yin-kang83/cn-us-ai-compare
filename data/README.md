# 数据说明

## 文件
- `key_claims.jsonl`：197 条可回溯主张（claim / value / unit / source / locator / retrieved_at / confidence / 口径）。
- `falsification_ledger.jsonl`：48 条证伪假设及证据/状态（C1/C2/C3 等）。
- `us_financials_12.json`：美国 12 家财务底表（SEC XBRL，FY 最新）。
- `us_capex_qtr.json`：美国四大云厂商单季 capex（10-Q/companyfacts）。
- `cn_23_2026q3.csv` / `cn_23_2026h1.csv`：A 股 23 家 2026 三季报/半年报财务摘要（亿元，原文核对）。
- `literature_ledger.jsonl`：文献元数据账本（OpenAlex/Crossref/arXiv，`evidence_level=L3_METADATA`，仅线索，不是事实结论）；由 `scripts/ingest_literature.py` 生成，详见 `docs/LITERATURE-PIPELINE.md`。

## 来源与许可
- 美国数据：SEC EDGAR（公开文件，美国联邦政府作品一般不受版权保护）。
- A 股数据：公司定期报告（巨潮资讯网）；本仓库仅保存**数字摘要**，不转载公告 PDF 全文；公司公告版权归各公司，引用请遵循其条款。
- 第三方数据（AAII/QuestMobile/IDC 等）不在本仓库保存原始数据，仅在报告中做结论级引用。

## 口径
- 单位：A 股为亿元人民币；美国为亿美元（TSM 为 TWD 折算，见报告注）。
- 财年：美国公司财年各异（见报告）；A 股为自然年。
- 证据等级：L1 一手原文 / L2 原文计算或扫描 / L3 媒体研报线索。
