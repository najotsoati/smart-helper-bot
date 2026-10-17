"""Generate the 'Fakti' mascot pose SVGs (rendered to PNG with headless Chromium afterwards)."""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "mascot"

BASE = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
  <defs>
    <radialGradient id="body" cx="40%" cy="30%" r="75%">
      <stop offset="0" stop-color="#8f7bff"/><stop offset="1" stop-color="#5b3fe0"/>
    </radialGradient>
    <radialGradient id="belly" cx="50%" cy="40%" r="60%">
      <stop offset="0" stop-color="#c9bfff"/><stop offset="1" stop-color="#a596ff"/>
    </radialGradient>
  </defs>
  <!-- shadow -->
  <ellipse cx="500" cy="955" rx="260" ry="28" fill="#000" opacity=".25"/>
  <!-- antenna -->
  <path d="M500 170 C 495 120, 530 90, 560 70" stroke="#2b1a7a" stroke-width="16" fill="none" stroke-linecap="round"/>
  <circle cx="565" cy="66" r="34" fill="#FFE500" stroke="#2b1a7a" stroke-width="12"/>
  <circle cx="555" cy="55" r="10" fill="#fff" opacity=".8"/>
  <!-- arms -->
  <path d="M215 640 C 140 650, 120 590, 150 545" stroke="#2b1a7a" stroke-width="18" fill="#6c4ff0" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M785 640 C 860 650, 880 590, 850 545" stroke="#2b1a7a" stroke-width="18" fill="#6c4ff0" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- body -->
  <path d="M500 170 C 760 170, 840 380, 830 600 C 820 820, 700 930, 500 930 C 300 930, 180 820, 170 600 C 160 380, 240 170, 500 170 Z"
        fill="url(#body)" stroke="#2b1a7a" stroke-width="18"/>
  <ellipse cx="500" cy="740" rx="210" ry="150" fill="url(#belly)" opacity=".55"/>
  <!-- cheeks -->
  <ellipse cx="300" cy="560" rx="52" ry="30" fill="#ff7aa8" opacity=".55"/>
  <ellipse cx="700" cy="560" rx="52" ry="30" fill="#ff7aa8" opacity=".55"/>
  {eyes}
  {mouth}
</svg>"""


def eyes(kind: str) -> str:
    if kind == "blink":
        return """
  <path d="M310 430 Q 370 460 430 430" stroke="#2b1a7a" stroke-width="16" fill="none" stroke-linecap="round"/>
  <path d="M570 430 Q 630 460 690 430" stroke="#2b1a7a" stroke-width="16" fill="none" stroke-linecap="round"/>
  <path d="M300 345 Q 365 315 430 335" stroke="#2b1a7a" stroke-width="16" fill="none" stroke-linecap="round"/>
  <path d="M570 335 Q 635 315 700 345" stroke="#2b1a7a" stroke-width="16" fill="none" stroke-linecap="round"/>"""
    r, pupil, brow_l, brow_r = (88, 30, "M290 300 Q 365 255 440 285", "M560 285 Q 635 255 710 300") if kind == "wide" \
        else (78, 36, "M300 330 Q 365 305 430 322", "M570 322 Q 635 305 700 330")
    return f"""
  <circle cx="370" cy="430" r="{r}" fill="#fff" stroke="#2b1a7a" stroke-width="14"/>
  <circle cx="630" cy="430" r="{r}" fill="#fff" stroke="#2b1a7a" stroke-width="14"/>
  <circle cx="385" cy="440" r="{pupil}" fill="#1a1040"/>
  <circle cx="645" cy="440" r="{pupil}" fill="#1a1040"/>
  <circle cx="397" cy="426" r="11" fill="#fff"/>
  <circle cx="657" cy="426" r="11" fill="#fff"/>
  <path d="{brow_l}" stroke="#2b1a7a" stroke-width="16" fill="none" stroke-linecap="round"/>
  <path d="{brow_r}" stroke="#2b1a7a" stroke-width="16" fill="none" stroke-linecap="round"/>"""


MOUTHS = {
    "closed": '<path d="M430 610 Q 500 660 570 610" stroke="#2b1a7a" stroke-width="16" fill="none" stroke-linecap="round"/>',
    "half": """<path d="M425 600 Q 500 600 575 600 Q 565 670 500 675 Q 435 670 425 600 Z" fill="#3a0f3f" stroke="#2b1a7a" stroke-width="14" stroke-linejoin="round"/>
  <ellipse cx="500" cy="655" rx="38" ry="14" fill="#ff6f91"/>""",
    "open": """<path d="M415 595 Q 500 590 585 595 Q 580 720 500 728 Q 420 720 415 595 Z" fill="#3a0f3f" stroke="#2b1a7a" stroke-width="14" stroke-linejoin="round"/>
  <path d="M440 600 L 560 600 L 555 625 L 445 625 Z" fill="#fff"/>
  <ellipse cx="500" cy="700" rx="48" ry="20" fill="#ff6f91"/>""",
    "o": """<ellipse cx="500" cy="650" rx="55" ry="72" fill="#3a0f3f" stroke="#2b1a7a" stroke-width="14"/>
  <ellipse cx="500" cy="690" rx="32" ry="16" fill="#ff6f91"/>""",
    "o_small": '<ellipse cx="500" cy="640" rx="34" ry="40" fill="#3a0f3f" stroke="#2b1a7a" stroke-width="14"/>',
}

POSES = {
    "closed": ("normal", "closed"),
    "half": ("normal", "half"),
    "open": ("normal", "open"),
    "blink": ("blink", "closed"),
    "surprised_closed": ("wide", "o_small"),
    "surprised_open": ("wide", "o"),
}

for name, (eye, mouth) in POSES.items():
    (OUT / f"{name}.svg").write_text(BASE.replace("{eyes}", eyes(eye)).replace("{mouth}", MOUTHS[mouth]))
print("ok")
