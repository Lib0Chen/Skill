# Skill Collection (Trae Skills)

这个仓库用来存放可复用的 Agent Skills（工具箱/流程模板/脚本）。

## 目录结构

- `skills/`：所有可发布的 skills（一个子文件夹 = 一个 skill）
  - `skills/<skill-name>/`：一个具体 skill
    - `SKILL.md`：Skill 说明与触发场景
    - `config.json`：站点/选择器/规则配置（通用化）
    - `scripts/`：可执行脚本（Searcher / Scraper / Parser）
    - `assets/`：模板文件
    - `references/`：SOP / 易错点 / 例子等

## 如何在某个项目里安装使用

Trae 会从“项目内”的 `.trae/skills/` 读取 skills。

所以使用步骤是：

1) 克隆本仓库（得到本地路径）
2) 把你要用的 skill 目录复制到目标项目的 `.trae/skills/` 下

示例（PowerShell）：

```powershell
Copy-Item -Recurse -Force "<本仓库>\skills\web-entity-research" "<你的项目>\.trae\skills\web-entity-research"
```

## 如何运行某个 skill

每个 skill 目录里都会有自己的 README（例如 `skills/web-entity-research/README.md`），里面写该 skill 的具体运行命令与配置方法。