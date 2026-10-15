"""The AI crew: hook maker, writer, director and reviewer.

Each role is one chat call with a fixed brief.  The rules are the channel's own
(Sticky Goes Broke): English money sketches, a twist and a punchline, a new shot
about every 2 seconds, a sound on every action.
"""

import json

from . import vocab
from .llm import chat
from .storyboard import normalize, to_table

CHANNEL = """You work for the YouTube Shorts channel "Sticky Goes Broke" (@StickyGoesBroke).
Videos are in ENGLISH. The hero is Sticky, a stickman who makes money mistakes and loses in a funny way.
Channel promise: Sticky makes the money mistake so the viewer doesn't. Topics everyone recognises:
payday and bills, get-rich courses, subscriptions, phone addiction, waiting for a reply, shopping, work.
Format: a 20-45 second sketch, no narrator, short spoken lines, a relatable situation that turns and
ends on a punchline. Comedy rules: Sticky's own choices cause his failures, he is humiliated not harmed,
the audience likes him, gravity is his enemy, the world's rules stay consistent. Beats connect with
"but" or "therefore", never "and then". Escalate like stairs; a twist at 40-70% of the runtime; end fast
on the high note, or loop back to the first image. Keep money content honest: jokes, never promises.
Never copy other creators' jokes, never use memes or copyrighted audio."""

HOOK_RULES = """The hook is the first 2 seconds. Frame 1 already moves. Four S's: Subject (instantly clear),
Stakes (money gained or lost, a choice), Speed (fewest words), Clarity (one reading).
Triple hook: the on-screen text hook (max 2 short lines, specific numbers beat vague words),
the visual hook and the spoken hook (first line starts at once, no greeting) all say the same thing.
Strong shapes: a choice ("Would you take X or Y?"), an outcome tease (show the end first),
a shocking number ("This $2,000 TV cost $4,064"), a contrarian claim."""


def make_hooks(brief, log=None):
    user = f"""Brief from the creator:
topic: {brief.get('topic')}
genre: {brief.get('genre', 'comedy sketch')}
target length: {brief.get('seconds', 35)} seconds
notes: {brief.get('notes', '')}

{HOOK_RULES}

Write 3 different sketch ideas for this topic, each with its hook. Score each hook 1-10 honestly
for how few viewers would swipe away. Return JSON:
{{"hooks": [{{"premise": "one sentence a 10-year-old understands",
  "text_hook": "ON-SCREEN TEXT, max 6 words",
  "spoken_hook": "Sticky's first line, max 8 words",
  "visual_hook": "what moves on frame 1",
  "twist": "the turn nobody expects",
  "score": 8.5, "why": "one sentence"}}]}}"""
    data = chat(CHANNEL, user, strong=True, temperature=0.95, log=log)
    hooks = data.get("hooks", data if isinstance(data, list) else [])
    return sorted(hooks, key=lambda h: -float(h.get("score", 0) or 0))[:3]


def write_script(brief, hook, log=None):
    user = f"""Brief: topic "{brief.get('topic')}", genre {brief.get('genre', 'comedy sketch')},
about {brief.get('seconds', 35)} seconds. Notes: {brief.get('notes', '')}
Chosen idea and hook: {json.dumps(hook, ensure_ascii=False)}

Write the sketch as beats. A new beat about every 2 seconds. Speakers: sticky (always on screen),
phone (his phone talks with a face on its screen), narrator (only if really needed).
Spoken lines are short (max 12 words), and real speech is shorter than it looks on paper, so fill
the time with beats that SHOW something (numbers, phone screens, reactions, falls), not with talk.
Spell numbers out in spoken lines ("ninety-nine dollars"); captions may use digits ("$99").

Return JSON:
{{"title": "SHORT ON-SCREEN TITLE, max 23 characters",
  "video_name": "Curiosity Title For YouTube Without The Twist",
  "beats": [{{"what": "what we see", "line": {{"speaker": "sticky", "text": "..."}} or null,
             "caption": "text on screen or empty", "sound": "what we hear"}}],
  "twist_at_beat": 6,
  "upload": {{"title": "...", "description": "two lines, keeps the twist back; Example numbers, not financial advice.",
             "hashtags": ["#shorts", "..."], "pinned_comment": "a question that starts an argument"}}}}"""
    return chat(CHANNEL, user, strong=True, temperature=0.9, log=log)


