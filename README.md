# 导演入门学习站

写给 Mark 的零基础「导演入门」多层级静态学习站：视听语言 → 剧本剧集 → 导演方法 → AI 影视创作。

内容改写自《导演入门学习路线》（基准日期 2026-10-12）。AI 工具信息以源文档为准，请以各官网最新信息为准。

## 如何本地打开

**最简单：**

1. 进入本文件夹 `director-learning-site`
2. 用浏览器打开（双击）`index.html`
3. 即可从首页进入各阶段；支持 `file://` 协议，无需安装服务器

**可选：本地小服务器（避免个别浏览器对本地文件的限制）：**

```bash
cd director-learning-site
python3 -m http.server 8080
```

浏览器访问：`http://127.0.0.1:8080/`

## 目录结构

```
director-learning-site/
├── index.html              # 首页总览
├── css/styles.css          # 统一样式（无外部 CDN）
├── js/nav.js               # 侧栏、主题切换、进度、回顶、术语搜索
├── README.md
├── stage1/                 # 阶段一：视听语言基础
├── stage2/                 # 阶段二：剧本与剧集创作
├── stage3/                 # 阶段三：导演工作方法
├── stage4/                 # 阶段四：AI 影视创作
├── lapian/                 # 每日逐帧：index.html、001.html，媒体在 lapian/001/
├── appendix/               # 术语速查、30 周进度表、书单片单
└── lapian_pages.py         # 把 lapian/NNN/ 收成页面
```

## 功能说明

- **侧栏导航**：四阶段折叠 + 附录；移动端点左上角 ☰
- **面包屑 / 上一章下一章 / 回首页**：每页齐全
- **深色 / 浅色**：右上角按钮切换（偏好记在本机）
- **阅读进度**：浏览过的页面记在浏览器 localStorage（仅本机）
- **术语速查**：附录页可搜索过滤
- **练习勾选**：各阶段练习清单勾选状态会保存在本机

## 设计说明

- 系统字体栈，无外部字体/CDN
- 正文最大阅读宽度约 700px，充足行高与边距
- 知识点结构：是什么 → 为什么 → 怎么用 → 练习
- 阶段强调色克制区分；专业术语旁附白话解释

## 重新生成（维护用）

若修改了 `_generate.py` 中的页面内容：

```bash
python3 _generate.py
```

日常学习只需打开 `index.html`，无需运行脚本。

## 如何增加一期「每日逐帧」

一期一个文件夹，期号三位数字。以第 002 期为例：

```
lapian/002/
├── meta.json          # date、title、tags、可选 nav
├── lesson.md          # 讲解正文，结构与 001 相同
├── narrated.mp4       # 带配音的成片，页面最上方播放
├── clip.mp4           # 无配音原片段
├── narration.srt      # 旁白字幕；生成时会写成 narration.vtt 供播放器轨道
├── script.txt         # 旁白稿，留在文件夹里备查
└── frame01.png …      # 静帧，lesson.md 里写 frame01、frame02…
```

`meta.json`：

```json
{
  "date": "2026-10-14",
  "title": "片名与这一期在讲什么",
  "tags": ["景别", "运镜"],
  "nav": "002 短标题"
}
```

`date` 必须是 `YYYY-MM-DD`。归档列表按日期新的在前。`tags` 是主题标签。`nav` 是侧栏里的短名字，不写就用期号加标题。

`lesson.md` 用这些二级标题，生成器认的就是这几个名字：

- `一句话看点`
- `逐镜头拆解`：每个镜头一行，格式为 `**① frame01：景别·内容**（片段 0:03）`，下面用 `- ` 写说明。静帧文件名对上 `frame01.png`。
- `10 分钟小练习（二选一）`
- `对应学习站章节`：写成 `- 景别与角度：https://sdxzy.github.io/director-learning/stage1/shot-size.html`，页面上会换成站内相对链接。
- `作品信息`：片源和授权，页面上放在「片源与授权」。
- `推荐延伸视频`

写完后在仓库根目录运行：

```bash
python3 _generate.py
```

会更新 `lapian/index.html`、`lapian/002.html`、侧栏、首页入口和搜索索引。媒体文件留在 `lapian/002/`，不要挪走。
