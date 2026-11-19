# 文献检索 → 证据账本（literature → ledger）

把 `skills/literature-retrieval/` 的检索结果接入本仓证据账本；只入**元数据**，不入全文。

## 1. 原则

- OpenAlex / Crossref / arXiv 只提供元数据与合法 OA 链接，**不下载、不转存全文**；
- 入账记录标注 `evidence_level = L3_METADATA`：文献是**线索**，不是事实结论；
- 要升级为 L1/L2，必须读原文并把具体数字/条款写入 `key_claims.jsonl`（带 source/locator）；
- DOI/标题/年份需核验（`verify_metadata.py` → `match/partial/mismatch/not_found`）；
- 去重：DOI → landing_page → 标题+年份；追加写，不覆盖。

## 2. 流程

```text
build_query_plan.py        # 关键词扩展（可审计）
        ↓
search_openalex.py / search_crossref.py / search_arxiv.py   # 元数据
        ↓
verify_metadata.py         # DOI 交叉核验（可选但建议）
        ↓
ingest_literature.py       # 去重、加 ID、写 data/literature_ledger.jsonl
```

## 3. 命令

```powershell
$py = "C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
& $py skills/literature-retrieval/scripts/search_arxiv.py --query "large language model compliance" --max-results 5 -o .tmp/arxiv.json
& $py skills/literature-retrieval/scripts/verify_metadata.py --doi 10.1000/xyz -o .tmp/verify.json
& $py scripts/ingest_literature.py --input .tmp/arxiv.json --verify .tmp/verify.json --ledger data/literature_ledger.jsonl
# 预览不写盘：--dry-run
```

## 4. 账本字段

`id / source_db / title / authors / year / doi / venue / type / cited_by_count / oa_url / pdf_url /
landing_page / query / retrieved_at / verification / evidence_level / note / ingested_at`

## 5. 边界

- 文献账号/订阅库（CNKI/万方/维普）不在本仓范围；如需中文库请走授权接口；
- 不保证覆盖全部文献（OpenAlex/Crossref/arXiv 各有偏差）；
- 平台/机构对下载有各自条款；本仓只保存元数据，不保存全文；
- 研究材料，不构成投资建议。
