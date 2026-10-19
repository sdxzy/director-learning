#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hand-composed line diagrams for the directing course. Palette matches the site."""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "assets" / "diagrams"
INK = "#1a1916"
MUTED = "#5c5852"
ACCENT = "#8d3a32"
LINE = "#cfc9bd"
PAPER = "#f7f5f1"
TINT = "#efece6"
FONT = '"Noto Sans CJK SC","Noto Sans SC","PingFang SC",sans-serif'


def wrap(w, h, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{label}">\n'
        f'<rect width="{w}" height="{h}" fill="{PAPER}"/>\n'
        f"{body}\n</svg>\n"
    )


def text(x, y, s, size=13, fill=MUTED, anchor="middle", weight="400"):
    return (
        f"<text x=\"{x}\" y=\"{y}\" text-anchor=\"{anchor}\" fill=\"{fill}\" "
        f"font-family='{FONT}' font-size=\"{size}\" font-weight=\"{weight}\">{s}</text>"
    )


def person(cx, feet, h, stroke=INK, face=True):
    top = feet - h
    hr = 0.105 * h
    hc = top + hr
    neck = hc + hr
    hip = feet - 0.46 * h
    arm = neck + 0.06 * h
    parts = [
        f'<g fill="none" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">',
        f'<circle cx="{cx:.1f}" cy="{hc:.1f}" r="{hr:.1f}" fill="{PAPER}"/>',
        f'<path d="M{cx:.1f} {neck:.1f} L{cx:.1f} {hip:.1f}"/>',
        f'<path d="M{cx:.1f} {arm:.1f} L{cx - 0.16 * h:.1f} {arm + 0.18 * h:.1f}"/>',
        f'<path d="M{cx:.1f} {arm:.1f} L{cx + 0.17 * h:.1f} {arm + 0.14 * h:.1f}"/>',
        f'<path d="M{cx:.1f} {hip:.1f} L{cx - 0.09 * h:.1f} {feet:.1f}"/>',
        f'<path d="M{cx:.1f} {hip:.1f} L{cx + 0.10 * h:.1f} {feet:.1f}"/>',
        "</g>",
    ]
    if face and hr >= 7:
        er = max(0.8, hr * 0.07)
        ey = hc - hr * 0.02
        ex = hr * 0.32
        parts.append(
            f'<g fill="{INK}" stroke="none">'
            f'<circle cx="{cx - ex:.1f}" cy="{ey:.1f}" r="{er:.1f}"/>'
            f'<circle cx="{cx + ex:.1f}" cy="{ey:.1f}" r="{er:.1f}"/>'
            f"</g>"
        )
        parts.append(
            f'<path d="M{cx:.1f} {hc + hr * 0.18:.1f} L{cx:.1f} {hc + hr * 0.40:.1f}" '
            f'fill="none" stroke="{INK}" stroke-width="1.2" stroke-linecap="round"/>'
        )
        parts.append(
            f'<path d="M{cx - hr * 0.22:.1f} {hc + hr * 0.55:.1f} '
            f'Q{cx:.1f} {hc + hr * 0.74:.1f} {cx + hr * 0.22:.1f} {hc + hr * 0.55:.1f}" '
            f'fill="none" stroke="{INK}" stroke-width="1.2" stroke-linecap="round"/>'
        )
    return "\n".join(parts)


def camera(x, y, rot=0, scale=1, accent=False):
    stroke = ACCENT if accent else INK
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({scale})" '
        f'fill="{PAPER}" stroke="{stroke}" stroke-width="1.5" stroke-linejoin="round">'
        f'<rect x="-16" y="-9" width="22" height="18"/>'
        f'<path d="M6 -6 L16 0 L6 6 Z"/>'
        f'<circle cx="-5" cy="-12" r="2.2" fill="{PAPER}"/>'
        f"</g>"
    )


def shot_sizes():
    frames = [
        # name, body height, feet offset from frame bottom (negative = feet below frame)
        ("大远景", 26, -8, True),
        ("远景", 52, -8, True),
        ("全景", 124, -6, False),
        ("中景", 214, 78, False),
        ("近景", 248, 109, False),
        ("特写", 400, 271, False),
    ]
    parts = []
    fw, fh, fy = 100, 150, 18
    for i, (name, hgt, drop, wide) in enumerate(frames):
        fx = 16 + i * 118
        fb = fy + fh
        feet = fb + drop
        cx = fx + fw / 2
        on = " is-on" if i == 3 else ""
        parts.append(f'<g class="shot{on}" data-shot="{i}" tabindex="0" role="button">')
        parts.append(f'<title>{name}</title>')
        parts.append(f'<clipPath id="shot-c{i}"><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}"/></clipPath>')
        parts.append(
            f'<rect class="frame" x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="{PAPER}" stroke="{LINE}"/>'
        )
        parts.append(f'<g clip-path="url(#shot-c{i})">')
        if wide:
            hy = fy + fh * 0.62
            parts.append(
                f'<line x1="{fx}" y1="{hy:.0f}" x2="{fx+fw}" y2="{hy:.0f}" stroke="{LINE}" stroke-width="1"/>'
            )
            parts.append(
                f'<path d="M{fx} {fb} L{fx+18} {hy+8:.0f} L{fx+34} {fb} Z" fill="{TINT}" stroke="{LINE}" stroke-width="1"/>'
            )
        parts.append(f'<line x1="{fx+8}" y1="{fb-1}" x2="{fx+fw-8}" y2="{fb-1}" stroke="{LINE}" stroke-width="1"/>')
        parts.append(person(cx, feet, hgt))
        parts.append("</g>")
        parts.append(text(cx, 192, name, 13))
        parts.append("</g>")
    return wrap(720, 214, "\n".join(parts), "景别阶梯：大远景到特写")


