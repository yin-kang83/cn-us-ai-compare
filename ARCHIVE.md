# 归档与引用（v1.4）

本仓库在 Zenodo 有**两条相互匹配的记录**：报告记录与代码/可复现包记录，二者指向**同一个
git tag `v1.4`、同一个归档包**（同一 sha256/md5），不是两份不同内容。

| 记录 | Zenodo record | DOI | 类型 | 归档包 |
|---|---|---|---|---|
| **报告（公开版 v1.4）** | [24373672](https://zenodo.org/records/24373672) | [`10.5281/zenodo.24373672`](https://doi.org/10.5281/zenodo.24373672) | publication / report | `cn-us-ai-compare-v1.4.zip` |
| **代码/可复现包（v1.4）** | [24373980](https://zenodo.org/records/24373980) | [`10.5281/zenodo.24373980`](https://doi.org/10.5281/zenodo.24373980) | software | `cn-us-ai-compare-v1.4.zip` |

## 匹配关系（可核验）
- **同一版本**：两者 metadata.version 均为 `v1.4`；
- **同一归档包**：两者文件均为 `cn-us-ai-compare-v1.4.zip`；
- **同一校验和**：sha256 `c22fd0da99ee8655861bcc87ad28a0f3276cb349b873dca19dff877459506a68`；md5 `ee31cd3afae30230a73dd435c2021095`；
- **同一来源**：git tag `v1.4`（Gitee/GitHub），归档包由 `git archive v1.4` 生成（行尾 LF，无 CRLF）；
- **关联声明**：代码记录 metadata.related_identifiers 含
  `isSupplementTo → 10.5281/zenodo.24373672`（代码补充该报告）；
- **三处一致性**：`scripts/check_consistency.py` 于 2026-11-19 返回 **PASS**
  （Gitee/GitHub tree 与本地 MATCH、Zenodo 报告记录 v1.4/DOI/文件 md5 MATCH）。

## 引用方式
- 引用**报告/研究结论**：使用报告 DOI `10.5281/zenodo.24373672`（概念 DOI `10.5281/zenodo.24353869` 始终指向最新版）；
- 引用**代码/可复现包**：使用软件 DOI `10.5281/zenodo.24373980`；
- 同时引用两者时，建议注明"代码与报告来自同一 v1.4 归档包（sha256 前 12 位 `c22fd0da99ee…`）"。

## 说明
- 报告记录资源类型为 publication/report；代码记录为 software（Zenodo 允许对同一研究成果分别登记）；
- 代码 `scripts/` 采用 MIT；报告文本与数据摘要采用 CC BY 4.0；
- v1.3.1 历史记录保留，不再修改；v1.4 起归档包统一 LF 行尾。
