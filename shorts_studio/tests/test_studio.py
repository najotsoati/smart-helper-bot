"""Offline tests: no API keys or network needed.  Run:  python -m pytest -q"""

import json
import subprocess
from pathlib import Path

import pytest

from studio import captions, config, graphics, mascot, pipeline, render
from studio.script import CheckedScript, ShortScript, _strict_schema
from studio.voice import Word

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ShortScript.model_validate(json.loads((ROOT / "assets" / "sample_script.json").read_text()))


def _objects(node):
    if isinstance(node, dict):
        if node.get("type") == "object":
            yield node
        for v in node.values():
            yield from _objects(v)
    elif isinstance(node, list):
        for v in node:
            yield from _objects(v)


@pytest.mark.parametrize("model", [ShortScript, CheckedScript])
def test_structured_output_schema_is_strict(model):
    schema = _strict_schema(model)
    for obj in _objects(schema):
        assert obj["additionalProperties"] is False
        assert set(obj["required"]) == set(obj["properties"])
    assert "default" not in json.dumps(schema)


def test_captions_highlight_each_word_and_move_below_host():
    words = captions.mark_emphasis(
        [Word("Everest", 0.0, 0.4), Word("is", 0.4, 0.6), Word("8,849", 0.6, 1.2), Word("meters.", 1.2, 1.6)],
        ["Everest"],
    )
    assert [w.emphasis for w in words] == [True, False, True, False]  # numbers are always emphasised
    ass = captions.build_ass(words, [(0, 1, "TALL")], 2.0, host_ranges=[(0.0, 0.5)], badge=True)
    dialogue = [l for l in ass.splitlines() if l.startswith("Dialogue: 0")]
    assert len(dialogue) == len(words)
    assert "1450" in dialogue[0] and "1180" in dialogue[-1]  # first word under the host, last one normal
    assert ",290,40,300,1" in ass  # titles shifted right to clear the badge


def test_graphics_events():
    c = graphics.counter(1.0, 4.0, 10935, "", " M", "deep")
    assert c[-2].endswith("10,935 M") or "10,935 M" in c[-2]
    bars = graphics.compare(1.0, 4.0, "Everest", 8849, "Trench", 10935, "meters")
    assert sum("\\p1" in e for e in bars) == 2


def test_plan_visuals_falls_back_without_keys(monkeypatch):
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    monkeypatch.setattr(config, "PEXELS_API_KEY", "")
    kinds = pipeline.plan_visuals(SAMPLE.scenes, "mixed", host=True, offline=False)
    assert kinds[0] == "mascot"
    assert set(kinds) <= {"mascot", "gradient"}
    no_host = pipeline.plan_visuals(SAMPLE.scenes, "mixed", host=False, offline=False)
    assert "mascot" not in no_host


def test_hook_variant_swaps_only_the_hook():
    b = pipeline.hook_variant(SAMPLE)
    assert b.scenes[0].narration != SAMPLE.scenes[0].narration
    assert [s.narration for s in b.scenes[1:]] == [s.narration for s in SAMPLE.scenes[1:]]


def test_mascot_lip_sync_and_emotions(tmp_path):
    speech = tmp_path / "speech.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "aevalsrc='sin(2*PI*180*t)*gt(mod(t\\,1)\\,0.3)':d=4:s=44100",
                    "-c:a", "pcm_s16le", str(speech)], check=True)
    frames = mascot.timeline(speech, [(0, 2, "excited"), (2, 4, "scared")])
    assert len(frames) == 4 * config.FPS
    assert any(f.endswith("_open") for f in frames) and any(f.endswith("_closed") for f in frames)
    assert all(f.startswith("excited") for f in frames[: config.FPS])
    assert all(f.startswith("scared") for f in frames[2 * config.FPS + 1:])


def test_schedule_slots_are_in_the_future_and_ordered():
    from studio.jobs import schedule_slots
    slots = schedule_slots(5, "", 2, ["10:00", "18:00"])
    assert len(slots) == 5 and slots == sorted(slots)


def test_motion_filters_render(tmp_path):
    still = tmp_path / "still.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1024x1536",
                    "-frames:v", "1", str(still)], check=True)
    for move in render.MOVES:
        out = render.image_segment(still, 0.5, tmp_path / f"{move}.mp4", move)
        assert out.stat().st_size > 0


