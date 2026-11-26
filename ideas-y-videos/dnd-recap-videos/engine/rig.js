/* rig.js — rig 2D por partes para sprites pixel art.
 *
 * Rig.draw(g, name, imgs, pose, x, y, opts) dibuja un personaje con los pies en (x,y).
 *   - jerarquía: cada parte rota/traslada alrededor de su pivote respecto a su padre (DOMMatrix)
 *   - pose = { parte:{dx,dy,a}, root:{dx,dy,a}, expr:'normal', tint:0..1, fx:{...} } (función pura de t)
 *   - ángulos cuantizados (QA°) y posiciones enteras: la rotación se ve "pixel", no suave
 * Rig.sample(name, anim, t, opts) devuelve la pose; las animaciones muestrean el tiempo a STEP fps (12 por defecto)
 * para que el movimiento tenga el ritmo entrecortado típico del pixel art.
 * Todo es función pura de t (sin estado), compatible con render.py (window.seek(t)).
 */
(function (G) {
  const TAU = Math.PI * 2, QA = 6, STEP = 12;
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const easeOut = t => 1 - Math.pow(1 - t, 3);
  const hash = (a, b = 0) => { let h = (a * 374761393 + b * 668265263) >>> 0; h = (h ^ (h >>> 13)) * 1274126177 >>> 0; return ((h ^ (h >>> 16)) >>> 0) / 4294967296 };
  const qa = a => Math.round(a / QA) * QA;
  const snap = (t, fps = STEP) => Math.floor(t * fps) / fps;
  const sin = Math.sin, abs = Math.abs, round = Math.round, max = Math.max;

  let RIGS = null; const IM = {};
  const tmp = document.createElement('canvas'); const tg = tmp.getContext('2d'); tg.imageSmoothingEnabled = false;

  /* ───────────── carga ───────────── */
  // sc.sprites: { 'kobold.torso': url, ... }  sc.meta: rig.json
  function init(sc, imgsByName) { RIGS = sc.meta; Object.assign(IM, imgsByName); }

  /* ───────────── dibujo ───────────── */
  function draw(g, name, pose, x, y, o = {}) {
    const R = RIGS[name], [w, h] = R.size, flip = o.flip ? -1 : 1, scale = o.scale || 1;
    const root = pose.root || {};
    const faceImg = IM[`${name}.face_${pose.expr || 'normal'}`];
    const byName = {}; R.parts.forEach(p => byName[p.n] = p);
    // props (kobolds): se insertan justo antes de la cabeza, heredan el brazo
    const parts = R.parts.slice();
    if (o.variant != null && R.props[o.variant]) {
      const ins = parts.findIndex(p => p.n === 'head');
      for (const [hand, pn] of Object.entries(R.props[o.variant])) {
        const par = R.prop_parent[hand], base = byName[par];
        const part = { n: pn, parent: par, pivot: base.pivot, same: par };
        byName[pn] = part; parts.splice(ins, 0, part);
      }
    }
    if (faceImg) { const hp = byName[R.face_parent]; const fp = { n: 'face_' + pose.expr, parent: R.face_parent, pivot: hp.pivot, same: R.face_parent, img: faceImg }; byName[fp.n] = fp; parts.push(fp); }
    const M = {};
    const Z = o.zoom || 1, X0 = o.ox || 0, Y0 = o.oy || 0;
    // base: pies en (x,y) [px nativos], todo en pantalla = X0/Y0 + Z·nativo. Flip horizontal alrededor de los pies.
    const base = new DOMMatrix().translate(X0 + Z * x, Y0 + Z * (y - R.feet[1])).scale(Z * flip * scale, Z * scale).translate(-R.feet[0], 0);
    const rp = R.feet;   // la raíz rota alrededor de los pies (muerte, saltos, inclinación)
    const rootM = base.translate(rp[0] + round(root.dx || 0), rp[1] + round(root.dy || 0)).rotate(qa(root.a || 0)).translate(-rp[0], -rp[1]);
    function world(p) {
      if (M[p.n]) return M[p.n];
      const par = p.parent === 'root' ? rootM : world(byName[p.parent]);
      const T = p.same ? {} : (pose[p.n] || {});   // props/cara viven en el espacio del padre: sin pose propia
      return M[p.n] = par.translate(p.pivot[0] + round(T.dx || 0), p.pivot[1] + round(T.dy || 0)).rotate(qa(T.a || 0)).translate(-p.pivot[0], -p.pivot[1]);
    }
    parts.forEach(world);
    g.save();
    if (o.shadow !== false) {   // sombra: elipse pixelada en el suelo, no rota con la raíz
      const sw = w * 0.4 * scale, lift = clamp(1 - abs(root.dy || 0) / 10, .4, 1);
      g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = 'rgba(0,0,0,.35)';
      g.fillRect(round(X0 + Z * (x - sw * lift)), round(Y0 + Z * y - Z), round(Z * sw * 2 * lift), round(Z * 2));
    }
    const tint = pose.tint || 0;
    for (const p of parts) {
      const img = p.img || IM[`${name}.${p.n}`]; if (!img) continue;
      const m = M[p.n]; g.setTransform(m.a, m.b, m.c, m.d, m.e, m.f);
      if (tint > 0) {
        tmp.width = w; tmp.height = h; tg.imageSmoothingEnabled = false; tg.clearRect(0, 0, w, h);
        tg.globalCompositeOperation = 'source-over'; tg.drawImage(img, 0, 0);
        tg.globalCompositeOperation = 'source-atop'; tg.fillStyle = `rgba(255,255,255,${tint})`; tg.fillRect(0, 0, w, h);
        g.drawImage(tmp, 0, 0);
      } else g.drawImage(img, 0, 0);
    }
    g.restore();
    // anclas en coordenadas de pantalla (para efectos: cristal, manos…)
    const A = {};
    for (const [k, [pn, ax, ay]] of Object.entries(R.anchors)) {
      const m = M[pn]; if (m) A[k] = [m.a * ax + m.c * ay + m.e, m.b * ax + m.d * ay + m.f];
    }
    return A;
  }

  /* ───────────── animaciones ───────────── */
  const set = (p, n, dx, dy, a) => { const q = p[n] || (p[n] = {}); if (dx != null) q.dx = (q.dx || 0) + dx; if (dy != null) q.dy = (q.dy || 0) + dy; if (a != null) q.a = (q.a || 0) + a; };
  const blinkAt = t => (t % 3.4) < 0.13;

  const K = {   // ───── kobold (frontal; las piernas tijeretean tipo "paper doll")
    idle(t) {
      const ts = snap(t), ph = ts * 0.9 * TAU, b = sin(ph) > 0.2 ? 1 : 0, p = { expr: blinkAt(t) ? 'blink' : 'normal' };
      set(p, 'torso', 0, b); set(p, 'head', 0, (sin(ph - 0.9) > 0.2 ? 1 : 0) - b);
      set(p, 'arm_L', 0, 0, 4 + sin(ph) * 3); set(p, 'arm_R', 0, 0, -4 - sin(ph) * 3);
      set(p, 'tail', 0, 0, sin(ts * 1.3 * TAU) * 9); return p;
    },
    walk(t, o = {}) {
      const sp = o.speed || 1, ts = snap(t), ph = ts * 2.2 * sp * TAU, s = sin(ph), c = sin(ph + TAU / 4), p = { expr: blinkAt(t) ? 'blink' : 'normal' };
      set(p, 'leg_L', 0, -max(0, s) * 2.2, s * 30); set(p, 'leg_R', 0, -max(0, -s) * 2.2, -s * 30);
      set(p, 'arm_L', 0, 0, -s * 32 + 4); set(p, 'arm_R', 0, 0, s * 32 - 4);
      set(p, 'root', 0, -abs(c) * 1.8); set(p, 'torso', 0, 0, s * 4); set(p, 'head', 0, 0, -s * 3);
      set(p, 'tail', 0, 0, sin(ph + 1.6) * 16); return p;
    },
    run(t) {
      const ts = snap(t), ph = ts * 3.6 * TAU, s = sin(ph), c = sin(ph + TAU / 4), p = { expr: 'normal' };
      set(p, 'leg_L', 0, -max(0, s) * 3.5, s * 48); set(p, 'leg_R', 0, -max(0, -s) * 3.5, -s * 48);
      set(p, 'arm_L', 0, 0, -s * 55 + 20); set(p, 'arm_R', 0, 0, s * 55 - 20);
      set(p, 'root', 0, -abs(c) * 3, 6); set(p, 'torso', 0, 0, s * 5); set(p, 'head', 0, 0, -s * 4 - 4);
      set(p, 'tail', 0, 0, sin(ph + 2) * 24 - 10); return p;
    },
    scared(t) {
      const j = (Math.floor(t * 24) % 2) ? 1 : -1, s = sin(t * 31), p = { expr: 'scared' };
      set(p, 'root', j, 0); set(p, 'arm_L', 0, 0, 138 + s * 12); set(p, 'arm_R', 0, 0, -138 - s * 12);
      set(p, 'leg_L', 0, 0, 7); set(p, 'leg_R', 0, 0, -7); set(p, 'head', 0, 0, s * 3); set(p, 'tail', 0, 0, sin(t * 22) * 14); return p;
    },
    sing(t, o = {}) {
      const ts = snap(t, 12), ph = ts * 0.8 * TAU, beat = sin(ts * 1.6 * TAU), m = Math.floor(hash(Math.floor(t * 8), o.seed || 0) * 3);
      const p = { expr: ['sing', 'sing_mid', 'happy'][m] };
      set(p, 'head', 0, 0, sin(ph) * 8 - 3); set(p, 'torso', 0, beat > 0.7 ? -1 : 0, sin(ph) * 3);
      set(p, 'arm_R', 0, 0, -(75 + beat * 16)); set(p, 'arm_L', 0, 0, 10 + sin(ph + 1) * 6); set(p, 'tail', 0, 0, sin(ts * 2 * TAU) * 14); return p;
    },
    cheer(t) {
      const ts = snap(t, 15), s = sin(ts * 1.4 * TAU), p = { expr: s > 0 ? 'sing' : 'happy' };
      set(p, 'root', 0, -abs(s) * 6); set(p, 'arm_L', 0, 0, 150 + s * 18); set(p, 'arm_R', 0, 0, -150 - s * 18);
      set(p, 'leg_L', 0, 0, 10 * abs(s)); set(p, 'leg_R', 0, 0, -10 * abs(s)); set(p, 'tail', 0, 0, s * 20); return p;
    },
    hurt(t) {   // t local; 0..0.6
      const k = clamp(t / 0.6), d = (1 - k), p = { expr: 'hurt', tint: t < 0.1 ? 0.9 : 0 };
      set(p, 'root', (Math.floor(t * 30) % 2 ? 2 : -2) * d - 3 * easeOut(clamp(t / .2)) * d, 0, -6 * d);
      set(p, 'torso', 0, 0, -14 * d); set(p, 'head', 0, 0, -10 * d); set(p, 'arm_L', 0, 0, 45 * d); set(p, 'arm_R', 0, 0, -45 * d);
      set(p, 'tail', 0, 0, 25 * d); return p;
    },
    die(t) {    // t local; cae sobre un costado y se queda
      const k = easeOut(clamp(t / 0.55)), p = { expr: t > 0.12 ? 'dead' : 'hurt', tint: t < 0.08 ? 0.9 : 0 };
      set(p, 'root', -3 * k, -9 * k - sin(clamp(t / 0.55) * Math.PI) * 5, 90 * k);
      set(p, 'arm_L', 0, 0, 55 * k); set(p, 'arm_R', 0, 0, -75 * k); set(p, 'leg_L', 0, 0, 12 * k); set(p, 'leg_R', 0, 0, -8 * k); set(p, 'tail', 0, 0, 20 * k); return p;
    },
  };

  const I = {   // ───── Mr. Iguana
    idle(t) {
      const ts = snap(t), ph = ts * 0.8 * TAU, b = sin(ph) > 0.1 ? 1 : 0, p = { expr: blinkAt(t) ? 'blink' : 'normal' };
      set(p, 'torso', 0, b); set(p, 'head', 0, 0); set(p, 'hat', 0, 0, sin(ph - 1) * 4); set(p, 'cape', 0, 0, sin(ts * 1.7 * TAU) * 5);
      set(p, 'arm_s', 0, 0, sin(ph) * 3); set(p, 'staff', 0, 0, sin(ph + 1) * 2); set(p, 'tail', 0, 0, sin(ts * 1.2 * TAU) * 10); return p;
    },
    walk(t, o = {}) {
      const sp = o.speed || 1, ts = snap(t), ph = ts * 2 * sp * TAU, s = sin(ph), c = sin(ph + TAU / 4), p = { expr: blinkAt(t) ? 'blink' : 'normal' };
      set(p, 'leg_L', 0, -max(0, s) * 2, s * 26); set(p, 'leg_R', 0, -max(0, -s) * 2, -s * 26);
      set(p, 'root', 0, -abs(c) * 1.6); set(p, 'torso', 0, 0, s * 3); set(p, 'head', 0, 0, -s * 2);
      set(p, 'hat', 0, 0, sin(ph - 1.2) * 9); set(p, 'cape', 0, 0, -8 + sin(ph - 0.8) * 8);
      set(p, 'arm_s', 0, 0, s * 8); set(p, 'staff', 0, 0, -s * 5); set(p, 'book', 0, 0, s * 2); set(p, 'tail', 0, 0, sin(ph + 1.5) * 16); return p;
    },
    cast(t, o = {}) {   // t local. 0-.55 carga, .55-.7 disparo, luego mantiene
      const wind = clamp(t / 0.55), rel = clamp((t - 0.55) / 0.15), hold = t > 0.7, ts = snap(t, 24);
      const p = { expr: hold ? 'cast' : (t > 0.2 ? 'angry' : 'normal') };
      const flut = sin(ts * 14) * (hold ? 1 : 0);
      set(p, 'root', hold ? -1 - (t < 1.1 ? 1 : 0) : 0, wind > 0.3 && !hold ? 1 : 0);
      set(p, 'arm_s', 0, hold ? -3 : 0, -28 * wind * (1 - rel) + 42 * rel + (hold ? 6 : 0));
      set(p, 'staff', 0, 0, -10 * wind * (1 - rel) + 18 * rel);
      set(p, 'book', 0, -wind * 2, 0); set(p, 'head', 0, 0, hold ? -5 : 4 * wind);
      set(p, 'hat', 0, 0, (hold ? -14 : -4 * wind) + flut * 9); set(p, 'cape', 0, 0, -16 * (hold ? 1 : wind) + flut * 6);
      set(p, 'tail', 0, 0, 14 + flut * 8);
      p.fx = { glow: hold ? 1 : wind * 0.6, burst: hold ? clamp(1 - (t - 0.7) / 0.6) : 0 }; return p;
    },
    hollow(t) {   // "algo dentro de él se rompió"
      const ts = snap(t, 8), p = { expr: t < 0.3 ? 'scared' : (t < 0.9 ? 'hollow' : 'sad') };
      const k = easeOut(clamp(t / 0.8));
      set(p, 'root', (t < 0.3 ? (Math.floor(t * 28) % 2 ? 1 : -1) : 0), 0);
      set(p, 'torso', 0, 1 * k, 0); set(p, 'head', 0, 1 * k, 12 * k); set(p, 'hat', 0, 1, 18 * k + sin(ts * 3) * 2);
      set(p, 'arm_s', 0, 0, 20 * k); set(p, 'staff', 0, 0, 14 * k); set(p, 'cape', 0, 0, 6 * k); set(p, 'tail', 0, 0, -12 * k);
      set(p, 'book', 0, 1 * k, 0); return p;
    },
  };

  const LIB = { kobold: K, iguana: I };
  function sample(name, anim, t, o) { const fn = LIB[name][anim]; return fn(t, o || {}); }

  /* ───────────── efectos ───────────── */
  // brillo + partículas deterministas alrededor de un punto (coordenadas de pantalla en px nativos)
  function glow(g, cx, cy, fx, t, o = {}) {
    if (!fx || fx.glow <= 0) return;
    const gl = fx.glow, pulse = .75 + .25 * sin(t * 14), col = o.col || [240, 90, 210];
    for (const [r, a] of [[10, .10], [7, .18], [4.5, .3], [2.5, .5]]) { g.fillStyle = `rgba(${col},${a * gl * pulse})`; g.fillRect(round(cx - r), round(cy - r), round(2 * r), round(2 * r)); }
    g.fillStyle = `rgba(255,255,255,${.85 * gl})`; g.fillRect(round(cx - 1), round(cy - 1), 3, 3);
    if (fx.burst > 0) for (let i = 0; i < 28; i++) {
      const age = (t * 2 + i * 0.37) % 1.1, a = hash(i, 5) * TAU, v = 5 + hash(i, 6) * 20;
      g.fillStyle = hash(i, 7) > .5 ? '#ff9af0' : '#ffffff'; g.globalAlpha = clamp(1 - age) * fx.burst;
      g.fillRect(round(cx + Math.cos(a) * v * age), round(cy + Math.sin(a) * v * age - age * 5), 1, 1);
    }
    g.globalAlpha = 1;
  }

  G.Rig = { init, draw, sample, glow, hash, clamp, easeOut, snap };
})(window);
