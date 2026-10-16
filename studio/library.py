"""The acting library: 100 poses and 100 actions for Sticky, built from the rig's rules.

Poses are angles in screen degrees (0 right, 90 up); ".L" is the limb on the screen's right.
Each pose = a left-arm slot + a right-arm slot (mirrored) + head + torso + legs, so every pose
stays inside what the puppet can do.  Actions are small recipes of tools calls that the
generated Blender script plays with act().
"""

# Arm slots for the limb on the screen's RIGHT (.L): (upper_arm, forearm, drawn in front of the body)
ARM = {
    "down": (-80, -86, False), "hip": (-45, -131, False), "out": (0, 0, False), "out_up": (35, 40, False),
    "out_down": (-35, -35, False), "up": (80, 85, False), "up_bent": (60, 110, False), "wave": (18, 78, False),
    "fist_up": (45, 100, False), "head": (50, 150, False), "ear": (35, 165, True), "salute": (30, 165, True),
    "face": (-40, 118, True), "chin": (-50, 108, True), "mouth": (-60, 112, True), "heart": (-115, 150, True),
    "across": (-110, 180, True), "forward": (-30, 10, False), "offer": (-32, -8, False), "shrug": (-42, 8, False),
    "point": (8, 14, False), "point_up": (75, 80, False), "point_down": (-60, -60, False),
    "behind": (-100, -150, False), "flex": (0, 90, False), "thumb": (-20, 60, False), "fist_low": (-55, 35, False),
    "robot": (-10, -95, False), "phone": (-62, 58, False),
}
HEAD = {"c": 90, "l": 102, "r": 78, "ll": 112, "rr": 68}
TORSO = {"c": None, "lean_r": 80, "lean_l": 100, "bend": 50, "back": 112}
LEGS = {
    "stand": {}, "wide": {"thigh.L": -70, "shin.L": -78, "thigh.R": -110, "shin.R": -102},
    "knee_l": {"thigh.L": -20, "shin.L": -90}, "knee_r": {"thigh.R": -160, "shin.R": -90},
    "cross": {"thigh.L": -112, "shin.L": -124, "thigh.R": -66, "shin.R": -58},
    "kick_l": {"thigh.L": -30, "shin.L": -30}, "kick_r": {"thigh.R": -150, "shin.R": -150},
}


def _mirror(a):
    m = 180 - a
    return m - 360 if m > 180 else m


def build(left, right, head="c", torso="c", legs="stand"):
    lu, lf, lfront = ARM[left]
    ru, rf, rfront = ARM[right]
    p = {"upper_arm.L": lu, "forearm.L": lf, "upper_arm.R": _mirror(ru), "forearm.R": _mirror(rf),
         "head": HEAD[head]}
    if TORSO[torso] is not None:
        p["torso"] = TORSO[torso]
    p.update(LEGS[legs])
    front = ("L" if lfront else "") + ("R" if rfront else "")
    if front:
        p["front"] = front
    return p


