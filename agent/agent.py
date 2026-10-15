"""Shorts Studio render agent for the Windows laptop.

It asks the server for a queued video, downloads the voice clips, runs Blender in
the background on stickman_shablon.blend, copies the MP4 into TAYYOR/ and sends it
back to the panel.  Only the Python standard library is used.

    python agent.py            # keeps running, checks every 15 s
    python agent.py --once     # one job and exit
"""

import configparser
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
cfg = configparser.ConfigParser()
cfg.read(HERE / "agent.ini", encoding="utf-8")
C = cfg["agent"] if cfg.has_section("agent") else {}

SERVER = C.get("server_url", "http://127.0.0.1:8080").rstrip("/")
TOKEN = C.get("agent_token", "")
BLENDER = C.get("blender_exe", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FOLDER = Path(C.get("stickman_dir", r"C:\Users\sasis\Documents\Stickman"))
TEMPLATE = FOLDER / C.get("template", "stickman_shablon.blend")
POLL = int(C.get("poll_seconds", "15"))
# Optional: "root@1.2.3.4".  The agent then keeps an SSH tunnel to the panel open itself
# (needs a key without a password: run setup_ssh_key.bat once).
SSH_HOST = C.get("ssh_host", "").strip()
_tunnel = {"proc": None}


def keep_tunnel():
    """Start or restart `ssh -N -L port:127.0.0.1:port host` when it is not running."""
    if not SSH_HOST:
        return
    p = _tunnel["proc"]
    if p is not None and p.poll() is None:
        return
    port = SERVER.rsplit(":", 1)[-1].split("/")[0]
    cmd = ["ssh", "-N", "-L", f"{port}:127.0.0.1:{port}", "-o", "BatchMode=yes",
           "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=30",
           "-o", "StrictHostKeyChecking=accept-new", SSH_HOST]
    key = Path.home() / ".ssh" / "studio_key"
    if key.exists():
        cmd[1:1] = ["-i", str(key)]
    log("tunnel:", " ".join(cmd[1:4]), SSH_HOST)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    _tunnel["proc"] = subprocess.Popen(cmd, creationflags=flags)
    time.sleep(3)
    if _tunnel["proc"].poll() is not None:
        log("tunnel failed: run setup_ssh_key.bat once, or check ssh_host in agent.ini")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def api(method, path, data=None, raw=None, ctype=None, timeout=60):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    elif raw is not None:
        body, headers["Content-Type"] = raw, ctype
    req = urllib.request.Request(SERVER + path, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def status(pid, message, state=None):
    try:
        api("POST", f"/api/agent/{pid}/status", {"message": message, "state": state})
    except urllib.error.URLError as e:
        log("status not sent:", e)


def upload(pid, mp4):
    boundary = uuid.uuid4().hex
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"video.mp4\"\r\n"
            f"Content-Type: video/mp4\r\n\r\n").encode()
    body = head + mp4.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    api("POST", f"/api/agent/{pid}/video", raw=body, ctype=f"multipart/form-data; boundary={boundary}", timeout=600)


def report_assets():
    """Tell the panel which music and sound files exist, so new ones you drop in get used."""
    music = sorted(f.name for pat in ("musiqa_*.wav", "musiqa_*.mp3") for f in FOLDER.glob(pat)
                   if not f.stem.endswith("_asl"))
    sfx = sorted(f.stem for f in (FOLDER / "sfx").glob("*.wav"))
    try:
        r = json.loads(api("POST", "/api/agent/assets", {"music": music, "sfx": sfx}))
        log(f"assets: {r.get('music')} music, {r.get('sfx')} sfx")
    except (urllib.error.URLError, OSError, ValueError) as e:
        log("assets not sent:", e)


def next_number():
    nums = [int(m.group(1)) for f in FOLDER.glob("video_*.blend") if (m := re.match(r"video_(\d+)\.blend$", f.name))]
    return max(nums, default=0) + 1


def run_job(job):
    pid = job["id"]
    log("job", pid, job["video_name"], f"{job['seconds']} s")
    adir = FOLDER / "studio_audio" / pid
    adir.mkdir(parents=True, exist_ok=True)
    for name in job["audio"]:
        (adir / name).write_bytes(api("GET", f"/api/agent/{pid}/audio/{name}"))
    jdir = FOLDER / "studio_jobs" / pid
    jdir.mkdir(parents=True, exist_ok=True)
    (jdir / "script.py").write_text(job["script"], encoding="utf-8")
    nn = next_number()
    result = jdir / "result.json"
    result.unlink(missing_ok=True)
    status(pid, f"Blender: video_{nn:02d} qurilmoqda va render qilinmoqda (~{int(job['seconds'] / 6) + 1} daqiqa)")
    cmd = [BLENDER, "-b", str(TEMPLATE), "--python", str(HERE / "blender_job.py"), "--",
           str(jdir), f"{nn:02d}"]
    with (jdir / "blender.log").open("w", encoding="utf-8", errors="replace") as lf:
        rc = subprocess.call(cmd, stdout=lf, stderr=subprocess.STDOUT)
    if not result.exists():
        tail = (jdir / "blender.log").read_text(encoding="utf-8", errors="replace")[-800:]
        raise RuntimeError(f"Blender exited with {rc} and no result. Log end: {tail}")
    res = json.loads(result.read_text(encoding="utf-8"))
    if not res.get("ok"):
        raise RuntimeError(res.get("error", "unknown error"))
    mp4 = Path(res["mp4"])
    status(pid, f"Yuklanmoqda: {mp4.name} ({res['frames']} kadr)")
    upload(pid, mp4)
    log("done", res)
    report_assets()


def main():
    if not TOKEN:
        sys.exit("agent.ini: agent_token is empty")
    if not TEMPLATE.exists():
        sys.exit(f"Template not found: {TEMPLATE}")
    if not Path(BLENDER).exists():
        sys.exit(f"Blender not found: {BLENDER}")
    log("agent started, server", SERVER)
    keep_tunnel()
    report_assets()
    if "--open" in sys.argv:
        import webbrowser
        webbrowser.open(SERVER)
    while True:
        try:
            job = json.loads(api("GET", "/api/agent/next")).get("job")
        except (urllib.error.URLError, OSError, ValueError) as e:
            log("server not reachable:", e)
            keep_tunnel()
            job = None
        if job:
            try:
                run_job(job)
            except Exception as e:
                log("FAILED", e)
                status(job["id"], str(e)[-480:], state="failed")
        if "--once" in sys.argv:
            break
        time.sleep(POLL if not job else 1)


if __name__ == "__main__":
    main()