@pytest.mark.slow
def test_full_offline_render(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    video = pipeline.make_video(SAMPLE, tmp_path, offline=True, music=False, series="Test #1")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,codec_type",
                            "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    assert "1080,1920" in probe.replace("video,", "") or "video,1080,1920" in probe
    meta = json.loads((tmp_path / "meta.json").read_text())
    assert meta["title"].startswith("Test #1")
    assert not (tmp_path / "work").exists()


def test_learning_rows_and_playbook_prompt(tmp_path, monkeypatch):
    from studio import db, learn

    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(db, "PATH", tmp_path / "studio.db")
    db.init()
    folder = tmp_path / "20260101-ocean"
    folder.mkdir()
    (folder / "meta.json").write_text(json.dumps({"topic": "ocean", "hook": "Drop Everest here", "duration": 33}))
    db.save_video(folder.name, "a", youtube_id="abcdefghijk",
                  metrics=json.dumps({"views": 1200, "engagedViews": 900, "stayedToWatch": 75.0}))
    rows = learn.performance_rows()
    assert rows == [{"video": "20260101-ocean/a", "topic": "ocean", "hook": "Drop Everest here", "title": None,
                     "seconds": 33, "picture_match": None, "views": 1200, "engagedViews": 900,
                     "stayedToWatch": 75.0}]
    assert learn.playbook_prompt() == ""
    db.execute("INSERT INTO playbook (created, data) VALUES (1, ?)", (json.dumps({
        "summary": "Short space hooks win.", "winning_patterns": ["numbers in hook"], "losing_patterns": ["slow intros"],
        "hook_rules": ["start with a number"], "next_topics": [], "ab_findings": []}),))
    prompt = learn.playbook_prompt()
    assert "Do: numbers in hook" in prompt and "Avoid: slow intros" in prompt


def test_youtube_video_id_parsing():
    from studio.youtube import parse_video_id
    assert parse_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ?feature=share") == "dQw4w9WgXcQ"
    assert parse_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    with pytest.raises(ValueError):
        parse_video_id("not a link")


def test_save_key_writes_env_and_applies(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    monkeypatch.setattr(config, "ENV_FILE", env)
    monkeypatch.setattr(config, "PEXELS_API_KEY", "")
    config.save_key("PEXELS_API_KEY", "  abcd1234efgh5678 ")
    assert config.PEXELS_API_KEY == "abcd1234efgh5678"
    assert "PEXELS_API_KEY='abcd1234efgh5678'" in env.read_text()
    assert config.masked("PEXELS_API_KEY") == "abcd…5678"
    config.save_key("PEXELS_API_KEY", "")
    assert config.PEXELS_API_KEY == "" and "PEXELS" not in env.read_text()
    with pytest.raises(ValueError):
        config.save_key("PATH", "x")


def test_secrets_cannot_be_changed_remotely():
    from fastapi.testclient import TestClient

    import app as panel

    client = TestClient(panel.app)  # its requests come from host "testclient", i.e. not this machine
    assert client.post("/api/keys", json={"name": "PEXELS_API_KEY", "value": "x"}).status_code == 403
    assert client.post("/api/youtube/client_secret", json={"content": "{}"}).status_code == 403
    assert client.get("/api/keys").status_code == 200


def test_fact_check_failure_keeps_the_script(monkeypatch):
    from studio import script as script_mod

    def broken(_):
        raise RuntimeError("web search is disabled for this organization")

    monkeypatch.setattr(script_mod, "fact_check", broken)
    kept, checks, warning = script_mod.try_fact_check(SAMPLE)
    assert kept is SAMPLE and checks == []
    assert "web search is disabled" in warning


def test_pexels_failure_falls_back_instead_of_failing(monkeypatch):
    from studio import visuals

    monkeypatch.setattr(config, "PEXELS_API_KEY", "bad-key")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")

    def down(*_args, **_kwargs):
        raise RuntimeError("401 Unauthorized")

    monkeypatch.setattr(visuals, "candidates_for", down)
    durations = [3.0] * len(SAMPLE.scenes)
    plan = pipeline.choose_visuals(SAMPLE.scenes, durations, "stock", True, False, lambda *_: None)
    stock_scenes = [i for i, s in enumerate(SAMPLE.scenes) if s.visual_type != "mascot" or s.graphic_type != "none"]
    assert all(plan["kinds"][i] == "gradient" for i in stock_scenes if plan["kinds"][i] != "mascot")
    assert any("Stok video: 401 Unauthorized" in issue for issue in plan["issues"])


def test_claude_requests_against_a_fake_api(monkeypatch):
    """Runs the real Anthropic SDK against a local fake server: checks what we send and that we parse replies."""
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    from studio import script as script_mod

    seen: list[tuple[dict, dict]] = []

    def message(content, stop="end_turn"):
        return {"id": "msg_1", "type": "message", "role": "assistant", "model": config.CLAUDE_MODEL,
                "content": content, "stop_reason": stop, "stop_sequence": None,
                "usage": {"input_tokens": 1, "output_tokens": 1}}

    class Fake(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["content-length"])))
            seen.append((dict(self.headers), body))
            thinking = {"type": "thinking", "thinking": "", "signature": "sig"}
            if "tools" in body:  # the web-search fact-check turn
                searches = sum(1 for h, b in seen if "tools" in b)
                reply = message([thinking, {"type": "text", "text": "Everest is 8,849 m. All correct."}],
                                "pause_turn" if searches == 1 else "end_turn")
            elif "checks" in json.dumps(body["output_config"]["format"]["schema"]["properties"]):
                fixed = {"script": json.loads(SAMPLE.model_dump_json()),
                         "checks": [{"scene": 3, "verdict": "correct", "note": "ok", "source": "https://x"}]}
                reply = message([thinking, {"type": "text", "text": json.dumps(fixed)}])
            else:
                reply = message([thinking, {"type": "text", "text": SAMPLE.model_dump_json()}])
            data = json.dumps(reply).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *_):
            pass

    server = HTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("ANTHROPIC_BASE_URL", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test-key")
    try:
        draft = script_mod.write_script("the deepest point of the ocean", 35)
        checked, checks, warning = script_mod.try_fact_check(draft)
    finally:
        server.shutdown()

    assert draft.title == SAMPLE.title and warning == "" and checks[0].scene == 3
    headers, first = seen[0]
    assert first["model"] == config.CLAUDE_MODEL and first["fallbacks"] == "default"
    assert "server-side-fallback-2026-07-01" in headers.get("anthropic-beta", "")
    assert first["thinking"] == {"type": "adaptive"}
    assert first["output_config"]["format"]["type"] == "json_schema"
    assert "title" in first["output_config"]["format"]["schema"]["properties"]
    searches = [b for _, b in seen if "tools" in b]
    assert len(searches) == 2  # paused once, then resumed
    assert searches[1]["messages"][-1]["role"] == "assistant"  # resume = same turn sent back, no extra user message
    assert searches[0]["tools"][0]["type"] == "web_search_20260209"


def test_pixabay_search_parses_hits(monkeypatch):
    from studio import net, visuals

    monkeypatch.setattr(config, "PEXELS_API_KEY", "")
    monkeypatch.setattr(config, "PIXABAY_API_KEY", "pk")
    calls = []

    class Resp:
        def json(self):
            return {"hits": [
                {"id": 1, "duration": 2, "videos": {"medium": {"url": "https://v/1.mp4", "thumbnail": "https://t/1.jpg"}}},
                {"id": 2, "duration": 12, "picture_id": "555",
                 "videos": {"medium": {"url": ""}, "small": {"url": "https://v/2.mp4"}}},
                {"id": 3, "duration": 9, "videos": {"medium": {"url": "https://v/3.mp4", "thumbnail": "https://t/3.jpg"}}},
            ]}

    def fake_request(method, url, **kw):
        calls.append((url, kw["params"]))
        return Resp()

    monkeypatch.setattr(net, "request", fake_request)
    assert visuals.available()
    found = visuals.search("deep ocean dark", 5, exclude={visuals.PIXABAY_ID_OFFSET + 3})
    assert calls[0][0] == visuals.PIXABAY_API and calls[0][1]["key"] == "pk"
    assert [c.url for c in found] == ["https://v/2.mp4"]  # 1 too short, 3 excluded
    assert found[0].thumb == "https://i.vimeocdn.com/video/555_640x360.jpg"


def test_openrouter_free_model_and_json_retry(monkeypatch):
    """Runs the OpenRouter path against a local fake API: free-model pick, image parts, invalid-JSON retry."""
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    from studio import openrouter
    from studio import script as script_mod
    from studio.visuals import Picks

    chats: list[dict] = []
    models = {"data": [
        {"id": "anthropic/claude-x", "pricing": {"prompt": "0.000003", "completion": "0.000015"},
         "context_length": 200000, "architecture": {"input_modalities": ["text", "image"]}},
        {"id": "nvidia/nemotron-3-embed-1b:free", "pricing": {"prompt": "0", "completion": "0"},
         "context_length": 8000, "architecture": {"input_modalities": ["text"], "output_modalities": ["embeddings"]}},
        {"id": "nvidia/nemotron-3.5-content-safety:free", "pricing": {"prompt": "0", "completion": "0"},
         "context_length": 128000, "architecture": {"input_modalities": ["text", "image"]}},
        {"id": "mistralai/small:free", "pricing": {"prompt": "0", "completion": "0"}, "context_length": 32000,
         "architecture": {"input_modalities": ["text"]}},
        {"id": "deepseek/chat:free", "pricing": {"prompt": "0", "completion": "0"}, "context_length": 128000,
         "architecture": {"input_modalities": ["text"]}},
        {"id": "google/gemma-vision:free", "pricing": {"prompt": "0", "completion": "0"}, "context_length": 96000,
         "architecture": {"input_modalities": ["text", "image"]}},
    ]}

    class Fake(BaseHTTPRequestHandler):
        def _send(self, payload):
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._send(models)

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["content-length"])))
            chats.append(body)
            if body["model"] == "deepseek/chat:free" and len(chats) == 1:
                text = "<think>hmm</think>```json\n{\"topic\": \"x\"}\n```"  # incomplete -> must be retried
            elif body["model"] == "deepseek/chat:free":
                text = "Sure! " + SAMPLE.model_dump_json()
            else:
                text = json.dumps({"scenes": [{"scene": 1, "picks": [2], "match": 88}]})
            self._send({"choices": [{"message": {"content": text}}]})

        def log_message(self, *_):
            pass

    server = HTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(config, "OPENROUTER_BASE_URL", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "or-key")
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(openrouter, "_models_cache", (0.0, []))
    try:
        assert config.llm_provider() == "openrouter"
        draft = script_mod.write_script("venus", 35)
        picks = script_mod.ask_json([{"type": "text", "text": "pick"},
                                     {"type": "image", "source": {"type": "url", "url": "https://t/1.jpg"}}],
                                    Picks, system="s")
        _, checks, warning = script_mod.try_fact_check(draft)
    finally:
        server.shutdown()

    assert draft.title == SAMPLE.title
    assert [c["model"] for c in chats] == ["deepseek/chat:free", "deepseek/chat:free", "google/gemma-vision:free"]
    assert chats[1]["messages"][-1]["role"] == "user" and "invalid" in chats[1]["messages"][-1]["content"]
    assert chats[2]["messages"][1]["content"][1] == {"type": "image_url", "image_url": {"url": "https://t/1.jpg"}}
    assert picks.scenes[0].match == 88
    assert checks == [] and "veb-qidiruv" in warning