def camera_angles():
    labels = ["仰拍", "平视", "俯拍", "鸟瞰", "荷兰角"]
    parts = ['<g class="diagram-angles">']
    for i, name in enumerate(labels):
        x = 18 + i * 142
        y = 16
        w, h = 128, 150
        rot = ""
        inner = []
        cx, cy = x + w / 2, y + 78
        if i == 4:
            inner.append(
                f'<g transform="rotate(-16 {cx} {cy})">'
            )
        if i == 0:
            inner.append(person(cx, y + 118, 96))
            inner.append(camera(cx, y + 138, -90, 0.85))
        elif i == 1:
            inner.append(person(cx, y + 132, 108))
            inner.append(camera(x + 18, y + 78, 0, 0.8))
        elif i == 2:
            inner.append(person(cx, y + 140, 80))
            inner.append(camera(cx, y + 28, 90, 0.85))
        elif i == 3:
            inner.append(f'<ellipse cx="{cx}" cy="{y+88}" rx="28" ry="10" fill="none" stroke="{INK}" stroke-width="1.5"/>')
            inner.append(f'<circle cx="{cx}" cy="{y+70}" r="14" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>')
            inner.append(camera(cx, y + 28, 90, 0.8))
        else:
            inner.append(
                f'<line x1="{x+16}" y1="{y+78}" x2="{x+w-16}" y2="{y+48}" stroke="{LINE}" stroke-width="1"/>'
            )
            inner.append(person(cx, y + 124, 90))
        block = "\n".join(inner)
        if i == 4:
            block += "</g>"
        parts.append(f'<g class="panel" tabindex="0"><title>{name}</title>')
        parts.append(f'<rect class="frame" x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{LINE}"/>')
        parts.append(block)
        parts.append(text(x + w / 2, y + h + 22, name, 13))
        parts.append("</g>")
    parts.append("</g>")
    return wrap(720, 210, "\n".join(parts), "机位角度：仰拍、平视、俯拍、鸟瞰、荷兰角")


def camera_moves():
    cells = []

    def cell(i, title, drawing):
        col, row = i % 3, i // 3
        x, y = 16 + col * 236, 14 + row * 168
        return (
            f'<g class="panel" tabindex="0"><title>{title}</title>'
            f'<rect class="frame" x="{x}" y="{y}" width="220" height="132" fill="{PAPER}" stroke="{LINE}"/>'
            f"{drawing(x, y)}"
            f"{text(x+110, y+154, title, 13)}"
            f"</g>"
        )

    def push(x, y):
        return (
            person(x + 168, y + 108, 78)
            + camera(x + 46, y + 70, 0, 0.9)
            + f'<path d="M{x+70} {y+70} H{x+120}" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>'
        )

    def pull(x, y):
        return (
            person(x + 168, y + 108, 78)
            + camera(x + 78, y + 70, 0, 0.9)
            + f'<path d="M{x+70} {y+70} H{x+28}" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>'
        )

    def pan(x, y):
        return (
            camera(x + 110, y + 88, 0, 0.95)
            + f'<path d="M{x+70} {y+36} Q{x+110} {y+16} {x+150} {y+36}" fill="none" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#arr)"/>'
            + f'<path d="M{x+150} {y+48} Q{x+110} {y+64} {x+70} {y+48}" fill="none" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#arr)"/>'
        )

    def truck(x, y):
        return (
            person(x + 150, y + 108, 78)
            + camera(x + 48, y + 78, 0, 0.9)
            + f'<path d="M{x+36} {y+112} H{x+96}" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>'
        )

    def follow(x, y):
        return (
            person(x + 150, y + 100, 70)
            + f'<path d="M{x+162} {y+78} H{x+196}" stroke="{INK}" stroke-width="1.5" fill="none" marker-end="url(#arr-ink)"/>'
            + camera(x + 52, y + 72, 0, 0.85)
            + f'<path d="M{x+78} {y+108} H{x+118}" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>'
        )

    def crane(x, y):
        return (
            person(x + 150, y + 112, 70)
            + camera(x + 78, y + 48, 20, 0.85)
            + f'<path d="M{x+48} {y+100} V{y+36}" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>'
            + f'<path d="M{x+36} {y+100} V{y+112}" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>'
        )

    drawings = [
        (0, "推", push),
        (1, "拉", pull),
        (2, "摇", pan),
        (3, "移", truck),
        (4, "跟", follow),
        (5, "升降", crane),
    ]
    body = [
        f'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker>'
        f'<marker id="arr-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 Z" fill="{INK}"/></marker></defs>'
    ]
    body.append('<g class="diagram-moves">')
    for i, title, fn in drawings:
        body.append(cell(i, title, fn))
    body.append("</g>")
    return wrap(720, 360, "\n".join(body), "运镜：推、拉、摇、移、跟、升降")


