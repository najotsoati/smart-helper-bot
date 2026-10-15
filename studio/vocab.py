"""The fixed vocabulary of a storyboard.

The director AI may only use the words listed here, the checker rejects anything
else, and blender_script.py turns each word into stickman_tools.py (v8) calls.
Everything comes from what was proven in the Blender template.
"""

FPS = 30
MAX_SECONDS = 59
MIN_SECONDS = 12

# Sticky's x position: plain room, or in front of the bed / armchair.
X_PLAIN = -0.55
X_FURNITURE = 0.15
PHONE_X = 40.0

SETS = ["none", "bed", "armchair"]
BACKDROPS = ["room", "white"]

POSES = [
    "rest", "stand", "hips", "think", "point", "point_left", "idea", "cheer",
    "wave", "wave2", "shrug", "present", "shock", "slump", "tip", "phone",
    # custom ones defined in the generated script
    "ph_tap", "ph_rage", "ph_hip", "rage",
]

# Custom poses written into st.POSES by the generated script (angles from the skill notes).
CUSTOM_POSES = {
    "ph_tap": {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -30, "forearm.R": 75, "front": "R"},
    "ph_rage": {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": 150, "forearm.R": 85},
    "ph_hip": {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -135, "forearm.R": -49},
    "rage": {"upper_arm.L": 45, "forearm.L": 100, "upper_arm.R": 135, "forearm.R": 80},
}

# Where the phone in the hand sits for poses that hold it; any other pose hides it.
PHONE_IN_HAND = {"phone": (0.62, 2.55), "ph_tap": (0.62, 2.55), "ph_rage": (0.62, 2.55),
                 "ph_hip": (0.62, 2.55), "cheer": (0.62, 3.28)}

EYES = ["normal", "wide", "money", "squint", "shut"]
MOUTHS = ["neutral", "smile", "grin", "open", "wide", "sad", "think", "scream"]
# brows(tilt, lift, cock): tilt > 0 worried, < 0 angry.  Values to calibrate against video_05..09.
BROWS = {
    "neutral": (0.0, 0.0, 0.0),
    "worried": (12.0, 0.04, 0.0),
    "angry": (-14.0, 0.0, 0.0),
    "surprised": (0.0, 0.10, 0.0),
    "suspicious": (-6.0, 0.0, 0.06),
}
LOOKS = {"camera": (0.0, 0.0), "phone": (0.04, -0.03), "left": (-0.05, 0.0), "right": (0.05, 0.0),
         "up": (0.0, 0.05), "down": (0.0, -0.05)}

PROPS = ["question", "exclaim", "bulb", "clock", "house", "money", "sweat"]
FX = ["star", "dust", "lines"]

ACTIONS = {
    # name: (description for the director, default length in seconds)
    "none": ("nothing extra", 0),
    "bounce": ("jumps up and lands (joy, panic)", 0.4),
    "punch": ("small squash jolt (startled, hit)", 0),
    "spin": ("spins like a top", 0.55),
    "flatten": ("squashed flat, then pops back", 0.5),
    "shiver": ("trembles for the whole shot", 0),
    "tears": ("tears stream for the whole shot", 0),
    "walk": ("paces left and right in panic for the whole shot", 0),
    "hop": ("small hop", 0.3),
    "fall_flat": ("falls face down on the floor with a star", 0.6),
    "coin_rain": ("gold coins rain from the top", 0.8),
    "money_fly": ("banknotes fly away from Sticky out of the frame", 1.2),
    "bills_chase": ("an angry bill with legs runs in from the door, grabs a banknote and runs off (set label)", 1.3),
    "fly_buzz": ("a fly buzzes out of his empty pocket/wallet: broke", 1.1),
    "knock": ("loud knocking on the door, the door shakes", 0.8),
}

SFX = {
    "ding": 0.5, "pop": 0.55, "tick": 1.0, "chaching": 0.6, "jump": 0.4, "land": 0.32,
    "knock3": 1.0, "slam": 0.8, "whoosh": 0.7, "drop": 0.7, "whirl": 0.7, "splat": 0.4,
    "fall": 0.3, "hit": 0.45, "spring": 0.45, "trombone": 0.55, "boom": 0.4, "rumble": 0.4,
    "buzz": 0.5, "type": 0.7, "error": 0.4, "glitch": 0.32, "scratch": 0.8, "rewind": 0.6,
    "ffwd": 0.6, "heart": 0.45, "heart_fast": 0.3, "riser": 0.18, "riser2": 0.6,
    "shopbell": 0.5, "shimmer": 0.4, "flush": 0.5, "clink": 0.5, "pickaxe": 0.5, "crowd": 0.35,
}

MUSIC = {
    "lofi": ("musiqa_01.wav", 0.16),
    "epic": ("musiqa_02_epic.wav", 0.10),
    "sneaky": ("musiqa_03_sneaky.wav", 0.12),
    "western": ("musiqa_04_western.wav", 0.12),
    "none": (None, 0.0),
}

# Camera presets.  Each value builds (x, z, scale) from Sticky's X.  "zoom_to" makes a slow push-in.
CAMERAS = {
    "wide": {"desc": "whole room", "at": lambda X: (0.0, 2.3, 7.0)},
    "room_push": {"desc": "wide shot slowly pushing in", "at": lambda X: (0.0, 2.3, 7.0),
                  "zoom_to": lambda X: (0.0, 2.6, 6.4)},
    "open_zoom": {"desc": "opening: fast zoom from medium-wide to the face (best first shot)",
                  "at": lambda X: (X, 2.5, 5.2), "zoom_to": lambda X: (X + 0.08, 2.75, 2.6), "zoom_frames": (3, 10)},
    "face": {"desc": "face close-up with a slow creep in", "at": lambda X: (X + 0.08, 2.75, 2.6),
             "zoom_to": lambda X: (X + 0.12, 2.8, 2.42)},
    "face_phone_up": {"desc": "face with the phone raised (use pose cheer)", "at": lambda X: (X + 0.05, 2.9, 2.7)},
    "medium": {"desc": "head, torso and phone", "at": lambda X: (X + 0.01, 2.6, 2.9)},
    "medium_wide": {"desc": "whole figure with room above the head", "at": lambda X: (X, 2.5, 5.2)},
    "extreme_closeup": {"desc": "eyes only, for a final stare", "at": lambda X: (X, 2.84, 2.1),
                        "zoom_to": lambda X: (X, 2.84, 1.85)},
    "floor": {"desc": "Sticky lying on the floor", "at": lambda X: (0.62, 1.78, 4.7)},
    "phone_screen": {"desc": "the big phone screen fills the frame (use phone_text)", "at": lambda X: (PHONE_X, 2.45, 6.0)},
    "phone_push": {"desc": "phone screen with a gentle push-in", "at": lambda X: (PHONE_X, 2.45, 6.0),
                   "zoom_to": lambda X: (PHONE_X, 2.85, 4.9)},
    "end_card": {"desc": "dark end card for the last line", "at": lambda X: (60.0, 2.3, 7.0)},
    "crash_zoom": {"desc": "violent fast zoom into the face (shock moment)", "at": lambda X: (X, 2.5, 5.2),
                   "zoom_to": lambda X: (X + 0.08, 2.78, 2.3), "zoom_frames": (1, 5)},
    "pull_back": {"desc": "starts on the face and pulls back to reveal the room (reveal moment)",
                  "at": lambda X: (X + 0.08, 2.75, 2.6), "zoom_to": lambda X: (0.0, 2.3, 7.0)},
}

# Cameras used for automatic extra cuts inside long shots, by situation.
COVERAGE = {
    "room": ["face", "medium", "medium_wide"],
    "phone": ["face", "phone_push"],
    "floor": ["floor"],
}
COVERAGE_EVERY = 50     # frames between automatic cuts (about 1.7 s)

CAPTION_COLORS = ["black", "white", "red", "green", "gold", "cream", "grey", "blue"]
CAPTION_POS = ["top", "bottom", "big"]

VOICES = {
    # speaker: ElevenLabs voice id, edge-tts voice
    "sticky": ("TX3LPaxmHKxFdv7VOQHJ", "en-US-AndrewMultilingualNeural"),   # Liam
    "phone": ("JBFqnCBsd6RMkjVDRZzb", "en-GB-RyanNeural"),                  # George
    "rick": ("JBFqnCBsd6RMkjVDRZzb", "en-GB-ThomasNeural"),
    "narrator": ("nPczCjzI2devNBz1zQrb", "en-US-BrianMultilingualNeural"),  # Brian
}

# How a line is said with the free voice: (rate, pitch, volume) for edge-tts.
MOODS = {
    "normal": ("+6%", "+0Hz", "+0%"),
    "excited": ("+16%", "+22Hz", "+10%"),
    "shout": ("+10%", "+32Hz", "+25%"),
    "scared": ("+20%", "+28Hz", "+0%"),
    "sad": ("-14%", "-18Hz", "-8%"),
    "whisper": ("-6%", "-8Hz", "-35%"),
    "smug": ("-6%", "-14Hz", "+0%"),
    "deadpan": ("-10%", "-6Hz", "-5%"),
    "confused": ("-4%", "+12Hz", "+0%"),
}

# Free English voices worth auditioning in the panel.
VOICE_CHOICES = [
    "en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", "en-US-AndrewNeural",
    "en-US-BrianNeural", "en-US-ChristopherNeural", "en-US-EricNeural", "en-US-GuyNeural",
    "en-US-RogerNeural", "en-US-SteffanNeural", "en-GB-RyanNeural", "en-GB-ThomasNeural",
    "en-AU-WilliamNeural", "en-US-AvaMultilingualNeural", "en-US-EmmaMultilingualNeural",
    "en-US-AriaNeural", "en-US-JennyNeural", "en-GB-SoniaNeural",
]


def vocabulary_text():
    """The vocabulary as plain text for the director prompt."""
    cams = "\n".join(f"  - {k}: {v['desc']}" for k, v in CAMERAS.items())
    acts = "\n".join(f"  - {k}: {v[0]}" for k, v in ACTIONS.items())
    return f"""camera (one per shot):
{cams}
pose: {", ".join(POSES)}
eyes: {", ".join(EYES)}
mouth: {", ".join(MOUTHS)}   (ignored while the shot's line is spoken; lip-sync takes over)
brows: {", ".join(BROWS)}
look: {", ".join(LOOKS)}
action:
{acts}
props (pop next to Sticky's head): {", ".join(PROPS)}
fx (at Sticky): {", ".join(FX)}
sfx (real recorded sounds, nothing else exists): {", ".join(SFX)}
music: {", ".join(MUSIC)}
caption color: {", ".join(CAPTION_COLORS)}; caption pos: top (under the title), bottom (on a cream plate), big (huge number in the middle)
set: {", ".join(SETS)}
speakers: {", ".join(VOICES)}
line mood (how it is said): {", ".join(MOODS)}"""
