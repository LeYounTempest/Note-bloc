#!/usr/bin/env python3
"""Render a recap episode (episode.json) to a vertical MP4.

Usage: python3 engine/render.py episodes/demo/episode.json out/demo.mp4 [--only N] [--frames-preview DIR]

- One encoded file per scene (same size/fps/encoder), joined with the concat demuxer (-c copy).
- Audio (optional, episode["audio"]) muxed at the end with -c:v copy.
- Scene text timing: scene["words"] = [{"t":sec,"d":sec,"w":"..."}] (relative to scene start, e.g. from WhisperX),
  or scene["narration"] = "texto" (evenly timed).
"""
import json, os, subprocess, sys, tempfile, shutil, argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
FPS_DEFAULT = 30
def _find_chrome():
    c = os.environ.get("CHROME")
    if c: return c
    for p in ("/usr/bin/google-chrome", "/opt/pw-browsers/chromium", "/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if os.path.exists(p): return p
    return None  # Playwright usará su Chromium propio

CHROME = _find_chrome()

def abs_url(base: Path, p):
    if not p: return None
    q = Path(p)
    if not q.is_absolute(): q = (base / q).resolve()
    return q.as_uri()

def scene_words(sc):
    if sc.get("words"): return sc["words"]
    txt = (sc.get("narration") or "").split()
    if not txt: return []
    d = sc["duration"]; a, b = 0.35, max(0.5, d - 0.45)
    step = (b - a) / len(txt)
    return [{"t": a + i * step, "d": step * 0.95, "w": w} for i, w in enumerate(txt)]

def encoder_cmd(fps, out):
    return ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
            "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(fps), out]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode"); ap.add_argument("out")
    ap.add_argument("--only", type=int, help="render only scene N (0-based)")
    ap.add_argument("--preview", help="dir: save JPEGs instead of rendering video")
    ap.add_argument("--at", help="con --preview: tiempos en segundos separados por coma (relativos a la escena)")
    a = ap.parse_args()

    ep_path = Path(a.episode).resolve(); base = ep_path.parent
    ep = json.loads(ep_path.read_text())
    fps = ep.get("fps", FPS_DEFAULT); W = ep.get("width", 1080); H = ep.get("height", 1920)
    tmp = Path(tempfile.mkdtemp(prefix="recap_"))
    files, gstart = [], 0.0

    with sync_playwright() as pw:
        br = pw.chromium.launch(**({"executable_path": CHROME} if CHROME else {}), args=["--no-sandbox", "--disable-gpu", "--allow-file-access-from-files"])
        page = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        cur_tpl = None
        for i, sc in enumerate(ep["scenes"]):
            d = sc["duration"]; n = int(round(d * fps))
            if a.only is not None and i != a.only:
                gstart += d; continue
            sc = dict(sc)
            for k in ("image",): sc[k] = abs_url(base, sc.get(k))
            if sc.get("sprites"): sc["sprites"] = {k: abs_url(base, v) for k, v in sc["sprites"].items()}
            if sc.get("metaFile"): sc["meta"] = json.loads((base / sc["metaFile"]).read_text())
            tpl = sc.get("template", "template.html")
            if tpl != cur_tpl:
                page.goto((ROOT / "engine" / tpl).as_uri()); cur_tpl = tpl
            page.evaluate("([s,w])=>window.setScene(s,w)", [sc, scene_words(ep["scenes"][i])])
            if a.preview:
                Path(a.preview).mkdir(parents=True, exist_ok=True)
                times = [float(x) for x in a.at.split(",")] if a.at else [d * 0.62]
                for tt in times:
                    page.evaluate("([t,g])=>window.seek(t,g)", [tt, gstart + tt])
                    page.screenshot(path=f"{a.preview}/scene{i:02d}_t{tt:05.1f}.jpg", type="jpeg", quality=92)
                gstart += d; continue
            part = tmp / f"s{i:03d}.part.mp4"; final = tmp / f"s{i:03d}.mp4"
            enc = subprocess.Popen(encoder_cmd(fps, str(part)), stdin=subprocess.PIPE)
            for f in range(n):
                t = f / fps
                page.evaluate("([t,g])=>window.seek(t,g)", [t, gstart + t])
                enc.stdin.write(page.screenshot(type="jpeg", quality=92))
            enc.stdin.close()
            if enc.wait() != 0: sys.exit(f"ffmpeg failed on scene {i}")
            part.rename(final); files.append(final); gstart += d
            print(f"scene {i} ok ({sc['type']}, {d}s)", flush=True)
        br.close()
    if a.preview: return

    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{f}'\n" for f in files))
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    silent = tmp / "all.mp4"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])
    audio = ep.get("audio")
    if audio:
        ap_ = (base / audio).resolve()
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(ap_), "-map", "0:v", "-map", "1:a",
                               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)])
    else:
        shutil.copy(silent, out)
    shutil.rmtree(tmp, ignore_errors=True)
    print("done ->", out)

if __name__ == "__main__":
    main()