def composition():
    def panel(x, title, inner):
        return (
            f'<g class="panel" tabindex="0"><title>{title}</title>'
            f'<rect class="frame" x="{x}" y="16" width="220" height="168" fill="{PAPER}" stroke="{LINE}"/>'
            f"{inner}"
            f"{text(x+110, 208, title, 13)}</g>"
        )

    thirds = []
    x = 16
    for i in range(1, 3):
        thirds.append(f'<line x1="{x + i * 220/3:.1f}" y1="16" x2="{x + i * 220/3:.1f}" y2="184" stroke="{LINE}" stroke-width="1"/>')
        thirds.append(f'<line x1="{x}" y1="{16 + i * 168/3:.1f}" x2="{x+220}" y2="{16 + i * 168/3:.1f}" stroke="{LINE}" stroke-width="1"/>')
    # intersection near right-lower third
    px = x + 2 * 220 / 3
    py = 16 + 168 / 3
    thirds.append(person(px, 16 + 150, 100))
    thirds.append(f'<circle cx="{px:.1f}" cy="{py+28:.1f}" r="3" fill="none" stroke="{ACCENT}"/>')

    x2 = 250
    lines = (
        f'<path d="M{x2+20} 184 L{x2+90} 70 L{x2+130} 70 L{x2+200} 184" fill="none" stroke="{INK}" stroke-width="1.5"/>'
        f'<path d="M{x2+40} 184 L{x2+100} 90 L{x2+120} 90 L{x2+180} 184" fill="none" stroke="{LINE}" stroke-width="1"/>'
        + person(x2 + 110, 168, 70)
    )

    x3 = 484
    frame = (
        f'<path d="M{x3+28} 36 H{x3+192} V168 H{x3+28} Z" fill="none" stroke="{INK}" stroke-width="1.5"/>'
        f'<path d="M{x3+48} 52 H{x3+172} V152 H{x3+48} Z" fill="none" stroke="{LINE}" stroke-width="1"/>'
        + person(x3 + 110, 150, 78)
    )
    body = '<g class="diagram-comp">' + panel(16, "三分法", "\n".join(thirds)) + panel(250, "引导线", lines) + panel(484, "框架", frame) + "</g>"
    return wrap(720, 228, body, "构图：三分法、引导线、框架")


def three_point():
    body = f'''
<rect x="80" y="36" width="560" height="280" fill="none" stroke="{LINE}"/>
{text(360, 28, "俯视", 12)}
<circle cx="360" cy="180" r="22" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>
{text(360, 184, "人", 12, INK)}
{camera(360, 300, -90, 1)}
{text(360, 332, "机位", 13)}
<path d="M150 70 L330 160" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
{text(150, 60, "主光", 13, ACCENT)}
<path d="M570 80 L390 160" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 3" fill="none" marker-end="url(#arr-ink)"/>
{text(560, 68, "辅光", 13)}
<path d="M360 70 L360 150" stroke="{INK}" stroke-width="1.5" fill="none" marker-end="url(#arr-ink)"/>
{text(400, 78, "轮廓光", 13)}
<defs>
<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker>
<marker id="arr-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{INK}"/></marker>
</defs>
'''
    return wrap(720, 360, body, "三点布光俯视图：主光、辅光、轮廓光和机位")


def high_low():
    def face(x, dark):
        bg = INK if dark else TINT
        skin = "#2a2826" if dark else PAPER
        shadow = INK if not dark else "#141311"
        return (
            f'<rect x="{x}" y="20" width="300" height="200" fill="{bg}" stroke="{LINE}"/>'
            f'<circle cx="{x+150}" cy="110" r="48" fill="{skin}" stroke="{INK if not dark else "#8a847c"}" stroke-width="1.5"/>'
            f'<path d="M{x+150} 62 A48 48 0 0 0 {x+108} 140 L{x+150} 150 Z" fill="{shadow}" opacity="{"0.18" if not dark else "0.85"}"/>'
            f'<circle cx="{x+136}" cy="104" r="2" fill="{ACCENT if dark else INK}"/>'
            f'<circle cx="{x+164}" cy="104" r="2" fill="{INK if not dark else "#8a847c"}"/>'
        )

    body = face(40, False) + face(380, True) + text(190, 244, "高调", 14) + text(530, 244, "低调", 14, ACCENT)
    return wrap(720, 268, body, "高调与低调")


def axis_180():
    body = f'''
<line x1="80" y1="150" x2="640" y2="150" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>
{text(360, 126, "轴线", 13, INK)}
<circle cx="230" cy="150" r="16" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>
{text(230, 154, "A", 12, INK)}
<circle cx="490" cy="150" r="16" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>
{text(490, 154, "B", 12, INK)}
{text(230, 186, "演员 A", 12)}
{text(490, 186, "演员 B", 12)}
<rect x="80" y="36" width="560" height="88" fill="url(#hatch)"/>
{text(430, 86, "禁区", 16, ACCENT)}
{camera(200, 78, 90, 0.75, accent=True)}
<path d="M186 64 L214 92 M214 64 L186 92" stroke="{ACCENT}" stroke-width="1.5"/>
{camera(280, 248, -90, 0.9)}
{text(280, 286, "机位 A · 拍 B", 13)}
{camera(460, 248, -90, 0.9)}
{text(460, 286, "机位 B · 拍 A", 13)}
<path d="M292 228 L390 168" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
<path d="M448 228 L350 168" stroke="{ACCENT}" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
<defs>
<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker>
<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse">
<path d="M0 8 L8 0" stroke="{LINE}" stroke-width="1"/>
</pattern>
</defs>
'''
    return wrap(720, 310, body, "180 度轴线：机位 A、机位 B 在同一侧，对面是禁区")


