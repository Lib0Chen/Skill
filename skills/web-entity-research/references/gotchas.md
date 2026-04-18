# 易错点与排查（持续迭代更新）

## 1) 搜索结果错配（Entity Mismatch）

### 常见表现
- 关键词属于某类实体，但结果指向同名的其他实体/品类页面。
- 结果列表第一条并不是你真正要的目标页。

### 快速排查
- 看 URL slug 是否包含目标名称。
- 看页面是否包含你配置的 content_root 或关键 anchor（例如 “Price / Specs / Rating History”）。

### 处理策略
- 候选多取：抓 Top-N（例如 5 条）再评分选最优。
- 评分维度：名称相似度 + slug 命中 + anchor 命中 + entity 类型（Entity vs Credit Summary）。
- 兜底：写 overrides（bank_name → canonical parent id / canonical url）。

## 2) 粘连文本导致数量不匹配

### 常见表现
- `18-Jul-202508-Apr-2025` 日期粘连。
- `dates != values`。

### 处理策略
- 先截取 Rating History 区块，再在 `Date : ... Rating : ... Action :` 的范围内提取。
- 保留 mismatch log（银行名+URL+counts），不停止运行。

## 3) 短期评级干扰

### 常见表现
- 页面里有多种“看起来像目标值”的字段，导致误填。

### 处理策略
- 把“口径选择规则”变成可配置的 parser.target_value_regex 或 anchor 截取规则。
- 必要时增加：对候选字段的黑名单/白名单。

## 4) Windows 写文件 PermissionError

### 常见表现
- Excel 打开了 xlsx，脚本写入失败。

### 处理策略
- 先写 CSV，再写 XLSX；XLSX 失败时提示用户关闭文件再跑。
