"""Generate the 'Fakti' mascot poses as SVG: 5 emotions x 3 mouth shapes (+ blinks).

Render to PNG with any SVG renderer (the bundled PNGs were made with headless Chromium), e.g.
    python tools/make_mascot.py && for f in assets/mascot/*.svg; do rsvg-convert -w 1000 "$f" -o "${f%.svg}.png"; done
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "mascot"
INK = "#2b1a7a"

BASE = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
  <defs>
    <radialGradient id="body" cx="40%" cy="30%" r="75%">
      <stop offset="0" stop-color="#8f7bff"/><stop offset="1" stop-color="#5b3fe0"/>
    </radialGradient>
    <radialGradient id="belly" cx="50%" cy="40%" r="60%">
      <stop offset="0" stop-color="#c9bfff"/><stop offset="1" stop-color="#a596ff"/>
    </radialGradient>
  </defs>
  <ellipse cx="500" cy="955" rx="260" ry="28" fill="#000" opacity=".25"/>
  <path d="M500 170 C 495 120, 530 90, 560 70" stroke="{ink}" stroke-width="16" fill="none" stroke-linecap="round"/>
  <circle cx="565" cy="66" r="34" fill="#FFE500" stroke="{ink}" stroke-width="12"/>
  <circle cx="555" cy="55" r="10" fill="#fff" opacity=".8"/>
  {arms}
  <path d="M500 170 C 760 170, 840 380, 830 600 C 820 820, 700 930, 500 930 C 300 930, 180 820, 170 600 C 160 380, 240 170, 500 170 Z"
        fill="url(#body)" stroke="{ink}" stroke-width="18"/>
  <ellipse cx="500" cy="740" rx="210" ry="150" fill="url(#belly)" opacity=".55"/>
  <ellipse cx="300" cy="560" rx="52" ry="30" fill="#ff7aa8" opacity=".55"/>
  <ellipse cx="700" cy="560" rx="52" ry="30" fill="#ff7aa8" opacity=".55"/>
  {eyes}
  {mouth}
  {extra}
</svg>"""


def arm(path: str) -> str:
    return (f'<path d="{path}" stroke="{INK}" stroke-width="18" fill="#6c4ff0" '
            'stroke-linecap="round" stroke-linejoin="round"/>')


ARMS = {
    "down": arm("M215 640 C 140 650, 120 590, 150 545") + arm("M785 640 C 860 650, 880 590, 850 545"),
    "up": arm("M200 610 C 110 570, 55 470, 75 350 C 80 320, 120 322, 118 352 C 105 450, 150 520, 205 545")
    + arm("M800 610 C 890 570, 945 470, 925 350 C 920 320, 880 322, 882 352 C 895 450, 850 520, 795 545")
    + f'<circle cx="95" cy="330" r="30" fill="#6c4ff0" stroke="{INK}" stroke-width="14"/>'
    + f'<circle cx="905" cy="330" r="30" fill="#6c4ff0" stroke="{INK}" stroke-width="14"/>',
    "point": arm("M215 640 C 140 650, 120 590, 150 545")
    + arm("M800 520 C 880 470, 930 380, 950 290 C 958 262, 925 250, 915 275 C 895 350, 855 420, 780 470")
    + f'<circle cx="935" cy="262" r="26" fill="#6c4ff0" stroke="{INK}" stroke-width="14"/>',
    "tucked": arm("M240 650 C 200 640, 200 590, 230 570") + arm("M760 650 C 800 640, 800 590, 770 570"),
}


def _eye_pair(r: int, pupil: int, dx: int = 15, dy: int = 10) -> str:
    out = ""
    for cx in (370, 630):
        out += (f'<circle cx="{cx}" cy="430" r="{r}" fill="#fff" stroke="{INK}" stroke-width="14"/>'
                f'<circle cx="{cx + dx}" cy="{430 + dy}" r="{pupil}" fill="#1a1040"/>'
                f'<circle cx="{cx + dx + 12}" cy="{430 + dy - 14}" r="{max(pupil // 3, 6)}" fill="#fff"/>')
    return out


def _brows(left: str, right: str) -> str:
    return "".join(f'<path d="{d}" stroke="{INK}" stroke-width="16" fill="none" stroke-linecap="round"/>'
                   for d in (left, right))


EYES = {
    "normal": _eye_pair(78, 36) + _brows("M300 330 Q 365 305 430 322", "M570 322 Q 635 305 700 330"),
    "blink": _brows("M310 430 Q 370 460 430 430", "M570 430 Q 630 460 690 430")
    + _brows("M300 345 Q 365 315 430 335", "M570 335 Q 635 315 700 345"),
    "happy": _brows("M305 450 Q 370 370 435 450", "M565 450 Q 630 370 695 450")
    + _brows("M300 320 Q 365 285 430 305", "M570 305 Q 635 285 700 320"),
    "wide": _eye_pair(88, 30) + _brows("M290 300 Q 365 255 440 285", "M560 285 Q 635 255 710 300"),
    "scared": _eye_pair(90, 18, 0, 0) + _brows("M300 330 Q 360 300 440 280", "M560 280 Q 640 300 700 330"),
    "look": _eye_pair(78, 36, 34, -12) + _brows("M300 325 Q 365 300 430 318", "M570 312 Q 635 285 700 318"),
}