def ots():
    def shoulder(x, flip, who):
        # flip False: shoulder from left, face on the right
        face_x = x + (168 if not flip else 70)
        sh_x = x + (36 if not flip else 184)
        return (
            f'<rect x="{x}" y="20" width="250" height="160" fill="{PAPER}" stroke="{LINE}"/>'
            f'<path d="M{sh_x} 180 C{sh_x + (40 if not flip else -40)} 120 {sh_x + (70 if not flip else -70)} 150 {x + (120 if not flip else 130)} 180" fill="{TINT}" stroke="{INK}" stroke-width="1.5"/>'
            f'<circle cx="{face_x}" cy="78" r="22" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>'
            f'<circle cx="{face_x-8}" cy="74" r="1.6" fill="{INK}"/>'
            f'<circle cx="{face_x+8}" cy="74" r="1.6" fill="{INK}"/>'
            f'<path d="M{face_x-8} {90} Q{face_x} {96} {face_x+8} {90}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
            + text(x + 125, 204, who, 13)
        )

    plan = (
        f'<circle cx="330" cy="250" r="8" fill="{PAPER}" stroke="{INK}"/>'
        f'<circle cx="390" cy="250" r="8" fill="{PAPER}" stroke="{INK}"/>'
        + text(330, 272, "A", 11, INK)
        + text(390, 272, "B", 11, INK)
        + camera(300, 292, -40, 0.55)
        + camera(420, 292, 220, 0.55)
    )
    body = shoulder(40, False, "过肩 · 拍 B") + shoulder(430, True, "过肩 · 拍 A") + plan
    return wrap(720, 320, body, "正反打过肩：从 A 肩后拍 B，再从 B 肩后拍 A")


def kuleshov():
    def row(y, obj, label):
        face = (
            f'<rect x="40" y="{y}" width="120" height="80" fill="{PAPER}" stroke="{LINE}"/>'
            + f'<circle cx="100" cy="{y+40}" r="22" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>'
            + f'<circle cx="92" cy="{y+36}" r="1.5" fill="{INK}"/><circle cx="108" cy="{y+36}" r="1.5" fill="{INK}"/>'
            + f'<path d="M92 {y+50} H108" stroke="{INK}" stroke-width="1.2"/>'
        )
        plus = text(190, y + 48, "+", 18, INK)
        thing = f'<rect x="220" y="{y}" width="120" height="80" fill="{PAPER}" stroke="{LINE}"/>' + obj(220, y)
        arrow = f'<path d="M360 {y+40} H420" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#arr)"/>'
        cap = text(520, y + 46, label, 16, ACCENT, anchor="start")
        return face + plus + thing + arrow + cap

    def soup(x, y):
        return f'<path d="M{x+30} {y+48} H{x+90} Q{x+90} {y+62} {x+60} {y+62} Q{x+30} {y+62} {x+30} {y+48}" fill="none" stroke="{INK}" stroke-width="1.5"/><path d="M{x+78} {y+40} q8 -8 16 0" fill="none" stroke="{LINE}"/>'

    def coffin(x, y):
        return f'<path d="M{x+36} {y+28} H{x+84} L{x+92} {y+58} H{x+28} Z" fill="none" stroke="{INK}" stroke-width="1.5"/><path d="M{x+46} {y+28} V{y+20} H{x+74} V{y+28}" fill="none" stroke="{INK}" stroke-width="1.5"/>'

    def child(x, y):
        return person(x + 60, y + 70, 48)

    body = (
        '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker></defs>'
        + text(100, 28, "同一张脸", 12)
        + row(40, soup, "饥饿")
        + row(140, coffin, "悲伤")
        + row(240, child, "慈爱")
    )
    return wrap(720, 350, body, "库里肖夫效应：同一张脸接上不同物体，意义会变")


def jl_cut():
    def track(y, label, segs):
        bits = [text(36, y + 28, label, 13, INK, anchor="start")]
        for x, w, title, accent in segs:
            fill = "#f3e4e1" if accent else TINT
            stroke = ACCENT if accent else LINE
            bits.append(f'<rect x="{x}" y="{y}" width="{w}" height="44" fill="{fill}" stroke="{stroke}"/>')
            bits.append(text(x + w / 2, y + 28, title, 13, ACCENT if accent else INK))
        return "".join(bits)

    j = (
        text(360, 28, "J 切 · 下一镜的声音先进来", 14, INK)
        + track(48, "画面", [(80, 250, "镜头 A", False), (330, 250, "镜头 B", False)])
        + track(110, "声音", [(80, 180, "声 A", False), (260, 320, "声 B", True)])
    )
    l = (
        text(360, 190, "L 切 · 上一镜的声音留到下一镜", 14, INK)
        + track(214, "画面", [(80, 250, "镜头 A", False), (330, 250, "镜头 B", False)])
        + track(276, "声音", [(80, 320, "声 A", True), (400, 180, "声 B", False)])
    )
    return wrap(720, 350, j + l, "J 切和 L 切的时间线")


def three_act():
    # curve points
    pts = [(40, 200), (120, 190), (180, 150), (280, 120), (360, 90), (460, 140), (520, 70), (600, 40), (680, 80)]
    d = "M " + " L ".join(f"{x} {y}" for x, y in pts)
    marks = [
        (150, 168, "激励事件"),
        (360, 78, "中点"),
        (470, 154, "最低谷"),
        (600, 28, "高潮"),
    ]
    labels = "".join(text(x, y, t, 12, ACCENT) for x, y, t in marks)
    bands = (
        f'<line x1="40" y1="230" x2="680" y2="230" stroke="{LINE}"/>'
        f'<line x1="200" y1="40" x2="200" y2="230" stroke="{LINE}" stroke-dasharray="3 3"/>'
        f'<line x1="520" y1="40" x2="520" y2="230" stroke="{LINE}" stroke-dasharray="3 3"/>'
        + text(120, 258, "第一幕 · 建置", 13)
        + text(360, 258, "第二幕 · 对抗", 13)
        + text(600, 258, "第三幕 · 解决", 13)
        + text(120, 276, "约 25%", 11)
        + text(360, 276, "约 50%", 11)
        + text(600, 276, "约 25%", 11)
    )
    body = f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="1.75"/>' + labels + bands
    return wrap(720, 300, body, "三幕曲线：建置、对抗、解决")


