"""Generate static SVG charts for the README (baseline attack + SensorGuard effect)."""
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
FONT = "font-family=\"'Segoe UI', 'Helvetica Neue', Arial, sans-serif\""
BG, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"
STYLE = f"""<style>
 .t1{{font-size:13px;fill:{INK}}} .t2{{font-size:11.5px;fill:{INK2}}} .tm{{font-size:11px;fill:{MUTED}}}
 .tb{{font-size:13px;font-weight:700;fill:{INK}}} .th{{font-size:14px;font-weight:700;fill:{INK}}}
 .grid{{stroke:{GRID};stroke-width:1}} .base{{stroke:{BASE};stroke-width:1}} .link{{stroke:#b9b8b2;stroke-width:2}}
</style>"""

MODELS = ["Gemini 3.5 flash-lite", "GPT-5.6 luna", "Claude Haiku 5.5", "GPT-6 luna", "GLM 5.3 flash", "DeepSeek flash"]


def svg(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {FONT}>\n'
            f'<title>{title}</title>\n{STYLE}\n<rect width="{w}" height="{h}" fill="{BG}"/>\n{body}</svg>\n')


# ---------- Fig 2: heatmap ASR theo taxonomy (baseline) ----------
RAMP = [(0, "#f0efec"), (5, "#cde2fb"), (10, "#9ec5f4"), (20, "#6da7ec"), (30, "#3987e5"), (40, "#256abf"), (50, "#104281")]


def ramp(v):
    c = RAMP[0][1]
    for t, col in RAMP:
        if v >= t:
            c = col
    return c


heat_cols = ["ASR tổng", "SUP (88)", "DH-A (100)", "DH-S (36)", "DS (30)"]
heat = {
    "Gemini 3.5 flash-lite": [27.6, 47.3, 26.3, 5.6, 0],
    "GPT-5.6 luna": [12.6, 29.5, 5.0, 2.8, 0],
    "Claude Haiku 5.5": [11.8, 30.7, 3.0, 0, 0],
    "GPT-6 luna": [6.9, 18.2, 1.5, 0, 0],
    "GLM 5.3 flash": [4.3, 8.0, 4.0, 0, 0],
    "DeepSeek flash": [2.8, 6.8, 1.0, 0, 0],
}
x0, y0, cw, ch, gap = 200, 70, 120, 40, 2
b = []
for j, c in enumerate(heat_cols):
    b.append(f'<text x="{x0 + j * cw + cw / 2}" y="{y0 - 14}" class="{"tb" if j == 0 else "t1"}" text-anchor="middle">{c}</text>')
for i, m in enumerate(MODELS):
    y = y0 + i * ch
    b.append(f'<text x="{x0 - 14}" y="{y + ch / 2 + 4}" class="t1" text-anchor="end">{m}</text>')
    for j, v in enumerate(heat[m]):
        fill = ramp(v)
        txt = "#ffffff" if v >= 30 else INK
        x = x0 + j * cw
        b.append(f'<rect x="{x + gap / 2}" y="{y + gap / 2}" width="{cw - gap}" height="{ch - gap}" rx="4" fill="{fill}"/>')
        label = "0" if v == 0 else f"{v:.1f}"
        b.append(f'<text x="{x + cw / 2}" y="{y + ch / 2 + 5}" font-size="13" font-weight="{700 if j == 0 else 400}" fill="{txt}" text-anchor="middle">{label}%</text>')
# legend
ly = y0 + 6 * ch + 30
b.append(f'<text x="{x0}" y="{ly + 12}" class="t2">ASR (%), thấp là tốt:</text>')
for k, (t, col) in enumerate(RAMP):
    lx = x0 + 140 + k * 52
    b.append(f'<rect x="{lx}" y="{ly}" width="50" height="16" rx="3" fill="{col}"/>')
    b.append(f'<text x="{lx + 25}" y="{ly + 32}" class="tm" text-anchor="middle">{"0" if t == 0 else "≥" + str(t)}</text>')
(OUT / "fig2_attack_taxonomy.svg").write_text(
    svg(820, ly + 50, "ASR baseline theo nhóm tấn công, 6 model", "\n".join(b)), encoding="utf-8")

# ---------- Fig 3: ASR theo chiến thuật ----------
tactics = [("drill_test", "giả diễn tập PCCC", 25.6), ("technical_notice", "giả hiệu chuẩn / thông báo kỹ thuật", 20.6),
           ("maintenance", "giả bảo trì, thử tải", 16.4), ("authority_claim", "mạo danh cấp trên", 10.0)]
x0, y0, rh, sc = 330, 30, 40, 14  # 1% = 14px
b = []
for v in range(0, 31, 10):
    x = x0 + v * sc
    b.append(f'<line x1="{x}" y1="{y0 - 6}" x2="{x}" y2="{y0 + 4 * rh}" class="{"base" if v == 0 else "grid"}"/>')
    b.append(f'<text x="{x}" y="{y0 + 4 * rh + 18}" class="tm" text-anchor="middle">{v}%</text>')
