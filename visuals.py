#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figures, verified stills, and click-to-load videos inserted into lesson HTML."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parent

VIDEOS = {
    "AyML8xuKfoc": ("Ultimate Guide to Camera Shots: Every Shot Size Explained [The Shot List, Ep 1]", "StudioBinder", "景别"),
    "wLfZL9PZI9k": ("Ultimate Guide to Camera Angles: Every Camera Shot Explained [Shot List, Ep. 3]", "StudioBinder", "机位角度"),
    "IiyBo-qLDeM": ("Ultimate Guide to Camera Movement — Every Camera Movement Technique Explained [The Shot List Ep6]", "StudioBinder", "运镜"),
    "doaQC-S8de8": ("Akira Kurosawa - Composing Movement", "Every Frame a Painting", "黑泽明：运动如何构图"),
    "hUmZldt0DTg": ("Ultimate Guide to Film Composition & Framing — Key Elements Explained [Shot List Ep. 11]", "StudioBinder", "构图与取景"),
    "wsI8UES59TM": ("Drive (2011) - The Quadrant System", "Every Frame a Painting", "四象限构图"),
    "r2nD_knsNrc": ("Ultimate Guide to Cinematic Lighting — Types of Light & Gear Explained [Shot List Ep. 12]", "StudioBinder", "光的类型"),
    "lINVnA3rVIE": ("Color Theory in Film — Color Psychology for Directors: Ep5", "StudioBinder", "色彩"),
    "4PcpGxihPac": ("Mandy: The Art Of Film Grain", "Nerdwriter1", "颗粒、色彩和质感"),
    "iW0bKUfvH2c": ("The 180 Degree Rule in Film (and How to Break The Line) #180degreerule", "StudioBinder", "180 度轴线"),
    "qQNiqzuXjoM": ("Camera Framing: Shot Composition & Cinematography Techniques Explained [The Shot List, Ep 2]", "StudioBinder", "过肩、单人与双人"),
    "FVR8zz8ci2k": ("6 Ways to Edit Any Scene — Essential Film & Video Editing Techniques Explained [Shot List Ep. 10]", "StudioBinder", "正反打、切点与 J/L 切"),
    "TKXBAaQB03U": ("Ultimate Guide to Scene Transitions – Every Editing Transition Explained [The Shot List, Ep 9]", "StudioBinder", "转场，含 J 切和 L 切"),
    "3FOzD4Sfgag": ("Edgar Wright - How to Do Visual Comedy", "Every Frame a Painting", "画与声如何一起做喜剧"),
    "j56WPBaiPYQ": ("The Avengers — Defining an Act", "Lessons from the Screenplay", "怎样界定一幕"),
    "mgk6e8gWDbk": ("10 Best Structured Movies of All Time", "CineFix", "三幕和其他结构"),
    "9AGaECt9j4g": ("Film Blocking Tutorial — Filmmaking Techniques for Directors:  Ep3", "StudioBinder", "场面调度"),
    "DgZPQMyzKiE": ("Masterpiece: The Making of Migrant Mother", "Nerdwriter1", "距离和角度怎样改一张脸"),
}


def load_svg(name):
    raw = (ROOT / "assets" / "diagrams" / f"{name}.svg").read_text(encoding="utf-8")
    raw = re.sub(r"<\?xml[^?]*\?>", "", raw).strip()
    return raw


WIDE = {
    "shot-sizes", "camera-angles", "camera-moves", "composition", "kuleshov",
    "jl-cut", "heros-journey", "episode-arc", "story-braid", "prompt-anatomy",
    "storyboard", "three-act", "axis-180", "ots-reverse", "blocking-plan",
    "turnaround", "color-pair", "high-low-key", "three-point",
}


def fig(name, caption):
    wide = " figure-wide" if name in WIDE else ""
    return (
        f'<figure class="figure{wide}">'
        f'<div class="figure-frame">{load_svg(name)}</div>'
        f"<figcaption>{caption}</figcaption>"
        f"</figure>"
    )


def shot_lab():
    return (
        '<figure class="figure shot-lab figure-wide" data-shot-lab '
        'data-labels="大远景,远景,全景,中景,近景,特写">'
        f'<div class="figure-frame">{load_svg("shot-sizes")}</div>'
        '<label class="shot-slider"><span>拖动看景别：<strong data-shot-name>中景</strong></span>'
        '<input type="range" min="0" max="5" value="3" aria-label="景别，从大远景到特写">'
        "</label>"
        "<figcaption>同一人物，从大远景收到特写。点一格，或拖动滑块。</figcaption>"
        "</figure>"
    )


