# Web Entity Research Skill (Toolbox)

这是一个通用的“站内搜索 → 进入结果页 → 抠取文字/表格 → 用正则解析 → 导出 CSV/XLSX”的工具箱（适配 Trae Skills）。

## 目录结构

- `skills/web-entity-research/`：Skill 主目录（SKILL.md / config.json / scripts / assets / references）

## 在 Trae 项目里怎么安装

Trae 会从你项目内的 `.trae/skills/` 读取 Skills。

把本仓库里的：

- `skills/web-entity-research/`

复制到你的目标项目：

- `<你的项目>/.trae/skills/web-entity-research/`

示例（PowerShell）：

```powershell
Copy-Item -Recurse -Force "<本仓库路径>\skills\web-entity-research" "<你的项目路径>\.trae\skills\web-entity-research"
```

## 如何运行（3 个脚本）

在你的目标项目根目录运行（脚本默认读取当前目录下的 mapping.csv 并在当前目录输出文件）：

1) Searcher：站内搜索 → 生成 verified_mapping.csv

```powershell
py .trae/skills/web-entity-research/scripts/url_discovery.py
```

2) Scraper：进入 Target_URL → 抓 raw_content + 截图 → 生成 scraped_data.csv

```powershell
py .trae/skills/web-entity-research/scripts/scraper.py
```

3) Parser：按 config.json 的 regex 解析 → 生成 final_report.csv/xlsx

```powershell
py .trae/skills/web-entity-research/scripts/parser.py
```

## 你需要改哪里

- `skills/web-entity-research/config.json`
  - `base_url`：网站首页
  - `search_url_template`：搜索 URL 模板（必须包含 `{query}`）
  - `result_selector`：搜索结果链接 selector
  - `content_root_selector`：详情页内容区域 selector（可选）
  - `parser.target_value_regex` / `parser.date_regex`

选择器怎么找：看 `skills/web-entity-research/SELECTORS.md`。