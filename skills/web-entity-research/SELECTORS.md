# 选择器（Selector）怎么找：给小白的 5 分钟说明

你要做的事：把“网页上那个按钮/输入框/结果列表/内容区域”的 CSS/XPath 选择器，填进 config.json 里对应的字段。

## 最常用的 3 个选择器字段

1) cookie_accept_selector  
- 用途：点掉 Cookie/隐私弹窗，避免挡住页面。
- 怎么找：页面弹窗上通常有 “Accept/Agree/OK/同意” 按钮。对按钮右键 → 检查（Inspect）→ 看它有没有稳定的 id / aria-label / 文本。

2) result_selector  
- 用途：从搜索结果页里抓“每条结果的链接”。
- 怎么找：在搜索结果列表里随便点一条标题链接 → 右键检查 → 观察它的 class（例如 `.search-result__title-link`）或是否是某个容器下的 `a` 标签。
- 经验：选择器尽量写得“只命中结果链接”，不要写太泛（例如 `a` 会抓到导航栏链接）。

3) content_root_selector（可选）
- 用途：在详情页只抓某个区域的文字（比如价格区域、参数表、评级历史表），避免抓全页噪音。
- 怎么找：在目标区域内任意文字上右键检查 → 选上层稳定容器（section/div）→ 用它的 id/class 作为 selector。

## 在浏览器里怎么拿到 selector（最简单做法）

1. 用 Chrome 打开目标网页
2. 右键你要抓取的元素 → Inspect（检查）
3. 在 Elements 面板中：
   - 右键该节点 → Copy → Copy selector（得到 CSS selector）
   - 或 Copy → Copy XPath（得到 XPath）

## 如何在 Playwright 里测试 selector 是否能命中

你可以先在 scraper.py 里把 content_root 设置成某个 selector，然后跑一条样本，看 scraped_data.csv 的 raw_content 是否只包含目标区域。

## 什么时候需要换 selector

- 网站改版、class 名变了、元素换成了 iframe/动态渲染
- 结果：脚本跑完但抓到空文本，或 note 显示 content_root_not_found