def heros_journey():
    import math
    labels = ["日常", "召唤", "拒绝", "导师", "门槛", "考验", "洞穴", "磨难", "奖赏", "归途", "复活", "回归"]
    cx, cy, r = 360, 168, 108
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.5"/>']
    parts.append(text(cx, cy + 4, "英雄之旅", 14, INK))
    for i, name in enumerate(labels):
        ang = -math.pi / 2 + i * (2 * math.pi / 12)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        lx = cx + (r + 36) * math.cos(ang)
        ly = cy + (r + 36) * math.sin(ang) + 4
        dot = ACCENT if name == "磨难" else INK
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{dot}"/>')
        parts.append(text(f"{lx:.1f}", f"{ly:.1f}", name, 12, ACCENT if name == "磨难" else MUTED))
    return wrap(720, 340, "\n".join(parts), "英雄之旅圆环")


def episode_arc():
    parts = [
        f'<path d="M40 70 Q360 20 680 70" fill="none" stroke="{INK}" stroke-width="1.5"/>',
        text(360, 36, "季问题", 13, INK),
    ]
    for i in range(4):
        x = 70 + i * 160
        parts.append(
            f'<path d="M{x} 180 Q{x+60} 110 {x+120} 180" fill="none" stroke="{ACCENT}" stroke-width="1.5"/>'
        )
        parts.append(text(x + 60, 200, f"第 {i+1} 集", 12))
        parts.append(f'<path d="M{x+112} 168 l8 10 h-16 z" fill="{ACCENT}"/>')
        parts.append(text(x + 60, 222, "钩子", 11, ACCENT))
    parts.append(text(70, 250, "冷开场", 12, ACCENT, anchor="start"))
    parts.append(f'<circle cx="58" cy="160" r="4" fill="{ACCENT}"/>')
    return wrap(720, 280, "\n".join(parts), "集弧线与季弧线，集尾留钩子")


def story_braid():
    import math
    parts = []
    colors = [ACCENT, INK, MUTED]
    names = ["A 主线", "B 副线", "C 伏笔"]
    for k, (col, name) in enumerate(zip(colors, names)):
        pts = []
        for i in range(37):
            x = 40 + i * 16
            y = 110 + math.sin((i / 4) + k * 2.1) * 36
            pts.append(f"{x:.0f} {y:.0f}")
        parts.append(f'<path d="M {" L ".join(pts)}" fill="none" stroke="{col}" stroke-width="1.75"/>')
        parts.append(text(80 + k * 200, 200, name, 13, col))
    return wrap(720, 230, "\n".join(parts), "A、B、C 三条故事线交织")


def blocking_plan():
    body = f'''
<rect x="80" y="30" width="560" height="300" fill="none" stroke="{INK}" stroke-width="1.5"/>
<path d="M80 250 V290" stroke="{PAPER}" stroke-width="8"/>
<path d="M80 250 V290" stroke="{INK}" stroke-width="1.5"/>
{text(58, 274, "门", 12, anchor="end")}
<rect x="480" y="30" width="70" height="8" fill="{TINT}" stroke="{LINE}"/>
{text(515, 22, "窗", 12)}
<rect x="300" y="150" width="90" height="50" fill="{TINT}" stroke="{LINE}"/>
{text(345, 178, "桌", 12, INK)}
<circle cx="250" cy="175" r="12" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>
{text(250, 179, "A", 12, INK)}
<circle cx="450" cy="175" r="12" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>
{text(450, 179, "B", 12, INK)}
<line x1="180" y1="175" x2="520" y2="175" stroke="{INK}" stroke-dasharray="4 3"/>
{text(360, 164, "轴线", 11)}
{camera(280, 270, -90, 0.8)}
{text(250, 300, "机位 1", 12)}
{camera(430, 270, -90, 0.8)}
{text(460, 300, "机位 2", 12)}
'''
    return wrap(720, 350, body, "场面调度平面图：演员、轴线和同侧机位")


def storyboard():
    scenes = [
        ("1", "大远景", "雨夜巷口"),
        ("2", "中景 · 跟", "她回头"),
        ("3", "特写", "短信"),
        ("4", "近景 · 仰", "抬头"),
    ]
    parts = []
    for i, (n, size, cap) in enumerate(scenes):
        x = 24 + i * 176
        parts.append(f'<rect x="{x}" y="24" width="156" height="100" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>')
        parts.append(f'<circle cx="{x+16}" cy="40" r="9" fill="{PAPER}" stroke="{ACCENT}"/>')
        parts.append(text(x + 16, 44, n, 11, ACCENT))
        if i == 0:
            parts.append(f'<line x1="{x+16}" y1="90" x2="{x+140}" y2="90" stroke="{LINE}"/>')
            parts.append(person(x + 78, 96, 28))
        elif i == 1:
            parts.append(person(x + 70, 108, 60))
            parts.append(f'<path d="M{x+100} 70 H{x+136}" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#arr)"/>')
        elif i == 2:
            parts.append(f'<rect x="{x+48}" y="48" width="60" height="40" fill="{TINT}" stroke="{INK}"/>')
            parts.append(text(x + 78, 72, "短信", 11, INK))
        else:
            parts.append(person(x + 78, 118, 90))
        parts.append(text(x + 78, 146, size, 12, INK))
        parts.append(text(x + 78, 166, cap, 12))
    parts.insert(0, f'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker></defs>')
    return wrap(720, 190, "\n".join(parts), "四格故事板：镜号、景别、画面")