# name: (left arm, right arm, head, torso, legs, feeling)
POSE_SPECS = {
    "victory": ("up", "up", "c", "c", "stand", "happy"),
    "touchdown": ("up", "up", "l", "c", "wide", "happy"),
    "hero_stance": ("hip", "hip", "c", "c", "wide", "proud"),
    "chin_stroke": ("chin", "down", "l", "c", "stand", "think"),
    "listen": ("ear", "down", "l", "lean_r", "stand", "think"),
    "shh": ("mouth", "down", "c", "c", "stand", "sneaky"),
    "hand_on_heart": ("heart", "down", "r", "c", "stand", "sad"),
    "oath": ("heart", "up", "c", "c", "stand", "proud"),
    "thumbs_up": ("thumb", "down", "l", "c", "stand", "happy"),
    "double_thumbs": ("thumb", "thumb", "c", "c", "wide", "happy"),
    "stop": ("forward", "down", "c", "lean_l", "stand", "angry"),
    "beckon": ("out_up", "down", "l", "c", "stand", "sneaky"),
    "point_far": ("point", "down", "r", "lean_r", "stand", "shock"),
    "point_back": ("down", "point", "l", "c", "stand", "think"),
    "both_ways": ("point", "point", "c", "c", "stand", "think"),
    "point_floor": ("point_down", "down", "rr", "c", "stand", "angry"),
    "point_sky": ("point_up", "down", "l", "c", "stand", "happy"),
    "airplane": ("out", "out", "c", "lean_r", "knee_r", "happy"),
    "t_pose": ("out", "out", "c", "c", "stand", "proud"),
    "scarecrow": ("out_down", "out_down", "r", "c", "stand", "sad"),
    "zombie": ("forward", "forward", "r", "c", "stand", "tired"),
    "surrender": ("up_bent", "up_bent", "c", "c", "stand", "shock"),
    "one_flex": ("flex", "down", "l", "c", "stand", "proud"),
    "bodybuilder": ("flex", "flex", "c", "c", "wide", "proud"),
    "shield_eyes": ("salute", "hip", "ll", "lean_r", "stand", "think"),
    "head_scratch": ("head", "down", "l", "c", "stand", "think"),
    "sassy": ("hip", "hip", "r", "lean_r", "cross", "proud"),
    "casual": ("hip", "down", "r", "c", "stand", "happy"),
    "hip_wave": ("hip", "wave", "c", "c", "stand", "happy"),
    "fist_pump": ("fist_up", "down", "c", "c", "stand", "happy"),
    "champion": ("fist_up", "fist_up", "c", "c", "wide", "proud"),
    "yes": ("fist_low", "down", "r", "lean_r", "knee_l", "happy"),
    "handshake": ("offer", "down", "c", "c", "stand", "happy"),
    "tada": ("out_up", "out_up", "c", "c", "wide", "happy"),
    "shrug_big": ("shrug", "shrug", "ll", "c", "stand", "think"),
    "innocent": ("behind", "behind", "l", "c", "cross", "sneaky"),
    "hi_there": ("behind", "wave", "l", "c", "stand", "happy"),
    "skeptical": ("across", "chin", "r", "c", "stand", "angry"),
    "touched": ("heart", "heart", "l", "c", "stand", "sad"),
    "beg": ("heart", "heart", "c", "lean_r", "knee_l", "beg"),
    "jump_joy": ("up", "up", "l", "c", "knee_l", "happy"),
    "march": ("down", "forward", "c", "c", "knee_r", "proud"),
    "kick": ("hip", "out", "c", "lean_l", "kick_l", "angry"),
    "karate": ("forward", "flex", "r", "c", "wide", "angry"),
    "boxer": ("fist_low", "fist_low", "r", "lean_r", "wide", "angry"),
    "sneak": ("out_down", "chin", "r", "lean_r", "knee_r", "sneaky"),
    "chill": ("hip", "behind", "l", "lean_l", "cross", "happy"),
    "on_call": ("ear", "hip", "l", "c", "stand", "think"),
    "selfie": ("out_up", "down", "ll", "c", "stand", "happy"),
    "photo": ("chin", "chin", "c", "c", "wide", "think"),
    "yawn": ("up_bent", "down", "ll", "c", "stand", "tired"),
    "stretch": ("up", "up", "ll", "lean_l", "stand", "tired"),
    "side_bend": ("up", "hip", "r", "lean_r", "stand", "tired"),
    "bow": ("down", "down", "rr", "bend", "stand", "sad"),
    "dead_tired": ("out_down", "out_down", "rr", "bend", "wide", "tired"),
    "dizzy": ("out", "out_down", "rr", "lean_l", "cross", "shock"),
    "slip": ("up", "out_down", "l", "back", "kick_l", "shock"),
    "whoa": ("up", "up", "ll", "back", "stand", "shock"),
    "faint": ("head", "out", "ll", "back", "kick_r", "shock"),
    "sob": ("face", "face", "r", "c", "stand", "sad"),
    "accuse": ("point", "fist_up", "r", "lean_r", "stand", "angry"),
    "rant": ("out_up", "fist_up", "l", "c", "wide", "angry"),
    "make_it_rain": ("up_bent", "up", "l", "c", "stand", "happy"),
    "carry": ("down", "out_down", "r", "lean_l", "stand", "tired"),
    "cold": ("across", "across", "r", "c", "cross", "sad"),
    "mic_drop": ("out_up", "down", "r", "c", "stand", "proud"),
    "rock_on": ("up_bent", "fist_up", "l", "c", "wide", "happy"),
    "reverse_dab": ("chin", "point", "ll", "c", "stand", "happy"),
    "disco": ("point_up", "point_down", "c", "lean_l", "stand", "happy"),
    "robot": ("robot", "robot", "c", "c", "stand", "happy"),
    "hello": ("wave", "wave", "c", "c", "stand", "happy"),
    "farewell": ("wave", "hip", "l", "c", "stand", "sad"),
    "taxi": ("point_up", "hip", "c", "lean_r", "stand", "think"),
    "hmm": ("shrug", "chin", "l", "c", "stand", "think"),
    "eureka": ("point_up", "down", "c", "c", "knee_l", "happy"),
    "deep_thought": ("chin", "across", "rr", "c", "cross", "think"),
    "nervous": ("mouth", "behind", "r", "c", "cross", "shock"),
    "shy": ("face", "behind", "rr", "lean_r", "cross", "sneaky"),
    "proud": ("hip", "heart", "l", "lean_l", "stand", "proud"),
    "boss": ("across", "across", "c", "lean_l", "wide", "proud"),
    "ceo": ("phone", "hip", "l", "c", "stand", "proud"),
    "salesman": ("offer", "point", "c", "lean_r", "stand", "sneaky"),
    "grab_cash": ("forward", "forward", "c", "lean_r", "wide", "greedy"),
    "empty_pockets": ("offer", "offer", "r", "c", "stand", "sad"),
    "cheers": ("out_up", "hip", "l", "c", "stand", "happy"),
    "weightlift": ("up_bent", "up_bent", "c", "c", "wide", "proud"),
    "sprint": ("fist_low", "flex", "r", "lean_r", "knee_l", "shock"),
    "awkward": ("behind", "down", "rr", "c", "cross", "sad"),
    "maestro": ("out_up", "up_bent", "l", "c", "stand", "happy"),
    "magic": ("up", "offer", "l", "c", "stand", "happy"),
    "zen": ("offer", "offer", "c", "c", "cross", "think"),
    "tiptoe": ("out_down", "out_down", "l", "c", "knee_r", "sneaky"),
    "lookout": ("salute", "down", "rr", "lean_r", "knee_l", "think"),
    "greedy": ("forward", "fist_low", "r", "lean_r", "stand", "greedy"),
    "plead": ("offer", "heart", "l", "c", "knee_l", "beg"),
    "smug": ("across", "thumb", "ll", "lean_l", "stand", "proud"),
    "facepalm_both": ("face", "head", "rr", "c", "stand", "sad"),
    "rooted": ("down", "down", "c", "c", "wide", "angry"),
    "hug_air": ("out_up", "out_up", "r", "lean_r", "stand", "happy"),
    "cheerleader": ("up", "hip", "l", "c", "knee_l", "happy"),
    "stop_both": ("forward", "forward", "l", "lean_l", "wide", "shock"),
    "pointing_self": ("chin", "down", "c", "c", "stand", "proud"),
}

