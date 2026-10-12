#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the director learning static site."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent
TOTAL_PAGES = 36  # updated after defining all pages

# Page order for prev/next navigation: (rel_path, title, stage)
# rel_path is relative to site root
NAV_ORDER = []


def esc(s):
    return html.escape(s, quote=True)


def rel_prefix(depth):
    return "" if depth == 0 else "../" * depth


ICON_MENU = (
    '<svg class="icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
    '<path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round"/></svg>'
)
ICON_SEARCH = (
    '<svg class="icon" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">'
    '<circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/>'
    '<path d="M16 16l5 5" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round"/></svg>'
)
THEME_BOOT = """<script>
(function(){
  try {
    var s = localStorage.getItem("director-site-theme");
    var dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    var t = (s === "light" || s === "dark") ? s : (dark ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", t);
    document.documentElement.style.colorScheme = t;
  } catch (e) {}
})();
</script>
"""


def sidebar_html(depth, current):
    p = rel_prefix(depth)

    def link(href, label, cls=""):
        return f'<a href="{p}{href}" class="{cls}">{label}</a>'

    def group(stage_key, summary, links):
        opened = " open" if current.startswith(stage_key) else ""
        return (
            f'<details class="nav-group"{opened}>\n'
            f"    <summary>{summary}</summary>\n"
            f"    <div class=\"nav-group-links\">\n{links}\n    </div>\n"
            f"  </details>"
        )

    return f"""
<aside class="sidebar" id="sidebar">
  <nav class="sidebar-nav" aria-label="课程目录">
  <div class="sidebar-section">总览</div>
  {link("index.html", "首页", "stage-link")}
  <div class="sidebar-section">学习阶段</div>
  {group("stage1", "阶段一 · 视听语言", f'''    {link("stage1/index.html", "阶段概览")}
    {link("stage1/shot-size.html", "景别与角度", "sub-link")}
    {link("stage1/camera-movement.html", "运镜", "sub-link")}
    {link("stage1/composition.html", "构图", "sub-link")}
    {link("stage1/light-color.html", "光线与色彩", "sub-link")}
    {link("stage1/axis.html", "轴线与正反打", "sub-link")}
    {link("stage1/montage.html", "蒙太奇与剪辑", "sub-link")}
    {link("stage1/sound.html", "声音", "sub-link")}
    {link("stage1/practice.html", "练习与资源", "sub-link")}''')}
  {group("stage2", "阶段二 · 剧本与剧集", f'''    {link("stage2/index.html", "阶段概览")}
    {link("stage2/story-structure.html", "故事结构", "sub-link")}
    {link("stage2/character-conflict.html", "人物与冲突", "sub-link")}
    {link("stage2/scene-writing.html", "场景写作", "sub-link")}
    {link("stage2/series-hooks.html", "剧集弧线与钩子", "sub-link")}
    {link("stage2/shot-list.html", "分镜头脚本", "sub-link")}
    {link("stage2/practice.html", "练习与资源", "sub-link")}''')}
  {group("stage3", "阶段三 · 导演方法", f'''    {link("stage3/index.html", "阶段概览")}
    {link("stage3/workflow.html", "导演流程", "sub-link")}
    {link("stage3/blocking.html", "场面调度", "sub-link")}
    {link("stage3/directing-actors.html", "演员指导", "sub-link")}
    {link("stage3/storyboard.html", "故事板与机位", "sub-link")}
    {link("stage3/shooting-plan.html", "拍摄计划", "sub-link")}
    {link("stage3/practice.html", "练习与资源", "sub-link")}''')}
  {group("stage4", "阶段四 · AI 影视", f'''    {link("stage4/index.html", "阶段概览")}
    {link("stage4/tools-2026.html", "2026 工具现状", "sub-link")}
    {link("stage4/prompt-structure.html", "提示词结构", "sub-link")}
    {link("stage4/character-consistency.html", "角色一致性", "sub-link")}
    {link("stage4/short-film-workflow.html", "短片流程", "sub-link")}
    {link("stage4/compliance.html", "合规提醒", "sub-link")}
    {link("stage4/practice.html", "练习与资源", "sub-link")}''')}
  <div class="sidebar-section">附录</div>
  {link("appendix/glossary.html", "镜头术语速查")}
  {link("appendix/progress.html", "30 周进度表")}
  {link("appendix/resources.html", "推荐书单片单")}
  </nav>
  <div class="sidebar-foot" id="sidebar-progress"></div>
</aside>
<div class="sidebar-overlay" id="sidebar-overlay"></div>
"""


def breadcrumb(items, depth):
    """items: list of (label, href_or_None)"""
    p = rel_prefix(depth)
    parts = []
    for i, (label, href) in enumerate(items):
        if i > 0:
            parts.append('<span class="sep">/</span>')
        if href:
            parts.append(f'<a href="{p}{href}">{label}</a>')
        else:
            parts.append(f"<span>{label}</span>")
    return f'<nav class="breadcrumb" aria-label="面包屑">{" ".join(parts)}</nav>'


def chapter_nav(prev_info, next_info, depth):
    p = rel_prefix(depth)
    left = ""
    right = ""
    if prev_info:
        href, title = prev_info
        left = (
            f'<a href="{p}{href}" class="prev"><span class="label">← 上一章</span>'
            f'<span class="chapter-title">{esc(title)}</span></a>'
        )
    if next_info:
        href, title = next_info
        right = (
            f'<a href="{p}{href}" class="next"><span class="label">下一章 →</span>'
            f'<span class="chapter-title">{esc(title)}</span></a>'
        )
    return f'<nav class="chapter-nav" aria-label="上一页和下一页">{left}{right}</nav>'


def page_shell(
    title,
    body,
    depth,
    current,
    breadcrumbs,
    prev_info,
    next_info,
    page_id,
    stage="",
    extra_head="",
):
    p = rel_prefix(depth)
    stage_attr = f' data-stage="{stage}"' if stage else ""
    bc = breadcrumb(breadcrumbs, depth)
    nav = chapter_nav(prev_info, next_info, depth)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · 导演入门学习站</title>
<meta name="description" content="零基础导演入门：视听语言、剧本剧集、导演方法与 AI 影视创作">
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="{p}css/styles.css">
{THEME_BOOT}{extra_head}
</head>
<body data-page="{page_id}" data-total-pages="{TOTAL_PAGES}"{stage_attr}>
<a class="skip-link" href="#content">跳到正文</a>
<header class="site-header">
  <button class="btn-icon menu-toggle" id="menu-toggle" type="button" aria-label="打开菜单" aria-expanded="false" aria-controls="sidebar">{ICON_MENU}</button>
  <a class="brand" href="{p}index.html">导演入门</a>
  <button class="search-trigger" id="search-trigger" type="button" aria-label="搜索全站" aria-keyshortcuts="Control+K Meta+K">{ICON_SEARCH}<span class="search-trigger-label">搜索全站</span><kbd class="search-kbd" id="search-kbd">Ctrl K</kbd></button>
  <div class="header-actions">
    <button class="btn-icon" id="theme-toggle" type="button" aria-label="切换主题" title="切换主题">☾</button>
  </div>
  <div class="read-progress" aria-hidden="true"><span id="read-progress-fill"></span></div>
</header>
<div class="layout">
{sidebar_html(depth, current)}
<div class="doc-shell">
<div class="doc-column">
<main class="main" id="content">
{bc}
{body}
<div class="learn-card" id="learn-card">
  <label class="learn-check">
    <input type="checkbox" id="learn-complete">
    <span>
      <span class="learn-title">我已学完本页</span>
      <span class="learn-hint">只保存在这台浏览器里，并计入首页总进度</span>
    </span>
  </label>
</div>
{nav}
</main>
<footer class="site-footer">
  写给 Mark · 零基础导演入门 · 目标：AI 影视创作 · 内容基准日期 2026-10-12 · AI 工具请以官网为准
</footer>
</div>
<aside class="toc-aside" id="toc-aside">
  <details class="toc-details" id="toc-details">
    <summary>本页目录</summary>
    <nav class="toc-nav" aria-label="本页目录">
      <ol id="toc-list"></ol>
    </nav>
  </details>
</aside>
</div>
</div>
<button class="back-to-top" id="back-to-top" type="button" aria-label="回到顶部">顶部</button>
<script src="{p}js/search-index.js"></script>
<script src="{p}js/nav.js"></script>
</body>
</html>
"""


# ========== Content helpers ==========

def remember(text):
    return f'<div class="remember callout"><strong>一句话记住：</strong>{text}</div>'


def tip(text):
    return f'<div class="tip callout"><strong>小提示：</strong>{text}</div>'


def warning(text):
    return f'<div class="warning-box callout"><strong>注意：</strong>{text}</div>'


def example(title, content):
    return f'<div class="example"><div class="label">{title}</div>{content}</div>'


def section_4(what, why, how, practice=""):
    parts = [
        f"<h3>是什么</h3>\n{what}",
        f"<h3>为什么重要</h3>\n{why}",
        f"<h3>怎么用</h3>\n{how}",
    ]
    if practice:
        parts.append(f"<h3>练一练</h3>\n{practice}")
    return "\n".join(parts)


# ========== Define all pages ==========
# Each: id, path (relative to root), title, stage, breadcrumbs, body_fn or body_html

pages = []


def add(page_id, path, title, stage, crumbs, body):
    pages.append({
        "id": page_id,
        "path": path,
        "title": title,
        "stage": stage,
        "crumbs": crumbs,
        "body": body,
    })


# ----- INDEX -----
add(
    "home",
    "index.html",
    "首页",
    "",
    [("首页", None)],
    f"""
<div class="hero">
  <h1>导演入门学习站</h1>
  <p class="lead">写给 Mark：完全零基础，从「电影怎么说话」学到「怎么用 AI 拍电影」。重点是剧集创作与镜头拍摄，最终目标是成为 AI 视频生成导演。</p>
  <div class="progress-bar-wrap">
    <div class="progress-bar" id="progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" aria-label="学习进度"><span id="progress-bar-fill"></span></div>
    <p class="progress-text" id="progress-text">已学完 0 / 34 页</p>
  </div>
</div>

<h2>四阶段 · 约 30 周总览</h2>
<ol class="syllabus">
  <li>
    <p class="syllabus-kicker">阶段一 · 6–8 周</p>
    <p class="syllabus-title"><a href="stage1/index.html">视听语言基础</a></p>
    <p>看懂每个镜头「为什么这么拍」：景别、运镜、构图、光线、轴线、剪辑与声音。</p>
    <p class="meta">产出：对话戏小片 + 拉片表格</p>
    <ol class="lesson-index">
      <li><a href="stage1/shot-size.html">景别与角度</a></li>
      <li><a href="stage1/camera-movement.html">运镜</a></li>
      <li><a href="stage1/composition.html">构图</a></li>
      <li><a href="stage1/light-color.html">光线与色彩</a></li>
      <li><a href="stage1/axis.html">轴线与正反打</a></li>
      <li><a href="stage1/montage.html">蒙太奇与剪辑</a></li>
      <li><a href="stage1/sound.html">声音</a></li>
      <li><a href="stage1/practice.html">练习与资源</a></li>
    </ol>
  </li>
  <li>
    <p class="syllabus-kicker">阶段二 · 8–10 周</p>
    <p class="syllabus-title"><a href="stage2/index.html">剧本与剧集创作</a></p>
    <p>一句话梗概 → 结构 → 人物冲突 → 剧集钩子 → 分镜头脚本。</p>
    <p class="meta">产出：一集短剧剧本 + 分镜表</p>
    <ol class="lesson-index">
      <li><a href="stage2/story-structure.html">故事结构</a></li>
      <li><a href="stage2/character-conflict.html">人物与冲突</a></li>
      <li><a href="stage2/scene-writing.html">场景写作</a></li>
      <li><a href="stage2/series-hooks.html">剧集弧线与钩子</a></li>
      <li><a href="stage2/shot-list.html">分镜头脚本</a></li>
      <li><a href="stage2/practice.html">练习与资源</a></li>
    </ol>
  </li>
  <li>
    <p class="syllabus-kicker">阶段三 · 6–8 周</p>
    <p class="syllabus-title"><a href="stage3/index.html">导演工作方法</a></p>
    <p>流程、场面调度、指导演员、故事板、拍摄计划；手机实拍一场戏。</p>
    <p class="meta">产出：2–3 分钟实拍作品</p>
    <ol class="lesson-index">
      <li><a href="stage3/workflow.html">导演流程</a></li>
      <li><a href="stage3/blocking.html">场面调度</a></li>
      <li><a href="stage3/directing-actors.html">演员指导</a></li>
      <li><a href="stage3/storyboard.html">故事板与机位</a></li>
      <li><a href="stage3/shooting-plan.html">拍摄计划</a></li>
      <li><a href="stage3/practice.html">练习与资源</a></li>
    </ol>
  </li>
  <li>
    <p class="syllabus-kicker">阶段四 · 8–12 周</p>
    <p class="syllabus-title"><a href="stage4/index.html">AI 影视创作</a></p>
    <p>工具选型、提示词、角色一致性、短片全流程与合规；完成 AI 短片。</p>
    <p class="meta">产出：1–3 分钟角色一致短片</p>
    <ol class="lesson-index">
      <li><a href="stage4/tools-2026.html">2026 工具现状</a></li>
      <li><a href="stage4/prompt-structure.html">提示词结构</a></li>
      <li><a href="stage4/character-consistency.html">角色一致性</a></li>
      <li><a href="stage4/short-film-workflow.html">短片流程</a></li>
      <li><a href="stage4/compliance.html">合规提醒</a></li>
      <li><a href="stage4/practice.html">练习与资源</a></li>
    </ol>
  </li>