def prompt_anatomy():
    chunks = [
        ("近景", "景别"),
        ("女人", "主体"),
        ("猛地抬头", "动作"),
        ("雨夜巷口", "环境"),
        ("左侧冷光", "光线"),
        ("缓推", "运镜"),
        ("写实", "风格"),
    ]
    parts = []
    x = 16
    for i, (word, kind) in enumerate(chunks):
        w = 96
        parts.append(f'<rect x="{x}" y="70" width="{w-8}" height="64" fill="{TINT if i % 2 == 0 else PAPER}" stroke="{ACCENT if i == 0 else LINE}"/>')
        parts.append(text(x + (w - 8) / 2, 98, word, 14, INK))
        parts.append(text(x + (w - 8) / 2, 116, kind, 11, ACCENT))
        if i < len(chunks) - 1:
            parts.append(f'<path d="M{x+w-6} 102 H{x+w+2}" stroke="{LINE}"/>')
        x += w
    parts.append(text(360, 40, "一条提示词拆开之后", 14, INK))
    parts.append(text(360, 180, "先有景别和主体，再写动作、环境、光和运动", 12))
    return wrap(720, 210, "\n".join(parts), "提示词解剖：景别、主体、动作、环境、光线、运镜、风格")


def sound_layers():
    rows = [
        (40, "对白", [(80, 420, False)], "画内 / 画外"),
        (110, "音效", [(80, 200, False), (300, 40, True), (360, 220, False)], "沉默留白"),
        (180, "音乐", [(220, 360, False)], "无源，晚入"),
    ]
    parts = []
    for y, name, segs, note in rows:
        parts.append(text(36, y + 26, name, 13, INK, anchor="start"))
        for x, w, gap in segs:
            if gap:
                parts.append(text(x + w / 2, y + 26, "静", 12, ACCENT))
            else:
                parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="40" fill="{TINT}" stroke="{LINE}"/>')
        parts.append(text(640, y + 26, note, 12, anchor="start"))
    return wrap(720, 250, "\n".join(parts), "声音三层：对白、音效、音乐，中间可以沉默")


def logline():
    words = ["主人公", "想要什么", "阻碍", "赌注"]
    parts = []
    for i, w in enumerate(words):
        x = 30 + i * 175
        parts.append(f'<rect x="{x}" y="70" width="140" height="64" fill="{PAPER}" stroke="{INK}"/>')
        parts.append(text(x + 70, 108, w, 15, INK))
        if i < 3:
            parts.append(f'<path d="M{x+148} 102 H{x+168}" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#arr)"/>')
    parts.insert(0, f'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker></defs>')
    return wrap(720, 200, "\n".join(parts), "一句话梗概：主人公、欲望、阻碍、赌注")


def want_need():
    body = f'''
<rect x="80" y="50" width="200" height="70" fill="{PAPER}" stroke="{INK}"/>
{text(180, 92, "想要 Want", 15, INK)}
<rect x="440" y="50" width="200" height="70" fill="{TINT}" stroke="{ACCENT}"/>
{text(540, 92, "需要 Need", 15, ACCENT)}
<path d="M180 120 C180 180 360 180 360 230" fill="none" stroke="{INK}" stroke-width="1.5"/>
<path d="M360 230 C360 250 460 200 540 140" fill="none" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#arr)"/>
{text(300, 210, "追想要的路上，撞见需要", 13)}
<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker></defs>
'''
    return wrap(720, 280, body, "欲望和需求：外在目标弯向内在成长")


def conflict_layers():
    boxes = [
        (80, 40, 560, 200, "外部 · 社会 / 环境 / 命运", MUTED),
        (140, 80, 440, 130, "人际 · 对手", INK),
        (220, 120, 280, 60, "内心 · 自己", ACCENT),
    ]
    parts = []
    for x, y, w, h, label, col in boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{col}" stroke-width="1.5"/>')
        parts.append(text(x + w / 2, y + 22, label, 13, col))
    return wrap(720, 280, "\n".join(parts), "三层冲突：内心、人际、外部")


def scene_inout():
    body = f'''
<rect x="40" y="80" width="150" height="48" fill="url(#hatch)" stroke="{LINE}"/>
<rect x="190" y="80" width="340" height="48" fill="{TINT}" stroke="{ACCENT}"/>
<rect x="530" y="80" width="150" height="48" fill="url(#hatch)" stroke="{LINE}"/>
{text(115, 108, "寒暄", 13)}
{text(360, 108, "这场戏真正发生的事", 14, ACCENT)}
{text(605, 108, "收尾废话", 13)}
{text(190, 160, "晚进", 13, ACCENT)}
{text(530, 160, "早出", 13, ACCENT)}
<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0 8 L8 0" stroke="{LINE}"/></pattern></defs>
'''
    return wrap(720, 200, body, "晚进早出：砍掉一场戏两头的废话")


def shot_strip():
    parts = [f'<rect x="30" y="40" width="660" height="120" fill="{INK}"/>']
    for i in range(8):
        parts.append(f'<rect x="{46 + i * 80}" y="48" width="14" height="16" fill="{PAPER}"/>')
        parts.append(f'<rect x="{46 + i * 80}" y="136" width="14" height="16" fill="{PAPER}"/>')
    labels = ["镜号", "景别", "运镜", "画面"]
    for i, lab in enumerate(labels):
        x = 70 + i * 160
        parts.append(f'<rect x="{x}" y="70" width="130" height="70" fill="{PAPER}"/>')
        parts.append(text(x + 65, 110, lab, 14, INK))
    return wrap(720, 200, "\n".join(parts), "分镜表的四个核心字段")


