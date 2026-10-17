"""Make a Short from the terminal.

    python cli.py "the deepest point of the ocean"
    python cli.py "black holes" --seconds 40 --voice en-US-BrianMultilingualNeural
    python cli.py "volcanoes" --series "Earth Facts #2" --rate +20%
    python cli.py --offline        # render the bundled sample with no API keys (silent, gradient backgrounds)
"""

import argparse
import json
from pathlib import Path

from studio import config, pipeline
from studio.script import ShortScript, fact_check, write_script

SAMPLE = Path(__file__).parent / "assets" / "sample_script.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", nargs="?", default="")
    parser.add_argument("--seconds", type=int, default=35)
    parser.add_argument("--voice", default=config.DEFAULT_EDGE_VOICE, help='edge-tts voice name or "elevenlabs"')
    parser.add_argument("--rate", default="+12%", help="edge-tts speed, e.g. +0%% or +20%%")
    parser.add_argument("--series", default="", help='e.g. "Ocean Facts #3"')
    parser.add_argument("--no-music", action="store_true")
    parser.add_argument("--no-factcheck", action="store_true")
    parser.add_argument("--offline", action="store_true", help="no API calls: sample script, silent voice")
    args = parser.parse_args()

    if args.offline:
        script = ShortScript.model_validate(json.loads(SAMPLE.read_text()))
    else:
        if not args.topic:
            parser.error("give a topic, e.g. python cli.py \"the deepest point of the ocean\"")
        print("Ssenariy yozilmoqda...")
        script = write_script(args.topic, args.seconds)
        if not args.no_factcheck:
            print("Faktlar internetdan tekshirilmoqda...")
            checked = fact_check(script)
            script = checked.script
            for c in checked.checks:
                if c.verdict != "correct":
                    print(f"  #{c.scene} {c.verdict}: {c.note}")
        print(f"Hook: {script.scenes[0].narration}")

    job = pipeline.new_job_dir(script.topic)
    video = pipeline.make_video(
        script, job, voice=args.voice, rate=args.rate, music=not args.no_music, series=args.series,
        offline=args.offline,
        progress=lambda step, pct: print(f"[{pct:4.0%}] {step}"),
    )
    print(f"\nVideo: {video}\nSarlavha: {script.title}")


if __name__ == "__main__":
    main()
