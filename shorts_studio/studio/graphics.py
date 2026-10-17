"""Animated infographics drawn as ASS subtitle events: a counting number and a two-bar comparison."""

from .captions import ts

YELLOW, WHITE = "&H0000E5FF&", "&H00FFFFFF&"
STYLES = (
    "Style: Big,Anton,230,&H0000E5FF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,10,8,5,40,40,0,1\n"
    "Style: Label,Anton,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,6,4,5,40,40,0,1\n"
)


def _fmt(value: float, decimals: int) -> str:
    return f"{value:,.{decimals}f}"


def _decimals(value: float) -> int:
    return 0 if float(value).is_integer() else 1


def counter(start: float, end: float, value: float, prefix: str, suffix: str, label: str) -> list[str]:
    """Number counts up with an ease-out over ~1.2 s, then holds with a little pop."""
    lines = []
    dec = _decimals(value)
    count_time = min(1.2, (end - start) * 0.6)
    steps = max(int(count_time * 20), 1)
    for i in range(steps):
        t0 = start + count_time * i / steps
        t1 = start + count_time * (i + 1) / steps
        p = 1 - (1 - i / steps) ** 3
        text = f"{prefix}{_fmt(value * p, dec)}{suffix}"
        lines.append(f"Dialogue: 2,{ts(t0)},{ts(t1)},Big,,0,0,0,,{{\\pos(540,760)}}{text.upper()}")
    final = f"{prefix}{_fmt(value, dec)}{suffix}".upper()
    lines.append(
        f"Dialogue: 2,{ts(start + count_time)},{ts(end)},Big,,0,0,0,,"
        f"{{\\pos(540,760)\\fscx115\\fscy115\\t(0,150,\\fscx100\\fscy100)}}{final}"
    )
    if label:
        lines.append(
            f"Dialogue: 2,{ts(start + 0.15)},{ts(end)},Label,,0,0,0,,"
            f"{{\\pos(540,930)\\alpha&HFF&\\t(0,250,\\alpha&H00&)}}{label.upper()}"
        )
    return lines


def compare(start: float, end: float, a_label: str, a: float, b_label: str, b: float, unit: str) -> list[str]:
    """Two bars grow from a baseline; the bigger one ends 500 px tall."""
    base, max_h, width = 980, 500, 250
    biggest = max(a, b, 1e-9)
    grow = min(0.9, (end - start) * 0.45)
    lines = []
    if unit:
        lines.append(
            f"Dialogue: 2,{ts(start)},{ts(end)},Label,,0,0,0,,{{\\pos(540,330)\\fs70}}{unit.upper()}"
        )
    for i, (label, value, color) in enumerate(((a_label, a, WHITE), (b_label, b, YELLOW))):
        delay = int(i * 350)  # second bar starts a beat later for drama
        x = 330 if i == 0 else 750
        h = max(14, round(max_h * value / biggest))
        left, top = x - width // 2, base - h
        bar = f"m 0 0 l {width} 0 l {width} {h} l 0 {h}"
        clip_from = f"\\clip({left},{base},{left + width},{base})"
        clip_to = f"\\clip({left},{top},{left + width},{base})"
        ms = int(grow * 1000)
        lines.append(
            f"Dialogue: 2,{ts(start)},{ts(end)},Label,,0,0,0,,"
            f"{{\\an7\\pos({left},{top})\\bord0\\shad0\\1c{color}{clip_from}\\t({delay},{delay + ms},0.6,{clip_to})\\p1}}{bar}"
        )
        value_text = _fmt(value, _decimals(value))
        lines.append(
            f"Dialogue: 3,{ts(start + (delay + ms) / 1000)},{ts(end)},Label,,0,0,0,,"
            f"{{\\an2\\pos({x},{top - 12})\\1c{color}\\fscx120\\fscy120\\t(0,140,\\fscx100\\fscy100)}}{value_text}"
        )
        lines.append(
            f"Dialogue: 2,{ts(start)},{ts(end)},Label,,0,0,0,,{{\\an8\\pos({x},{base + 18})\\fs64}}{label.upper()}"
        )
    return lines