</ol>

<h2>核心思路</h2>
<p>先学「电影怎么说话」，再学「讲什么故事」，再学「怎么组织拍摄」，最后把这些全部翻译给 AI。</p>
<p>AI 能替你「拍」，但不能替你「导」——镜头该怎么切、演员什么情绪、观众什么时候该紧张，这些判断永远是导演的工作。所以前三个阶段不是可选项，而是 AI 导演的核心竞争力。</p>
{remember("工具会过时；镜头语言、故事和对人的理解不会。")}

<table>
  <thead><tr><th>阶段</th><th>建议周期</th><th>一句话目标</th></tr></thead>
  <tbody>
    <tr><td>视听语言</td><td>6–8 周</td><td>看懂每个镜头「为什么这么拍」</td></tr>
    <tr><td>剧本与剧集</td><td>8–10 周</td><td>写出一集完整短剧剧本 + 分镜头脚本</td></tr>
    <tr><td>导演方法</td><td>6–8 周</td><td>用手机独立拍出一场 2–3 分钟的戏</td></tr>
    <tr><td>AI 影视创作</td><td>8–12 周（持续）</td><td>用 AI 完成一部 1–3 分钟、角色一致的短片</td></tr>
  </tbody>
</table>

<h2>如何使用本站</h2>
<ol>
  <li><strong>按阶段顺序学</strong>：左侧目录可折叠各阶段，右侧是本页目录，页底有上一章 / 下一章。</li>
  <li><strong>每页结构固定</strong>：是什么 → 为什么 → 怎么用 → 练习；遇到术语会立刻白话解释。</li>
  <li><strong>边学边练</strong>：各阶段末有练习与资源；附录有术语速查、30 周进度表、书单片单。</li>
  <li><strong>本地打开即可</strong>：双击 <code>index.html</code>，无需服务器。顶栏可搜索全站（Ctrl 或 ⌘ 加 K），主题默认跟随系统。</li>
  <li><strong>进度会记在本机</strong>：勾选每页的「我已学完本页」，首页显示总进度（只存在这台浏览器，不上传）。</li>
</ol>

<h2>零基础学习习惯（贯穿全程）</h2>
<p>每周建议投入 <strong>8–12 小时</strong>，可按「3 看 + 3 学 + 3 练」：3 小时拉片、3 小时读书/看课、3 小时动手。</p>
<div class="habit-list">
  <div class="habit">
    <h3>1. 拉片</h3>
    <p>选一部片，逐镜头暂停，记录景别、角度、运镜、时长，以及「这个镜头想让我感受到什么」。这是导演最核心的自学方法。</p>
  </div>
  <div class="habit">
    <h3>2. 建「镜头库」</h3>
    <p>看到好镜头就截图存档，按景别 / 光线 / 情绪分类。到第四阶段，它会直接变成你给 AI 的参考图库。</p>
  </div>
  <div class="habit">
    <h3>3. 每周一个小作品</h3>
    <p>哪怕只有 30 秒。手机就够了，不要等「设备齐了再开始」。</p>
  </div>
</div>

{tip("推荐免费工具：手机 + 剪映 / CapCut（剪辑）、DaVinci Resolve 免费版（剪辑与调色）、Storyboarder（免费故事板）。")}

<h2>附录入口</h2>
<ul class="index-list">
  <li><a href="appendix/glossary.html">镜头术语中英速查</a><span>可搜索，按景别/运镜/剪辑/AI 等分类。</span></li>
  <li><a href="appendix/progress.html">30 周进度表</a><span>按周拆好的学习节奏，可自行调整。</span></li>
  <li><a href="appendix/resources.html">推荐书单与片单</a><span>四阶段书籍、课程、拉片片单汇总。</span></li>
</ul>
""",
)

# ----- STAGE 1 -----
add(
    "s1-index",
    "stage1/index.html",
    "阶段一：视听语言基础",
    "1",
    [("首页", "index.html"), ("阶段一", None)],
    f"""
<span class="badge s1">6–8 周</span>
<h1>阶段一：视听语言基础</h1>
<p class="lead">电影用画面和声音「说话」。这个阶段你要练的本事是：看到任意一个镜头，能说出它怎么拍的，以及为什么这样拍。</p>

<h2>学完你能做什么</h2>
<ul>
  <li>说出任意镜头的景别、角度、运镜，并解释情绪作用。</li>
  <li>理解剪辑如何制造意义：两个镜头放一起，会产生第三种意思。</li>
  <li>拍对话戏时不会「跳轴」。</li>
</ul>

{remember("越远越客观，越近越主观；运镜必须有动机。")}

<div class="toc">
  <h2>本章目录</h2>
  <ol>
    <li><a href="shot-size.html">景别与角度</a></li>
    <li><a href="camera-movement.html">运镜</a></li>
    <li><a href="composition.html">构图</a></li>
    <li><a href="light-color.html">光线与色彩</a></li>
    <li><a href="axis.html">轴线与正反打</a></li>
    <li><a href="montage.html">蒙太奇与剪辑</a></li>
    <li><a href="sound.html">声音</a></li>
    <li><a href="practice.html">本阶段练习与资源</a></li>
  </ol>
</div>
""",
)

add(
    "s1-shot",
    "stage1/shot-size.html",
    "景别与角度",
    "1",
    [("首页", "index.html"), ("阶段一", "stage1/index.html"), ("景别与角度", None)],
    f"""
<span class="badge s1">阶段一</span>
<h1>景别与角度</h1>
<p class="lead">景别回答「摄影机离人多远」；角度回答「从哪个方向和高度看」。两者一起决定观众和角色的心理距离。</p>

<h2>景别</h2>
{section_4(
    """<p>景别（Shot Size）就是画面里人物占多大——从「人像蚂蚁」到「只剩一只眼睛」。</p>
<ul>
  <li><strong>远景 / 大远景</strong>：交代环境，人很小。开场、孤独感常用。</li>
  <li><strong>全景</strong>：从头到脚完整入画，动作和空间都清楚。</li>
  <li><strong>中景</strong>：膝盖或腰部以上，最常用的「讲故事」距离。</li>
  <li><strong>近景</strong>：胸部以上，观众开始盯表情。</li>
  <li><strong>特写 / 大特写</strong>：脸或局部（眼睛、手、物件），情绪最强、信息最集中。</li>
</ul>""",
    """<p>换景别 = 换观众和角色的「亲密程度」。远景像旁观，特写像贴在脸上——导演用这个控制你什么时候冷静、什么时候心疼。</p>""",
    """<p>叙事节奏常见套路：先用远景/全景<strong>建立空间</strong>，中景<strong>推进情节</strong>，近景/特写<strong>砸情绪</strong>。对话戏里情绪升级时，景别往往会一寸寸推近。</p>""",
    """<p>用手机拍同一个人泡茶：远景、全景、中景、近景、特写各一条，剪成 30 秒，感受信息量变化。</p>""",
)}
{remember("越远越客观，越近越主观。")}

<h2>角度</h2>
{section_4(
    """<p>角度（Camera Angle）是摄影机相对人物的高度和方向。</p>
<ul>
  <li><strong>平视</strong>：中立、真实，像旁观者。</li>
  <li><strong>仰拍</strong>：从下往上——高大、威胁或力量。</li>
  <li><strong>俯拍</strong>：从上往下——渺小、无助、被控制。</li>
  <li><strong>顶拍（上帝视角）</strong>：正上方，强设计感或宿命感。</li>
  <li><strong>荷兰角</strong>：画面歪斜——不安、失衡、精神错乱。</li>
  <li><strong>主观镜头（POV）</strong>：观众「变成」角色，看到角色看到的。</li>
  <li><strong>过肩镜头（OTS）</strong>：越过一人肩膀拍另一人，对话戏标配。</li>
</ul>""",
    """<p>同一句台词，仰拍像宣战，俯拍像求饶。角度是最便宜、最有效的「权力关系」工具。</p>""",
    """<ul>
  <li>想表现强势角色：试仰拍或让他占画面上方。</li>
  <li>想表现脆弱：俯拍，或把他挤到画面边缘。</li>
  <li>对话戏：先用过肩建立两人关系，再用正反打切表情。</li>
</ul>""",
    """<p>拍同一个人说同一句话：仰、平、俯各一条，对比感觉差异。</p>""",
)}

{example("小例子", "<p>审讯戏：警察常被仰拍或占画面优势；嫌疑人俯拍或坐在暗处。不用台词，权力已经写在画面上。</p>")}
""",
)

add(
    "s1-move",
    "stage1/camera-movement.html",
    "运镜",
    "1",
    [("首页", "index.html"), ("阶段一", "stage1/index.html"), ("运镜", None)],
    f"""
<span class="badge s1">阶段一</span>
<h1>运镜</h1>
<p class="lead">运镜 = 摄影机怎么动。动得好，观众跟着情绪走；为动而动，只会晃得人烦。</p>

{section_4(
    """<ul>
  <li><strong>摇（Pan / Tilt）</strong>：机位不动，镜头左右摇或上下摇，像人转头看。</li>
  <li><strong>推 / 拉（Dolly in / out）</strong>：摄影机靠近或远离。推=聚焦、加压；拉=揭示环境、疏离。</li>
  <li><strong>移 / 跟（Tracking / Follow）</strong>：跟着人物平行移动或尾随。</li>
  <li><strong>升降（Crane / Jib）</strong>：上升或下降，开场结尾常有「宏大感」。</li>
  <li><strong>手持（Handheld）</strong>：晃、真、紧，纪实与动作戏常见。</li>
  <li><strong>稳定器 / 斯坦尼康</strong>：流畅穿过空间跟随人物。</li>
  <li><strong>变焦（Zoom）</strong>：机位不动只改焦距，感觉比「推」更人工。</li>
  <li><strong>希区柯克变焦（Dolly Zoom）</strong>：推拉与变焦反向，制造眩晕——世界塌了的感觉。</li>
</ul>""",
    """<p>静止镜头让人「看清楚」；运动镜头让人「被带着体验」。运镜是叙事节奏和沉浸感的油门。</p>""",
    f"""<p><strong>原则：运镜必须有动机</strong>——跟随人物、揭示信息、或表达情绪。写分镜或 AI 提示词时，先问自己：这个运动在帮观众得到什么？</p>
{example("对比", "<div class='compare'><div class='col bad'><h4>弱</h4><p>镜头随便推近，因为「看起来更电影」。</p></div><div class='col good'><h4>强</h4><p>她读完恐吓短信后镜头缓慢推近——观众被迫盯住她的恐惧。</p></div></div>")}""",
    """<p>同一段走路：固定、跟拍、手持各拍一次，剪在一起对比「客观 / 跟随 / 紧张」三种感觉。</p>""",
)}
{remember("运镜必须有动机——跟随、揭示、或表达情绪，不要为动而动。")}
""",
)

add(
    "s1-comp",
    "stage1/composition.html",
    "构图",
    "1",
    [("首页", "index.html"), ("阶段一", "stage1/index.html"), ("构图", None)],
    f"""
<span class="badge s1">阶段一</span>
<h1>构图</h1>
<p class="lead">构图 = 把画面里的东西摆在哪。好构图让观众一眼知道看谁、感受什么。</p>

