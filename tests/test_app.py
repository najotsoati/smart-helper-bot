import json
import time

import pytest
from fastapi.testclient import TestClient

from studio import app as studio_app, config, store, tts

from .test_pipeline import SAMPLE, run_script


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "PANEL_PASSWORD", "pw")
    monkeypatch.setattr(config, "AGENT_TOKEN", "tok")
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "")
    return TestClient(studio_app.app)


def wait_idle(pid):
    for _ in range(100):
        if not store.load(pid).get("busy"):
            return store.load(pid)
        time.sleep(0.05)
    raise AssertionError("still busy")


def test_panel_needs_login(client):
    assert client.get("/").status_code == 401
    assert client.get("/", auth=("admin", "nope")).status_code == 401
    assert client.get("/", auth=("admin", "pw")).status_code == 200


def test_agent_needs_token(client):
    assert client.get("/api/agent/next").status_code == 401
    assert client.get("/api/agent/next", headers={"Authorization": "Bearer tok"}).json() == {"job": None}


def test_full_flow_with_storyboard_json(client, monkeypatch):
    auth = ("admin", "pw")
    r = client.post("/own", data={"text": json.dumps(SAMPLE)}, auth=auth, follow_redirects=False)
    assert r.status_code == 303
    pid = r.headers["location"].rsplit("/", 1)[1]
    p = store.load(pid)
    assert p["state"] == "storyboard" and p["check"]["errors"] == []
    page = client.get(f"/p/{pid}", auth=auth).text
    assert "Rejissyor jadvali" in page and "My Salary Lasted 5 Minutes" in page

    # queue before voice is refused
    client.post(f"/p/{pid}/do/queue", auth=auth)
    assert store.load(pid)["state"] == "storyboard"

    def fake_voice(sb, audio_dir, **kw):
        audio_dir.mkdir(parents=True, exist_ok=True)
        for ln in sb["lines"]:
            (audio_dir / f"{ln['id']}.mp3").write_bytes(b"ID3")
            ln["file"], ln["seconds"] = f"{ln['id']}.mp3", 1.2
        return sb
    monkeypatch.setattr(tts, "voice_lines", fake_voice)
    client.post(f"/p/{pid}/do/voice", auth=auth)
    p = wait_idle(pid)
    assert p["state"] == "voiced", p["error"]
    client.post(f"/p/{pid}/do/queue", auth=auth)
    assert store.load(pid)["state"] == "queued"

    h = {"Authorization": "Bearer tok"}
    job = client.get("/api/agent/next", headers=h).json()["job"]
    assert job["id"] == pid and job["audio"][0] == "S01.mp3"
    assert 'A = "//studio_audio/' + pid + '/"' in job["script"]
    assert client.get(f"/api/agent/{pid}/audio/S01.mp3", headers=h).content == b"ID3"
    assert client.get(f"/api/agent/{pid}/audio/..%2Fproject.json", headers=h).status_code == 404
    assert store.load(pid)["state"] == "rendering"
    assert client.get("/api/agent/next", headers=h).json() == {"job": None}

    client.post(f"/api/agent/{pid}/status", headers=h, json={"message": "Blender: video_10"})
    r = client.post(f"/api/agent/{pid}/video", headers=h, files={"file": ("video.mp4", b"MP4DATA", "video/mp4")})
    assert r.json() == {"ok": True}
    assert store.load(pid)["state"] == "done"
    assert client.get(f"/p/{pid}/video.mp4", auth=auth).content == b"MP4DATA"
    assert "video.mp4" in client.get(f"/p/{pid}", auth=auth).text


def test_save_storyboard_rejects_bad_json(client):
    auth = ("admin", "pw")
    r = client.post("/own", data={"text": json.dumps(SAMPLE)}, auth=auth, follow_redirects=False)
    pid = r.headers["location"].rsplit("/", 1)[1]
    client.post(f"/p/{pid}/do/save_storyboard", data={"sb_json": "{nope"}, auth=auth)
    assert "JSON" in store.load(pid)["error"]


def test_ai_step_without_key_shows_error(client):
    auth = ("admin", "pw")
    r = client.post("/new", data={"topic": "payday", "seconds": 35}, auth=auth, follow_redirects=False)
    pid = r.headers["location"].rsplit("/", 1)[1]
    p = wait_idle(pid)
    assert "OPENROUTER_API_KEY" in p["error"]
    assert "OPENROUTER_API_KEY" in client.get(f"/p/{pid}", auth=auth).text


def test_rejected_key_is_reported_once(monkeypatch, tmp_path):
    import httpx
    from studio import llm
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "sk-or-v1-x")
    monkeypatch.setattr(config, "OPENROUTER_MODELS", ["a:free", "b:free", "c:free"])
    calls = []

    def fake_post(url, **kw):
        calls.append(kw["json"]["model"])
        return httpx.Response(401, json={"error": {"message": "Missing Authentication header"}})
    monkeypatch.setattr(httpx, "post", fake_post)
    with pytest.raises(llm.LLMError) as e:
        llm.chat("s", "u")
    assert calls == ["a:free"]
    assert "OPENROUTER_API_KEY" in str(e.value)


def test_forbidden_model_tries_next(monkeypatch, tmp_path):
    import httpx
    from studio import llm
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "sk-or-v1-x")
    monkeypatch.setattr(config, "OPENROUTER_MODELS", ["a:free", "b:free"])

    def fake_post(url, **kw):
        if kw["json"]["model"] == "a:free":
            return httpx.Response(403, json={"error": {"message": "model not available"}})
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"ok": 1}'}}]})
    monkeypatch.setattr(httpx, "post", fake_post)
    assert llm.chat("s", "u") == {"ok": 1}


def test_voices_page_and_choice(client, monkeypatch):
    auth = ("admin", "pw")
    assert "Ovozlar" in client.get("/voices", auth=auth).text
    r = client.post("/voices", data={"sticky": "en-US-GuyNeural", "phone": "nope"}, auth=auth,
                    follow_redirects=False)
    assert r.status_code == 303
    assert store.settings()["voices"] == {"sticky": "en-US-GuyNeural"}
    assert tts.edge_voice("sticky") == "en-US-GuyNeural"
    assert client.get("/voices/sample.mp3?voice=bad&mood=normal", auth=auth).status_code == 400

    calls = []
    monkeypatch.setattr(tts, "_edge", lambda text, voice, path, mood="normal": (calls.append((voice, mood)),
                                                                            path.write_bytes(b"ID3")))
    r = client.get("/voices/sample.mp3?voice=en-US-GuyNeural&mood=shout", auth=auth)
    assert r.status_code == 200 and calls == [("en-US-GuyNeural", "shout")]


def test_unknown_mood_falls_back():
    from studio.storyboard import normalize
    sb = normalize({"lines": [{"id": "S01", "text": "hi", "mood": "furious"}], "shots": []})
    assert sb["lines"][0]["mood"] == "normal"


def test_grok_writes_first_when_key_set(monkeypatch):
    from studio import llm
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "or")
    monkeypatch.setattr(config, "OPENROUTER_MODELS", ["a:free"])
    monkeypatch.setattr(config, "XAI_API_KEY", "xk")
    monkeypatch.setattr(config, "XAI_FIRST", True)
    assert [c[0] for c in llm._candidates(strong=True)] == ["xai", "openrouter"]
    assert [c[0] for c in llm._candidates(strong=False)] == ["openrouter", "xai"]
    monkeypatch.setattr(config, "XAI_FIRST", False)
    assert [c[0] for c in llm._candidates(strong=True)] == ["openrouter", "xai"]
