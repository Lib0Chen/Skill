---
name: "web-entity-research"
description: "自动化“先搜索定位实体页→处理跳转/混淆→抽取指定字段→导出CSV/XLSX”。当用户要在网站内搜索实体并抓取结构化信息(含窗口/时点规则)时触发。"
---

# Web Entity Research Toolbox

## 目标

把“人类在网站上搜索目标→选对结果→进入目标页面→抽取指定信息→清洗/对齐→输出报告”的流程沉淀成通用框架，可迁移到任何“站内搜索 + 结果列表 + 详情页”的网站（电商价格、企业信息、公告、产品参数、评级/财务、招聘等）。

## 适用范围（Scope）

- 站内搜索驱动：目标实体页需要通过搜索入口定位，而不是已知 URL 列表。
- 结果可能混淆：同名/相似名、非目标实体（政府/项目/信用摘要）会出现在前列。
- 需要结构化输出：把网页内容抽成确定表头的 CSV/XLSX，便于审计与复用。
- 抽取规则可配置：字段可能是评级、日期、数值、段落、表格单元格；也可能需要按“窗口/时点”取最近值。

不适用（建议人工或另选策略）：

- 强反爬（必须登录、强验证码、频繁阻断）且无可用账号/白名单。
- 内容主要在 PDF/图片且无 OCR 允许或要求极高精度。

## 工作流总览（Workflow Overview）

### 0) 定义需求与输出 Schema
- 做什么：明确要抓哪些字段、输出表头、每列的数据标准（缺失值、NR/WD/Manual Check 等）。
- 工具：SKILL.md + assets 模板。
- 输入：业务需求、目标站点、示例页面/截图。
- 输出：schema（列名+含义+取值规则）、缺失策略。

### 1) 输入清单准备（Mapping）
- 做什么：准备输入清单，至少包含 `Search_Key` 与 `Search_Query`。
- 工具：assets/mapping_template.csv
- 输入：名单（Excel/CSV）。
- 输出：mapping.csv（可直接喂给脚本/Agent）。

### 2) URL 定位（Search → Disambiguation → Canonical URL）
- 做什么：对任意站点执行站内搜索，抓取候选结果链接并输出目标页 URL。
- 工具：Playwright（本地 Chrome channel），scripts/searcher.py
- 输入：mapping.csv + config.json（base_url、search_url_template、result_selector）。
- 输出：verified_mapping.csv（Search_Key/Search_Query/Target_URL/Note）。

### 3) 抓取与证据留存（Capture + Screenshot + Raw）
- 做什么：进入 Target_URL，按 content_root（可选）截取页面文字，并保存截图作为证据。
- 工具：Playwright，scripts/scraper.py
- 输入：verified_mapping.csv + config.json（content_root_selector 可选）。
- 输出：scraped_data.csv（Target_URL + raw_content + screenshot_path + Search_Key）。

### 4) 解析与对齐（Parse → Normalize → Align）
- 做什么：用 config.json 中的正则把 raw_content 抽取成结构化字段（Target_Value/Target_Date），可选进行窗口/时点计算。
- 工具：pandas + regex，scripts/parser.py
- 输入：scraped_data.csv + config.json（parser.date_regex / parser.target_value_regex / cutoffs）。
- 输出：parsed_results.csv（中间表）+ final_report.csv/xlsx（可选）。

### 5) 合并回全量清单（Left Join + Propagate）
- 做什么：以 URL 为 key 左连接回 65 行全量；同一母行 URL 覆盖多个分行；对“错配 URL”用推断/人工字典兜底。
- 工具：pandas，scripts/final_report_builder.py
- 输入：verified_mapping.csv + scraped_data.csv (+ overrides.json 可选)。
- 输出：最终报告（XLSX+CSV），并生成异常清单。

### 6) QA 与抽样审计（Audit）
- 做什么：自动生成异常列表（URL 缺失、错配、NR/WD、日期/评级数量不匹配）；输出抽样校验表便于人工复核。
- 工具：pandas
- 输入：最终表 + 中间表。
- 输出：audit_report.csv（异常/抽样）。

## 自动化 vs 人工干预（建议分工）

### 可自动化（优先交给 Agent）
- 站内搜索、候选结果抓取、跳转处理、基础置信度排序。
- 抓取目标区域（有明确 anchor/标题/表格结构）。
- 固定 schema 输出、CSV/XLSX 转换、截图证据。
- 规则化解析：日期/评级/数值正则，窗口/时点计算。

### 需要人工兜底（必须保留“Manual Check”通道）
- 搜索结果强混淆且目标不在第一页（需要业务判断）。
- 站点结构变更（selector 失效）。
- 需要登录/权限或 Premium 内容不可见。
- “目标字段”语义依赖上下文（例如多种评级口径需选择某一种）。

## 输出标准（Output Standards）

- 所有最终输出必须可复现：包含输入 mapping、已确认 URL、raw_content、截图路径、版本号/日期。
- 任何无法自动确定的结果统一落到：
  - NR（无评级/无该周期数据）
  - WD（撤销）
  - Manual Check（需要人工）
- 必须提供：异常清单（错配/缺失/数量不匹配/页面类型异常）。

## 易错点（最高信号）

1) 搜索结果错配（Entity Mismatch）
- 表现：同名/相似名导致抓到错误实体或错误品类页面。
- 处理：不要只取第一个结果；抓 Top-N 并打分（名称相似度、slug 命中、关键 anchor 命中）；必要时写 overrides。

2) raw_content 粘连与分界
- 表现：日期/数值粘连、数量不匹配、页面文本重复。
- 处理：先定位 content_root（例如详情页某块容器）再抽取；始终输出 mismatch 日志与截图。

3) 目标值口径混淆
- 表现：页面同时包含多个相似字段（价格/折扣价/会员价；不同口径的评级/指标）。
- 处理：把“口径选择规则”写进 parser.target_value_regex 或 anchor 截取规则，并保留 raw_content 供审计。

4) 文件占用导致 PermissionError（Windows）
- 表现：Excel 正打开导致写 xlsx 失败。
- 处理：先写 CSV，再尝试写 xlsx；失败时提示用户关闭文件重跑。

## 使用方式（给 Agent 的执行指令）

当你要让 Agent 执行一轮“搜索→抓取→解析→合并”时，给它这 3 个输入：

1) config.json：base_url + search_url_template + result_links/content_root + parser 规则
2) mapping.csv（Search_Key, Search_Query）
3) 输出 schema（列名+规则），以及是否需要窗口/时点逻辑

脚本入口参考：
- scripts/searcher.py
- scripts/scraper.py
- scripts/parser.py

更详细操作见 references/workflow.md。  