{section_4(
    """<ul>
  <li><strong>三分法</strong>：画面横竖各分三份，人物或视线放在交叉点附近，自然稳。</li>
  <li><strong>引导线</strong>：道路、栏杆、走廊把视线引向主体。</li>
  <li><strong>前景 / 框架构图</strong>：门框、窗户、树枝「框住」人物——有层次，或「被困」感。</li>
  <li><strong>视线空间（Look room）</strong>：人看向哪边，哪边多留空，才不憋。</li>
  <li><strong>对称构图</strong>：庄重、秩序，或刻意「不真实」（如韦斯·安德森）。</li>
  <li><strong>负空间</strong>：大面积留白，突出孤独或压迫。</li>
</ul>""",
    """<p>构图是「无声的导演说明」。人贴边、头顶顶天、或被门框卡住——观众还没听台词，已经不安了。</p>""",
    """<ul>
  <li>对话：给说话者留视线空间；反应镜头同样注意。</li>
  <li>想拍孤独：人很小 + 大片负空间，或框架构图把人关起来。</li>
  <li>给 AI 写提示词时，可直接写：<em>rule of thirds、leading lines、framed by doorway、lots of negative space</em>。</li>
</ul>""",
    """<p>去 FILMGRAB 或你自己的镜头库，找 5 张剧照，用一句话写出它的构图手段和情绪。</p>""",
)}
{remember("构图先回答：观众第一眼该看哪里？第二眼该感受到什么？")}
""",
)

add(
    "s1-light",
    "stage1/light-color.html",
    "光线与色彩",
    "1",
    [("首页", "index.html"), ("阶段一", "stage1/index.html"), ("光线与色彩", None)],
    f"""
<span class="badge s1">阶段一</span>
<h1>光线与色彩</h1>
<p class="lead">光塑造立体感和氛围；颜色直接对情绪「说话」。AI 时代，这两样都要写进提示词。</p>

<h2>光线</h2>
{section_4(
    """<ul>
  <li><strong>三点布光</strong>：主光（Key）塑形、辅光（Fill）补阴影、轮廓光/背光（Back）把人从背景「抠」出来——所有布光的起点。</li>
  <li><strong>高调 vs 低调</strong>：高调亮、阴影少（喜剧、广告）；低调暗部多、反差大（悬疑、黑色电影）。</li>
  <li><strong>硬光 vs 柔光</strong>：硬光阴影锋利、戏剧强；柔光过渡软、自然温柔。</li>
  <li><strong>方向</strong>：顺光平；侧光有立体；逆光有轮廓和氛围；顶光/底光易诡异。</li>
  <li><strong>色温</strong>：暖光约 3200K（钨丝灯感）；冷光约 5600K（日光感）。</li>
  <li><strong>黄金时刻 / 蓝调时刻</strong>：日出后或日落前约 1 小时偏暖；日落后天空深蓝。</li>
</ul>""",
    """<p>《教父》顶光让眼睛陷进阴影——角色立刻显得危险。光不只是「看得见」，而是在写性格。</p>""",
    """<p>写提示词时写清<strong>方向 + 颜色</strong>，例如：「左侧冷蓝月光 + 右侧暖色烛光」。实拍时台灯就能练四种方向光。</p>""",
    """<p>一盏台灯，同一张脸：顺光、侧光、逆光、底光各拍一张，对比情绪。</p>""",
)}

<h2>色彩</h2>
{section_4(
    """<p>颜色会说话，但含义看上下文：红≈激情/危险，蓝≈冷静/忧郁，绿≈自然/病态，黄≈温暖/焦虑……</p>
<ul>
  <li><strong>互补色对比</strong>（如经典橙青）让人物从背景跳出来。</li>
  <li>一部片/剧通常有统一色彩方案；有时每条故事线各有颜色。</li>
</ul>""",
    """<p>统一色调 = 作品「身份证」。AI 短片若每镜色调乱跳，观众会觉得不是同一部片。</p>""",
    """<p>开拍或生成前先定 Mood board：3–5 张参考图钉死主色与风格词（如 desaturated teal-and-red）。</p>""",
    """<p>为你的短片选一对主辅色，写进分镜备注和提示词模板。</p>""",
)}
{remember("光写方向与软硬；色定方案后贯穿全片。")}
""",
)

add(
    "s1-axis",
    "stage1/axis.html",
    "轴线与正反打",
    "1",
    [("首页", "index.html"), ("阶段一", "stage1/index.html"), ("轴线与正反打", None)],
    f"""
<span class="badge s1">阶段一</span>
<h1>轴线与正反打</h1>
<p class="lead">对话戏拍砸，多半是「跳轴」或没有反应镜头。这两条规则学会，对话戏立刻像样。</p>

<h2>轴线规则（180 度规则）</h2>
{section_4(
    """<p>两个人对话时，在他们之间画一条假想线——叫<strong>轴线</strong>。摄影机始终待在线的<strong>同一侧</strong>，观众才不会搞乱「谁在左、谁在右」。</p>
<p>越过轴线叫<strong>跳轴</strong>，方向感会乱。合理越轴的办法包括：拍一个运动镜头跨过轴线；插入一个正好在轴线上的镜头；或让人物走动，自然改掉轴线。</p>""",
    """<p>观众大脑在默默建立空间地图。跳轴等于把地图撕了重画——出戏。</p>""",
    """<p>开拍前画一张<strong>俯视机位图</strong>：两人位置 + 轴线 + 所有机位都画在同一侧。给 AI 生成正反打时，同样要在提示词里固定左右关系。</p>""",
    """<p>找朋友拍 6–10 个镜头的两人对话；再故意拍一版跳轴，对比「晕不晕」。</p>""",
)}

<h2>正反打（Shot / Reverse Shot）</h2>
{section_4(
    """<p>对话戏基本拍法：先拍 A 说话（常用过肩），再反过来拍 B 回应，交替剪辑。</p>
<ul>
  <li>进阶：情绪升级时，景别从中景逐步推到近景、特写。</li>
  <li>别忘了<strong>反应镜头</strong>：听的人的脸，往往比说的人更有戏。</li>
</ul>""",
    """<p>观众靠正反打「在两人之间来回站」。反应镜头告诉观众：这句话伤到了谁、激怒了谁。</p>""",
    """<ol>
  <li>先拍主镜头（全景把整场演完）。</li>
  <li>再拍 A 过肩 / 近景覆盖。</li>
  <li>再拍 B 过肩 / 近景覆盖。</li>
  <li>补反应与插入镜头（手、手机、门等）。</li>
</ol>""",
    """<p>一场「表面聊晚饭、实际谈分手」的对话：至少含正反打 + 过肩 + 两个反应镜头。</p>""",
)}
{remember("摄影机待在轴线同一侧；反应镜头比台词更会演戏。")}
""",
)

add(
    "s1-montage",
    "stage1/montage.html",
    "蒙太奇与剪辑",
    "1",
    [("首页", "index.html"), ("阶段一", "stage1/index.html"), ("蒙太奇与剪辑", None)],
    f"""
<span class="badge s1">阶段一</span>
<h1>蒙太奇与剪辑</h1>
<p class="lead">单个镜头是词；剪辑是造句。意义往往不在某一个画面里，而在「接」出来的关系里。</p>

{section_4(
    """<ul>
  <li><strong>库里肖夫效应</strong>：同一张无表情的脸，接上汤 / 棺材 / 小孩，观众会分别「看出」饥饿、悲伤、慈爱——意义来自组接。</li>
  <li><strong>爱森斯坦蒙太奇</strong>：用镜头冲突碰撞制造思想与情绪（如《战舰波将金号》「敖德萨阶梯」）。</li>
  <li><strong>连续性剪辑</strong>：让人感觉不到剪辑——动作剪辑（Match on action）、视线匹配（Eyeline match）。</li>
  <li>常见手法：硬切、交叉剪辑（两条线平行推悬念）、匹配剪辑、跳切、J-cut / L-cut（声音先于或晚于画面）。</li>
  <li><strong>沃尔特·默奇剪辑六原则</strong>：情感 &gt; 故事 &gt; 节奏 &gt; 视线 &gt; 二维平面 &gt; 三维空间。<strong>情感永远第一。</strong></li>
</ul>""",
    """<p>你会剪，才知道该拍什么；你会拍，提示词才写得进「剪辑感」。AI 生成的是镜头素材，<strong>成片仍靠你剪</strong>。</p>""",
    """<ul>
  <li>剪对话：优先保住情绪点，再修轴线与动作连贯。</li>
  <li>需要悬念：试交叉剪辑——一边是主角开门，一边是另一空间的危险逼近。</li>
  <li>声音可提前进下一场（J-cut），转场更丝滑。</li>
</ul>""",
    """<p><strong>库里肖夫实验</strong>：拍一张面无表情特写，分别接三种画面，问朋友「他在想什么」。</p>""",
)}
{remember("意义来自镜头的组接；剪辑时情感永远排第一。")}
""",
)

add(
    "s1-sound",
    "stage1/sound.html",
    "声音",
    "1",
    [("首页", "index.html"), ("阶段一", "stage1/index.html"), ("声音", None)],
    f"""
<span class="badge s1">阶段一</span>
<h1>声音</h1>
<p class="lead">业内常说「声音占观感的一半」。画面外一声脚步，有时比看见人更吓人。AI 视频同样成立。</p>

{section_4(
    """<ul>
  <li>三大类：<strong>对白</strong>、<strong>音效</strong>（环境音、拟音）、<strong>音乐</strong>。</li>
  <li><strong>有源声音</strong>：画面内找得到声源（电视、脚步）。</li>
  <li><strong>无源声音</strong>：配乐、旁白——画外讲故事。</li>
  <li>声音能在画面外叙事：远处狗叫、门外脚步。</li>
  <li><strong>沉默</strong>是最强的声音之一。</li>
</ul>""",
    """<p>《现代启示录》开场几乎是声音设计课。没声音的「电影感」，多半是半成品。</p>""",
    """<ul>
  <li>剪辑时先听听节奏：该喘口气的地方，别塞满 BGM。</li>
  <li>写 AI 提示词可带声音层：雨声、远处电视、一声手机震动。</li>
  <li>对白优先干净；环境音铺底；音乐最后「点睛」而非从头糊满。</li>
</ul>""",
    """<p>给一段 30 秒画面做两个版本：只有环境音 vs 环境音+音乐，对比情绪差。</p>""",
)}
{remember("声音能在画外讲故事；适时的沉默比音乐更狠。")}
""",
)

add(
    "s1-practice",
    "stage1/practice.html",
    "阶段一：练习与资源",
    "1",
    [("首页", "index.html"), ("阶段一", "stage1/index.html"), ("练习与资源", None)],
    f"""
<span class="badge s1">阶段一</span>
<h1>练习与资源</h1>
<p class="lead">知识要变成肌肉记忆：拍、剪、拉片，三件事循环做。</p>

<h2>练习清单</h2>
<div class="checklist">
  <label><input type="checkbox" id="s1p1" data-key="s1p1"> <span><strong>景别练习</strong>：同一个人泡茶，远/全/中/近/特各一条，剪成 30 秒。</span></label>
  <label><input type="checkbox" id="s1p2" data-key="s1p2"> <span><strong>角度练习</strong>：仰/平/俯各配一句台词。</span></label>
  <label><input type="checkbox" id="s1p3" data-key="s1p3"> <span><strong>轴线练习</strong>：6–10 镜两人对话（正反打+过肩+反应），再拍一版跳轴对比。</span></label>
  <label><input type="checkbox" id="s1p4" data-key="s1p4"> <span><strong>库里肖夫实验</strong>：无表情特写接三种画面，做观众小测试。</span></label>
  <label><input type="checkbox" id="s1p5" data-key="s1p5"> <span><strong>拉片作业</strong>：选片单中一部，3 分钟段落逐镜头表格（镜号/时长/景别/角度/运镜/声音/作用）。</span></label>
  <label><input type="checkbox" id="s1p6" data-key="s1p6"> <span><strong>光线练习</strong>：一盏台灯，顺/侧/逆/底四种脸部光。</span></label>
</div>

<h2>优先阅读</h2>
<p>先读《镜头的语法》+《眨眼之间》；《电影语言的语法》《电影镜头设计》当工具书翻。</p>
<ul>
  <li>《镜头的语法》— 零基础最友好</li>
  <li>《眨眼之间》— 剪辑思维，薄而精</li>
  <li>《电影语言的语法》— 对话戏机位百科</li>
  <li>《认识电影》— 比《电影艺术》更好读的入门教材</li>
</ul>
<p>完整书单与片单见 <a href="../appendix/resources.html">附录：推荐书单片单</a>。</p>

<h2>拉片片单（阶段一重点）</h2>
<div class="table-wrap"><table>
<thead><tr><th>作品</th><th>重点看</th></tr></thead>
<tbody>
<tr><td>《战舰波将金号》</td><td>敖德萨阶梯：蒙太奇源头</td></tr>
<tr><td>《公民凯恩》</td><td>深焦、仰拍、低调光</td></tr>
<tr><td>《惊魂记》</td><td>浴室戏：短镜头制造恐惧</td></tr>
<tr><td>《教父》</td><td>顶光塑人；洗礼段交叉剪辑</td></tr>
<tr><td>《花样年华》</td><td>框架构图、色彩、音乐</td></tr>
<tr><td>《布达佩斯大饭店》</td><td>对称、色彩方案、平移</td></tr>
<tr><td>《爆裂鼓手》</td><td>剪辑节奏与声画配合</td></tr>
</tbody>
</table></div>