DIRECTOR_RULES = f"""You are the director. You turn a sketch into a shot table that a Blender program
builds automatically. You may ONLY use these words; anything else breaks the render:

{vocab.vocabulary_text()}

Rules:
- Shot 1 camera is open_zoom (or room_push), with the text hook as a caption and the first line at line_at 0.1.
- A new shot every 1.5-2.5 s. Alternate wide/medium/face/phone shots. Never two identical cameras in a row.
- A shot with a spoken line stretches to fit it automatically; "seconds" is the minimum length.
- Every action gets a matching sfx (bounce, spin, flatten, fall_flat and coin_rain already add theirs).
- Exaggerated faces: eyes wide/money, mouth scream, brows angry/worried, props sweat/exclaim/question.
- Phone screens: camera phone_screen or phone_push with phone_text (up to 3 short lines: label, BIG NUMBER, small red line).
- Captions: max 6 words, never pos "big" on a face close-up.
- Use music_stop on the shock moment; the twist sits at 40-70% of the runtime.
- Last shot: the punchline, or an end_card shot with end_text (2 short lines).
- Keep every spoken line word for word; one line per shot at most.
- Give every line a mood that matches the moment (excited, shout, scared, sad, whisper, smug, deadpan,
  confused, normal); comedy lives in contrast, e.g. a deadpan line after a shout.
- Total length must stay under {vocab.MAX_SECONDS} s."""

STORYBOARD_SHAPE = """Return JSON exactly in this shape:
{"title": "...", "video_name": "...", "set": "none", "backdrop": "room", "music": "sneaky", "holds_phone": true,
 "lines": [{"id": "S01", "speaker": "sticky", "text": "...", "mood": "excited"}],
 "shots": [{"camera": "open_zoom", "seconds": 2.0, "line": "S01", "line_at": 0.1, "pose": "shock",
            "eyes": "wide", "mouth": "open", "brows": "worried", "look": "camera", "action": "punch",
            "shake": false, "music_stop": false, "caption": {"text": "...", "color": "red", "pos": "top"},
            "phone_text": [], "props": ["sweat"], "fx": null, "sfx": [{"name": "whoosh", "at": 0.0}]}],
 "end_text": [],
 "upload": {"title": "...", "description": "...", "hashtags": ["#shorts"], "pinned_comment": "..."}}
Line ids: S01, S02... for sticky, P01... for phone, N01... for narrator, R01... for rick."""


def direct(script, brief=None, log=None):
    user = f"""Sketch to film (JSON or text):
{script if isinstance(script, str) else json.dumps(script, ensure_ascii=False)}

Target length: about {(brief or {}).get('seconds', 35)} seconds.
{STORYBOARD_SHAPE}"""
    return normalize(chat(DIRECTOR_RULES, user, strong=True, temperature=0.5, log=log))


def direct_own_script(text, log=None):
    """The creator's own script: keep his words, only add the filming."""
    user = f"""This is the creator's OWN finished script. Keep every spoken line and the title word for word,
keep his order of events and his jokes; only decide cameras, poses, faces, captions and sounds.
If he wrote timings, follow them.

{text}

{STORYBOARD_SHAPE}"""
    return normalize(chat(DIRECTOR_RULES, user, strong=True, temperature=0.3, log=log))


def review(sb, check_result, log=None):
    user = f"""Shot table (time | camera | pose | action | spoken | caption | sfx):
{to_table(sb)}

Title: {sb.get('title')}
Rule checker said: {json.dumps(check_result, ensure_ascii=False)}

Review this Short like a strict head of retention. Check: the first 2 seconds (would people swipe?),
but/therefore links, something changing every 2-3 s, the twist at 40-70%, the payoff answering the hook,
a fast ending or loop, whether the joke lands. Return JSON:
{{"score": 7.5, "verdict": "one sentence", "keep": ["what works"],
  "fix": ["concrete change 1, naming the shot number", "..."]}}"""
    return chat(CHANNEL + "\n\n" + HOOK_RULES, user, temperature=0.3, log=log)


def revise(sb, notes, log=None):
    user = f"""Current storyboard:
{json.dumps(sb, ensure_ascii=False)}

Apply these fixes and keep everything else, including every spoken line word for word unless a fix
names it: {json.dumps(notes, ensure_ascii=False)}

{STORYBOARD_SHAPE}"""
    return normalize(chat(DIRECTOR_RULES, user, strong=True, temperature=0.3, log=log))
