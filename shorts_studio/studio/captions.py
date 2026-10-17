"""Animated word-by-word captions as an ASS subtitle file (rendered by ffmpeg/libass).

Style: 1-3 big words at a time, the word being spoken pops and turns yellow,
emphasis words (numbers, the surprising word) are green. Scene titles slam in at the top.
"""

import re
from dataclasses import dataclass

from .voice import Word

WHITE, YELLOW, GREEN = "&H00FFFFFF&", "&H0000E5FF&", "&H0040FF7A&"  # ASS colours are &HBBGGRR&

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Anton,138,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,9,5,5,60,60,0,1
Style: Title,Anton,104,&H00000000,&H00000000,&H0000E5FF,&H00000000,0,0,0,0,100,100,2,-3,3,24,0,8,60,60,300,1
Style: Series,Anton,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,3,14,0,8,60,60,150,1
{extra_styles}
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


@dataclass
class TimedWord(Word):
    emphasis: bool = False


def ts(t: float) -> str:
    t = max(t, 0)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _norm(s: str) -> str:
    return re.sub(r"[^\w%$]", "", s.lower())


def mark_emphasis(words: list[Word], emphasis: list[str]) -> list[TimedWord]:
    keys = {_norm(k) for phrase in emphasis for k in phrase.split()}
    return [TimedWord(w.text, w.start, w.end, _norm(w.text) in keys or bool(re.search(r"\d", w.text))) for w in words]


def _groups(words: list[TimedWord], max_words: int = 3, max_chars: int = 18) -> list[list[TimedWord]]:
    groups, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or len(" ".join(x.text for x in cur + [w])) > max_chars):
            groups.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?,;:]$", w.text):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def _clean(text: str) -> str:
    return text.upper().replace("{", "(").replace("}", ")").strip(",;:")


def build_ass(
    words: list[TimedWord],
    titles: list[tuple[float, float, str]],
    total: float,
    extra_events: list[str] = (),
    series: str = "",
    host_ranges: list[tuple[float, float]] = (),
    badge: bool = False,
) -> str:
    """`host_ranges`: when the big host is on screen, captions drop below it.
    `badge`: the round host badge sits top-left, so scene titles shift right to clear it."""
    from .graphics import STYLES

    header = HEADER.replace("{extra_styles}", STYLES)
    if badge:
        header = header.replace(",2,-3,3,24,0,8,60,60,300,1", ",2,-3,3,24,0,8,290,40,300,1")
    lines = [header]
    groups = _groups(words)
    for gi, group in enumerate(groups):
        group_end = groups[gi + 1][0].start if gi + 1 < len(groups) else total
        for i, w in enumerate(group):
            start = w.start
            end = group[i + 1].start if i + 1 < len(group) else group_end
            parts = []
            for j, other in enumerate(group):
                text = _clean(other.text)
                if j == i:
                    color = GREEN if other.emphasis else YELLOW
                    # pop: quick overshoot then settle
                    parts.append(
                        f"{{\\c{color}\\fscx118\\fscy118\\t(0,90,\\fscx100\\fscy100)}}{text}{{\\c{WHITE}\\fscx100\\fscy100}}"
                    )
                else:
                    parts.append(f"{{\\c{GREEN if other.emphasis else WHITE}}}{text}{{\\c{WHITE}}}")
            y = 1450 if any(a <= start < b for a, b in host_ranges) else 1180
            # first word of a group slides up slightly to sell the "new line"
            intro = f"{{\\move(540,{y + 35},540,{y},0,80)}}" if i == 0 else f"{{\\pos(540,{y})}}"
            lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Caption,,0,0,0,,{intro}{' '.join(parts)}\n")

    for start, end, text in titles:
        slam = "{\\fscx160\\fscy160\\alpha&HFF&\\t(0,140,\\fscx100\\fscy100\\alpha&H00&)}"
        lines.append(f"Dialogue: 1,{ts(start)},{ts(end)},Title,,0,0,0,,{slam}{_clean(text)}\n")
    if series:
        lines.append(f"Dialogue: 1,{ts(0)},{ts(min(3.0, total))},Series,,0,0,0,,{_clean(series)}\n")
    lines += [e + "\n" for e in extra_events]
    return "".join(lines)