<h2>网上资源</h2>
<ul>
  <li>StudioBinder YouTube / 博客：镜头语言系统讲解</li>
  <li>Every Frame a Painting：经典视频散文（已停更，仍值得看）</li>
  <li>FILMGRAB：高清剧照库，研究构图光色</li>
  <li>B 站可搜「StudioBinder 中字」「Every Frame a Painting 中字」</li>
</ul>
""",
)

# ----- STAGE 2 -----
add(
    "s2-index",
    "stage2/index.html",
    "阶段二：剧本与剧集创作",
    "2",
    [("首页", "index.html"), ("阶段二", None)],
    f"""
<span class="badge s2">8–10 周</span>
<h1>阶段二：剧本与剧集创作</h1>
<p class="lead">你会「看镜头」之后，要学会「讲故事」。剧集和电影不一样：一集要有小满足，整季要有大悬念。</p>

<h2>学完你能做什么</h2>
<ul>
  <li>用一句话（logline）讲清故事，并展开成完整大纲。</li>
  <li>理解剧集节奏：冷开场、幕转折、结尾钩子。</li>
  <li>写出一集 10–15 分钟短剧（或竖屏短剧前 3 集），并改成有镜头的分镜表。</li>
</ul>

<div class="toc">
  <h2>本章目录</h2>
  <ol>
    <li><a href="story-structure.html">故事结构</a></li>
    <li><a href="character-conflict.html">人物与冲突</a></li>
    <li><a href="scene-writing.html">场景写作</a></li>
    <li><a href="series-hooks.html">剧集弧线与钩子</a></li>
    <li><a href="shot-list.html">分镜头脚本</a></li>
    <li><a href="practice.html">练习与资源</a></li>
  </ol>
</div>
""",
)

add(
    "s2-story",
    "stage2/story-structure.html",
    "故事结构",
    "2",
    [("首页", "index.html"), ("阶段二", "stage2/index.html"), ("故事结构", None)],
    f"""
<span class="badge s2">阶段二</span>
<h1>故事结构</h1>
<p class="lead">先能用一句话说清，再谈三幕和英雄之旅。结构是脚手架，不是监狱。</p>

<h2>一句话梗概（Logline）</h2>
{section_4(
    """<p>公式：<strong>一个（有特点的）主人公 + 想要什么 + 遇到什么阻碍 + 赌注是什么。</strong></p>""",
    """<p>写不出来 logline，通常是故事核心还糊。AI 短片选题也一样：一句话说不清，就别开工。</p>""",
    f"""{example("例子", "<p>一位患癌的高中化学老师，为了给家人留下钱，开始制毒，却一步步变成自己最恐惧的人。（《绝命毒师》）</p>")}
<p>每天写 3 条，坚持两周，你会明显感到「什么算一个故事」。</p>""",
    """<p>今天写下 3 条 logline，挑一条最想拍的留下来。</p>""",
)}

<h2>三幕剧结构</h2>
{section_4(
    """<ul>
  <li><strong>第一幕（约前 25%）建置</strong>：日常世界；激励事件打破平衡；主人公决定进入新局面。</li>
  <li><strong>第二幕（约中间 50%）对抗</strong>：追目标，阻碍升级；中点大转折；结尾掉进「最低谷」。</li>
  <li><strong>第三幕（约最后 25%）解决</strong>：最终选择 → 高潮 → 结局。</li>
</ul>""",
    """<p>观众需要「提问 → 越来越难 → 回答」。没结构的故事像散步，有结构的故事像登山。</p>""",
    f"""{remember("提出问题 → 把问题搞得越来越难 → 回答问题。")}
<p>《救猫咪》的「节拍表」是把三幕拆成可填空的检查点，零基础特别好用。</p>""",
    """<p>用救猫咪节拍表拆一部你熟的电影，只标 8–15 个关键节拍即可。</p>""",
)}

<h2>英雄之旅（简版）</h2>
<p>源自约瑟夫·坎贝尔，沃格勒整理为约 12 阶段：平凡世界 → 召唤 → 拒绝 → 导师 → 门槛 → 考验盟友敌人 → 深穴 → 磨难 → 奖赏 → 返回 → 复活 → 携药回归。</p>
<p>把它当<strong>检查清单</strong>：故事有没有成长感？而不是必须逐步打卡的公式。</p>
""",
)

add(
    "s2-char",
    "stage2/character-conflict.html",
    "人物与冲突",
    "2",
    [("首页", "index.html"), ("阶段二", "stage2/index.html"), ("人物与冲突", None)],
    f"""
<span class="badge s2">阶段二</span>
<h1>人物与冲突</h1>
<p class="lead">戏剧 = 冲突。没冲突的人物只是资料卡；有欲望和阻碍，戏才开始。</p>

<h2>人物塑造</h2>
{section_4(
    """<ul>
  <li><strong>欲望（Want）vs 需求（Need）</strong>：想要的外在目标，往往不是真正需要的内在成长。好故事：追「想要」时发现「需要」。</li>
  <li><strong>缺陷</strong>：完美的人没有戏。给弱点或执念。</li>
  <li><strong>人物弧光</strong>：从头到尾内心发生了什么变化。</li>
  <li><strong>Show, don't tell</strong>：别让角色说「我很善良」，让他在没人看见时帮一只流浪猫。</li>
</ul>""",
    """<p>观众追的是「人变了没有」。弧光清晰，剧集跨集才立得住——AI 短剧也同样。</p>""",
    """<p>每人写一页小传：欲望、需求、缺陷、秘密、说话方式。写对白前先读小传。</p>""",
    """<p>给你的主角写一页人物小传，并写一件「只做不说」的善良/残忍小事。</p>""",
)}

<h2>冲突三层</h2>
{section_4(
    """<ul>
  <li>内心冲突：与自己</li>
  <li>人际冲突：与他人</li>
  <li>外部冲突：与社会 / 环境 / 命运</li>
</ul>
<p>每场戏都问三句：<strong>谁想要什么？谁在阻止他？最后谁赢了？</strong></p>""",
    """<p>没有阻力的目标不是戏，是流水账。冲突升级，观众才肯往下看。</p>""",
    """<p>把你剧本里每场戏用一句话标出「欲望 vs 阻碍」。标不出来的场，考虑删或改。</p>""",
    """<p>写一场两人对话：表面在选晚饭，实际在谈分手——冲突藏在潜台词里。</p>""",
)}
{remember("每场戏：谁想要什么？谁在阻止？谁赢了？")}
""",
)

add(
    "s2-scene",
    "stage2/scene-writing.html",
    "场景写作",
    "2",
    [("首页", "index.html"), ("阶段二", "stage2/index.html"), ("场景写作", None)],
    f"""
<span class="badge s2">阶段二</span>
<h1>场景写作</h1>
<p class="lead">每场戏都是迷你故事：有开始、转折、结束；结尾时局面应和开头不同。</p>

{section_4(
    """<ul>
  <li><strong>晚进早出</strong>：尽量晚进入一场戏，尽量早离开——砍掉寒暄和收尾废话。</li>
  <li><strong>潜台词</strong>：人物很少直说真心；「说的」和「想的」落差最有戏。</li>
  <li><strong>剧本格式</strong>：场景标题（内/外景 · 地点 · 日/夜）→ 动作描述（只写看得见听得见的）→ 人物名 + 对白。</li>
</ul>""",
    """<p>场景是分镜与拍摄的最小砖块。场写不干净，后面分镜和 AI 提示词都会散。</p>""",
    f"""{example("转向", "<p>开头：两人和气讨论周末计划。结尾：其中一人把另一人的钥匙放回桌上——关系已经变了。中间可以一句分手都没说。</p>")}
<p>动作描述保持可拍摄：写「他握紧杯子指节发白」，别写「他内心非常崩溃」。</p>""",
    """<p>把一场 3 页对话砍到 1.5 页：删开场寒暄与重复句，只留转向前后。</p>""",
)}
{remember("晚进早出；结尾局面必须和开头不同。")}
""",
)

add(
    "s2-series",
    "stage2/series-hooks.html",
    "剧集弧线与钩子",
    "2",
    [("首页", "index.html"), ("阶段二", "stage2/index.html"), ("剧集弧线与钩子", None)],
    f"""
<span class="badge s2">阶段二</span>
<h1>剧集弧线与钩子</h1>
<p class="lead">电影吃一次满足；剧集要「这集爽 + 还想看下一集」。钩子是续命工具。</p>

{section_4(
    """<ul>
  <li><strong>集弧线 vs 季弧线</strong>：每集有小目标小结局；同时推进整季大问题。</li>
  <li><strong>钩子（Hook）</strong>：开场 1–3 分钟抓住人（冷开场 Cold Open）；集尾留悬念（Cliffhanger）。竖屏短剧更极端：开头约 3 秒要有冲突，每集 1–2 分钟内至少一个反转。</li>
  <li><strong>A / B / C 线</strong>：A 主线；B 副线（感情/配角）；C 轻松线或伏笔。多线交叉，主题呼应。</li>
  <li><strong>幕</strong>：美剧常 Teaser + 4–5 幕，每幕尾有小转折。</li>
  <li><strong>试播集 Pilot</strong>：建世界、让人迷上主角、抛出整季核心问题。</li>
  <li><strong>剧集圣经 Series Bible</strong>：世界观、人物小传、季规划——AI 创作时保一致性的好帮手。</li>
</ul>""",
    """<p>没有钩子的剧集会「看完就忘」。短剧市场里，前几秒留不住人等于没做。</p>""",
    """<p>拉一集剧：画时间轴，标 A/B/C 出现时段、每幕转折、结尾钩子。写自己的短剧时，先写集尾钩子再倒推。</p>""",
    """<p>为你的故事写：冷开场 5 句 + 集尾钩子 3 句 + A/B 线各一句话。</p>""",
)}

<div class="table-wrap"><table>
<thead><tr><th>作品</th><th>可学什么</th></tr></thead>
<tbody>
<tr><td>《绝命毒师》S1</td><td>试播集教科书；人物弧光</td></tr>
<tr><td>《切尔诺贝利》</td><td>限定剧季弧线；冷开场</td></tr>
<tr><td>《请回答 1988》</td><td>多线群像与情感钩子</td></tr>
<tr><td>《隐秘的角落》</td><td>国产悬疑节奏与集尾钩子</td></tr>
<tr><td>《黑镜》</td><td>单元剧：每集完整结构</td></tr>
</tbody>
</table></div>
{remember("每集给小满足，季线留大悬念；竖屏前 3 秒就要有冲突。")}
""",
)

add(
    "s2-shotlist",
    "stage2/shot-list.html",
    "分镜头脚本",
    "2",
    [("首页", "index.html"), ("阶段二", "stage2/index.html"), ("分镜头脚本", None)],
    f"""
<span class="badge s2">阶段二</span>
<h1>分镜头脚本</h1>
<p class="lead">分镜表把剧本「翻译」成镜头清单——连接编剧、实拍与 AI 生成的桥梁。</p>

{section_4(
    """<p>常见字段：<strong>镜号 | 景别 | 角度 | 运镜 | 画面内容 | 台词/声音 | 时长 | 备注</strong>（光线、情绪、道具）。</p>""",
    """<p>没有分镜，拍摄会漏覆盖；做 AI 短片时，没有分镜就只能「碰运气抽卡」。</p>""",
    f"""{example("示例片段", '''<div class="table-wrap"><table>
<thead><tr><th>镜号</th><th>景别</th><th>角度/运镜</th><th>画面</th><th>声音</th><th>时长</th></tr></thead>
<tbody>
<tr><td>1</td><td>大远景</td><td>平视/缓推</td><td>雨夜城中村巷口，霓虹闪烁</td><td>雨声、远处电视</td><td>4s</td></tr>
<tr><td>2</td><td>中景</td><td>手持跟拍</td><td>女主撑破伞快步进巷，不时回头</td><td>脚步、喘息</td><td>5s</td></tr>
<tr><td>3</td><td>特写</td><td>主观</td><td>手机屏幕：陌生短信「我看见你了」</td><td>震动</td><td>2s</td></tr>
<tr><td>4</td><td>近景</td><td>微仰/固定</td><td>她猛抬头，脸被霓虹照红</td><td>音乐骤停</td><td>2s</td></tr>
</tbody>
</table></div>''')}
<p>写的时候同步想：这个镜头在情绪链条上负责哪一环？能否用上一阶段的术语精确描述？</p>""",
    """<p>把剧本里最重要的一场戏改成至少 15 个镜头的分镜表。</p>""",
)}
{remember("分镜表 = 给摄影组（或 AI）的施工图，字段越专业结果越可控。")}
""",
)

add(
    "s2-practice",
    "stage2/practice.html",
    "阶段二：练习与资源",
    "2",
    [("首页", "index.html"), ("阶段二", "stage2/index.html"), ("练习与资源", None)],
    f"""
