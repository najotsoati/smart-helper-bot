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
    parser.add_argument("--visuals", default="mixed", choices=["mixed", "illustration", "stock"])
    parser.add_argument("--no-host", action="store_true", help="no cartoon host")
    parser.add_argument("--ab", action="store_true", help="also render the runner-up hook as video_b.mp4")
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
    render_args = dict(voice=args.voice, rate=args.rate, music=not args.no_music, series=args.series,
                       visual_mode=args.visuals, host=not args.no_host, offline=args.offline)
    video = pipeline.make_video(script, job, progress=lambda step, pct: print(f"[{pct:4.0%}] {step}"), **render_args)
    variant = pipeline.hook_variant(script) if args.ab else None
    if variant:
        print("A/B: ikkinchi hook bilan variant yasalmoqda...")
        plan = json.loads((job / "plan.json").read_text())
        pipeline.make_video(variant, job, plan=plan, variant="b", **render_args)
        print(f"B variant: {job / 'video_b.mp4'}")
    meta = json.loads((job / "meta.json").read_text())
    print(f"\nVideo: {video}\nSarlavha: {meta['title']}")
    if meta["match_average"] is not None:
        print(f"Kadr va matn mosligi: {meta['match_average']}%")


if __name__ == "__main__":
    main()
