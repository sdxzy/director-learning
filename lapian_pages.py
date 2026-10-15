#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 每日逐帧 pages from lapian/NNN/ folders.

Each issue folder needs meta.json and lesson.md. Media (narrated.mp4,
clip.mp4, narration.srt, frameNN.png) is optional and used when present.
diagram.svg or diagram.png, when present, is drawn after the lead.
"""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent
LAPIAN = ROOT / "lapian"

COURSE_URL = re.compile(
    r"https://sdxzy\.github\.io/director-learning/(stage\d+/[\w.-]+\.html)"
)
SHOT_RE = re.compile(
    r"^\*\*([①②③④⑤⑥⑦⑧⑨⑩])\s+frame(\d+)：(.+?)\*\*\s*（(.+?)）\s*$"
)
BARE_URL = re.compile(r"https?://[^\s<]+")
YOUTUBE_ID = re.compile(r"youtube\.com/watch\?v=([A-Za-z0-9_-]{11})")
LECTURE_TITLE = re.compile(r"《([^》]+)》")
LECTURE_CHANNEL = re.compile(r"先看\s+(.+?)\s*的《")


def load_issues():
    issues = []
    if not LAPIAN.is_dir():
        return issues
    for folder in sorted(LAPIAN.iterdir()):
        if not folder.is_dir() or not re.fullmatch(r"\d{3}", folder.name):
            continue
        meta_path = folder / "meta.json"
        lesson_path = folder / "lesson.md"
        if not meta_path.is_file() or not lesson_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        issue_id = folder.name
        title = (meta.get("title") or "").strip()
        if not title:
            raise SystemExit(f"{meta_path}: missing title")
        date = (meta.get("date") or "").strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            raise SystemExit(f"{meta_path}: date must be YYYY-MM-DD")
        tags = [str(t).strip() for t in meta.get("tags") or [] if str(t).strip()]
        nav = (meta.get("nav") or f"{issue_id} {title}").strip()
        issues.append(
            {
                "id": issue_id,
                "date": date,
                "title": title,
                "tags": tags,
                "nav": nav,
                "folder": folder,
                "path": f"lapian/{issue_id}.html",
                "lesson": lesson_path.read_text(encoding="utf-8"),
            }
        )
    issues.sort(key=lambda item: (item["date"], item["id"]), reverse=True)
    return issues


def _srt_to_vtt(srt: str) -> str:
    text = srt.replace("\r\n", "\n").replace("\r", "\n").strip()
    out = ["WEBVTT", ""]
    for line in text.split("\n"):
        if re.fullmatch(r"\d+", line.strip()):
            continue
        out.append(re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", line))
    return "\n".join(out).rstrip() + "\n"


def ensure_vtt(folder: Path):
    srt = folder / "narration.srt"
    vtt = folder / "narration.vtt"
    if srt.is_file():
        vtt.write_text(_srt_to_vtt(srt.read_text(encoding="utf-8")), encoding="utf-8")
    return vtt if vtt.is_file() else None


def _inline(text: str) -> str:
    labeled = re.fullmatch(
        r"(.+?)：\s*https://sdxzy\.github\.io/director-learning/(stage\d+/[\w.-]+\.html)\s*",
        text.strip(),
    )
    if labeled:
        return f'<a href="../{labeled.group(2)}">{html.escape(labeled.group(1))}</a>'

    parts = BARE_URL.split(text)
    urls = BARE_URL.findall(text)
    out = []
    for i, part in enumerate(parts):
        escaped = html.escape(part)
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
        escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
        out.append(escaped)
        if i < len(urls):
            href = html.escape(urls[i], quote=True)
            out.append(f'<a href="{href}">{href}</a>')
    return "".join(out)


def _blocks(lines):
    parts = []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        if lines[i].lstrip().startswith("- "):
            items = []
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                item = lines[i].strip()[2:]
                i += 1
                while i < len(lines) and lines[i].startswith((" ", "\t")) and lines[i].strip():
                    item += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{_inline(item)}</li>")
            parts.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue
        para = [lines[i].strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith("- "):
            para.append(lines[i].strip())
            i += 1
        parts.append(f"<p>{_inline(' '.join(para))}</p>")
    return "\n".join(parts)


def _sections(markdown: str):
    title = ""
    sections = []
    current = None
    buf = []
    for line in markdown.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            if current is not None:
                sections.append((current, buf))
            current = line[3:].strip()
            buf = []
            continue
        buf.append(line)
    if current is not None:
        sections.append((current, buf))
    return title, sections


def _shots(lines):
    shots = []
    rest = []
    i = 0
    while i < len(lines):
        match = SHOT_RE.match(lines[i].strip())
        if not match:
            if lines[i].strip():
                rest.append(lines[i])
            i += 1
            continue
        bullets = []
        i += 1
        while i < len(lines) and lines[i].lstrip().startswith("- "):
            bullets.append(lines[i].strip()[2:])
            i += 1
        shots.append(
            {
                "mark": match.group(1),
                "file": f"frame{int(match.group(2)):02d}.png",
                "title": match.group(3).strip(),
                "when": match.group(4).strip(),
                "bullets": bullets,
            }
        )
    return shots, rest


def _player(src, caption, poster=None, track=None):
    poster_attr = f' poster="{html.escape(poster, quote=True)}"' if poster else ""
    track_html = ""
    if track:
        track_html = (
            f'<track kind="subtitles" src="{html.escape(track, quote=True)}" '
            'srclang="zh-Hans" label="中文旁白">'
        )
    return (
        '<figure class="lapian-player">'
        f'<video controls preload="metadata" playsinline{poster_attr}>'
        f'<source src="{html.escape(src, quote=True)}" type="video/mp4">'
        f"{track_html}"
        "</video>"
        f"<figcaption>{caption}</figcaption>"
        "</figure>"
    )


def _first_youtube_id(lines):
    match = YOUTUBE_ID.search("\n".join(lines))
    return match.group(1) if match else ""


def _lecture_facade(lines):
    """Click-to-load the first lecture. Title and channel come from 「先看某某的《标题》」."""
    video_id = _first_youtube_id(lines)
    if not video_id:
        return ""
    title = ""
    channel = ""
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        title_match = LECTURE_TITLE.search(stripped)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        channel_match = LECTURE_CHANNEL.search(stripped)
        if channel_match:
            channel = channel_match.group(1).strip()
        break
    if not title:
        return ""
    credit = (
        f"{channel} · YouTube · 点击播放；离线时打开链接。"
        if channel
        else "YouTube · 点击播放；离线时打开链接。"
    )
    return _youtube_facade(video_id, title, credit)


def _youtube_facade(video_id, title, credit):
    """Same click-to-load control as the stage lessons, without a film still."""
    embed = (
        "https://www.youtube-nocookie.com/embed/"
        + video_id
        + "?rel=0&amp;autoplay=1"
    )
    safe = html.escape(title)
    return (
        '<figure class="video-card">'
        '<button type="button" class="video-facade no-poster" '
        f'data-embed="{embed}" data-title="{html.escape(title, quote=True)}">'
        '<span class="play-btn" aria-hidden="true"></span>'
        f'<span class="facade-label">{safe}</span>'
        f'<span class="sr-only">播放：{safe}</span>'
        "</button>"
        "<figcaption>"
        f'<a href="https://www.youtube.com/watch?v={video_id}">{safe}</a>'
        f'<span class="credit">{html.escape(credit)}</span>'
        "</figcaption></figure>"
    )


def _diagram_html(folder, issue_id):
    caption = '自绘示意图<span class="credit">不是影片剧照。</span>'
    svg = folder / "diagram.svg"
    png = folder / "diagram.png"
    if svg.is_file():
        raw = re.sub(r"<\?xml[^?]*\?>", "", svg.read_text(encoding="utf-8")).strip()
        return (
            '<figure class="figure">'
            f'<div class="figure-frame">{raw}</div>'
            f"<figcaption>{caption}</figcaption>"
            "</figure>"
        )
    if png.is_file():
        return (
            '<figure class="figure">'
            '<div class="figure-frame">'
            f'<img src="{issue_id}/{png.name}" alt="自绘示意图" loading="lazy">'
            "</div>"
            f"<figcaption>{caption}</figcaption>"
            "</figure>"
        )
    return ""


def _shot_html(issue_id, folder, shot):
    bullets = "\n".join(f"<li>{_inline(item)}</li>" for item in shot["bullets"])
    image = ""
    if (folder / shot["file"]).is_file():
        alt = html.escape(f"{shot['mark']} {shot['title']}", quote=True)
        image = f'<img src="{issue_id}/{shot["file"]}" alt="{alt}" loading="lazy">'
    row_class = "shot-row" if image else "shot-row shot-row--plain"
    return (
        f'<article class="{row_class}">'
        f"{image}"
        "<div>"
        f"<h3>{html.escape(shot['mark'])} {html.escape(shot['title'])}</h3>"
        f'<p class="shot-when">{html.escape(shot["when"])}</p>'
        f"<ul>\n{bullets}\n</ul>"
        "</div>"
        "</article>"
    )


def archive_body(issues):
    rows = []
    for issue in issues:
        tags = "、".join(html.escape(tag) for tag in issue["tags"]) or "—"
        href = f'{issue["id"]}.html'
        rows.append(
            "<tr>"
            f'<td><a href="{href}">{issue["id"]}</a></td>'
            f'<td>{html.escape(issue["date"])}</td>'
            f'<td><a href="{href}">{html.escape(issue["title"])}</a></td>'
            f"<td>{tags}</td>"
            "</tr>"
        )
    table = (
        '<div class="table-wrap"><table>'
        "<thead><tr><th>期号</th><th>日期</th><th>标题</th><th>主题</th></tr></thead>"
        f'<tbody>{"".join(rows)}</tbody></table></div>'
        if rows
        else "<p>还没有一期。加一集的方法写在 README。</p>"
    )
    return (
        "<h1>每日逐帧</h1>"
        "<p class=\"lead\">一期一个片段。先看配音讲解，再对着静帧看景别、构图和剪辑。新的在前。</p>"
        f"{table}"
    )


def issue_body(issue):
    folder = issue["folder"]
    issue_id = issue["id"]
    _, sections = _sections(issue["lesson"])
    by_name = {name: lines for name, lines in sections}
    vtt = ensure_vtt(folder)
    tags = " · ".join(html.escape(tag) for tag in issue["tags"])
    parts = [
        f'<p class="lapian-kicker">每日逐帧 · 第 {issue_id} 期 · {html.escape(issue["date"])}'
        + (f" · {tags}" if tags else "")
        + "</p>",
        f'<h1>{html.escape(issue["title"])}</h1>',
    ]
    if (folder / "narrated.mp4").is_file():
        parts.append(
            _player(
                f"{issue_id}/narrated.mp4",
                "配音讲解。字幕已经烧进画面；播放器里可以另外打开「中文旁白」轨道。",
                poster=f"{issue_id}/frame01.png" if (folder / "frame01.png").is_file() else None,
                track=f"{issue_id}/narration.vtt" if vtt else None,
            )
        )
    if "一句话看点" in by_name:
        parts.append(_blocks(by_name["一句话看点"]))
    # Narrated issues keep the player at the top. The lecture list is for
    # issues that cannot ship a clip.
    if "先看讲解视频" in by_name and not (folder / "narrated.mp4").is_file():
        lines = by_name["先看讲解视频"]
        parts.append("<h2>先看讲解视频</h2>")
        facade = _lecture_facade(lines)
        if facade:
            parts.append(facade)
        parts.append(_blocks(lines))
    diagram = _diagram_html(folder, issue_id)
    if diagram:
        parts.append(diagram)
    if "逐镜头拆解" in by_name:
        shots, rest = _shots(by_name["逐镜头拆解"])
        parts.append("<h2>逐镜头拆解</h2>")
        parts.extend(_shot_html(issue_id, folder, shot) for shot in shots)
        if rest:
            parts.append(_blocks(rest))
    if (folder / "clip.mp4").is_file():
        parts.append(
            _player(
                f"{issue_id}/clip.mp4",
                "clip.mp4 无配音版。对着画面自己讲一遍。",
                poster=f"{issue_id}/frame02.png" if (folder / "frame02.png").is_file() else None,
            )
        )
    for name in ("10 分钟小练习（二选一）",):
        if name in by_name:
            parts.append(f"<h2>{html.escape(name)}</h2>")
            parts.append(_blocks(by_name[name]))
    if "对应学习站章节" in by_name:
        parts.append("<h2>对应课程</h2>")
        parts.append(_blocks(by_name["对应学习站章节"]))
    if "作品信息" in by_name:
        parts.append("<h2>片源与授权</h2>")
        parts.append(_blocks(by_name["作品信息"]))
    if "推荐延伸视频" in by_name:
        parts.append("<h2>推荐延伸</h2>")
        parts.append(_blocks(by_name["推荐延伸视频"]))
    return "\n".join(parts)


def neighbors_for(path, issues):
    """Prev/next inside 每日逐帧. Oldest issue points back at the archive."""
    if path == "lapian/index.html":
        if not issues:
            return None, None
        newest = issues[0]
        return None, (newest["path"], newest["title"])
    chrono = list(reversed(issues))
    paths = [item["path"] for item in chrono]
    if path not in paths:
        return None, None
    index = paths.index(path)
    prev_info = (
        (chrono[index - 1]["path"], chrono[index - 1]["title"])
        if index > 0
        else ("lapian/index.html", "每日逐帧")
    )
    next_info = (
        (chrono[index + 1]["path"], chrono[index + 1]["title"])
        if index + 1 < len(chrono)
        else None
    )
    return prev_info, next_info