<span class="badge s2">阶段二</span>
<h1>练习与资源</h1>

<h2>练习清单</h2>
<div class="checklist">
  <label><input type="checkbox" id="s2p1"> <span>每天 3 条 logline，坚持 2 周，选出后续作品。</span></label>
  <label><input type="checkbox" id="s2p2"> <span>用救猫咪节拍表拆一部喜欢的电影。</span></label>
  <label><input type="checkbox" id="s2p3"> <span>写主要人物小传（欲望/需求/缺陷/秘密/说话方式）。</span></label>
  <label><input type="checkbox" id="s2p4"> <span>写一场潜台词对话：表面晚饭，实际分手。</span></label>
  <label><input type="checkbox" id="s2p5"> <span><strong>核心</strong>：一集 10–15 分钟短剧（或竖屏前 3 集），含 A/B 线、冷开场、结尾钩子。</span></label>
  <label><input type="checkbox" id="s2p6"> <span>最重要一场戏改成 ≥15 镜分镜表。</span></label>
</div>

<h2>优先阅读</h2>
<ul>
  <li>《救猫咪》— 零基础编剧首选</li>
  <li>《故事》（麦基）— 第二遍再精读</li>
  <li>《作家之旅》— 英雄之旅实操</li>
  <li>《电影剧本写作基础》（悉德·菲尔德）— 三幕经典表述</li>
  <li>Save the Cat! Writes for TV、Writing the TV Drama Series（英文，剧集向）</li>
</ul>
<p>拉剧片单与课程见 <a href="../appendix/resources.html">附录资源</a>。推荐：Lessons from the Screenplay、BBC Writersroom 剧本库、Script Slug。</p>
""",
)

# ----- STAGE 3 -----
add(
    "s3-index",
    "stage3/index.html",
    "阶段三：导演工作方法",
    "3",
    [("首页", "index.html"), ("阶段三", None)],
    f"""
<span class="badge s3">6–8 周</span>
<h1>阶段三：导演工作方法</h1>
<p class="lead">导演不只「有感觉」，而是能把感觉落成调度、表演指令和拍摄计划。这个阶段用手机把第二阶段的戏真正拍出来。</p>

<h2>学完你能做什么</h2>
<ul>
  <li>说清导演在前期 / 拍摄 / 后期各做什么。</li>
  <li>用场面调度和分镜规划一场戏，并能和演员有效沟通。</li>
  <li>用手机 + 朋友，拍完剪完一场 2–3 分钟的戏。</li>
</ul>

<div class="toc">
  <h2>本章目录</h2>
  <ol>
    <li><a href="workflow.html">导演流程</a></li>
    <li><a href="blocking.html">场面调度</a></li>
    <li><a href="directing-actors.html">演员指导</a></li>
    <li><a href="storyboard.html">故事板与机位</a></li>
    <li><a href="shooting-plan.html">拍摄计划</a></li>
    <li><a href="practice.html">练习与资源</a></li>
  </ol>
</div>
""",
)

add(
    "s3-workflow",
    "stage3/workflow.html",
    "导演流程",
    "3",
    [("首页", "index.html"), ("阶段三", "stage3/index.html"), ("导演流程", None)],
    f"""
<span class="badge s3">阶段三</span>
<h1>导演流程</h1>
<p class="lead">把「想拍」变成可执行步骤。流程清楚，现场才不会只剩救火。</p>

{section_4(
    """<ul>
  <li><strong>前期</strong>：读剧本 → 导演阐述（讲什么、什么风格）→ 视觉参考 Mood board → 分镜/故事板 → 选角排练 → 勘景 → 拍摄计划。</li>
  <li><strong>拍摄期</strong>：调度演员与摄影机，确保每场「拍到需要的东西」。</li>
  <li><strong>后期</strong>：与剪辑、声音、调色、配乐合作，完成作品。</li>
</ul>""",
    """<p>AI 短片也有几乎一样的前期：阐述、Mood board、分镜、角色设定——只是「摄影机」换成了生成模型。</p>""",
    """<p>开拍前至少产出三样：一页导演阐述、Mood board（5–10 张）、分镜或故事板。缺一样就先补，别急着按快门或点生成。</p>""",
    """<p>为你的核心场戏写一页导演阐述：主题一句、观众应有的情绪、风格参考列表。</p>""",
)}
{remember("前期想清楚，现场才拍得到；AI 亦然。")}
""",
)

add(
    "s3-blocking",
    "stage3/blocking.html",
    "场面调度",
    "3",
    [("首页", "index.html"), ("阶段三", "stage3/index.html"), ("场面调度", None)],
    f"""
<span class="badge s3">阶段三</span>
<h1>场面调度</h1>
<p class="lead">Mise-en-scène / Blocking：画面里的一切安排——人站哪、怎么走、机位在哪、布景道具怎么放。</p>

{section_4(
    """<p>核心思想：<strong>用空间关系表达人物关系</strong>。两人距离、谁站谁坐、谁在光里谁在影里、谁前景谁背景，都在讲故事。</p>
<ul>
  <li>走位要有动机：移动通常因为情绪或目的变了。</li>
  <li>两种思路：一个镜头内调度完（长镜头）vs 靠剪辑完成调度。</li>
</ul>""",
    """<p>《寄生虫》用楼梯上下写阶级；《十二怒汉》一个房间靠站位和镜头高度推进戏剧。调度是导演的空间语法。</p>""",
    """<p>排练时先定「关系站位」，再定走位路径，最后才定机位。画俯视图检查：空间关系是否一眼可读？</p>""",
    """<p>同一场争吵：第一版两人始终隔桌；第二版其中一人逼近又退开。对比权力如何变化。</p>""",
)}
{remember("空间关系 = 人物关系；人移动要有动机。")}
""",
)

add(
    "s3-actors",
    "stage3/directing-actors.html",
    "演员指导",
    "3",
    [("首页", "index.html"), ("阶段三", "stage3/index.html"), ("演员指导", None)],
    f"""
<span class="badge s3">阶段三</span>
<h1>演员指导</h1>
<p class="lead">给演员「可以演的指令」——动词和目的，而不是形容词和结果。这对写 AI 表演提示词同样关键。</p>

{section_4(
    f"""{example("指令对比", "<div class='compare'><div class='col bad'><h4>弱</h4><p>「这里你要更伤心一点。」</p></div><div class='col good'><h4>强</h4><p>「你想让他留下来，但你不能开口求他。」</p></div></div>")}
<p>每场戏帮演员搞清：我是谁、我想要什么、为什么现在要、什么在阻碍我。</p>
<ul>
  <li>先围读理解人物，再现场微调。</li>
  <li>保护安全感：先肯定做对的，再给一个具体调整。</li>
</ul>""",
    """<p>结果型形容词（「更悲伤」）让演员做表情；目的型指令让演员做人。观众感觉得到差别。</p>""",
    """<p>给 AI 写表演时同样写<strong>动作与意图变化</strong>：「从困惑变成恐惧，缓缓抬头望向镜头外」——不要只写「悲伤」。</p>""",
    """<p>请朋友演同一场：用两种不同「动词+目的」指令各拍一遍，对比哪版更真。</p>""",
)}
{remember("指令用动词和目的，不用形容词和结果。")}
""",
)

add(
    "s3-board",
    "stage3/storyboard.html",
    "故事板与机位",
    "3",
    [("首页", "index.html"), ("阶段三", "stage3/index.html"), ("故事板与机位", None)],
    f"""
<span class="badge s3">阶段三</span>
<h1>故事板与机位</h1>
<p class="lead">画得丑没关系。火柴人 + 箭头，就能提前看见成片；俯视图能救命般避免跳轴。</p>

{section_4(
    """<ul>
  <li><strong>故事板 Storyboard</strong>：每镜简笔画面，箭头表示运动。</li>
  <li><strong>俯视机位图 Floor plan</strong>：从上往下画人物、走位、摄影机，对照轴线。</li>
  <li><strong>动态预演 Animatic</strong>：故事板按时长剪好，配临时声，先「看」节奏。AI 时代可用关键帧直接做这一步。</li>
</ul>""",
    """<p>脑子里的电影往往过于完美。画出来才知道少镜头、缺覆盖、节奏拖。</p>""",
    """<p>工具：Storyboarder（免费开源）、Shot Designer（俯视图，有免费版）。不会画画就用几何块 + 箭头。</p>""",
    """<p>为第二阶段核心戏画故事板 + 一张俯视机位图。</p>""",
)}
{remember("先画后拍（或先关键帧后生成）；俯视图检查轴线。")}
""",
)

add(
    "s3-plan",
    "stage3/shooting-plan.html",
    "拍摄计划",
    "3",
    [("首页", "index.html"), ("阶段三", "stage3/index.html"), ("拍摄计划", None)],
    f"""
<span class="badge s3">阶段三</span>
<h1>拍摄计划</h1>
<p class="lead">拍摄不按剧本顺序，而按场景 / 地点 / 演员档期集中拍。计划是为了少加班、少漏镜。</p>

{section_4(
    """<ul>
  <li>常用文件：分镜表 Shot list、拍摄日程 Shooting schedule、通告单 Call sheet、场记单。</li>
  <li><strong>覆盖 Coverage</strong>：先拍主镜头（全景把整场演完），再拍中景、近景、反应，保证剪辑有料。</li>
  <li>预留时间与 B 计划：天气、光线、演员状态都会出事。</li>
</ul>""",
    """<p>业余团队最常见死因不是没创意，而是当天发现「反应镜头没拍」。覆盖原则就是保险。</p>""",
    """<p>把分镜表按地点重组拍摄顺序；标出必拍镜（没它剪不动）与可砍镜。AI 流程里，「必拍」=必须生成成功的关键叙事镜。</p>""",
    """<p>做一版简单通告单：集合时间、地点、演员、设备、当日镜号列表。</p>""",
)}
{remember("先主镜头，再覆盖；必拍镜优先，留 B 计划。")}
""",
)

add(
    "s3-practice",
    "stage3/practice.html",
    "阶段三：练习与资源",
    "3",
    [("首页", "index.html"), ("阶段三", "stage3/index.html"), ("练习与资源", None)],
    f"""
<span class="badge s3">阶段三</span>
<h1>练习与资源</h1>

<div class="checklist">
  <label><input type="checkbox" id="s3p1"> <span>核心戏：故事板（火柴人即可）+ 俯视机位图。</span></label>
  <label><input type="checkbox" id="s3p2"> <span>一页导演阐述 + 5–10 张视觉参考。</span></label>
  <label><input type="checkbox" id="s3p3"> <span>用「动词+目的」指导朋友，两版指令对比。</span></label>
  <label><input type="checkbox" id="s3p4"> <span>分镜表 + 简单通告单。</span></label>
  <label><input type="checkbox" id="s3p5"> <span><strong>核心</strong>：手机拍完剪完 2–3 分钟戏（主镜头+覆盖），配声音音乐。</span></label>
  <label><input type="checkbox" id="s3p6"> <span>复盘：成片 vs 故事板，写下差异与原因。</span></label>
</div>

<h2>优先阅读与工具</h2>
<ul>
  <li>Making Movies（吕美特）、On Directing Film /《导演功课》（马麦特）、Directing Actors（韦斯顿）</li>
  <li>《电影镜头设计》调度与故事板章节、《希区柯克与特吕弗对话录》</li>
  <li>工具：Storyboarder、Shot Designer、StudioBinder、Celtx</li>
</ul>
<p>拉片：《十二怒汉》《好家伙》科帕卡巴纳长镜、《寄生虫》《婚姻故事》争吵戏等，详见附录。</p>
""",
)

# ----- STAGE 4 -----
add(
    "s4-index",
    "stage4/index.html",
    "阶段四：AI 影视创作",
    "4",
    [("首页", "index.html"), ("阶段四", None)],
    f"""
<span class="badge s4">8–12 周 · 持续迭代</span>
<h1>阶段四：AI 影视创作</h1>
<p class="lead">把前三阶段的镜头语言、故事和导演判断，翻译成提示词与工作流。学方法，别死记某个按钮。</p>

{warning("OpenAI 的 Sora 已停止服务（网页/App 于 2026-04-26 下线，API 于 2026-09-24 停止）。大量旧「Sora 教程」已过时，不要再投入学习时间。以下工具信息以源文档 2026-10 核实为准，请以各官网最新信息为准。")}

<h2>学完你能做什么</h2>
<ul>
  <li>了解 2026 主流 AI 视频/图像工具特点，熟练 2–3 个。</li>
  <li>把镜头语言准确写进提示词。</li>
  <li>掌握角色一致性，完成 1–3 分钟、多镜头、有声音的 AI 短片。</li>
