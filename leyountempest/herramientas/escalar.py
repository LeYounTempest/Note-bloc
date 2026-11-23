"""Reescalado x4 con Real-ESRGAN (modelo para anime/ilustración) en CPU, con mosaicos solapados.

Requiere:  pip install torch spandrel pillow numpy
Pesos:     RealESRGAN_x4plus_anime_6B.pth  (https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.2.4)
           en la carpeta indicada por la variable de entorno REALESRGAN_PESOS.
Si falta algo, `ampliar()` devuelve la imagen intacta (factor 1) y el resto de los scripts siguen funcionando.
"""
import os
import numpy as np
from PIL import Image

_modelo = None


def _cargar():
    global _modelo
    if _modelo is None:
        import torch
        from spandrel import ModelLoader
        torch.set_num_threads(os.cpu_count() or 4)
        ruta = os.path.join(os.environ["REALESRGAN_PESOS"], "RealESRGAN_x4plus_anime_6B.pth")
        _modelo = ModelLoader().load_from_file(ruta).eval()
    return _modelo


def ampliar(im, tile=192, pad=12):
    """Devuelve (imagen_x4, 4) o (imagen, 1) si el modelo no está disponible. Conserva el canal alfa si lo hay."""
    try:
        import torch
        m = _cargar()
    except Exception:
        return im, 1
    s = m.scale
    alfa = im.getchannel("A") if im.mode == "RGBA" else None
    a = torch.from_numpy(np.asarray(im.convert("RGB")).astype(np.float32) / 255).permute(2, 0, 1)[None]
    _, _, H, W = a.shape
    out = torch.zeros(1, 3, H * s, W * s)
    for y in range(0, H, tile):
        for x in range(0, W, tile):
            y0, x0 = max(y - pad, 0), max(x - pad, 0)
            y1, x1 = min(y + tile + pad, H), min(x + tile + pad, W)
            with torch.no_grad():
                t = m(a[:, :, y0:y1, x0:x1])
            cy, cx = (y - y0) * s, (x - x0) * s
            hh, ww = min(tile, H - y) * s, min(tile, W - x) * s
            out[:, :, y * s:y * s + hh, x * s:x * s + ww] = t[:, :, cy:cy + hh, cx:cx + ww]
    res = Image.fromarray((out[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8))
    if alfa is not None:
        res = res.convert("RGBA")
        res.putalpha(alfa.resize(res.size, Image.LANCZOS))
    return res, s
