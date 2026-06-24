# web-entity-research

一个通用的“站内搜索/直接定位 → 进入目标页 → 抠取文字/表格 → 解析为结构化数据 → 导出 CSV/XLSX”的工具箱（适配 Trae Skills）。

## 你会得到什么

- 三段式流水线：Searcher（URL Discovery）→ Scraper（抓取+截图）→ Parser（解析+导出）
- 配置驱动：把网站差异都放在 config.json（站点 URL 模板、选择器、解析模式、输出路径、浏览器参数）
- 可审计：保留 raw_content、raw_html、matrix_json（可选）和截图路径

## 目录结构

- scripts/
  - url_discovery.py：站内搜索或 direct 模式生成目标 URL，输出 verified mapping
  - scraper.py：进入 Target_URL，抓 raw_content/raw_html，保存截图，可额外输出 matrix_json
  - parser.py：按 parser.mode 解析并导出最终 CSV/XLSX
- assets/
  - mapping_template.csv：输入清单模板（Search_Key, Search_Query）
  - output_schema_template.csv：输出字段模板（用于先把“要什么输出”定义清楚）
- references/
  - workflow.md：从 0 到交付的 SOP
- SELECTORS.md：5 分钟学会找 selector（给小白）
- config.json：站点/选择器/规则配置（默认值，可用环境变量覆盖）

## 运行前准备（Windows）

1) 安装 Python（建议 3.10+）

2) 安装依赖

```bash
py -m pip install -U pip
py -m pip install pandas playwright
py -m playwright install chromium
```

3) Chrome（可选）
- 如果 config.json 里 browser.channel 使用 "chrome"，本机需要安装 Google Chrome。
- 不想依赖本机 Chrome：把 channel 改成 "chromium"。

## 在 Trae 项目里怎么安装

Trae 会从你项目内的 `.trae/skills/` 读取 Skills。

如果你把这个 skill 放在 GitHub 仓库里（例如 `Lib0Chen/Skill`），那么安装到某个项目的做法是把：

- `skills/web-entity-research/`

复制到你的目标项目：

- `<你的项目>/.trae/skills/web-entity-research/`

PowerShell 示例：

```powershell
Copy-Item -Recurse -Force "<本仓库路径>\skills\web-entity-research" "<你的项目路径>\.trae\skills\web-entity-research"
```

## 最快上手（3 个命令）

在你的项目根目录（Trae 项目）依次执行：

```bash
py .trae/skills/web-entity-research/scripts/url_discovery.py
py .trae/skills/web-entity-research/scripts/scraper.py
py .trae/skills/web-entity-research/scripts/parser.py
```

对应输入/输出（路径由 config.json 的 io.* 控制）：
- 输入：io.mapping_csv 指向的 CSV（推荐列：Search_Key, Search_Query；也兼容旧列：Original Name, Search Keyword）
- 输出 1：io.verified_mapping_csv（Search_Key, Search_Query, Target_URL, Note）
- 输出 2：io.scraped_data_csv（raw_content/raw_html/matrix_json + screenshot_path）
- 输出 3：io.final_csv（regex 模式是“最终报告”；table_matrix 模式是“矩阵 CSV”）

## 用环境变量切换配置（推荐）

不想每次改默认 config.json，就用环境变量指定配置文件路径：

PowerShell（当前窗口生效）：

```powershell
$env:WEB_ENTITY_RESEARCH_CONFIG = ".trae/skills/web-entity-research/examples/wise/config.json"
py .trae/skills/web-entity-research/scripts/url_discovery.py
py .trae/skills/web-entity-research/scripts/scraper.py
py .trae/skills/web-entity-research/scripts/parser.py
```

## Wise 示例（表格矩阵导出）

如果你要抓 Wise 的历史汇率矩阵（保留行列结构），用：

- parser.mode = table_matrix
- scraper 输出 matrix_json

推荐直接用 examples/wise 的 config + mapping：
- `.trae/skills/web-entity-research/examples/wise/config.json`
- `.trae/skills/web-entity-research/examples/wise/test_wise.csv`

## config.json 关键字段（读这一段就够）

- site.base_url：网站首页（用于初始化、拼接相对链接）
- site.search_url_template：搜索 URL 模板，必须包含 {query}
- site.search_mode：
  - "results"：打开搜索页后，按 result_selectors 找结果链接并点击/抽 href
  - "direct"：不走结果页，直接用 search_url_template 生成目标页（适合 Wise 这类可预测 URL）
- selectors.cookie_accept_selectors：cookie 弹窗按钮 selector 列表（按顺序尝试）
- selectors.result_selectors：搜索结果“链接”的 selector 列表（用于 results 模式）
- selectors.content_root_selectors：详情页“目标内容区域”的 selector 列表（用于降低噪音；按顺序尝试）
- parser.mode：
  - "regex"：从 raw_content 用正则抽 date/value，可配置 cutoffs 做“截止日期前最新值”
  - "table_matrix"：优先从 matrix_json 输出矩阵 CSV（保留行列结构）
- io.*：输入/输出文件路径与截图目录
- browser.*：channel/headless/slow_mo_ms/timeout_ms

## 常见问题（你不用自己踩坑）

- 抓到空内容：优先检查 selectors.content_root_selectors；看 scraped_data.csv 的 note 是否为 content_root_not_found
- 搜索结果错配：检查 verified_mapping.csv 的 Target_URL；必要时人工改 URL 后只重跑 scraper + parser
- 页面加载慢/动态渲染：加大 browser.timeout_ms，或在 scraper 里增加等待（networkidle 已做兜底）
- Excel 写不进去：xlsx 被占用时会失败；先用 CSV 做交付/审计更稳

更详细流程与异常处理见 references/workflow.md。  