for i, (k, d, v) in enumerate(tactics):
    y = y0 + i * rh
    b.append(f'<text x="{x0 - 14}" y="{y + 15}" class="tb" text-anchor="end">{k}</text>')
    b.append(f'<text x="{x0 - 14}" y="{y + 30}" class="t2" text-anchor="end">{d}</text>')
    w = v * sc
    b.append(f'<path d="M{x0},{y + 6} H{x0 + w - 4} a4,4 0 0 1 4,4 V{y + 24} a4,4 0 0 1 -4,4 H{x0} z" fill="{ORANGE}"/>')
    b.append(f'<text x="{x0 + w + 8}" y="{y + 22}" class="tb">{v:.1f}%</text>')
(OUT / "fig3_attack_tactics.svg").write_text(
    svg(820, y0 + 4 * rh + 30, "ASR theo chiến thuật payload, gộp 6 model", "\n".join(b)), encoding="utf-8")

# ---------- Fig 4: baseline vs SensorGuard, 3 panel ----------
# Nguồn: reports/DEFENSE_PROPOSAL.md §4 (GT v2.2.0 STRICT; Gemini r2/r3, GPT-6 r1/r2, còn lại k=1)
guard = {  # model: (ASR0, ASR1, SUP0, SUP1, BU0, BU1)
    "Gemini 3.5 flash-lite": (30.1, 4.9, 52.3, 1.1, 93.0, 97.0),
    "GPT-5.6 luna": (12.6, 0.8, 29.5, 0.0, 92.0, 94.0),
    "Claude Haiku 5.5": (11.8, 0.4, 30.7, 0.0, 84.0, 94.0),
    "GPT-6 luna": (6.9, 0.4, 18.2, 0.0, 92.0, 94.0),
    "GLM 5.3 flash": (4.3, 0.8, 8.0, 0.0, 86.0, 93.0),
    "DeepSeek flash": (2.8, 0.4, 6.8, 0.0, 92.0, 94.0),
}
panels = [("ASR ↓", 0, 0, 35, [0, 10, 20, 30]), ("SUP ↓", 2, 0, 60, [0, 20, 40, 60]), ("BU ↑", 4, 80, 100, [80, 90, 100])]
L, pw, pg, top, rh = 180, 250, 40, 92, 40
W = L + 3 * pw + 2 * pg + 20
H = top + 6 * rh + 40
b = []
# legend
b.append(f'<circle cx="{L + 6}" cy="26" r="6" fill="{ORANGE}" stroke="{BG}" stroke-width="2"/>')
b.append(f'<text x="{L + 18}" y="30" class="t1">Baseline (agent gốc)</text>')
b.append(f'<rect x="{L + 186}" y="20" width="12" height="12" rx="2" fill="{BLUE}" stroke="{BG}" stroke-width="2"/>')
b.append(f'<text x="{L + 206}" y="30" class="t1">Có SensorGuard</text>')
for i, m in enumerate(MODELS):
    b.append(f'<text x="{L - 14}" y="{top + i * rh + 4}" class="t1" text-anchor="end">{m}</text>')
for p, (name, idx, lo, hi, ticks) in enumerate(panels):
    px = L + p * (pw + pg)
    sx = lambda v: px + (v - lo) / (hi - lo) * pw
    b.append(f'<text x="{px}" y="{top - 34}" class="th">{name}</text>')
    for t in ticks:
        b.append(f'<line x1="{sx(t)}" y1="{top - 20}" x2="{sx(t)}" y2="{top + 5 * rh + 18}" class="{"base" if t == lo else "grid"}"/>')
        b.append(f'<text x="{sx(t)}" y="{top + 5 * rh + 36}" class="tm" text-anchor="middle">{t}%</text>')
    for i, m in enumerate(MODELS):
        y = top + i * rh
        v0, v1 = guard[m][idx], guard[m][idx + 1]
        x0_, x1_ = sx(v0), sx(v1)
        b.append(f'<line x1="{x0_}" y1="{y}" x2="{x1_}" y2="{y}" class="link"/>')
        b.append(f'<circle cx="{x0_}" cy="{y}" r="6" fill="{ORANGE}" stroke="{BG}" stroke-width="2"/>')
        b.append(f'<rect x="{x1_ - 6}" y="{y - 6}" width="12" height="12" rx="2" fill="{BLUE}" stroke="{BG}" stroke-width="2"/>')
        # nhãn: baseline phía ngoài, guard phía trong
        if v1 < v0:  # giảm: guard bên trái
            b.append(f'<text x="{x0_ + 11}" y="{y + 4}" class="t2">{v0:g}</text>')
            b.append(f'<text x="{x1_ + (12 if x1_ - px < 30 else -11)}" y="{y - 9}" class="tb" font-size="11.5" text-anchor="{"start" if x1_ - px < 30 else "end"}">{v1:g}</text>')
        else:  # tăng: guard bên phải
            b.append(f'<text x="{x0_ - 11}" y="{y + 4}" class="t2" text-anchor="end">{v0:g}</text>')
            b.append(f'<text x="{x1_ + 11}" y="{y + 4}" class="tb" font-size="11.5">{v1:g}</text>')
(OUT / "fig4_guard_effect.svg").write_text(
    svg(W, H, "Baseline so với có SensorGuard: ASR, SUP và BU của 6 model", "\n".join(b)), encoding="utf-8")
print("ok")