</ul>

<div class="toc">
  <h2>本章目录</h2>
  <ol>
    <li><a href="tools-2026.html">2026 工具现状</a></li>
    <li><a href="prompt-structure.html">提示词结构</a></li>
    <li><a href="character-consistency.html">角色一致性</a></li>
    <li><a href="short-film-workflow.html">短片流程</a></li>
    <li><a href="compliance.html">合规提醒</a></li>
    <li><a href="practice.html">练习与资源</a></li>
  </ol>
</div>
""",
)

add(
    "s4-tools",
    "stage4/tools-2026.html",
    "2026 工具现状",
    "4",
    [("首页", "index.html"), ("阶段四", "stage4/index.html"), ("2026 工具现状", None)],
    f"""
<span class="badge s4">阶段四</span>
<h1>2026 工具现状</h1>
<p class="lead">版本几乎每 1–3 个月大变。选工具看「控制力与场景」，学可迁移的方法。</p>

{warning("Sora 已停服。不要在过时教程上浪费时间。")}

<h2>主流 AI 视频工具（截至 2026.10）</h2>
<div class="table-wrap"><table>
<thead><tr><th>工具</th><th>公司</th><th>主力版本</th><th>特点与适用</th></tr></thead>
<tbody>
<tr><td><strong>即梦 AI</strong>（Seedance）</td><td>字节</td><td>Seedance 2.5（2026-07-31）；2.0 仍常用</td><td>多模态参考、自动分镜与多镜头、音画同步；2.5 单次最长约 30 秒。国内短剧广告常用。jimeng.jianying.com</td></tr>
<tr><td><strong>可灵 Kling</strong></td><td>快手</td><td>Kling 3.0（含 Omni）为主；4.0 于 2026-09-30 发布，4.0 Flash 小范围，完整版 10 月逐步开放</td><td>电影质感、表情动作强；3.0 最高约 4K、约 3–15 秒；4.0 宣称单次 30 秒、多关键帧。klingai.kuaishou.com / app.klingai.com</td></tr>
<tr><td><strong>海螺 Hailuo</strong></td><td>MiniMax</td><td>Hailuo 2.3；2026-07 推出 MiniMax H3（Hailuo 3.0）</td><td>写实、3D/舞蹈动作出色，性价比高，适合试错；多镜头叙事相对弱。hailuoai.com</td></tr>
<tr><td><strong>Veo + Flow</strong></td><td>Google</td><td>Veo 3.1（Lite/Fast/标准）</td><td>长复杂提示词、原生音频、参考图保角色；Flow 管理镜头场景。deepmind.google/models/veo · labs.google/flow</td></tr>
<tr><td><strong>Runway</strong></td><td>Runway</td><td>Gen-4.5</td><td>@参考保一致、关键帧、视频转视频；Aleph 编辑、Act-Two 表演驱动。runwayml.com</td></tr>
<tr><td><strong>通义万相 Wan</strong></td><td>阿里</td><td>Wan 3.0（2026-08）</td><td>约 30 秒、原生 1080p、音画同步；旧版 2.1/2.2 可开源本地。tongyi.aliyun.com/wanxiang</td></tr>
<tr><td><strong>Vidu</strong></td><td>生数</td><td>Vidu Q 系列</td><td>国产第一梯队；参考生视频（多主体一致）是特色。vidu.cn</td></tr>
</tbody>
</table></div>

<h2>图像工具（角色/关键帧/分镜预演）</h2>
<ul>
  <li>即梦图片（Seedream）、可灵图片：中文友好</li>
  <li>Google Nano Banana 系列（Gemini 图像，可用于 Gemini/Flow）：参考图一致与局部改</li>
  <li>Midjourney V8：电影感与美术风格强，适合概念图</li>
  <li>OpenAI GPT Image（ChatGPT 内）：提示词理解准、编辑方便</li>
</ul>

<h2>怎么选（初学者）</h2>
<ol>
  <li>先选 <strong>1 个国产</strong>（即梦或可灵）+ <strong>1 个国际</strong>（Veo/Flow 或 Runway）深入，其他了解即可。</li>
  <li>学方法 &gt; 学按钮位置。</li>
  <li>先用免费额度/低价快速版试错，镜头定了再用高质量出片。</li>
</ol>
{remember("先 1 国产 + 1 国际吃透；方法比版本号重要。")}
""",
)

add(
    "s4-prompt",
    "stage4/prompt-structure.html",
    "提示词结构",
    "4",
    [("首页", "index.html"), ("阶段四", "stage4/index.html"), ("提示词结构", None)],
    f"""
<span class="badge s4">阶段四</span>
<h1>提示词结构</h1>
<p class="lead">把 AI 想成「听话但缺判断的摄影组」。信息越像专业分镜表，结果越可控。</p>

{section_4(
    """<p>通用结构（一个镜头 = 一条提示词）：</p>
<div class="prompt-block">[景别 + 角度] + [主体与外观] + [动作/表演] + [场景环境] + [光线] + [运镜] + [风格/色调/镜头质感] + [声音]</div>""",
    """<p>前三阶段的术语，在这里全部变现。不会说 dolly in / OTS / low-key，就只能得到「随机好看」。</p>""",
    f"""{example("中文示例", '''<div class="prompt-block">近景，轻微仰拍。一位 30 岁左右的短发女人，穿湿透的米色风衣，站在雨夜的城中村巷口。她握着手机，先低头看屏幕，然后缓缓抬头望向镜头外，眼神从困惑变成恐惧。红色霓虹灯从画面左侧打在她脸上，背景虚化，有雨丝。镜头缓慢推近至特写。电影感，35mm 胶片质感，低饱和、红青色调。声音：雨声，远处电视嘈杂声，最后一声手机震动。</div>''')}
{example("英文示例（国际工具往往更稳）", '''<div class="prompt-block">Medium close-up, low angle. A woman in her 30s with short hair and a soaked beige trench coat stands at the mouth of a narrow alley on a rainy night. She looks down at her phone, then slowly raises her eyes off-screen; her expression shifts from confusion to fear. Red neon light from frame left, shallow depth of field, rain streaks in the background. Slow dolly-in to a close-up. Cinematic, 35mm film grain, desaturated teal-and-red palette. Audio: heavy rain, distant TV chatter, a single phone buzz.</div>''')}
<ul>
  <li><strong>一镜一事</strong>：一个主动作 + 一种运镜，动作太多易崩。</li>
  <li><strong>用专业术语</strong>：dolly in、tracking、OTS、shallow depth of field 等。</li>
  <li><strong>表演写变化与意图</strong>：从……变成……</li>
  <li><strong>光线写方向和颜色</strong></li>
  <li><strong>控制时长</strong>：多数 5–15 秒，部分可达约 30 秒</li>
  <li><strong>先图后视频</strong>：首帧/首尾帧可控性更高</li>
  <li><strong>多镜头模式</strong>：即梦 Seedance、可灵等可在一条里写镜头 1、镜头 2…</li>
</ul>
<p>官方指南建议精读，如 Google Veo 提示词指南（Vertex AI 文档）。</p>""",
    """<p>用本页示例提示词，在 2–3 个工具各生成一次，记录画质、人物、运镜、成本差异。</p>""",
)}
{remember("一镜一事；术语 + 光色方向 + 表演变化 = 可控提示词。")}
""",
)

add(
    "s4-consistency",
    "stage4/character-consistency.html",
    "角色一致性",
    "4",
    [("首页", "index.html"), ("阶段四", "stage4/index.html"), ("角色一致性", None)],
    f"""
<span class="badge s4">阶段四</span>
<h1>角色一致性</h1>
<p class="lead">观众最容易出戏的一点：下一镜主角的脸变了。剧集向创作，这是核心难题。</p>

{section_4(
    """<ol>
  <li><strong>角色设定图 Character sheet</strong>：正面清晰、光均匀、表情中性的定妆照 + 正/侧/背 + 全身。</li>
  <li><strong>参考功能</strong>：Runway @参考、即梦/可灵多图参考、Veo 3.1 参考图、Vidu 参考生视频。</li>
  <li><strong>固定描述词</strong>：发型、服装、年龄、特征写成一段，每次原样复制。</li>
  <li><strong>服装道具锁定</strong>：一场戏内少改变量。</li>
  <li><strong>场景参考图</strong>：主场景也做参考，跨机位复用。</li>
  <li><strong>先图后视频</strong>：关键帧先一致，再转视频，比直接文生视频稳。</li>
  <li><strong>后期修补</strong>：局部重绘、视频编辑工具修最刺眼的不一致。</li>
</ol>""",
    """<p>没有一致性，就没有「同一部剧」。这比单镜炫更重要。</p>""",
    """<p>开工模板：角色设定文件夹 + 固定外貌段落 + 场景参考 + 分镜表里标注「必须吃参考」的镜头。</p>""",
    """<p>为主角做正/侧/背 + 3 种表情，并在 5 个不同场景测试是否像同一个人。</p>""",
)}
{remember("先定妆与参考图，再生成；先图后视频更稳。")}
""",
)


add(
    "s4-workflow",
    "stage4/short-film-workflow.html",
    "短片流程",
    "4",
    [("首页", "index.html"), ("阶段四", "stage4/index.html"), ("短片流程", None)],
    f"""
<span class="badge s4">阶段四</span>
<h1>AI 短片制作流程</h1>
<p class="lead">把四个阶段串成一条流水线。初学建议：1–3 分钟、1–2 角色、1–3 场景。</p>

<div class="structure-flow">
  <div class="step"><span class="step-num">1</span><div><strong>创意与剧本</strong>（阶段二）：logline → 大纲 → 剧本</div></div>
  <div class="step"><span class="step-num">2</span><div><strong>视觉开发</strong>：Mood board；图像工具出角色/场景设定</div></div>
  <div class="step"><span class="step-num">3</span><div><strong>分镜头脚本</strong>（阶段一/二）：景别、角度、运镜、动作、时长</div></div>
  <div class="step"><span class="step-num">4</span><div><strong>关键帧生成</strong>：每镜首帧（必要时尾帧），查人物与构图</div></div>
  <div class="step"><span class="step-num">5</span><div><strong>视频生成</strong>：图生/参考生视频；每镜 3–5 版「抽卡」，记录有效提示词</div></div>
  <div class="step"><span class="step-num">6</span><div><strong>声音</strong>：对白（原生或 AI 配音）、音效、配乐；注意口型</div></div>
  <div class="step"><span class="step-num">7</span><div><strong>剪辑</strong>（阶段一原理）：剪映 / DaVinci Resolve 按分镜剪，补生成缺失镜</div></div>
  <div class="step"><span class="step-num">8</span><div><strong>调色与包装</strong>：统一色调、字幕、片头片尾</div></div>
  <div class="step"><span class="step-num">9</span><div><strong>复盘与发布</strong>：记录生成次数与问题，积累提示词库</div></div>
</div>
{remember("短片是导演流程的压缩版：剧本 → 视觉 → 分镜 → 生成 → 声音 → 剪辑。")}
""",
)

add(
    "s4-compliance",
    "stage4/compliance.html",
    "合规提醒",
    "4",
    [("首页", "index.html"), ("阶段四", "stage4/index.html"), ("合规提醒", None)],
    f"""
<span class="badge s4">阶段四</span>
<h1>合规提醒</h1>
<p class="lead">能生成，不代表能随便发、随便商用。提前避开坑，比事后删片省事。</p>

{section_4(
    """<ul>
  <li>不要用真实公众人物肖像，或受版权保护的角色与商标做「假乱真」内容。</li>
  <li>看清各平台<strong>商用授权</strong>条款：免费额度、订阅档、素材版权范围可能不同。</li>
  <li>国内平台发布 AI 生成内容，通常需按规定标注「AI 生成」。</li>
  <li>涉及深度伪造、诽谤、诈骗用途的内容既违法也不道德——本路线只服务创作学习。</li>
</ul>""",
    """<p>合规是持续创作的前提。账号与作品被平台处理，往往比「少一个特效」损失更大。</p>""",
    """<ul>
  <li>发布前核对：人物是否虚构、音乐是否有授权、平台是否要求 AI 标注。</li>
  <li>商用项目单独确认工具的商业许可与素材来源。</li>
  <li>剧集圣经与角色设定尽量原创，避免「擦边」知名 IP。</li>
</ul>""",
    """<p>列出你常用 2 个工具的商用条款要点（能否商用、是否需署名/标注），存进项目笔记。</p>""",
)}
{warning("工具与法规都在变，发布前以平台规则与当地法律为准。")}
""",
)

add(
    "s4-practice",
    "stage4/practice.html",
    "阶段四：练习与资源",
    "4",
    [("首页", "index.html"), ("阶段四", "stage4/index.html"), ("练习与资源", None)],
    f"""