def still(prefix, filename, alt, caption, credit):
    return (
        '<figure class="still">'
        f'<img src="{prefix}assets/img/{filename}" alt="{html.escape(alt, quote=True)}" loading="lazy">'
        f"<figcaption>{caption}<span class=\"credit\">{credit}</span></figcaption>"
        "</figure>"
    )


def wiki(filename):
    return "https://commons.wikimedia.org/wiki/File:" + filename.replace(" ", "_")


def credit_pd(artist, commons_name):
    href = html.escape(wiki(commons_name), quote=True)
    name = html.escape(commons_name)
    return (
        f"{html.escape(artist)}。"
        f'<a href="{href}" target="_blank" rel="noopener noreferrer">Wikimedia Commons，{name}</a>。'
        "公有领域（Public domain）。"
    )


def _a(href, label):
    return f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(label)}</a>'


# Tears of Steel: mango.blender.org/about states CC BY 3.0. Frames grabbed from the
# official 720p file on download.blender.org.
TOS = (
    "Blender Studio / Blender Foundation，《钢铁之泪》（Tears of Steel，2012）。本站从成片截取。"
    + _a("https://download.blender.org/demo/movies/ToS/tears_of_steel_720p.mov", "tears_of_steel_720p.mov")
    + "。"
    + _a("https://mango.blender.org/about/", "项目说明")
    + "，"
    + _a("https://creativecommons.org/licenses/by/3.0/", "CC BY 3.0")
    + "。"
)
# Spring webm on Commons is the official short, LicenseShortName CC BY 4.0,
# artist Andy Goralczyk / Blender Foundation.
SPRING = (
    "Andy Goralczyk / Blender Foundation，《春》（Spring，2019）。本站从官方成片截取。"
    + _a("https://commons.wikimedia.org/wiki/File:Spring_-_Blender_Open_Movie.webm", "Wikimedia Commons，Spring - Blender Open Movie.webm")
    + "。"
    + _a("https://creativecommons.org/licenses/by/4.0/", "CC BY 4.0")
    + "。"
)


def credit_commons(artist, commons_name, license_label, deed):
    return (
        f"{html.escape(artist)}。"
        + _a(wiki(commons_name), "Wikimedia Commons，" + commons_name)
        + "。"
        + _a(deed, license_label)
        + "。"
    )


BBB_DEED = "https://creativecommons.org/licenses/by/3.0/"
# Peach about page: the open movie, including published files, is CC BY 3.0.
# Each still below also carries LicenseShortName CC BY 3.0 on its Commons file.


def still_pair(inner):
    return f'<div class="still-pair">{inner}</div>'


def video(prefix, vid):
    title, channel, gloss = VIDEOS[vid]
    safe_title = html.escape(title)
    return (
        '<figure class="video-card">'
        f'<button type="button" class="video-facade" data-embed="https://www.youtube-nocookie.com/embed/{vid}?rel=0&amp;autoplay=1" data-title="{html.escape(title, quote=True)}">'
        f'<img src="{prefix}assets/img/posters/{vid}.jpg" alt="" width="480" height="360" loading="lazy">'
        '<span class="play-btn" aria-hidden="true"></span>'
        f'<span class="sr-only">播放：{safe_title}</span>'
        "</button>"
        "<figcaption>"
        f'<a href="https://www.youtube.com/watch?v={vid}">{safe_title}</a>'
        f'<span class="credit">{html.escape(channel)} · YouTube · {html.escape(gloss)}。点击封面播放；离线时打开链接。</span>'
        "</figcaption></figure>"
    )


def videos(prefix, ids):
    inner = "".join(video(prefix, vid) for vid in ids)
    return f'<div class="media-block"><p class="media-kicker">影像例子</p>{inner}</div>'


def pull(items):
    lis = "".join(f"<li>{item}</li>" for item in items)
    return (
        '<div class="pull"><p class="media-kicker">推荐拉片镜头</p><ul>'
        f"{lis}</ul>"
        '<p class="credit-note">只写片名和场面。分钟数随修复版和网络拷贝变化，没有对某一份文件逐帧核对，所以不标时间点。</p>'
        "</div>"
    )


