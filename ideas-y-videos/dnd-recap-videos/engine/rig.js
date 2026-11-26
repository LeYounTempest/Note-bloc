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
  const off = document.createElement('canvas'), og = off.getContext('2d');
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
    const tint = pose.tint || 0, hide = pose.hide || [], alpha = pose.alpha == null ? 1 : pose.alpha;
    let gg = g;
    if (alpha < 1) { if (off.width !== g.canvas.width) { off.width = g.canvas.width; off.height = g.canvas.height; } og.setTransform(1, 0, 0, 1, 0, 0); og.clearRect(0, 0, off.width, off.height); og.imageSmoothingEnabled = false; gg = og; }
    for (const p of parts) {
      if (hide.includes(p.n)) continue;
      const img = p.img || IM[`${name}.${p.n}`]; if (!img) continue;
      const m = M[p.n]; gg.setTransform(m.a, m.b, m.c, m.d, m.e, m.f);
      if (tint > 0) {
        tmp.width = w; tmp.height = h; tg.imageSmoothingEnabled = false; tg.clearRect(0, 0, w, h);
        tg.globalCompositeOperation = 'source-over'; tg.drawImage(img, 0, 0);
        tg.globalCompositeOperation = 'source-atop'; tg.fillStyle = `rgba(${pose.tintc || '255,255,255'},${tint})`; tg.fillRect(0, 0, w, h);
        gg.drawImage(tmp, 0, 0);
      } else gg.drawImage(img, 0, 0);
    }
    if (alpha < 1) { g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = alpha; g.drawImage(off, 0, 0); g.globalAlpha = 1; }
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


  /* ───────────── humanoides altos: kenku, Dei, Hans ───────────── */
  // helpers comunes
  const hurtPose = (t, cfg) => { const k = clamp(t / 0.6), d = 1 - k, p = { expr: cfg.hurt, tint: t < 0.1 ? 0.8 : 0 };
    set(p, 'root', (Math.floor(t * 30) % 2 ? 2 : -2) * d - 3 * easeOut(clamp(t / .2)) * d, 0, -5 * d);
    set(p, 'torso', 0, 0, -12 * d); set(p, 'head', 0, 0, -9 * d); set(p, 'arm_L', 0, 0, 35 * d); set(p, 'arm_R', 0, 0, -35 * d); return p; };
  const diePose = (t, cfg) => { const k = easeOut(clamp(t / 0.7)), p = { expr: t > 0.15 ? cfg.dead : cfg.hurt, tint: t < 0.08 ? 0.8 : 0 };
    set(p, 'root', -4 * k, -cfg.h * 0.28 * k - sin(clamp(t / 0.7) * Math.PI) * 5, -90 * k);
    set(p, 'arm_L', 0, 0, 45 * k); set(p, 'arm_R', 0, 0, -50 * k); set(p, 'leg_L', 0, 0, 10 * k); set(p, 'leg_R', 0, 0, -8 * k); return p; };
  const stride = (t, sp, amp, cfg) => { const ts = snap(t), ph = ts * 2 * sp * TAU, s = sin(ph), c = sin(ph + TAU / 4), p = { expr: cfg.expr || 'normal', ph, s };
    set(p, 'leg_L', 0, -max(0, s) * 2, s * amp); set(p, 'leg_R', 0, -max(0, -s) * 2, -s * amp);
    set(p, 'root', 0, -abs(c) * 1.4); set(p, 'torso', 0, 0, s * 2.5); set(p, 'head', 0, 0, -s * 2); return p; };

  const KN = {   // kenku paladín: pesado, solemne
    idle(t) { const ts = snap(t), ph = ts * 0.7 * TAU, b = sin(ph) > 0.1 ? 1 : 0, p = { expr: blinkAt(t) ? 'blink' : 'serene', fx: { aura: 1 } };
      set(p, 'torso', 0, b); set(p, 'halo', 0, 0, Math.floor(t * 8) * 6); set(p, 'arm_L', 0, 0, sin(ph) * 2); set(p, 'arm_R', 0, 0, -3 - sin(ph) * 2);
      set(p, 'ribbon_L', 0, 0, 8 + sin(ts * 1.6 * TAU) * 7); set(p, 'ribbon_R', 0, 0, -8 - sin(ts * 1.6 * TAU + 1) * 7); set(p, 'cape', 0, 0, sin(ts * 1.1 * TAU) * 3); set(p, 'hood', 0, 0, 0); return p; },
    walk(t, o = {}) { const p = stride(t, (o.speed || 1) * 0.9, 20, { expr: 'serene' }); p.fx = { aura: 1 };
      set(p, 'halo', 0, 0, Math.floor(t * 8) * 6); set(p, 'arm_L', 0, 0, p.s * 6); set(p, 'arm_R', 0, 0, -p.s * 4 - 4);
      set(p, 'ribbon_L', 0, 0, 14 + sin(p.ph - 1) * 10); set(p, 'ribbon_R', 0, 0, -14 - sin(p.ph - 1.4) * 10); set(p, 'cape', 0, 0, sin(p.ph - 1) * 4); return p; },
    guard(t) {   // "el kenku resistía": escudo arriba, impactos
      const ts = snap(t, 24), imp = hash(Math.floor(t * 6), 4) > 0.45 && (t * 6 % 1) < 0.35, p = { expr: 'angry', fx: { aura: 1.6 + (imp ? 1 : 0) }, tint: imp ? 0.3 : 0 };
      set(p, 'arm_R', 0, -1, -34 + (imp ? 6 : 0)); set(p, 'arm_L', 0, 0, 6); set(p, 'head', 0, 1, 4); set(p, 'torso', imp ? -1 : 0, 1, imp ? -4 : 0);
      set(p, 'root', imp ? -1 : 0, 0); set(p, 'halo', 0, 0, Math.floor(t * 12) * 6); set(p, 'ribbon_L', 0, 0, 16 + sin(ts) * 6); set(p, 'ribbon_R', 0, 0, -16 + sin(ts + 1) * 6); return p; },
    smite(t) {   // lanzada; t local
      const wind = clamp(t / 0.35), thr = clamp((t - 0.35) / 0.12), rec = clamp((t - 0.5) / 0.4), p = { expr: 'angry', fx: { aura: 1.5 + (1 - rec) } };
      set(p, 'arm_L', 0, 0, -30 * wind * (1 - thr) + 55 * thr * (1 - rec)); set(p, 'torso', -1 * wind + 2 * thr * (1 - rec), 0, -6 * wind + 10 * thr * (1 - rec));
      set(p, 'root', 2 * thr * (1 - rec), 0); set(p, 'halo', 0, 0, Math.floor(t * 12) * 6); set(p, 'arm_R', 0, 0, -10); return p; },
    hurt(t) { const p = hurtPose(t, { hurt: 'hurt' }); p.fx = { aura: 0.6 }; return p; },
    die(t) { const p = diePose(t, { hurt: 'hurt', dead: 'dead', h: 42 }); p.fx = { aura: Math.max(0, 1 - t) }; return p; },
  };

  const DEI = {   // Dei: bardo eléctrico, canchero
    idle(t) { const ts = snap(t), ph = ts * 0.8 * TAU, b = sin(ph) > 0.1 ? 1 : 0, p = { expr: blinkAt(t) ? 'blink' : 'smirk' };
      set(p, 'torso', 0, b); set(p, 'head', 0, 0, sin(ph) * 3); set(p, 'arm_L', 0, 0, -30); set(p, 'arm_R', 0, 0, 30); set(p, 'tail', 0, 0, sin(ts * 1.2 * TAU) * 10); return p; },
    walk(t, o = {}) { const p = stride(t, (o.speed || 1) * 0.95, 24, { expr: 'smirk' });
      set(p, 'arm_L', 0, 0, -30 + p.s * 4); set(p, 'arm_R', 0, 0, 30 - p.s * 4); set(p, 'tail', 0, 0, sin(p.ph + 1.4) * 14); return p; },
    play(t) {   // rasguea el laúd cantando
      const ts = snap(t, 16), st = sin(ts * 7 * TAU), m = hash(Math.floor(t * 8), 2) > 0.4, p = { expr: m ? 'sing' : 'smirk' };
      set(p, 'arm_L', 0, 0, -32); set(p, 'arm_R', 0, 0, 36 + st * 12); set(p, 'torso', 0, st > 0.6 ? -1 : 0, sin(ts * 1.6 * TAU) * 3);
      set(p, 'head', 0, 0, sin(ts * 0.8 * TAU) * 6 - 2); set(p, 'tail', 0, 0, sin(ts * 2 * TAU) * 14); return p; },
    cast(t) {   // relámpago: manos arriba, laúd guardado; t local
      const k = clamp(t / 0.35), hold = t > 0.35, ts = snap(t, 24), p = { expr: hold ? 'cast' : 'angry', hide: ['lute'], fx: { arcs: hold ? 1 : k * 0.5, bolt: hold ? 1 : 0 } };
      set(p, 'arm_L', 0, 0, 100 * easeOut(k) + sin(ts * 9) * (hold ? 5 : 0)); set(p, 'arm_R', 0, 0, -100 * easeOut(k) - sin(ts * 9 + 1) * (hold ? 5 : 0));
      set(p, 'head', 0, 0, hold ? -8 : 0); set(p, 'root', hold ? (Math.floor(t * 30) % 2 ? 1 : -1) : 0, 0); set(p, 'tail', 0, 0, 12 + sin(ts * 12) * 6); return p; },
    tumble(t) {   // arrastrado por el viento: brazos y cola al aire
      const ts = snap(t, 15), p = { expr: 'hurt', hide: ['lute'] };
      set(p, 'arm_L', 0, 0, 110 + sin(ts * 9) * 25); set(p, 'arm_R', 0, 0, -110 - sin(ts * 9 + 1) * 25); set(p, 'leg_L', 0, 0, 25 + sin(ts * 7) * 15); set(p, 'leg_R', 0, 0, -25 - sin(ts * 7) * 15);
      set(p, 'head', 0, 0, sin(ts * 6) * 10); set(p, 'tail', 0, 0, sin(ts * 10) * 30); return p; },
    hurt(t) { const p = hurtPose(t, { hurt: 'hurt' }); return p; },
    die(t) { return diePose(t, { hurt: 'hurt', dead: 'dead', h: 64 }); },
  };

  const HA = {   // Hans: elfo elegante con vino
    idle(t) { const ts = snap(t), ph = ts * 0.8 * TAU, b = sin(ph) > 0.1 ? 1 : 0, p = { expr: blinkAt(t) ? 'blink' : 'smile' };
      set(p, 'torso', 0, b); set(p, 'head', 0, 0, sin(ph) * 3); set(p, 'arm_L', 0, 0, -14 + sin(ph) * 2); set(p, 'arm_R', 0, 0, 5); return p; },
    walk(t, o = {}) { const p = stride(t, (o.speed || 1) * 1.0, 22, { expr: 'smile' });
      set(p, 'arm_L', 0, 0, -14 - p.s * 6); set(p, 'arm_R', 0, 0, p.s * 14); return p; },
    toast(t) {   // brinda con la botella
      const ts = snap(t, 12), s = sin(ts * 2.2 * TAU), p = { expr: 'smile' };
      set(p, 'arm_R', 0, 0, -(120 + s * 8)); set(p, 'torso', 0, 0, s * 2); set(p, 'head', 0, 0, 4 + s * 2); set(p, 'arm_L', 0, 0, -14); return p; },
    vanish(t, o = {}) {   // se vuelve invisible; t local. alpha se queda bajo y titila
      const k = clamp(t / 0.6), flick = 0.12 + 0.06 * sin(Math.floor(t * 12) * 2.3), p = { expr: 'smile' };
      p.alpha = t < 0.6 ? 1 - 0.85 * k : flick; set(p, 'arm_L', 0, 0, -14); set(p, 'arm_R', 0, 0, 5); set(p, 'torso', 0, (sin(t * 8) > 0.2 ? 1 : 0)); return p; },
    scared(t) { const j = (Math.floor(t * 24) % 2) ? 1 : -1, p = { expr: 'scared' }; set(p, 'root', j, 0); set(p, 'arm_L', 0, 0, 40); set(p, 'arm_R', 0, 0, -40); return p; },
    sneak(t, o = {}) {   // pícaro: agachado, paso corto y silencioso; alpha opcional (o.alpha)
      const p = stride(t, 0.55, 14, { expr: 'smile' }); set(p, 'root', 0, 3); set(p, 'torso', 0, 0, 9); set(p, 'head', 0, 1, 6);
      set(p, 'arm_L', 0, 0, 20); set(p, 'arm_R', 0, 0, -28 + p.s * 6); if (o.alpha != null) p.alpha = o.alpha; return p; },
    stab(t) {   // puñalada; t local (usa variante 1 = daga)
      const wind = clamp(t / 0.3), thr = clamp((t - 0.3) / 0.1), rec = clamp((t - 0.45) / 0.35), p = { expr: t > 0.28 ? 'angry' : 'smile' };
      set(p, 'arm_R', 0, 0, -75 * wind * (1 - thr) + 95 * thr * (1 - rec)); set(p, 'torso', 0, 0, -8 * wind + 14 * thr * (1 - rec));
      set(p, 'root', 4 * thr * (1 - rec), 2 * wind * (1 - thr)); set(p, 'arm_L', 0, 0, 25 * wind); set(p, 'head', 0, 0, 5 * thr * (1 - rec)); return p; },
    hurt(t) { return hurtPose(t, { hurt: 'hurt' }); },
    die(t) { return diePose(t, { hurt: 'hurt', dead: 'dead', h: 58 }); },
  };

  const o_ice = '150,210,255';

  const DR = {   // dragón de cobre (perfil mirando a la izquierda)
    _wings(p, ph, amp, up = 0) { set(p, 'wing_near', 0, 0, up + sin(ph) * amp); set(p, 'wing_far', 0, 0, up + sin(ph - 0.7) * amp * 0.9); },
    _tail(p, ph, k = 1) { set(p, 'tail1', 0, 0, sin(ph) * 6 * k); set(p, 'tail2', 0, 0, sin(ph - 0.9) * 9 * k); set(p, 'tail3', 0, 0, sin(ph - 1.8) * 14 * k); },
    idle(t) { const ts = snap(t, 10), ph = ts * 0.9 * TAU, p = { expr: blinkAt(t) ? 'blink' : 'normal' };
      set(p, 'body', 0, sin(ph) > 0.2 ? 1 : 0); set(p, 'neck', 0, 0, sin(ph - 0.6) * 3); set(p, 'head', 0, 0, sin(ph - 1.2) * 3);
      DR._wings(p, ts * 0.6 * TAU, 7, -6); DR._tail(p, ts * 1.1 * TAU); return p; },
    emerge(t) {   // rugido al salir del mar; t local
      const k = easeOut(clamp(t / 1.2)), ts = snap(t, 12), p = { expr: 'roar' };
      set(p, 'wing_near', 0, 0, -30 * k + sin(ts * 5) * 6); set(p, 'wing_far', 0, 0, -30 * k + sin(ts * 5 - 1) * 6);
      set(p, 'head', 0, 0, -14 * k); set(p, 'neck', 0, 0, -6 * k); set(p, 'jaw', 0, 0, -30 * k); set(p, 'root', (Math.floor(t * 28) % 2 ? 1 : -1) * k, 0);
      DR._tail(p, ts * 2 * TAU, 1.4); return p; },
    roar(t) { const k = clamp(t / 0.25) * clamp((1.6 - t) / 0.3), ts = snap(t, 12), p = { expr: 'roar' };
      set(p, 'head', 0, 0, -13 * k); set(p, 'neck', 0, 0, -7 * k); set(p, 'jaw', 0, 0, -30 * k); set(p, 'wing_near', 0, 0, -26 * k + sin(ts * 6) * 5 * k); set(p, 'wing_far', 0, 0, -26 * k + sin(ts * 6 - 1) * 5 * k);
      set(p, 'root', (Math.floor(t * 28) % 2 ? 1 : -1) * k, 0); DR._tail(p, ts * 2 * TAU, 1.2); return p; },
    breathe(t, o = {}) {   // aliento de fuego; t local: carga .45 s, fuego hasta o.dur (1.6)
      const dur = o.dur || 1.6, w = clamp(t / 0.45), on = t >= 0.45 && t < dur, end = clamp((t - dur) / 0.3), ts = snap(t, 12), p = { expr: 'angry' };
      set(p, 'head', 0, 0, 6 * w + (on ? 12 : 0) * (1 - end)); set(p, 'neck', 0, 0, 4 * w + (on ? 6 : 0) * (1 - end)); set(p, 'jaw', 0, 0, -10 * w - (on ? 22 : 0) * (1 - end));
      set(p, 'body', 0, 0, on ? -2 : 0); set(p, 'wing_near', 0, 0, -18 * w * (1 - end) + sin(ts * 4) * 5); set(p, 'wing_far', 0, 0, -18 * w * (1 - end) + sin(ts * 4 - 1) * 5);
      DR._tail(p, ts * 1.6 * TAU, 1.2); if (on) p.fx = { fire: clamp((t - 0.45) / 0.15) * (1 - end) }; return p; },
    hurt(t) { const k = clamp(t / 0.7), d = 1 - k, p = { expr: 'hurt', tint: t < 0.12 ? 0.5 : 0, tintc: o_ice };
      set(p, 'head', 0, 0, -16 * d); set(p, 'neck', 0, 0, -8 * d); set(p, 'jaw', 0, 0, -22 * d); set(p, 'root', (Math.floor(t * 30) % 2 ? 2 : -2) * d, 0);
      set(p, 'wing_near', 0, 0, -22 * d); set(p, 'wing_far', 0, 0, -22 * d); DR._tail(p, snap(t, 12) * 3 * TAU, 1.5 * d + 0.3); return p; },
    frozen(t) { const p = { expr: 'hurt', tint: 0.55, tintc: o_ice }; set(p, 'wing_near', 0, 0, -14); set(p, 'wing_far', 0, 0, -14); set(p, 'head', 0, 0, -8); set(p, 'jaw', 0, 0, -16);
      p.fx = { sparkle: 1 }; return p; },
  };

  const LIB = { kobold: K, iguana: I, kenku: KN, dei: DEI, hans: HA, dragon: DR };
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


  // aura plateada del kenku: anillos expansivos + motas que suben (coordenadas de pantalla)
  function aura(g, cx, cy, t, k = 1, o = {}) {
    const R = (o.r || 14) * 1; g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
    for (let i = 0; i < 3; i++) {
      const ph = ((t * 0.7 + i / 3) % 1), r = (4 + ph * R) * (o.z || 1);
      g.globalAlpha = (1 - ph) * 0.5 * Math.min(1, k);
      g.fillStyle = '#dfe8ff';
      const n = Math.max(12, Math.round(r * 2.2));
      for (let j = 0; j < n; j++) { const a = j / n * TAU; g.fillRect(round(cx + Math.cos(a) * r * 1.1), round(cy + Math.sin(a) * r * 1.35), o.z || 1, o.z || 1); }
    }
    for (let i = 0; i < 16 * Math.min(1.5, k); i++) {
      const age = (t * 0.6 + hash(i, 3)) % 1, x = cx + (hash(i, 4) - .5) * R * 1.6 * (o.z || 1), y = cy + R * 0.9 * (o.z || 1) - age * R * 2 * (o.z || 1);
      g.globalAlpha = Math.sin(age * Math.PI) * 0.9; g.fillStyle = hash(i, 5) > .5 ? '#ffffff' : '#b9c6ff'; g.fillRect(round(x), round(y), o.z || 1, o.z || 1);
    }
    g.restore();
  }
  // relámpago irregular de (x0,y0) a (x1,y1); se re-sortea a 20 fps
  function bolt(g, x0, y0, x1, y1, t, o = {}) {
    const seed = Math.floor(t * 20), n = o.seg || 9, z = o.z || 1, pts = [[x0, y0]];
    const dx = x1 - x0, dy = y1 - y0, len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len;
    for (let i = 1; i < n; i++) { const off = (hash(seed, i + (o.id || 0) * 13) - .5) * (o.amp || 10) * Math.min(1, i / 2, (n - i) / 2); pts.push([x0 + dx * i / n + nx * off, y0 + dy * i / n + ny * off]); }
    pts.push([x1, y1]);
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
    const line = (a, b, col, w) => { const steps = Math.max(abs(b[0] - a[0]), abs(b[1] - a[1])) | 0; g.fillStyle = col; for (let s_ = 0; s_ <= steps; s_++) { const f = steps ? s_ / steps : 0; g.fillRect(round(a[0] + (b[0] - a[0]) * f - w / 2), round(a[1] + (b[1] - a[1]) * f - w / 2), w, w); } };
    const cl = o.cols || ['rgba(120,210,255,.55)', '#9ee8ff', '#ffffff'];
    for (let i = 0; i < pts.length - 1; i++) line(pts[i], pts[i + 1], cl[0], (o.w || 3) * z);
    for (let i = 0; i < pts.length - 1; i++) line(pts[i], pts[i + 1], cl[1], Math.max(1, (o.w || 3) - 1) * z);
    for (let i = 0; i < pts.length - 1; i++) line(pts[i], pts[i + 1], cl[2], 1 * z);
    if (o.fork !== false) for (let k = 0; k < 2; k++) { const i = 2 + k * 3, a = pts[i], b = [a[0] + (hash(seed, 40 + k) - .5) * 24 * z, a[1] + (hash(seed, 50 + k) - .2) * 18 * z]; line(a, b, '#9ee8ff', 1 * z); }
    g.restore();
  }
  // arcos eléctricos cortos alrededor de un punto
  function arcs(g, cx, cy, t, k = 1, o = {}) {
    const z = o.z || 1, n = Math.round(4 * k);
    for (let i = 0; i < n; i++) { const a = hash(Math.floor(t * 14), i) * TAU, r0 = (4 + hash(Math.floor(t * 14), i + 9) * 4) * z, r1 = r0 + (8 + hash(Math.floor(t * 14), i + 19) * 10) * z;
      bolt(g, cx + Math.cos(a) * r0, cy + Math.sin(a) * r0, cx + Math.cos(a) * r1, cy + Math.sin(a) * r1, t + i * 0.013, { seg: 4, amp: 5 * z, z: Math.max(1, z / 2), id: i, fork: false }); }
  }

  const has = (name, anim) => !!(LIB[name] && LIB[name][anim]);

  // aliento de fuego: partículas deterministas desde (x,y) en dirección (dx,dy)
  function fire(g, x, y, dx, dy, t, k = 1, o = {}) {
    const L = (o.len || 130) * Math.min(1, k + 0.2), n = 90, z = o.z || 1; g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
    const len = Math.hypot(dx, dy) || 1, ux = dx / len, uy = dy / len, nx = -uy, ny = ux;
    for (let i = 0; i < n; i++) {
      const age = (t * 1.9 + hash(i, 1)) % 1, d = age * L, sp = (hash(i, 2) - .5) * (4 + age * 34) * z, flick = Math.sin(t * 25 + i) * 1.5;
      const px = x + ux * d + nx * (sp + flick), py = y + uy * d + ny * (sp + flick) - age * age * 14, sz = (1 + age * 4 * (o.size || 1)) * z;
      const col = age < .18 ? '#fff4c0' : age < .4 ? '#ffd048' : age < .7 ? '#f07a28' : '#a02a1c';
      g.globalAlpha = Math.min(1, k * 1.4) * (age > .85 ? (1 - age) / .15 : 1); g.fillStyle = col; g.fillRect(round(px), round(py), round(sz), round(sz));
    }
    g.globalAlpha = 1; g.restore();
  }
  function sparkle(g, cx, cy, w, h, t) { g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
    for (let i = 0; i < 24; i++) { const ph = (t * 1.3 + hash(i, 1)) % 1; g.globalAlpha = Math.sin(ph * Math.PI); g.fillStyle = hash(i, 2) > .5 ? '#ffffff' : '#9fd8ff';
      const x = round(cx + (hash(i, 3) - .5) * w), y = round(cy + (hash(i, 4) - .5) * h); g.fillRect(x, y, 1, 1); if (ph > .4 && ph < .6) { g.fillRect(x - 1, y, 3, 1); g.fillRect(x, y - 1, 1, 3) } }
    g.globalAlpha = 1; g.restore(); }

  G.Rig = { init, draw, sample, has, fire, sparkle, glow, aura, bolt, arcs, hash, clamp, easeOut, snap };
})(window);