<span class="badge s4">阶段四</span>
<h1>练习与资源</h1>

<div class="checklist">
  <label><input type="checkbox" id="s4p1"> <span><strong>工具对比</strong>：同一提示词在 2–3 个工具生成，记效果/速度/成本。</span></label>
  <label><input type="checkbox" id="s4p2"> <span><strong>景别运镜复刻</strong>：从镜头库挑 10 个经典镜头，用 AI 复刻。</span></label>
  <label><input type="checkbox" id="s4p3"> <span><strong>角色设定</strong>：正/侧/背 + 3 表情，5 场景测一致性。</span></label>
  <label><input type="checkbox" id="s4p4"> <span><strong>正反打挑战</strong>：两人对话 ≥6 镜，查跳轴与人物一致。</span></label>
  <label><input type="checkbox" id="s4p5"> <span><strong>核心</strong>：第二阶段剧本做成 1–3 分钟 AI 短片，走完全流程。</span></label>
  <label><input type="checkbox" id="s4p6"> <span><strong>进阶</strong>：3–5 集竖屏短剧（每集约 1 分钟），练钩子与跨集一致。</span></label>
</div>

<h2>学习资源</h2>
<ul>
  <li>Runway Academy（官方免费教程）</li>
  <li>Runway AI Film Festival（AIFF）：最好的 AI 拉片片单</li>
  <li>Google Flow 作品与 Veo 官方提示词指南</li>
  <li>即梦 Seedance 官方项目页与示例</li>
  <li>Curious Refuge（英文付费 AI 电影课程）</li>
  <li>各平台作品广场：看别人作品与公开提示词</li>
</ul>
{tip("最后提醒：工具会过时；镜头语言、故事和对人的理解不会。AI 导演真正稀缺的是「知道要什么，并能精确说出来」。")}
""",
)

# ----- APPENDIX -----
add(
    "app-glossary",
    "appendix/glossary.html",
    "镜头术语中英速查",
    "",
    [("首页", "index.html"), ("术语速查", None)],
    """
<h1>镜头术语中英速查表</h1>
<p class="lead">写分镜和 AI 提示词时随手查。可用下方搜索过滤；也可点分类锚点跳转。</p>
<input type="search" id="glossary-search" class="search-box" placeholder="搜索中文、英文或缩写…" autocomplete="off">
<nav class="glossary-nav">
  <a href="#shot-size">景别</a>
  <a href="#angle">角度</a>
  <a href="#movement">运镜</a>
  <a href="#comp-light">构图镜头光线</a>
  <a href="#editing">剪辑叙事制作</a>
  <a href="#ai-terms">AI 视频</a>
</nav>

<h2 id="shot-size">景别 Shot Size</h2>
<div class="table-wrap"><table>
<thead><tr><th>中文</th><th>英文</th><th>缩写</th><th>说明</th></tr></thead>
<tbody>
<tr class="term-row"><td>大远景</td><td>Extreme Wide / Extreme Long Shot</td><td>EWS / ELS</td><td>宏大环境，人物极小</td></tr>
<tr class="term-row"><td>远景</td><td>Wide Shot / Long Shot</td><td>WS / LS</td><td>交代环境与人物位置</td></tr>
<tr class="term-row"><td>全景</td><td>Full Shot</td><td>FS</td><td>从头到脚完整入画</td></tr>
<tr class="term-row"><td>中全景</td><td>Medium Full / Cowboy Shot</td><td>MFS</td><td>膝盖以上</td></tr>
<tr class="term-row"><td>中景</td><td>Medium Shot</td><td>MS</td><td>腰部以上</td></tr>
<tr class="term-row"><td>近景</td><td>Medium Close-Up</td><td>MCU</td><td>胸部以上</td></tr>
<tr class="term-row"><td>特写</td><td>Close-Up</td><td>CU</td><td>脸部</td></tr>
<tr class="term-row"><td>大特写</td><td>Extreme Close-Up</td><td>ECU</td><td>眼睛、嘴唇等局部</td></tr>
<tr class="term-row"><td>插入镜头</td><td>Insert Shot</td><td>—</td><td>物件特写</td></tr>
<tr class="term-row"><td>双人镜头</td><td>Two Shot</td><td>—</td><td>同一画面两人</td></tr>
<tr class="term-row"><td>建立镜头</td><td>Establishing Shot</td><td>—</td><td>场景开头交代地点</td></tr>
</tbody></table></div>

<h2 id="angle">角度 Camera Angle</h2>
<div class="table-wrap"><table>
<thead><tr><th>中文</th><th>英文</th><th>说明</th></tr></thead>
<tbody>
<tr class="term-row"><td>平视</td><td>Eye Level</td><td>中立、客观</td></tr>
<tr class="term-row"><td>仰拍</td><td>Low Angle</td><td>高大、有力</td></tr>
<tr class="term-row"><td>俯拍</td><td>High Angle</td><td>渺小、无助</td></tr>
<tr class="term-row"><td>顶拍 / 鸟瞰</td><td>Overhead / Bird's-Eye</td><td>正上方垂直向下</td></tr>
<tr class="term-row"><td>虫视</td><td>Worm's-Eye View</td><td>极低角度向上</td></tr>
<tr class="term-row"><td>荷兰角</td><td>Dutch Angle / Dutch Tilt</td><td>不安、失衡</td></tr>
<tr class="term-row"><td>过肩镜头</td><td>Over-the-Shoulder (OTS)</td><td>对话戏常用</td></tr>
<tr class="term-row"><td>主观镜头</td><td>Point of View (POV)</td><td>角色视角</td></tr>
</tbody></table></div>

<h2 id="movement">运镜 Camera Movement</h2>
<div class="table-wrap"><table>
<thead><tr><th>中文</th><th>英文</th><th>说明</th></tr></thead>
<tbody>
<tr class="term-row"><td>固定镜头</td><td>Static / Locked-off</td><td>机位不动</td></tr>
<tr class="term-row"><td>左右摇</td><td>Pan</td><td>水平转动</td></tr>
<tr class="term-row"><td>上下摇</td><td>Tilt</td><td>垂直转动</td></tr>
<tr class="term-row"><td>推镜头</td><td>Dolly In / Push In</td><td>靠近主体</td></tr>
<tr class="term-row"><td>拉镜头</td><td>Dolly Out / Pull Out</td><td>远离主体</td></tr>
<tr class="term-row"><td>移镜头 / 跟拍</td><td>Tracking / Follow Shot</td><td>跟随人物</td></tr>
<tr class="term-row"><td>横移</td><td>Truck Left / Right</td><td>左右平移</td></tr>
<tr class="term-row"><td>升降</td><td>Crane / Jib / Pedestal</td><td>上升或下降</td></tr>
<tr class="term-row"><td>环绕</td><td>Arc Shot / Orbit</td><td>绕主体旋转</td></tr>
<tr class="term-row"><td>手持</td><td>Handheld</td><td>晃动、真实感</td></tr>
<tr class="term-row"><td>斯坦尼康 / 稳定器</td><td>Steadicam / Gimbal</td><td>流畅跟随</td></tr>
<tr class="term-row"><td>变焦</td><td>Zoom In / Out</td><td>焦距变化</td></tr>
<tr class="term-row"><td>希区柯克变焦</td><td>Dolly Zoom / Vertigo Effect</td><td>推拉与变焦反向</td></tr>
<tr class="term-row"><td>航拍</td><td>Aerial / Drone Shot</td><td>无人机</td></tr>
<tr class="term-row"><td>一镜到底 / 长镜头</td><td>Long Take / Oner</td><td>不剪辑的长时间镜头</td></tr>
</tbody></table></div>

<h2 id="comp-light">构图、镜头与光线</h2>
<div class="table-wrap"><table>
<thead><tr><th>中文</th><th>英文</th><th>说明</th></tr></thead>
<tbody>
<tr class="term-row"><td>三分法</td><td>Rule of Thirds</td><td>主体放在三分线交点</td></tr>
<tr class="term-row"><td>对称构图</td><td>Symmetrical Composition</td><td>庄重、秩序</td></tr>
<tr class="term-row"><td>引导线</td><td>Leading Lines</td><td>引导视线</td></tr>
<tr class="term-row"><td>视线空间</td><td>Look Room / Nose Room</td><td>视线方向留白</td></tr>
<tr class="term-row"><td>头顶空间</td><td>Headroom</td><td>头顶到画框距离</td></tr>
<tr class="term-row"><td>浅景深</td><td>Shallow Depth of Field</td><td>背景虚化</td></tr>
<tr class="term-row"><td>深焦</td><td>Deep Focus</td><td>前后景都清晰</td></tr>
<tr class="term-row"><td>移焦 / 拉焦</td><td>Rack Focus / Focus Pull</td><td>焦点前后转移</td></tr>
<tr class="term-row"><td>广角 / 长焦</td><td>Wide-Angle / Telephoto</td><td>视野夸张 vs 压缩空间</td></tr>
<tr class="term-row"><td>主光 / 辅光 / 轮廓光</td><td>Key / Fill / Back (Rim) Light</td><td>三点布光</td></tr>
<tr class="term-row"><td>高调 / 低调</td><td>High-Key / Low-Key Lighting</td><td>明亮 vs 暗部多</td></tr>
<tr class="term-row"><td>硬光 / 柔光</td><td>Hard Light / Soft Light</td><td>阴影锋利 vs 柔和</td></tr>
<tr class="term-row"><td>逆光 / 剪影</td><td>Backlight / Silhouette</td><td>轮廓与氛围</td></tr>
<tr class="term-row"><td>实用光源</td><td>Practical Light</td><td>画面中可见灯具</td></tr>
<tr class="term-row"><td>黄金 / 蓝调时刻</td><td>Golden Hour / Blue Hour</td><td>暖光 vs 深蓝天光</td></tr>
<tr class="term-row"><td>调色</td><td>Color Grading</td><td>后期统一色调</td></tr>
</tbody></table></div>

<h2 id="editing">剪辑、叙事与制作</h2>
<div class="table-wrap"><table>
<thead><tr><th>中文</th><th>英文</th><th>说明</th></tr></thead>
<tbody>
<tr class="term-row"><td>轴线 / 180 度规则</td><td>180-Degree Rule / Axis of Action</td><td>对话戏机位规则</td></tr>
<tr class="term-row"><td>跳轴</td><td>Crossing the Line</td><td>违反轴线</td></tr>
<tr class="term-row"><td>正反打</td><td>Shot / Reverse Shot</td><td>对话基本剪法</td></tr>
<tr class="term-row"><td>反应镜头</td><td>Reaction Shot</td><td>听者表情</td></tr>
<tr class="term-row"><td>硬切</td><td>Cut</td><td>直接切换</td></tr>
<tr class="term-row"><td>动作剪辑</td><td>Match on Action</td><td>动作中切换</td></tr>
<tr class="term-row"><td>匹配剪辑</td><td>Match Cut</td><td>形状/动作相似转场</td></tr>
<tr class="term-row"><td>跳切</td><td>Jump Cut</td><td>同机位时间跳跃</td></tr>
<tr class="term-row"><td>交叉剪辑</td><td>Cross-Cutting / Parallel Editing</td><td>两条线交替</td></tr>
<tr class="term-row"><td>溶镜 / 淡入淡出</td><td>Dissolve / Fade In-Out</td><td>交融或到黑</td></tr>
<tr class="term-row"><td>J-cut / L-cut</td><td>J-Cut / L-Cut</td><td>声音与画面错开</td></tr>
<tr class="term-row"><td>蒙太奇</td><td>Montage</td><td>组接产生意义</td></tr>
<tr class="term-row"><td>场面调度</td><td>Mise-en-scène / Blocking</td><td>画面元素与走位</td></tr>
<tr class="term-row"><td>主镜头 / 覆盖</td><td>Master Shot / Coverage</td><td>全景覆盖 + 补充镜</td></tr>
<tr class="term-row"><td>分镜表 / 故事板</td><td>Shot List / Storyboard</td><td>镜头清单与草图</td></tr>
<tr class="term-row"><td>动态分镜</td><td>Animatic / Previs</td><td>带时长的预览</td></tr>
<tr class="term-row"><td>一句话梗概</td><td>Logline</td><td>故事核心</td></tr>
<tr class="term-row"><td>冷开场 / 悬念结尾</td><td>Cold Open / Cliffhanger</td><td>开场戏与集尾钩子</td></tr>
<tr class="term-row"><td>试播集 / 剧集圣经</td><td>Pilot / Series Bible</td><td>第一集与设定文档</td></tr>
<tr class="term-row"><td>有源 / 无源声音</td><td>Diegetic / Non-diegetic</td><td>画内 / 画外声源</td></tr>
<tr class="term-row"><td>拟音</td><td>Foley</td><td>后期动作音效</td></tr>
</tbody></table></div>

