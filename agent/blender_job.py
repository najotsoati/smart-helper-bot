"""Runs inside Blender (background) on stickman_shablon.blend.

blender -b stickman_shablon.blend --python blender_job.py -- <job_dir> <NN>

Saves the template as video_NN.blend, stores the generated script as the text
video_NN.py, runs it, saves, renders the animation with the template's settings
(Workbench, 1080x1920, 30 fps, H264/AAC), checks the MP4 and copies it to TAYYOR/.
"""

import json
import os
import shutil
import sys
import traceback

import bpy

job_dir, nn = sys.argv[sys.argv.index("--") + 1:][:2]
result_path = os.path.join(job_dir, "result.json")


def finish(**kw):
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(kw, f)


try:
    folder = os.path.dirname(bpy.data.filepath)
    tools = bpy.data.texts.get("stickman_tools.py")
    if not tools or "Stickman_Rig" not in bpy.data.objects or "Stickman_Extras" not in bpy.data.collections:
        raise RuntimeError("The template has no Stickman_Rig / Stickman_Extras / stickman_tools.py")
    if "v8" not in tools.lines[0].body:
        print("WARNING: stickman_tools.py first line is not v8:", tools.lines[0].body)
    target = os.path.join(folder, f"video_{nn}.blend")
    if os.path.exists(target):
        raise RuntimeError(f"{target} already exists")
    bpy.ops.wm.save_as_mainfile(filepath=target)

    for t in list(bpy.data.texts):
        if t.name.startswith("video_") and t.name.endswith(".py"):
            bpy.data.texts.remove(t)
    src = open(os.path.join(job_dir, "script.py"), encoding="utf-8").read()
    txt = bpy.data.texts.new(f"video_{nn}.py")
    txt.write(src)
    exec(compile(src, f"video_{nn}.py", "exec"), {"__name__": "__main__"})

    S = bpy.context.scene
    S.render.image_settings.media_type = "VIDEO"
    S.render.image_settings.file_format = "FFMPEG"
    bpy.ops.wm.save_mainfile()
    bpy.ops.render.render(animation=True)

    mp4 = bpy.path.abspath(S.render.filepath)
    clip = bpy.data.movieclips.load(mp4)
    frames = clip.frame_duration
    bpy.data.movieclips.remove(clip)
    if frames < S.frame_end - 1:
        raise RuntimeError(f"Render is short: {frames} of {S.frame_end} frames")
    os.makedirs(os.path.join(folder, "TAYYOR"), exist_ok=True)
    final = os.path.join(folder, "TAYYOR", os.path.basename(mp4))
    shutil.copy2(mp4, final)
    finish(ok=True, mp4=final, frames=frames, blend=target)
except Exception as e:
    traceback.print_exc()
    finish(ok=False, error=f"{e.__class__.__name__}: {e}"[-480:])