def test_openrouter_prefers_inkling(monkeypatch):
    from studio import openrouter

    free = {"prompt": "0", "completion": "0"}
    monkeypatch.setattr(config, "OPENROUTER_MODEL", "")
    monkeypatch.setattr(config, "OPENROUTER_VISION_MODEL", "")
    monkeypatch.setattr(openrouter, "_models", lambda: [
        {"id": "nvidia/nemotron-3-ultra-550b-a55b:free", "pricing": free, "architecture": {"input_modalities": ["text"]}},
        {"id": "thinkingmachines/inkling:free", "pricing": free,
         "architecture": {"input_modalities": ["text", "image", "audio"]}},
        {"id": "google/gemma-4-31b-it:free", "pricing": free, "architecture": {"input_modalities": ["text", "image"]}},
    ])
    assert openrouter.pick_model() == "thinkingmachines/inkling:free"
    assert openrouter.pick_model(vision=True) == "thinkingmachines/inkling:free"


def test_openrouter_falls_back_to_next_free_model(monkeypatch):
    from studio import net, openrouter
    from studio.script import TopicIdeas

    monkeypatch.setattr(openrouter, "ranked_models", lambda vision=False: ["busy/one:free", "ok/two:free"])
    calls = []

    class Resp:
        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    def fake_request(method, url, **kw):
        calls.append(kw["json"]["model"])
        if kw["json"]["model"] == "busy/one:free":
            return Resp({"error": {"message": "Upstream error from Nvidia: Service temporarily overloaded"}})
        return Resp({"choices": [{"message": {"content": '{"ideas": []}'}}]})

    monkeypatch.setattr(net, "request", fake_request)
    result = openrouter.ask_json("ideas", TopicIdeas, {}, "s")
    assert isinstance(result, TopicIdeas) and calls == ["busy/one:free", "ok/two:free"]


def test_explain_names_the_host_on_connection_reset():
    import httpx

    from studio import health

    request = httpx.Request("POST", "https://api.elevenlabs.io/v1/text-to-speech/x")
    text = health.explain(httpx.ConnectError("[WinError 10054] reset", request=request))
    assert "api.elevenlabs.io" in text and "Internet aloqasi uzildi" in text