TONGUE = '<ellipse cx="500" cy="{y}" rx="{rx}" ry="{ry}" fill="#ff6f91"/>'
MOUTHS = {
    "smile": f'<path d="M430 610 Q 500 660 570 610" stroke="{INK}" stroke-width="16" fill="none" stroke-linecap="round"/>',
    "half": f'<path d="M425 600 Q 500 600 575 600 Q 565 670 500 675 Q 435 670 425 600 Z" fill="#3a0f3f" '
            f'stroke="{INK}" stroke-width="14" stroke-linejoin="round"/>' + TONGUE.format(y=655, rx=38, ry=14),
    "open": f'<path d="M415 595 Q 500 590 585 595 Q 580 720 500 728 Q 420 720 415 595 Z" fill="#3a0f3f" '
            f'stroke="{INK}" stroke-width="14" stroke-linejoin="round"/>'
            '<path d="M440 600 L 560 600 L 555 625 L 445 625 Z" fill="#fff"/>' + TONGUE.format(y=700, rx=48, ry=20),
    "grin": f'<path d="M390 590 Q 500 600 610 590 Q 590 690 500 700 Q 410 690 390 590 Z" fill="#3a0f3f" '
            f'stroke="{INK}" stroke-width="14" stroke-linejoin="round"/>'
            '<path d="M410 597 L 590 597 L 582 622 L 418 622 Z" fill="#fff"/>' + TONGUE.format(y=670, rx=50, ry=16),
    "grin_open": f'<path d="M385 585 Q 500 595 615 585 Q 600 750 500 760 Q 400 750 385 585 Z" fill="#3a0f3f" '
                 f'stroke="{INK}" stroke-width="14" stroke-linejoin="round"/>'
                 '<path d="M408 592 L 592 592 L 584 620 L 416 620 Z" fill="#fff"/>' + TONGUE.format(y=725, rx=60, ry=22),
    "o_small": f'<ellipse cx="500" cy="640" rx="34" ry="40" fill="#3a0f3f" stroke="{INK}" stroke-width="14"/>',
    "o": f'<ellipse cx="500" cy="650" rx="55" ry="72" fill="#3a0f3f" stroke="{INK}" stroke-width="14"/>'
         + TONGUE.format(y=690, rx=32, ry=16),
    "o_big": f'<ellipse cx="500" cy="660" rx="68" ry="92" fill="#3a0f3f" stroke="{INK}" stroke-width="14"/>'
             + TONGUE.format(y=715, rx=40, ry=20),
    "wavy": f'<path d="M420 630 Q 445 605 470 630 T 520 630 T 580 630" stroke="{INK}" stroke-width="16" '
            'fill="none" stroke-linecap="round"/>',
    "teeth": f'<rect x="420" y="600" width="160" height="62" rx="22" fill="#fff" stroke="{INK}" stroke-width="14"/>'
             f'<path d="M420 631 L 580 631 M460 600 L 460 662 M500 600 L 500 662 M540 600 L 540 662" '
             f'stroke="{INK}" stroke-width="8"/>',
    "teeth_open": f'<rect x="410" y="592" width="180" height="96" rx="30" fill="#3a0f3f" stroke="{INK}" '
                  f'stroke-width="14"/><rect x="424" y="602" width="152" height="24" rx="8" fill="#fff"/>'
                  '<rect x="424" y="652" width="152" height="24" rx="8" fill="#fff"/>',
}

SWEAT = ('<path d="M790 300 C 770 340, 760 370, 790 385 C 820 370, 810 340, 790 300 Z" fill="#7fd8ff" '
         f'stroke="{INK}" stroke-width="10"/>')

# emotion -> (arms, eyes, {closed, half, open} mouths, extra)
EMOTIONS = {
    "neutral": ("down", "normal", ("smile", "half", "open"), ""),
    "excited": ("up", "happy", ("grin", "grin", "grin_open"), ""),
    "surprised": ("tucked", "wide", ("o_small", "o", "o_big"), ""),
    "scared": ("tucked", "scared", ("wavy", "teeth", "teeth_open"), SWEAT),
    "pointing": ("point", "look", ("smile", "half", "open"), ""),
}


def svg(arms: str, eyes: str, mouth: str, extra: str) -> str:
    return (BASE.replace("{ink}", INK).replace("{arms}", ARMS[arms]).replace("{eyes}", EYES[eyes])
            .replace("{mouth}", MOUTHS[mouth]).replace("{extra}", extra))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for emotion, (arms, eyes, mouths, extra) in EMOTIONS.items():
        for shape, mouth in zip(("closed", "half", "open"), mouths):
            (OUT / f"{emotion}_{shape}.svg").write_text(svg(arms, eyes, mouth, extra))
        if eyes in ("normal", "look"):
            (OUT / f"{emotion}_blink.svg").write_text(svg(arms, "blink", mouths[0], extra))
    print(f"wrote SVGs to {OUT}")