def workflow():
    words = [("前期", "剧本 · 分镜 · 计划"), ("拍摄", "调度 · 表演 · 覆盖"), ("后期", "剪辑 · 声音 · 调色")]
    parts = []
    for i, (a, b) in enumerate(words):
        x = 40 + i * 230
        parts.append(f'<rect x="{x}" y="70" width="180" height="80" fill="{PAPER}" stroke="{INK}"/>')
        parts.append(text(x + 90, 104, a, 16, INK))
        parts.append(text(x + 90, 128, b, 12))
        if i < 2:
            parts.append(f'<path d="M{x+188} 110 H{x+222}" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#arr)"/>')
    parts.insert(0, f'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker></defs>')
    return wrap(720, 220, "\n".join(parts), "导演流程：前期、拍摄、后期")


def crew_map():
    def box(x, y, w, h, title, sub=None, accent=False, size=14):
        stroke = ACCENT if accent else INK
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{stroke}"/>']
        cx = x + w / 2
        if sub:
            out.append(text(cx, y + h / 2 - 3, title, size, INK))
            out.append(text(cx, y + h / 2 + 14, sub, 11))
        else:
            out.append(text(cx, y + h / 2 + 5, title, size, INK))
        return "\n".join(out)

    arrow = f'stroke="{INK}" stroke-width="1.25" fill="none" marker-end="url(#arr-ink)"'
    dashed = f'stroke="{MUTED}" stroke-width="1.25" fill="none" stroke-dasharray="5 4"'
    p = [
        f'<defs><marker id="arr-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{INK}"/></marker></defs>',
        text(30, 30, "制片线 · 钱、人、时间", 12, MUTED, "start"),
        text(690, 30, "创作线 · 作品长什么样", 12, MUTED, "end"),
        box(270, 18, 180, 40, "出品方 / 平台"),
        f'<path d="M360 58 V88" {arrow}/>',
        box(270, 92, 180, 44, "制片人", "统管项目、预算、进度"),
        f'<path d="M270 114 H115 V170" {arrow}/>',
        box(30, 174, 170, 44, "执行制片 / 制片主任", "现场后勤与花销", size=13),
        f'<path d="M115 218 V248" {arrow}/>',
        box(30, 252, 170, 44, "统筹", "排期与通告单"),
        f'<path d="M360 136 V170" {arrow}/>',
        box(290, 174, 140, 44, "导演", "对创作负总责", accent=True),
        f'<path d="M438 196 H522" {arrow} marker-start="url(#arr-ink)"/>',
        box(530, 174, 160, 44, "编剧 / 总编剧", "故事讲什么"),
        f'<path d="M360 218 V320" stroke="{INK}" stroke-width="1.25" fill="none"/>',
        f'<path d="M84 320 H636" stroke="{INK}" stroke-width="1.25" fill="none"/>',
        f'<rect x="14" y="336" width="692" height="150" fill="none" stroke="{LINE}"/>',
        text(24, 478, "各部门负责人", 11, MUTED, "start"),
        f'<path d="M44 296 V336" {dashed}/>',
        text(52, 318, "预算 · 排期", 11, MUTED, "start"),
    ]
    heads = [
        ("摄影指导", ["摄影组", "灯光组", "机械组"], True),
        ("美术指导", ["置景 · 道具", "服装 · 化妆"], True),
        ("演员", ["主演 · 配角", "群演"], False),
        ("副导演 / 场记", ["现场调度", "场记单"], False),
        ("剪辑师", ["调色 · 视效", "声音 · 混录", "作曲"], False),
    ]
    for i, (name, subs, accent) in enumerate(heads):
        x = 24 + i * 138
        cx = x + 60
        p.append(f'<path d="M{cx} 320 V352" {arrow}/>')
        p.append(box(x, 356, 120, 38, name, accent=accent, size=13 if len(name) > 4 else 14))
        for j, s in enumerate(subs):
            p.append(text(cx, 416 + j * 18, s, 12))
    p.append(f'<rect x="24" y="502" width="14" height="10" fill="{PAPER}" stroke="{ACCENT}"/>')
    p.append(text(46, 511, "朱红框：创作铁三角　实线：创作上向导演负责　虚线：预算和排期对接制片", 12, MUTED, "start"))
    return wrap(720, 528, "\n".join(p), "剧组汇报与协作关系：制片线管钱、人和时间，创作线由导演统领各部门")


def verb_adjective():
    body = f'''
<rect x="40" y="40" width="300" height="120" fill="{PAPER}" stroke="{LINE}"/>
{text(190, 78, "形容词", 13)}
{text(190, 112, "你看起来很生气", 16, MUTED)}
<line x1="90" y1="108" x2="290" y2="108" stroke="{ACCENT}" stroke-width="1.25"/>
<rect x="380" y="40" width="300" height="120" fill="{PAPER}" stroke="{ACCENT}"/>
{text(530, 78, "动词", 13, ACCENT)}
{text(530, 112, "摔上门，别看他", 16, INK)}
'''
    return wrap(720, 200, body, "指导演员用动词，不用形容词")


