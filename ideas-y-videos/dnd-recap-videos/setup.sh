#!/usr/bin/env bash
# Dependencias del render. Requiere Python 3, ffmpeg y Google Chrome/Chromium.
set -e
pip install --break-system-packages playwright 2>/dev/null || pip install playwright
command -v ffmpeg >/dev/null || { echo "Falta ffmpeg"; exit 1; }
echo "Chrome: ${CHROME:-/usr/bin/google-chrome} (cambia con la variable CHROME)"
echo "Prueba: python3 engine/render.py episodes/demo/episode.json out/demo.mp4"
