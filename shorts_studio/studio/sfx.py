"""Sound effects. Real files dropped in assets/sfx/ (e.g. whoosh_1.wav, riser.mp3) win over the built-in
synthesized ones, which are generated with ffmpeg so the panel works out of the box."""

import random
from pathlib import Path

from . import config
from .ffmpeg import run

SFX_DIR = config.ASSETS / "sfx"

# name -> (lavfi source, extra audio filter)
SYNTH = {
    "whoosh": ("anoisesrc=d=0.45:c=pink:a=0.7:r=44100",
               "highpass=f=600,lowpass=f=7000,afade=t=in:d=0.32:curve=exp,afade=t=out:st=0.32:d=0.13"),
    "impact": ("aevalsrc='0.95*sin(2*PI*(42+150*exp(-16*t))*t)*exp(-4.5*t)':d=0.9:s=44100", "alimiter=limit=0.9"),
    # rising filtered noise + tone, 1.6 s, ends right on the twist
    "riser": ("aevalsrc='0.35*sin(2*PI*(180+500*t*t)*t)*(t/1.6)+0.25*(random(0)-0.5)*(t/1.6)^2':d=1.6:s=44100",
              "highpass=f=200,afade=t=out:st=1.55:d=0.05"),
    "drop": ("aevalsrc='0.9*tanh(3*sin(2*PI*(70*exp(-1.4*t))*t))*exp(-2.2*t)':d=1.4:s=44100", "lowpass=f=900"),
    "ding": ("aevalsrc='0.4*sin(2*PI*1568*t)*exp(-7*t)+0.2*sin(2*PI*3136*t)*exp(-11*t)':d=0.7:s=44100", "anull"),
}


def get(name: str, work: Path) -> Path:
    custom = [p for p in SFX_DIR.glob(f"{name}*") if p.suffix.lower() in {".wav", ".mp3", ".ogg", ".m4a"}]
    if custom:
        return random.choice(custom).resolve()
    out = work / f"sfx_{name}.wav"
    if not out.exists():
        src, af = SYNTH[name]
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", src, "-af", af, "-ac", "1", "-ar", "44100", str(out)])
    return out.resolve()