def coverage():
    body = f'''
<rect x="40" y="30" width="250" height="180" fill="none" stroke="{INK}"/>
<circle cx="110" cy="110" r="10" fill="{PAPER}" stroke="{INK}"/>
<circle cx="210" cy="110" r="10" fill="{PAPER}" stroke="{INK}"/>
{text(110, 114, "A", 11, INK)}
{text(210, 114, "B", 11, INK)}
{camera(160, 180, -90, 0.7)}
{text(160, 198, "主镜头", 12)}
{text(360, 60, "1  主镜头 · 全场演完", 14, INK, anchor="start")}
{text(360, 96, "2  覆盖 A · 过肩 / 近景", 14, INK, anchor="start")}
{text(360, 132, "3  覆盖 B · 过肩 / 近景", 14, INK, anchor="start")}
{text(360, 168, "4  插入 · 手、道具、门", 14, ACCENT, anchor="start")}
'''
    return wrap(720, 240, body, "一场戏的覆盖：主镜头、正反打、插入")


def turnaround():
    parts = []
    labels = ["正面", "侧面", "背面"]
    for i, lab in enumerate(labels):
        x = 80 + i * 210
        parts.append(f'<rect x="{x}" y="24" width="160" height="200" fill="{PAPER}" stroke="{LINE}"/>')
        parts.append(person(x + 80, 190, 140, face=(i == 0)))
        if i == 0:
            parts.append(f'<path d="M{x+58} 78 H{x+102}" stroke="{ACCENT}" stroke-width="2"/>')
        elif i == 1:
            parts.append(f'<path d="M{x+70} 78 H{x+96}" stroke="{ACCENT}" stroke-width="2"/>')
        else:
            parts.append(f'<path d="M{x+62} 90 H{x+98}" stroke="{ACCENT}" stroke-width="2"/>')
        parts.append(text(x + 80, 246, lab, 13))
    parts.append(text(360, 276, "同一处标记（领口）三面都在", 12, ACCENT))
    return wrap(720, 300, "\n".join(parts), "角色转面：正面、侧面、背面保持同一标记")


def compliance():
    gates = ["素材权利", "肖像同意", "平台规则"]
    parts = [f'<path d="M40 110 H680" stroke="{LINE}" stroke-width="1.5"/>']
    for i, name in enumerate(gates):
        x = 80 + i * 210
        parts.append(f'<rect x="{x}" y="70" width="150" height="80" fill="{PAPER}" stroke="{INK}"/>')
        parts.append(text(x + 75, 116, name, 15, INK))
        parts.append(f'<circle cx="{x+75}" cy="110" r="0"/>')
    parts.append(text(360, 190, "三道门都过了，再生成、再发布", 13, ACCENT))
    return wrap(720, 230, "\n".join(parts), "合规三道门：素材权利、肖像同意、平台规则")


def color_pair():
    body = f'''
<rect x="60" y="40" width="250" height="160" fill="#3e4c52"/>
<rect x="410" y="40" width="250" height="160" fill="{ACCENT}"/>
{person(185, 170, 110, stroke="{PAPER}")}
{person(535, 170, 110, stroke="{PAPER}")}
{text(185, 230, "青 · 背景冷", 14, INK)}
{text(535, 230, "橙红 · 主体暖", 14, ACCENT)}
{text(360, 270, "互补色让人从背景里站出来", 13)}
'''
    # person() stroke argument can't be a format leftover - I passed stroke="{PAPER}" wrongly as literal with quotes inside the f-string.
    return wrap(720, 300, body, "互补色：冷背景和暖主体")


def color_pair_fixed():
    cold = person(185, 170, 110, stroke=PAPER)
    warm = person(535, 170, 110, stroke=PAPER)
    body = (
        f'<rect x="60" y="40" width="250" height="160" fill="#3e4c52"/>'
        f'<rect x="410" y="40" width="250" height="160" fill="{ACCENT}"/>'
        + cold + warm
        + text(185, 230, "青 · 背景冷", 14)
        + text(535, 230, "橙红 · 主体暖", 14, ACCENT)
        + text(360, 270, "互补色让人从背景里站出来", 13)
    )
    return wrap(720, 300, body, "互补色：冷背景和暖主体")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    diagrams = {
        "shot-sizes": shot_sizes(),
        "camera-angles": camera_angles(),
        "camera-moves": camera_moves(),
        "composition": composition(),
        "three-point": three_point(),
        "high-low-key": high_low(),
        "axis-180": axis_180(),
        "ots-reverse": ots(),
        "kuleshov": kuleshov(),
        "jl-cut": jl_cut(),
        "three-act": three_act(),
        "heros-journey": heros_journey(),
        "episode-arc": episode_arc(),
        "story-braid": story_braid(),
        "blocking-plan": blocking_plan(),
        "storyboard": storyboard(),
        "prompt-anatomy": prompt_anatomy(),
        "sound-layers": sound_layers(),
        "logline": logline(),
        "want-need": want_need(),
        "conflict-layers": conflict_layers(),
        "scene-inout": scene_inout(),
        "shot-strip": shot_strip(),
        "workflow": workflow(),
        "crew-map": crew_map(),
        "verb-adjective": verb_adjective(),
        "coverage": coverage(),
        "turnaround": turnaround(),
        "compliance": compliance(),
        "color-pair": color_pair_fixed(),
    }
    for name, data in diagrams.items():
        for token in ("arr-ink", "arr", "hatch"):
            data = data.replace(f'id="{token}"', f'id="{name}-{token}"')
            data = data.replace(f"url(#{token})", f"url(#{name}-{token})")
        (OUT / f"{name}.svg").write_text(data, encoding="utf-8")
    print(f"wrote {len(diagrams)} diagrams")


if __name__ == "__main__":
    main()
