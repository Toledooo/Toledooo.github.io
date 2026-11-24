"""SVGs animados gerados em Python. As animações ficam no CSS (assets/style.css),
que as desliga em `prefers-reduced-motion`. Textos são escapados."""
from __future__ import annotations

import colorsys
import random
from html import escape

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#9d6cd8", "Java": "#b07219", "Shell": "#89e051", "Dockerfile": "#384d54",
    "PLpgSQL": "#336790", "PLSQL": "#dad8d8", "TSQL": "#e38c00", "Jupyter Notebook": "#DA5B0B",
    "Go": "#00ADD8", "Rust": "#dea584", "C": "#8a8a8a", "C++": "#f34b7d", "C#": "#6fb04f",
    "PHP": "#8892bf", "Ruby": "#cc342d", "Kotlin": "#A97BFF", "Jinja": "#a52a22",
}
OTHER_COLOR = "#6e7681"


def lang_color(name: str) -> str:
    if name in LANG_COLORS:
        return LANG_COLORS[name]
    hue = (sum(ord(c) for c in name) * 37 % 360) / 360
    r, g, b = colorsys.hls_to_rgb(hue, 0.6, 0.5)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def aggregate_languages(per_repo: list[dict[str, int]], top: int = 6) -> list[tuple[str, float]]:
    """Soma bytes por linguagem e devolve [(nome, percentual)], agrupando o resto em 'other'."""
    total: dict[str, int] = {}
    for langs in per_repo:
        for name, size in langs.items():
            total[name] = total.get(name, 0) + size
    grand = sum(total.values())
    if not grand:
        return []
    ranked = sorted(total.items(), key=lambda kv: (-kv[1], kv[0]))
    shown = [(n, s * 100 / grand) for n, s in ranked[:top]]
    rest = sum(s for _, s in ranked[top:])
    if rest:
        shown.append(("other", rest * 100 / grand))
    return shown


def pipeline_svg(nodes: list[str], label: str) -> str:
    """Diagrama do Hero: caixas ligadas por linhas tracejadas com fluxo animado."""
    if not nodes:
        return ""
    char_w, pad, h, gap = 9.0, 14, 44, 30
    widths = [len(n) * char_w + pad * 2 for n in nodes]
    total = sum(widths) + gap * (len(nodes) - 1)
    y_mid = 4 + h / 2
    x = 0.0
    parts = []
    for i, (node, w) in enumerate(zip(nodes, widths)):
        parts.append(
            f'<g class="pipe-node" style="--i:{i}">'
            f'<rect x="{x:.1f}" y="4" width="{w:.1f}" height="{h}" rx="6"/>'
            f'<text x="{x + w / 2:.1f}" y="{y_mid + 5:.1f}" text-anchor="middle">{escape(node)}</text></g>'
        )
        if i < len(nodes) - 1:
            x1, x2 = x + w, x + w + gap
            parts.append(
                f'<line class="pipe-link" x1="{x1 + 4:.1f}" y1="{y_mid}" x2="{x2 - 4:.1f}" y2="{y_mid}"/>'
            )
        x += w + gap
    return (
        f'<svg class="pipeline" viewBox="0 0 {total:.1f} {h + 8}" role="img" '
        f'aria-label="{escape(label)}" xmlns="http://www.w3.org/2000/svg">'
        f'<title>{escape(label)}</title>{"".join(parts)}</svg>'
    )


def language_bars_svg(langs: list[tuple[str, float]], other_label: str, label: str) -> str:
    """Barras horizontais de linguagens. Percentual em texto: nada depende só de cor."""
    if not langs:
        return ""
    row_h, label_w, track_w, pct_w = 30, 120, 230, 60
    width = label_w + track_w + pct_w
    rows = []
    for i, (name, pct) in enumerate(langs):
        y = i * row_h
        shown = other_label if name == "other" else name
        color = OTHER_COLOR if name == "other" else lang_color(name)
        fill_w = max(track_w * pct / 100, 2)
        rows.append(
            f'<g transform="translate(0 {y})">'
            f'<text class="bar-label" x="0" y="19">{escape(shown)}</text>'
            f'<rect class="bar-track" x="{label_w}" y="7" width="{track_w}" height="14" rx="3"/>'
            f'<rect class="bar" x="{label_w}" y="7" width="{fill_w:.1f}" height="14" rx="3" '
            f'fill="{color}" style="--i:{i}"/>'
            f'<text class="bar-pct" x="{width}" y="19" text-anchor="end">{pct:.1f}%</text></g>'
        )
    return (
        f'<svg class="lang-bars" viewBox="0 0 {width} {len(langs) * row_h}" role="img" '
        f'aria-label="{escape(label)}" xmlns="http://www.w3.org/2000/svg">'
        f'<title>{escape(label)}</title>{"".join(rows)}</svg>'
    )


def card_svg(name: str, langs: dict[str, int]) -> str:
    """Imagem padrão de um projeto (quando não há docs/preview.png): matriz de pontos
    determinística a partir do nome, com alguns pontos piscando, e a barra de linguagens."""
    w, h, cols, rows = 480, 240, 24, 8
    rnd = random.Random(name)
    dots = []
    for r in range(rows):
        for c in range(cols):
            x, y = 20 + c * 18.5, 70 + r * 14
            if rnd.random() < 0.13:
                delay = rnd.uniform(0, 4)
                dots.append(
                    f'<circle class="dot hot" cx="{x:.1f}" cy="{y}" r="2.6" style="--d:{delay:.2f}s"/>'
                )
            else:
                dots.append(f'<circle class="dot" cx="{x:.1f}" cy="{y}" r="1.6"/>')
    title = name if len(name) <= 30 else name[:29] + "…"
    total = sum(langs.values())
    segs, x = [], 20.0
    for lang, size in sorted(langs.items(), key=lambda kv: -kv[1])[:5] if total else []:
        seg_w = (w - 40) * size / total
        segs.append(
            f'<rect x="{x:.1f}" y="206" width="{max(seg_w - 1.5, 1):.1f}" height="8" rx="2" '
            f'fill="{lang_color(lang)}"/>'
        )
        x += seg_w
    return (
        f'<svg class="card-art" viewBox="0 0 {w} {h}" aria-hidden="true" '
        f'xmlns="http://www.w3.org/2000/svg"><rect width="{w}" height="{h}" class="card-bg"/>'
        f'<text x="20" y="38" class="card-title">$ cat {escape(title)}/</text>'
        f'{"".join(dots)}{"".join(segs)}</svg>'
    )