POSE_LIB = {name: build(*spec[:5]) for name, spec in POSE_SPECS.items()}
POSE_FEEL = {name: spec[5] for name, spec in POSE_SPECS.items()}

# ---------------------------------------------------------------------------
# Actions.  Steps (frames are offsets from the shot start, e = shot end):
#   ("pose", name, f)  ("cycle", [poses], step)  ("bounce", f, height)  ("hop", f, height)
#   ("spin", f, turns)  ("punch", f, amount)  ("shiver", amp)  ("flatten", f, hold)
#   ("eyes", mode, f)  ("mouth", name, f)  ("squint", v, f)  ("look", dx, dz, f)
#   ("sfx", name, f, volume)  ("prop", name, f)  ("fx", kind, f, dx, z, size)
#   ("shake", f, length, amp)  ("walk", dx, step, arms_pose)  ("tears", f)
#   ("notes", f)  ("coins", f)  ("fly", f)  ("slide", dx, f0, f1)
A = {
    # --- joy ---
    "victory_jump": ("jumps with both arms up", [("pose", "victory", 1), ("bounce", 3, 0.4), ("sfx", "chaching", 6, 0.5), ("mouth", "grin", 1)]),
    "touchdown_dance": ("touchdown celebration, wide stance, arms up and down", [("cycle", ["touchdown", "champion"], 6), ("sfx", "crowd", 2, 0.35)]),
    "spin_cheer": ("spins and lands in a victory pose", [("spin", 1, 1), ("pose", "victory", 17), ("fx", "star", 18, 0.0, 3.3, 0.6), ("sfx", "whirl", 1, 0.6)]),
    "happy_hops": ("three small happy hops", [("pose", "jump_joy", 1), ("hop", 2, 0.2), ("hop", 12, 0.2), ("hop", 22, 0.2), ("mouth", "grin", 1)]),
    "rock_star": ("air guitar, head banging", [("cycle", ["rock_on", "hello"], 4), ("sfx", "riser2", 1, 0.3)]),
    "disco_fever": ("disco pointing up and down", [("cycle", ["disco", "point_floor"], 7), ("hop", 10, 0.12)]),
    "robot_dance": ("stiff robot dance", [("cycle", ["robot", "t_pose", "robot", "stop_both"], 5), ("sfx", "glitch", 3, 0.3)]),
    "cheerleader_kicks": ("cheerleader moves with kicks", [("cycle", ["cheerleader", "hip_wave", "victory"], 6), ("hop", 6, 0.15)]),
    "maestro_conduct": ("conducts an invisible orchestra", [("cycle", ["maestro", "magic", "maestro", "tada"], 7)]),
    "hello_wave": ("big two-handed hello", [("cycle", ["hello", "hip_wave"], 5), ("mouth", "smile", 1)]),
    "jump_kick_joy": ("jumps and kicks the air", [("pose", "kick", 2), ("bounce", 2, 0.3), ("sfx", "whoosh", 2, 0.6)]),
    "airplane_run": ("runs like an airplane", [("walk", 0.7, 5, "airplane"), ("sfx", "whoosh", 3, 0.5)]),
    "moonwalk": ("slides backwards smoothly", [("pose", "chill", 1), ("slide", -0.6, 2, 26), ("sfx", "whoosh", 2, 0.4)]),
    "tada_reveal": ("ta-da with sparkle", [("pose", "tada", 2), ("fx", "star", 4, 0.8, 3.2, 0.6), ("fx", "star", 6, -0.8, 3.2, 0.6), ("sfx", "pop", 2, 0.6)]),
    "hug_the_world": ("opens arms for a huge hug", [("pose", "hug_air", 2), ("eyes", "wide", 2), ("mouth", "grin", 2), ("bounce", 4, 0.15)]),
    "payday_jump": ("jumps with money eyes", [("eyes", "money", 1), ("pose", "fist_pump", 1), ("bounce", 3, 0.35), ("sfx", "chaching", 4, 0.6), ("coins", 4)]),
    # --- money ---
    "make_it_rain": ("throws banknotes into the air", [("cycle", ["make_it_rain", "victory"], 6), ("notes", 3), ("sfx", "chaching", 3, 0.5)]),
    "count_fast": ("counts money very fast", [("cycle", ["count_a", "count_b"], 3), ("sfx", "type", 2, 0.4)]),
    "grab_the_cash": ("lunges and grabs the cash", [("pose", "grab_cash", 2), ("punch", 3, 0.06), ("eyes", "money", 2), ("sfx", "clink", 4, 0.5)]),
    "empty_wallet": ("shows empty pockets, a fly comes out", [("pose", "empty_pockets", 2), ("fly", 6), ("sfx", "buzz", 6, 0.4), ("mouth", "sad", 2)]),
    "money_slips_away": ("a banknote flies away, he reaches for it", [("pose", "stop", 4), ("notes", 1), ("look", 0.05, 0.03, 4), ("sfx", "whoosh", 2, 0.5)]),
    "coin_catch": ("coins rain and he tries to catch them", [("cycle", ["grab_cash", "surrender"], 6), ("coins", 1), ("sfx", "chaching", 3, 0.5)]),
    "greedy_rub": ("rubs hands greedily", [("cycle", ["greedy", "grab_cash"], 4), ("eyes", "money", 1), ("mouth", "grin", 1)]),
    "salesman_pitch": ("smooth sales pitch", [("cycle", ["salesman", "handshake", "point_far"], 8), ("mouth", "grin", 1)]),
    "ceo_walk": ("walks like a CEO on the phone", [("walk", 0.5, 8, "ceo")]),
    "boss_pose": ("crosses arms like the boss", [("pose", "boss", 2), ("squint", 0.55, 2), ("sfx", "shimmer", 2, 0.3)]),
    "check_receipt": ("reads a long receipt, gets shocked", [("pose", "photo", 1), ("pose", "whoa", 20), ("eyes", "wide", 20), ("sfx", "boom", 20, 0.35)]),
    "piggy_smash": ("smashes the piggy bank (karate)", [("pose", "karate", 2), ("punch", 6, 0.1), ("fx", "star", 6, 0.6, 1.4, 0.8), ("sfx", "hit", 6, 0.5), ("coins", 7)]),
    # --- shock ---
    "double_take": ("looks, looks away, looks back shocked", [("look", 0.05, 0.0, 1), ("look", -0.05, 0.0, 8), ("look", 0.0, 0.0, 14), ("pose", "whoa", 14), ("punch", 14, 0.08), ("eyes", "wide", 14)]),
    "jaw_drop": ("freezes with a huge open mouth", [("mouth", "scream", 2), ("eyes", "wide", 2), ("pose", "surrender", 2), ("fx", "lines", 2, 0.0, 2.78, 1.0)]),
    "faint_dramatic": ("faints dramatically", [("pose", "faint", 4), ("squint", 0.1, 6), ("sfx", "fall", 2, 0.3), ("shake", 8, 6, 0.04)]),
    "heart_attack": ("clutches his heart, heartbeat", [("pose", "hand_on_heart", 2), ("shiver", 0.02), ("sfx", "heart_fast", 1, 0.3), ("eyes", "wide", 2)]),
    "jump_scare": ("jumps out of his skin", [("pose", "whoa", 1), ("bounce", 1, 0.55), ("sfx", "boom", 1, 0.4), ("eyes", "wide", 1), ("mouth", "scream", 1)]),
    "frozen_stare": ("frozen stare, nothing moves", [("pose", "rooted", 1), ("squint", 0.55, 4), ("mouth", "neutral", 1)]),
    "panic_run": ("runs in circles panicking", [("walk", 0.8, 4, "panic"), ("sfx", "riser", 1, 0.2), ("prop", "sweat", 2)]),
    "stop_stop": ("waves both hands: STOP!", [("cycle", ["stop_both", "surrender"], 5), ("mouth", "scream", 1)]),
    "dizzy_spin": ("spins and wobbles dizzy", [("spin", 1, 2), ("pose", "dizzy", 17), ("fx", "star", 18, 0.0, 3.4, 0.5), ("sfx", "whirl", 1, 0.6)]),
    "slip_banana": ("slips and almost falls", [("pose", "slip", 2), ("sfx", "spring", 2, 0.45), ("shake", 3, 6, 0.04), ("pose", "whoa", 14)]),
    "whoa_back": ("leans back in disbelief", [("pose", "whoa", 2), ("eyes", "wide", 2), ("sfx", "rewind", 2, 0.3)]),
    "nervous_sweat": ("sweats nervously", [("pose", "nervous", 1), ("prop", "sweat", 3), ("shiver", 0.01), ("look", -0.04, 0.0, 6)]),
    "point_and_scream": ("points at something and screams", [("pose", "point_far", 2), ("mouth", "scream", 2), ("eyes", "wide", 2), ("sfx", "boom", 2, 0.3)]),
    # --- sad ---
    "sob_story": ("sobs into his hands", [("pose", "sob", 2), ("tears", 3), ("sfx", "trombone", 4, 0.45)]),
    "slow_slump": ("slowly slumps down", [("pose", "awkward", 2), ("pose", "bow", 22), ("mouth", "sad", 2)]),
    "beg_please": ("begs on one knee", [("cycle", ["beg", "plead"], 8), ("mouth", "sad", 1)]),
    "deflate": ("deflates like a balloon", [("pose", "scarecrow", 1), ("flatten", 4, 10), ("sfx", "trombone", 2, 0.5)]),
    "big_sigh": ("a huge tired sigh", [("pose", "dead_tired", 4), ("squint", 0.55, 4)]),
    "touched_tear": ("touched, one tear", [("pose", "touched", 2), ("tears", 6), ("mouth", "smile", 2)]),
    "lonely_wave": ("waves goodbye sadly", [("cycle", ["farewell", "awkward"], 9), ("mouth", "sad", 1)]),
    "cold_shiver": ("shivers from cold", [("pose", "cold", 1), ("shiver", 0.025)]),
    "head_hang": ("hangs his head in shame", [("pose", "facepalm_both", 2), ("squint", 0.1, 4), ("sfx", "trombone", 3, 0.4)]),
    # --- angry ---
    "stomp_stomp": ("stomps angrily", [("pose", "rooted", 1), ("hop", 2, 0.1), ("hop", 10, 0.1), ("hop", 18, 0.1), ("sfx", "land", 4, 0.4), ("sfx", "land", 12, 0.4), ("shake", 4, 16, 0.03)]),
    "fist_shake": ("shakes his fist", [("cycle", ["fist_pump", "accuse"], 4), ("mouth", "scream", 1)]),
    "rant_mode": ("rants with wild gestures", [("cycle", ["rant", "accuse", "both_ways"], 6), ("mouth", "open", 1)]),
    "karate_chop": ("karate chop with a yell", [("pose", "karate", 2), ("punch", 4, 0.08), ("sfx", "hit", 4, 0.5), ("fx", "lines", 4, 0.0, 2.78, 1.0)]),
    "shadow_boxing": ("boxes the air", [("cycle", ["boxer", "stop", "boxer", "karate"], 4), ("sfx", "hit", 6, 0.3)]),
    "kick_air": ("kicks the air in anger", [("pose", "kick", 3), ("sfx", "whoosh", 3, 0.6), ("punch", 5, 0.05)]),
    "skeptic_glare": ("crosses arms and glares", [("pose", "skeptical", 2), ("squint", 0.55, 2), ("look", 0.04, 0.0, 2)]),
    "rage_quake": ("shakes with rage, rumble", [("pose", "champion", 1), ("shiver", 0.03), ("sfx", "rumble", 1, 0.38), ("mouth", "scream", 1)]),
    "accuse_point": ("points accusingly", [("pose", "accuse", 2), ("punch", 3, 0.05), ("brows", -14, 0.0, 2)]),
    # --- thinking / sneaky ---
    "eureka_bulb": ("gets a brilliant idea", [("pose", "eureka", 3), ("prop", "bulb", 3), ("sfx", "ding", 3, 0.6), ("eyes", "wide", 3)]),
    "hmm_think": ("thinks hard, question mark", [("pose", "hmm", 2), ("prop", "question", 4), ("look", 0.0, 0.05, 2)]),
    "deep_think": ("deep thought, looks up", [("pose", "deep_thought", 2), ("look", 0.03, 0.05, 6)]),
    "chin_rub": ("rubs his chin slowly", [("cycle", ["chin_stroke", "hmm"], 10)]),
    "sneak_walk": ("sneaks on tiptoes", [("walk", 0.6, 9, "sneak")]),
    "tiptoe_peek": ("tiptoes and peeks", [("pose", "tiptoe", 2), ("look", 0.05, 0.0, 4), ("look", -0.05, 0.0, 14)]),
    "shh_secret": ("shh, it's a secret", [("pose", "shh", 2), ("squint", 0.55, 2), ("sfx", "drop", 2, 0.2)]),
    "listen_close": ("listens closely", [("pose", "listen", 2), ("look", 0.05, 0.0, 2), ("prop", "exclaim", 14)]),
    "lookout_scan": ("scans the horizon", [("pose", "lookout", 1), ("look", -0.05, 0.0, 2), ("look", 0.05, 0.0, 14)]),
    "innocent_whistle": ("acts innocent", [("pose", "innocent", 2), ("look", 0.0, 0.05, 2), ("mouth", "think", 2)]),
    "salesman_wink": ("winks with a sly smile", [("pose", "salesman", 2), ("squint", 0.1, 8), ("squint", 1.0, 12), ("mouth", "grin", 2)]),
    "both_ways_confused": ("points both ways, confused", [("cycle", ["both_ways", "shrug_big"], 8), ("prop", "question", 4)]),
    # --- body / physical comedy ---
    "stretch_yawn": ("stretches and yawns", [("pose", "stretch", 2), ("pose", "yawn", 16), ("mouth", "open", 16), ("squint", 0.3, 16)]),
    "side_stretch": ("side stretches like a gym bro", [("cycle", ["side_bend", "stretch"], 9)]),
    "weightlifting": ("lifts an invisible weight, shaking", [("pose", "weightlift", 2), ("shiver", 0.015), ("prop", "sweat", 6)]),
    "bodybuilder_flex": ("flexes like a bodybuilder", [("cycle", ["bodybuilder", "one_flex"], 8), ("fx", "star", 4, 0.75, 3.1, 0.5)]),
    "hero_landing": ("superhero landing", [("bounce", 1, 0.5), ("pose", "hero_stance", 12), ("fx", "dust", 13, 0.0, 0.1, 1.0), ("sfx", "land", 13, 0.5), ("shake", 13, 6, 0.05)]),
    "march_proud": ("marches proudly", [("cycle", ["march", "rooted"], 7), ("sfx", "land", 4, 0.2)]),
    "zombie_walk": ("walks like a sleepy zombie", [("walk", 0.5, 10, "zombie"), ("squint", 0.3, 1)]),
    "sprint_in_place": ("sprints in place", [("cycle", ["sprint", "yes"], 3), ("sfx", "whoosh", 2, 0.4)]),
    "bow_thanks": ("bows deeply", [("pose", "bow", 3), ("sfx", "crowd", 4, 0.3)]),
    "selfie_snap": ("takes a selfie", [("pose", "selfie", 2), ("mouth", "grin", 2), ("sfx", "pop", 10, 0.5)]),
    "photo_frame": ("frames a photo with his hands", [("pose", "photo", 2), ("squint", 0.55, 2), ("sfx", "pop", 12, 0.5)]),
    "phone_call": ("answers an important call", [("pose", "on_call", 2), ("sfx", "ding", 1, 0.5), ("mouth", "open", 6)]),
    "taxi_whistle": ("calls a taxi", [("pose", "taxi", 2), ("sfx", "whoosh", 3, 0.3), ("look", -0.05, 0.0, 2)]),
    "salute_sir": ("salutes like a soldier", [("pose", "salute", 2), ("punch", 2, 0.04), ("sfx", "hit", 2, 0.2)]),
    "oath_promise": ("swears an oath", [("pose", "oath", 2), ("squint", 0.55, 2), ("sfx", "riser", 2, 0.15)]),
    "magic_trick": ("does a magic trick", [("pose", "magic", 2), ("fx", "star", 5, 0.6, 2.4, 0.7), ("sfx", "pop", 5, 0.6), ("pose", "tada", 14)]),
    "mic_drop_move": ("drops the mic", [("pose", "mic_drop", 2), ("pose", "chill", 14), ("sfx", "boom", 14, 0.4)]),
    "zen_breath": ("meditates calmly", [("pose", "zen", 2), ("squint", 0.1, 2), ("hop", 10, 0.06)]),
    "thumbs_up_wink": ("thumbs up and wink", [("pose", "thumbs_up", 2), ("squint", 0.1, 6), ("squint", 1.0, 10), ("sfx", "ding", 6, 0.4)]),
    "double_thumbs_bounce": ("double thumbs up with a bounce", [("pose", "double_thumbs", 2), ("bounce", 3, 0.18)]),
    "cheers_toast": ("raises a toast", [("pose", "cheers", 2), ("sfx", "clink", 4, 0.6), ("mouth", "grin", 2)]),
    "handshake_deal": ("offers a deal handshake", [("pose", "handshake", 2), ("mouth", "grin", 2), ("sfx", "chaching", 8, 0.4)]),
    "beckon_come": ("beckons: come here", [("cycle", ["beckon", "casual"], 6), ("squint", 0.55, 1)]),
    "point_self_proud": ("points at himself proudly", [("pose", "pointing_self", 2), ("bounce", 3, 0.12), ("mouth", "grin", 2)]),
    "proud_chest": ("puffs up his chest", [("pose", "proud", 2), ("bounce", 4, 0.1), ("sfx", "shimmer", 4, 0.3)]),
    "sassy_turn": ("sassy hip turn", [("cycle", ["sassy", "casual"], 9)]),
    "chill_lean": ("leans back, totally chill", [("pose", "chill", 2), ("squint", 0.55, 4), ("mouth", "smile", 2)]),
    "smug_grin": ("smug face, arms crossed", [("pose", "smug", 2), ("mouth", "grin", 2), ("squint", 0.55, 2)]),
    "awkward_wave": ("awkward little wave", [("cycle", ["hi_there", "awkward"], 8), ("mouth", "smile", 1)]),
    "shy_hide": ("hides his face shyly", [("pose", "shy", 2), ("look", 0.04, -0.03, 2)]),
    "head_scratch_confused": ("scratches his head", [("cycle", ["head_scratch", "hmm"], 6), ("prop", "question", 3)]),
    "hug_surprise": ("ready for a hug that never comes", [("pose", "hug_air", 2), ("pose", "awkward", 22), ("sfx", "error", 22, 0.35)]),
    "reverse_dab_move": ("reverse dab", [("pose", "reverse_dab", 2), ("sfx", "whoosh", 1, 0.6)]),
}
ACTION_LIB = A