def inject(body, pairs, path):
    parts = body.split("<h3>是什么</h3>")
    if len(parts) - 1 != len(pairs):
        raise SystemExit(f"{path}: {len(parts) - 1} 是什么 headings, {len(pairs)} visuals")
    out = [parts[0]]
    for (lead, tail), rest in zip(pairs, parts[1:]):
        if "<h3>为什么重要</h3>" not in rest:
            raise SystemExit(f"{path}: 是什么 section has no 为什么重要")
        what, sep, after = rest.partition("<h3>为什么重要</h3>")
        out.append("<h3>是什么</h3>\n" + lead + "\n" + what + "\n" + tail + "\n" + sep + after)
    return "".join(out)


def pairs_for(path, prefix):
    if path == "stage1/shot-size.html":
        return [
            (
                shot_lab(),
                still(prefix, "spring-wide.jpg", "春，开阔的冷色远景", "大远景：主体很小，冷的天空占了大部分。", SPRING)
                + still(prefix, "bbb-forest.jpg", "大兔兔宾尼，树林", "远景：树林占满画面，角色还没成为中心。",
                        credit_commons("Blender Foundation / Project Peach，《大兔兔宾尼》（Big Buck Bunny，2008）",
                                       "Big Buck Bunny - forest.jpg", "CC BY 3.0", BBB_DEED))
                + still(prefix, "bbb-bunny.jpg", "大兔兔宾尼，兔子的脸", "近景到特写：脸占满画面，环境退到后面。",
                        credit_commons("Blender Foundation，《大兔兔宾尼》（Big Buck Bunny，2008）",
                                       "BBB-Bunny.png", "CC BY 3.0", BBB_DEED))
                + still(prefix, "bbb-yawn.jpg", "大兔兔宾尼，兔子打哈欠", "大特写：一个哈欠就是这一格的全部信息。",
                        credit_commons("Blender Foundation，《大兔兔宾尼》（Big Buck Bunny，2008）。截图：Wikimedia 用户 Church of emacs",
                                       "BBB sbadiglia.png", "CC BY 3.0", BBB_DEED))
                + videos(prefix, ["AyML8xuKfoc"])
                + pull([
                    "《沙丘》（2021）：人站在沙漠和采砂机前面，先交代尺度。",
                    "《鱿鱼游戏》（2021）第一集「一二三木头人」：操场的大全景比任何一张脸都大。",
                    "《春》（2019，Blender Studio）：飞过地面的远景。",
                ]),
            ),
            (
                fig("camera-angles", "仰、平、俯、鸟瞰、荷兰角。悬停或点选一格，边框会变成朱红。"),
                still(prefix, "cosmos-franck.jpg", "宇宙洗衣店，大片留白里的角色", "人没有顶满画面，周围的空让他显得不那么逼人。角度课先看这张：空的多少，会改变你觉得他有多强。",
                        credit_commons("Blender Foundation，《宇宙洗衣店》（Cosmos Laundromat，2015）",
                                       "CosmosLaundromatFranck.jpg", "CC BY 3.0", BBB_DEED))
                + videos(prefix, ["wLfZL9PZI9k", "DgZPQMyzKiE"])
                + pull([
                    "《寄生虫》（2019）：楼梯是纵向的，人往下走，空间本身在写「被压到下一层」。",
                ]),
            ),
        ]
    if path == "stage1/camera-movement.html":
        return [(
            fig("camera-moves", "推、拉、摇、移、跟、升降。箭头是摄影机要去的方向。"),
            still_pair(
                still(prefix, "tos-pan-a.jpg", "钢铁之泪，横移前", "同一镜头，这一格。", TOS)
                + still(prefix, "tos-pan-b.jpg", "钢铁之泪，横移后", "约 0.8 秒后，整个画面横着挪了一截。是摇或横移，不是硬切。", TOS)
            )
            + still_pair(
                still(prefix, "spring-rise-a.jpg", "春，上下移动前", "同一镜头，这一格。", SPRING)
                + still(prefix, "spring-rise-b.jpg", "春，上下移动后", "约 0.8 秒后，画面沿上下方向移开。是俯仰或升降，不是换镜头。", SPRING)
            )
            + videos(prefix, ["IiyBo-qLDeM", "doaQC-S8de8"])
            + pull([
                "《1917》（2019）：整部片做成一次走完的错觉，切点藏在全黑和挡镜里。",
                "《熊家餐馆》第一季第 7 集「Review」：一条在后厨里走完的长镜头。",
                "《继承之战》：对话里常用突然的变焦扎进人脸。",
            ]),
        )]
    if path == "stage1/composition.html":
        return [(
            fig("composition", "三分法、引导线、框架。悬停一格，边框变朱红。"),
            still(prefix, "tos-close.jpg", "钢铁之泪，人在画面一侧", "人靠在一侧，另一侧留出空，视线才有地方去。", TOS)
            + still(prefix, "tos-slit.jpg", "钢铁之泪，暗场里的一条亮", "大部分留在暗里，只留一条亮缝，先把看的地方定死。", TOS)
            + still(prefix, "spring-space.jpg", "春，大片留白", "主体几乎只是一个点，空的地方本身就是构图。", SPRING)
            + videos(prefix, ["hUmZldt0DTg", "wsI8UES59TM"])
            + pull([
                "《人生切割术》（2022–）：被切割的办公层几乎绝对居中、对称。",
                "《寄生虫》（2019）：楼梯的线条把人往下带。",
                "《爱乐之城》（2016）开场公路歌舞：人群沿着匝道铺开。",
            ]),
        )]
    if path == "stage1/light-color.html":
        return [
            (
                fig("three-point", "俯视：主光塑形，辅光填一点阴影，轮廓光把人从背景上撕开。")
                + fig("high-low-key", "高调几乎没有死黑；低调只留一小块能读的亮。"),
                still(prefix, "spring-highkey.jpg", "春，明亮的高调画面", "高调：亮部多，阴影很浅。", SPRING)
                + still(prefix, "tos-lowkey.jpg", "钢铁之泪，沉在暗里的画面", "低调：大部分沉在暗里，只留一点能读的形。", TOS)
                + videos(prefix, ["r2nD_knsNrc"])
                + pull([
                    "《寄生虫》（2019）：半地下室靠街面那一扇窗；朴社长家是整面玻璃的日光。",
                    "《奥本海默》（2023）三一试验：一场真实爆炸把人脸打进同一阵白光。诺兰说过试验场面用的是实拍爆炸，不是后期做的火球。",
                ]),
            ),
            (
                fig("color-pair", "冷背景配暖主体。黑白片靠明暗做这件事，彩色片可以直接用互补色。"),
                still(prefix, "spring-wide.jpg", "春，偏冷的蓝色远景", "冷：蓝占主导，距离感更远。", SPRING)
                + still(prefix, "spring-highkey.jpg", "春，偏暖的高调画面", "暖：同一部短片里换一档颜色，情绪就换一档。", SPRING)
                + videos(prefix, ["lINVnA3rVIE", "4PcpGxihPac"])
                + pull([
                    "《爱乐之城》（2016）：黄、蓝、红把歌舞从日常里分离出来。",
                    "《绝命毒师》：玛丽长期穿紫，是剧组给定的人物颜色。",
                    "《奥本海默》（2023）：彩色一条线、黑白一条线。诺兰把彩色说成奥本海默的视角。",
                ]),
            ),
        ]
    if path == "stage1/axis.html":
        return [
            (
                fig("axis-180", "机位 A、机位 B 都在轴线这一侧。斜线区域是禁区，那里的机位会跳轴。"),
                videos(prefix, ["iW0bKUfvH2c"]),
            ),
            (
                fig("ots-reverse", "先从一侧肩后看对方，再换到另一侧肩后。左右关系不要换。"),
                videos(prefix, ["qQNiqzuXjoM"]),
            ),
        ]
    if path == "stage1/montage.html":
        return [(
            fig("kuleshov", "脸没有变。变的是后面那一格，观众却觉得表情变了。")
            + fig("jl-cut", "J 切是下一镜的声音先到；L 切是上一镜的声音留下来。"),
            still_pair(
                still(prefix, "tos-cut-a.jpg", "钢铁之泪，硬切前", "这一格。", TOS)
                + still(prefix, "tos-cut-b.jpg", "钢铁之泪，硬切后", "不到一秒，已经是另一个画面。意思从这一下里出来。", TOS)
            )
            + still(prefix, "potemkin-face.jpg", "战舰波将金号，阶梯段落中的女子近景", "经典对照：一张脸接上阶梯上的混乱，情绪是剪出来的。",
                    "经典对照。" + credit_pd("S. M. Eisenstein，《战舰波将金号》（1925）", "Potemkin-still6.jpg"))
            + videos(prefix, ["TKXBAaQB03U", "FVR8zz8ci2k"])
            + pull([
                "《瞬息全宇宙》（2022）：硬切和画幅变化，把同一个动作接到另一个宇宙。",
                "《奥本海默》（2023）：听证会和三一试验交叉剪。",
                "经典对照：《战舰波将金号》（1925）敖德萨阶梯，脸、台阶、人群交替。",
            ]),
        )]
    if path == "stage1/sound.html":
        return [(
            fig("sound-layers", "对白、音效、音乐叠在三条上。音效中间那一格是故意留下的静。"),
            videos(prefix, ["3FOzD4Sfgag"]),
        )]
    if path == "stage2/story-structure.html":
        return [
            (fig("logline", "四个空填满，才算有一句能拍的梗概。"), ""),
            (
                fig("three-act", "曲线先抬起，中点转向，低谷之后才是高潮。"),
                videos(prefix, ["j56WPBaiPYQ", "mgk6e8gWDbk"]),
            ),
        ]
    if path == "stage2/character-conflict.html":
        return [
            (fig("want-need", "想要是外面的目标。需要是走完这段路才承认的那件事。"), ""),
            (fig("conflict-layers", "一场戏至少要碰到其中一层，最好让外层挤压内层。"), ""),
        ]
    if path == "stage2/scene-writing.html":
        return [(fig("scene-inout", "斜线是可以删的两头。中间那一截才是这场戏。"), "")]
    if path == "stage2/series-hooks.html":
        return [(
            fig("episode-arc", "上面一根是整季的问题，下面每集自己拱起，集尾用三角标记钩子。")
            + fig("story-braid", "A 线不断，B 线和 C 线穿进来，而不是三条平行的流水账。"),
            "",
        )]
    if path == "stage2/shot-list.html":
        return [(fig("shot-strip", "分镜条先问这四列：镜号、景别、运镜、画面。声音和时长写在旁边。"), "")]
    if path == "stage3/workflow.html":
        return [(fig("workflow", "前期决定拍什么，拍摄决定怎么覆盖，后期决定观众实际看见什么。"), "")]
    if path == "stage3/blocking.html":
        return [(
            fig("blocking-plan", "圆点是演员，虚线是轴线，两个机位都画在同一侧。"),
            videos(prefix, ["9AGaECt9j4g"]),
        )]
    if path == "stage3/directing-actors.html":
        return [(fig("verb-adjective", "划掉形容词。留下观众能看见的动作。"), "")]
    if path == "stage3/storyboard.html":
        return [(fig("storyboard", "一格只做一件事：景别、运动方向、观众该看的那一点。"), "")]
    if path == "stage3/shooting-plan.html":
        return [(fig("coverage", "先让整场在主镜头里演完，再补两侧覆盖和插入。"), "")]
    if path == "stage4/prompt-structure.html":
        return [(fig("prompt-anatomy", "提示词按这个顺序写，生成结果才跟分镜是同一件事。"), "")]
    if path == "stage4/character-consistency.html":
        return [(fig("turnaround", "领口那一笔在正面、侧面、背面都在。标记比形容词更稳。"), "")]
    if path == "stage4/compliance.html":
        return [(fig("compliance", "权利、肖像、平台。三道门都过了再往下做。"), "")]
    return None


def apply_visuals(path, body):
    prefix = "../" * path.count("/")
    pairs = pairs_for(path, prefix)
    if pairs:
        body = inject(body, pairs, path)
    if path == "index.html":
        needle = "<h2>四阶段 · 约 30 周总览</h2>"
        if needle not in body:
            raise SystemExit("home syllabus heading not found")
        home_fig = fig(
            "shot-sizes",
            '同一人物的六种景别。课表从这里往下走。<a href="stage1/shot-size.html">打开「景别与角度」</a>',
        )
        body = body.replace(needle, home_fig + "\n" + needle, 1)
    if path == "stage2/story-structure.html":
        needle = "<h2>英雄之旅（简版）</h2>"
        if needle not in body:
            raise SystemExit("hero heading not found")
        body = body.replace(
            needle,
            needle + "\n" + fig("heros-journey", "十二个站顺时针走一圈。把它当检查清单，不是打卡表。磨难标成朱红。"),
            1,
        )
    return body
