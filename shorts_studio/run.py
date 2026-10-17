"""Start the panel: checks Python and ffmpeg, picks a free port and opens the browser.
Normally launched by start.bat (Windows) or start.sh (macOS / Linux)."""

import os
import shutil
import socket
import sys
import threading
import time
import webbrowser

FFMPEG_HELP = """
  ffmpeg topilmadi. O'rnating, keyin qaytadan ishga tushiring:
    Windows:  PowerShell'da   winget install Gyan.FFmpeg   (keyin terminalni yopib qayta oching)
    macOS:    brew install ffmpeg
    Linux:    sudo apt install ffmpeg
"""


def free_port(start: int = 8000) -> int:
    for port in range(start, start + 20):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise SystemExit("8000-8019 portlarning hammasi band")


def main() -> None:
    if sys.version_info < (3, 11):
        raise SystemExit(f"Python 3.11 yoki yangisi kerak (sizda {sys.version.split()[0]})")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # so "app:app" imports from any working directory
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit(FFMPEG_HELP)

    import uvicorn

    port = free_port()
    url = f"http://127.0.0.1:{port}"

    def open_browser():
        time.sleep(2)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()
    print(f"\n  Shorts Studio ishga tushdi: {url}\n  To'xtatish uchun shu oynada Ctrl+C bosing.\n")
    # 127.0.0.1 only: the panel holds your API keys, so it must not be reachable from other devices
    uvicorn.run("app:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
