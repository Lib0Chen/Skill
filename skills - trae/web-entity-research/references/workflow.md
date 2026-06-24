# Workflow SOP（从 0 到交付）

## 如何运行（最常用命令）

在项目根目录打开 PowerShell，然后依次执行：

1) 站内搜索拿 URL（Searcher）
- 输入：mapping.csv（Search_Key, Search_Query）
- 输出：verified_mapping.csv
- 命令：
  - `py .trae/skills/web-entity-research/scripts/url_discovery.py`

2) 进入 URL 抠 raw_content + 截图（Scraper）
- 输入：verified_mapping.csv
- 输出：scraped_data.csv + screenshots/
- 命令：
  - `py .trae/skills/web-entity-research/scripts/scraper.py`

3) 按 regex 解析 Target_Value（Parser）
- 输入：scraped_data.csv + config.json(parser)
- 输出：final_report.csv / final_report.xlsx + parser_mismatch.csv（如有）
- 命令：
  - `py .trae/skills/web-entity-research/scripts/parser.py`

## Step 0: 定义抽取目标与数据标准
- 做什么：把“要抓什么”写成可执行规格：字段名、字段来源、过滤规则、缺失策略、审计点。
- 用什么：schema 表（assets/output_schema_template.csv）+ config.json。
- 输入：业务口径、示例页面、边界情况。
- 输出：schema + 缺失值策略 + 兜底规则（NR/WD/Manual Check）。

## Step 1: 准备 mapping.csv
- 做什么：把输入名单整理为两列：Search_Key（原始行名/实体标识）+ Search_Query（用于站内搜索的关键词）。
- 用什么：assets/mapping_template.csv。
- 输入：Excel/CSV 名单。
- 输出：mapping.csv。

## Step 2: URL Discovery（站内搜索定位实体页）
- 做什么：对每行 keyword 执行站内搜索，抽取候选实体链接，并选择最优结果。
- 用什么：Playwright + scripts/searcher.py。
- 输入：mapping.csv、config.json（base_url、search_url_template、result_selector）。
- 输出：verified_mapping.csv（Search_Key/Search_Query/Target_URL/Note）。

## Step 3: Evidence Capture（抓取与截图）
- 做什么：进入 URL，等待目标区域出现，抓取 raw_content，并保存截图（用作审计证据）。
- 用什么：Playwright + scripts/scraper.py。
- 输入：verified_mapping.csv、content_root_selector（可选）、screenshots_dir。
- 输出：scraped_data.csv（Target_URL + raw_content + Search_Key）、screenshots/*.png。

## Step 4: Parse & Normalize（解析与标准化）
- 做什么：从 raw_content 提取“可对齐的历史序列”（如 Target_Date + Target_Value），并落到中间表。
- 用什么：pandas + regex + scripts/parser.py。
- 输入：scraped_data.csv、parser.date_regex、parser.target_value_regex。
- 输出：parsed_results.csv（每条记录一行，包含 Target_URL、Target_Date、Target_Value）。

## Step 5: Window/Point-in-time 计算
- 做什么：对每个 URL，在截止日期（cutoff）之前取最新的一条。
- 用什么：pandas groupby + max(date)。
- 输入：parsed_results.csv + cutoffs。
- 输出：url_level_features.csv（每个 URL 一行，含各窗口 Target_Value/Target_Date）。

## Step 6: Merge Back to 65 rows
- 做什么：以 URL 左连接回 verified_mapping.csv，确保同 URL 的多个分行都拿到同一结果。
- 用什么：pandas merge。
- 输入：verified_mapping.csv + url_level_features.csv。
- 输出：final_report.xlsx / final_report.csv。

## Step 7: 异常与抽样审计
- 做什么：输出“需要人工确认”的列表：错配、无数据、数量不匹配、疑似非银行实体。
- 用什么：pandas 规则检测。
- 输入：final_report + scraped_data + parsed_history。
- 输出：audit_report.csv（异常原因、建议动作、截图路径）。

## 人工介入点（建议流程）
- 当 “Entity Mismatch” 出现：人工在 verified_mapping.csv 修正 URL 或写 overrides，再重跑 Step 3-6。
- 当 Premium 内容不可见：记录为 Manual Check 并保留截图证据。
- 当字段口径争议：在 schema 中明确选择规则，再重跑解析模块。