<h2 id="ai-terms">AI 视频常用术语</h2>
<div class="table-wrap"><table>
<thead><tr><th>中文</th><th>英文</th><th>说明</th></tr></thead>
<tbody>
<tr class="term-row"><td>文生视频</td><td>Text-to-Video (T2V)</td><td>文字生成视频</td></tr>
<tr class="term-row"><td>图生视频</td><td>Image-to-Video (I2V)</td><td>图片作首帧生成</td></tr>
<tr class="term-row"><td>参考生视频</td><td>Reference-to-Video</td><td>参考图保持主体</td></tr>
<tr class="term-row"><td>首尾帧 / 关键帧</td><td>First/Last Frame / Keyframe</td><td>控制起止与中间</td></tr>
<tr class="term-row"><td>提示词 / 负面提示词</td><td>Prompt / Negative Prompt</td><td>想要 / 不想要</td></tr>
<tr class="term-row"><td>角色一致性</td><td>Character Consistency</td><td>跨镜保持外观</td></tr>
<tr class="term-row"><td>角色设定图</td><td>Character Sheet / Turnaround</td><td>多角度角色参考</td></tr>
<tr class="term-row"><td>种子值</td><td>Seed</td><td>固定随机以复现</td></tr>
<tr class="term-row"><td>原生音频</td><td>Native Audio</td><td>模型同时出声</td></tr>
<tr class="term-row"><td>口型同步</td><td>Lip Sync</td><td>嘴型与对白匹配</td></tr>
<tr class="term-row"><td>超分</td><td>Upscale</td><td>提高分辨率</td></tr>
<tr class="term-row"><td>抽卡</td><td>Re-roll / Regenerate</td><td>同提示多次挑选</td></tr>
</tbody></table></div>
""",
)

add(
    "app-progress",
    "appendix/progress.html",
    "30 周进度表",
    "",
    [("首页", "index.html"), ("进度表", None)],
    f"""
<h1>30 周进度表</h1>
<p class="lead">可按自己节奏压缩或拉长。每周约 8–12 小时：3 看 + 3 学 + 3 练。</p>

<div class="week-grid">
  <div class="week-item"><span class="wk">第 1–2 周</span><span>景别、角度、构图；读《镜头的语法》</span><span class="out">景别练习小片</span></div>
  <div class="week-item"><span class="wk">第 3–4 周</span><span>运镜、光线、色彩</span><span class="out">光线练习、镜头库起步</span></div>
  <div class="week-item"><span class="wk">第 5–6 周</span><span>轴线、正反打、剪辑、声音；读《眨眼之间》</span><span class="out">对话戏 + 拉片表</span></div>
  <div class="week-item"><span class="wk">第 7–8 周</span><span>复习 + 拉 2 部片</span><span class="out">阶段一小结</span></div>
  <div class="week-item"><span class="wk">第 9–11 周</span><span>故事结构、人物、冲突；读《救猫咪》</span><span class="out">logline 库、人物小传</span></div>
  <div class="week-item"><span class="wk">第 12–14 周</span><span>场景写作、剧集结构；拉剧</span><span class="out">结构拆解图</span></div>
  <div class="week-item"><span class="wk">第 15–17 周</span><span>写剧本 + 分镜头脚本</span><span class="out">短剧剧本 + 分镜表</span></div>
  <div class="week-item"><span class="wk">第 18–20 周</span><span>场面调度、故事板、演员指导</span><span class="out">故事板 + 导演阐述</span></div>
  <div class="week-item"><span class="wk">第 21–23 周</span><span>拍摄计划、实拍、剪辑</span><span class="out">2–3 分钟实拍</span></div>
  <div class="week-item"><span class="wk">第 24–26 周</span><span>AI 工具上手、提示词与镜头语言</span><span class="out">工具对比 + 10 镜复刻</span></div>
  <div class="week-item"><span class="wk">第 27–28 周</span><span>角色一致性、多镜头叙事</span><span class="out">角色设定 + AI 正反打</span></div>
  <div class="week-item"><span class="wk">第 29–30 周</span><span>完整 AI 短片制作</span><span class="out">1–3 分钟 AI 短片</span></div>
</div>

{remember("工具会过时；镜头语言、故事和对人的理解不会。祝创作愉快！")}

<p style="margin-top:1.5rem"><a href="../index.html">← 回到首页</a> · <a href="resources.html">推荐书单片单 →</a></p>
""",
)

add(
    "app-resources",
    "appendix/resources.html",
    "推荐书单与片单",
    "",
    [("首页", "index.html"), ("书单片单", None)],
    """
<h1>推荐书单与片单</h1>
<p class="lead">汇总四阶段书籍、课程与拉片片单。先薄后厚，工具书随用随查。</p>

<h2>阶段一书单（视听语言）</h2>
<div class="table-wrap"><table>
<thead><tr><th>书名</th><th>作者</th><th>理由</th></tr></thead>
<tbody>
<tr><td>《电影语言的语法》</td><td>Daniel Arijon</td><td>机位与轴线百科，对话戏图解最全</td></tr>
<tr><td>《镜头的语法》</td><td>Bowen / Thompson</td><td>零基础最友好</td></tr>
<tr><td>《剪辑的语法》</td><td>Bowen / Thompson</td><td>剪辑入门姊妹篇</td></tr>
<tr><td>《电影镜头设计》</td><td>Steven D. Katz</td><td>分镜到调度，导演必读</td></tr>
<tr><td>《眨眼之间》</td><td>Walter Murch</td><td>剪辑师思维，薄本</td></tr>
<tr><td>《电影艺术：形式与风格》</td><td>Bordwell / Thompson</td><td>系统教材，按章查读</td></tr>
<tr><td>《认识电影》</td><td>Louis Giannetti</td><td>比上者更易读的经典入门</td></tr>
<tr><td>《电影摄影：理论与实践》</td><td>Blain Brown</td><td>光、镜头、运动系统讲</td></tr>
<tr><td>If It's Purple, Someone's Gonna Die</td><td>Patti Bellantoni</td><td>色彩与情绪（英文）</td></tr>
<tr><td>Sound Design</td><td>David Sonnenschein</td><td>声音设计入门（英文）</td></tr>
</tbody></table></div>

<h2>阶段二书单（剧本剧集）</h2>
<div class="table-wrap"><table>
<thead><tr><th>书名</th><th>作者</th><th>理由</th></tr></thead>
<tbody>
<tr><td>《救猫咪》</td><td>Blake Snyder</td><td>零基础编剧首选，节拍表实用</td></tr>
<tr><td>Save the Cat! Writes for TV</td><td>Jamie Nash</td><td>剧集版节拍（英文）</td></tr>
<tr><td>《故事》《人物》《对白》</td><td>Robert McKee</td><td>编剧深度三部曲</td></tr>
<tr><td>《作家之旅》</td><td>Christopher Vogler</td><td>英雄之旅实操</td></tr>
<tr><td>《千面英雄》</td><td>Joseph Campbell</td><td>理论源头，选读</td></tr>
<tr><td>《电影剧本写作基础》</td><td>Syd Field</td><td>三幕经典表述</td></tr>
<tr><td>Writing the TV Drama Series</td><td>Pamela Douglas</td><td>美剧写作教材（英文）</td></tr>
</tbody></table></div>

<h2>阶段三书单（导演方法）</h2>
<div class="table-wrap"><table>
<thead><tr><th>书名</th><th>作者</th><th>理由</th></tr></thead>
<tbody>
<tr><td>Making Movies</td><td>Sidney Lumet</td><td>导演全流程，极其务实</td></tr>
<tr><td>On Directing Film /《导演功课》</td><td>David Mamet</td><td>镜头叙事思维，薄而犀利</td></tr>
<tr><td>Directing Actors</td><td>Judith Weston</td><td>演员指导经典</td></tr>
<tr><td>Film Directing Fundamentals</td><td>Nicholas T. Proferes</td><td>剧本分析到调度</td></tr>
<tr><td>《希区柯克与特吕弗对话录》</td><td>Truffaut</td><td>悬念与导演控制</td></tr>
<tr><td>《雕刻时光》</td><td>Tarkovsky</td><td>艺术观与时间观，选读</td></tr>
<tr><td>《演员的自我修养》</td><td>斯坦尼斯拉夫斯基</td><td>理解演员方法，选读</td></tr>
</tbody></table></div>

<h2>拉片片单精选</h2>
<div class="table-wrap"><table>
<thead><tr><th>阶段</th><th>作品</th><th>重点</th></tr></thead>
<tbody>
<tr><td>一</td><td>《战舰波将金号》《公民凯恩》《惊魂记》《教父》《花样年华》《一一》《人类之子》《布达佩斯大饭店》《爆裂鼓手》《现代启示录》</td><td>蒙太奇、光影、构图、剪辑、声音</td></tr>
<tr><td>二</td><td>《绝命毒师》S1、《切尔诺贝利》、《继承之战》、《熊家餐馆》、《黑镜》、《请回答 1988》、《隐秘的角落》、《漫长的季节》</td><td>试播、钩子、多线、潜台词</td></tr>
<tr><td>三</td><td>《十二怒汉》《好家伙》《饮食男女》《寄生虫》《罗马》《婚姻故事》</td><td>调度、长镜、群像、表演</td></tr>
<tr><td>四</td><td>Runway AIFF 历年入围/获奖短片</td><td>AI 叙事与一致性参考</td></tr>
</tbody></table></div>

<h2>课程与网站（节选）</h2>
<ul>
  <li>StudioBinder、Every Frame a Painting、Nerdwriter1、Lessons from the Screenplay</li>
  <li>FILMGRAB、ShotDeck；BBC Writersroom、Script Slug</li>
  <li>MasterClass：Shonda Rhimes / Ron Howard / Martin Scorsese（付费）</li>
  <li>Storyboarder、Shot Designer、剪映 / CapCut、DaVinci Resolve 免费版</li>
  <li>Runway Academy、Google Flow、Curious Refuge</li>
</ul>
""",
)


# ========== Render all pages ==========

def depth_of(path: str) -> int:
    return path.count("/")

def current_key(path: str) -> str:
    if path.startswith("stage1"):
        return "stage1"
    if path.startswith("stage2"):
        return "stage2"
    if path.startswith("stage3"):
        return "stage3"
    if path.startswith("stage4"):
        return "stage4"
    if path.startswith("appendix"):
        return "appendix"
    return "home"

# Fix TOTAL_PAGES
TOTAL_PAGES = len(pages)

# Rebuild NAV_ORDER
NAV_ORDER = [(p["path"], p["title"]) for p in pages]

def neighbors(path: str):
    paths = [p["path"] for p in pages]
    i = paths.index(path)
    prev_info = None
    next_info = None
    if i > 0:
        prev_info = (pages[i - 1]["path"], pages[i - 1]["title"])
    if i < len(pages) - 1:
        next_info = (pages[i + 1]["path"], pages[i + 1]["title"])
    return prev_info, next_info

# Patch page_shell to use updated TOTAL_PAGES — redefine thin wrapper
def render(page):
    path = page["path"]
    depth = depth_of(path)
    prev_info, next_info = neighbors(path)
    # Inject total pages into shell via global
    global TOTAL_PAGES
    html_out = page_shell(
        title=page["title"],
        body=page["body"],
        depth=depth,
        current=current_key(path),
        breadcrumbs=page["crumbs"],
        prev_info=prev_info,
        next_info=next_info,
        page_id=page["id"],
        stage=page["stage"],
    )
    # Fix data-total-pages in case TOTAL_PAGES changed after shell def
    import re
    html_out = re.sub(
        r'data-total-pages="\d+"',
        f'data-total-pages="{TOTAL_PAGES}"',
        html_out,
    )
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_out, encoding="utf-8")
    return out

def plain_text(fragment):
    text = re.sub(r"<script[\s\S]*?</script>", " ", fragment, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def section_of(page):
    labels = {"1": "阶段一", "2": "阶段二", "3": "阶段三", "4": "阶段四"}
    stage = str(page.get("stage") or "")
    if stage in labels:
        return labels[stage]
    if page["path"].startswith("appendix"):
        return "附录"
    return "总览"


def write_search_index():
    items = []
    for page in pages:
        items.append(
            {
                "title": page["title"],
                "path": page["path"],
                "section": section_of(page),
                "text": plain_text(page["body"])[:4000],
            }
        )
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    out = ROOT / "js" / "search-index.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "/* Generated by _generate.py — do not edit by hand. */\n"
        "window.DIRECTOR_SEARCH_INDEX=" + payload + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote search index ({len(items)} pages)")


def main():
    written = []
    for page in pages:
        out = render(page)
        written.append(str(out.relative_to(ROOT)))
    write_search_index()
    print(f"Wrote {len(written)} pages:")
    for w in written:
        print(" ", w)

if __name__ == "__main__":
    main()
