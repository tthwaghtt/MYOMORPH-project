// MYOMORPH procedural SFX v2 — pure functions that render Float32Array samples.
// Same code runs in the browser (→ AudioBuffer) and in Node (→ WAV for spectral checks).
// Each sound is built exciter → resonator, from the physics of the part that makes it.

export const TI = { E: 113.8e9, rho: 4430, nu: 0.34 };

function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

// RBJ biquad, applied in place on a copy
function biquad(x, sr, type, f, Q = 0.707) {
  const w = 2 * Math.PI * f / sr, cw = Math.cos(w), al = Math.sin(w) / (2 * Q);
  let b0, b1, b2, a0, a1, a2;
  if (type === 'bp') { b0 = al; b1 = 0; b2 = -al; a0 = 1 + al; a1 = -2 * cw; a2 = 1 - al; }
  else if (type === 'hp') { b0 = (1 + cw) / 2; b1 = -(1 + cw); b2 = (1 + cw) / 2; a0 = 1 + al; a1 = -2 * cw; a2 = 1 - al; }
  else { b0 = (1 - cw) / 2; b1 = 1 - cw; b2 = (1 - cw) / 2; a0 = 1 + al; a1 = -2 * cw; a2 = 1 - al; }
  const y = new Float32Array(x.length);
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  for (let i = 0; i < x.length; i++) {
    const v = (b0 * x[i] + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2) / a0;
    x2 = x1; x1 = x[i]; y2 = y1; y1 = v; y[i] = v;
  }
  return y;
}

// spectral weight of a half-sine contact force pulse of duration tc (hard contact = short tc = bright)
const contactWeight = (f, tc) => {
  const u = 2 * f * tc;
  return Math.abs(u - 1) < 1e-3 ? Math.PI / 4 : Math.abs(Math.cos(Math.PI * f * tc) / (1 - u * u));
};

// add a bank of damped sinusoids excited at sample i0
function addModes(out, sr, i0, modes, tc, gain, r) {
  for (const m of modes) {
    const w = contactWeight(m.f, tc), a = m.a * w * gain, n = Math.min(out.length - i0, Math.ceil(m.tau * 7 * sr));
    const ph = r() * 6.283, k = 2 * Math.PI * m.f / sr, d = Math.exp(-1 / (m.tau * sr));
    let env = a;
    for (let i = 0; i < n; i++) { out[i0 + i] += env * Math.sin(k * i + ph); env *= d; }
  }
}

function addNoise(out, sr, i0, dur, amp, r, shape = 'decay', filt) {
  const n = Math.min(out.length - i0, Math.ceil(dur * sr));
  let buf = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const t = i / n;
    const env = shape === 'rise' ? t * t : shape === 'flat' ? 1 : (1 - t) ** 3;
    buf[i] = (r() * 2 - 1) * env;
  }
  if (filt) buf = biquad(buf, sr, filt[0], filt[1], filt[2] ?? 0.9);
  for (let i = 0; i < n; i++) out[i0 + i] += buf[i] * amp;
}

// thin plate bending modes (simply supported): f_mn = (pi/2) sqrt(D / (rho h)) ((m/a)^2 + (n/b)^2)
export function plateModes(a, b, h, mat = TI) {
  const D = mat.E * h ** 3 / (12 * (1 - mat.nu ** 2)), k = (Math.PI / 2) * Math.sqrt(D / (mat.rho * h));
  const list = [];
  for (let m = 1; m <= 6; m++) for (let n = 1; n <= 6; n++) {
    const f = k * ((m / a) ** 2 + (n / b) ** 2);
    if (f < 14000) list.push({ f, m, n });
  }
  return list.sort((p, q) => p.f - q.f);
}

function finish(out, sr, room = true) {
  if (room) { // small hard room: three early reflections
    const src = Float32Array.from(out);
    for (const [ms, g] of [[9, 0.16], [17, 0.09], [29, 0.05]]) {
      const d = Math.round(ms * sr / 1000);
      for (let i = d; i < out.length; i++) out[i] += src[i - d] * g;
    }
  }
  let pk = 0; for (const v of out) pk = Math.max(pk, Math.abs(v));
  const g = pk > 0 ? 0.92 / pk : 1;
  for (let i = 0; i < out.length; i++) out[i] = Math.tanh(out[i] * g * 1.15) / Math.tanh(1.15);
  return out;
}

/**
 * "철컥" panel lock. Two impacts: the steel pawl snaps over the catch (bright "철"),
 * then the titanium panel seats hard against its stop (solid "컥") with one or two micro-bounces.
 * part: { a, b, h } panel size in m; massG drives how heavy the seat sounds.
 */
export function renderLockV2(sr, part = { a: 0.16, b: 0.10, h: 0.001, massG: 70 }, seed = 1) {
  const r = rng(seed), dur = 0.55, out = new Float32Array(Math.ceil(dur * sr));
  const heavy = Math.min(1, Math.max(0, Math.log10(part.massG / 20) / Math.log10(30)));   // 20 g → 0, 600 g → 1
  const jitter = () => 1 + (r() - 0.5) * 0.04;
  // 0) guide slide into position (polymer guide on Ti): faint rising hiss
  addNoise(out, sr, 0, 0.06, 0.035, r, 'rise', ['bp', 3200, 1.1]);
  // 1) "철": hardened-steel pawl strike — very short contact, small-part modes 3–11 kHz, light damping
  const t1 = Math.round(0.06 * sr);
  const pawl = [3150, 4870, 6620, 8930, 11400].map((f, i) => ({ f: f * jitter(), a: [1, 0.75, 0.6, 0.42, 0.28][i], tau: [0.024, 0.019, 0.015, 0.011, 0.008][i] }));     // short, dry ring: a latch, not a bell
  addModes(out, sr, t1, pawl, 0.00006, 0.55, r);
  addNoise(out, sr, t1, 0.0008, 0.9, r, 'decay', ['hp', 2500, 0.7]);
  // 2) "컥": panel seats on hard stop — longer contact, panel modes damped by isolators, mid "chunk", short body
  const t2 = t1 + Math.round((0.038 + 0.012 * heavy) * sr);
  const panel = plateModes(part.a, part.b, part.h).slice(0, 18).map((p) => ({
    f: p.f * jitter(),
    a: 0.55 / Math.sqrt(p.m * p.n) * (p.f < 500 ? 0.35 : 1),                // low modes kept small: no "뚱"
    tau: Math.min(0.045, 0.018 * Math.pow(1200 / p.f, 0.35)),                // isolator-damped
  }));
  const seat = (i0, g) => {
    addModes(out, sr, i0, panel, 0.00022, 0.9 * g, r);
    addNoise(out, sr, i0, 0.007, 0.75 * g, r, 'decay', ['bp', 1700 + 600 * (1 - heavy), 0.8]);
    addModes(out, sr, i0, [{ f: 105 + 40 * (1 - heavy), a: 1, tau: 0.028 }], 0.0003, (0.28 + 0.25 * heavy) * g, r);
    addModes(out, sr, i0, pawl.map((m) => ({ ...m, a: m.a * 0.35, tau: m.tau * 0.6 })), 0.00008, 0.35 * g, r);
  };
  seat(t2, 1);
  seat(t2 + Math.round(0.0055 * sr), 0.28);                                   // micro-bounce
  seat(t2 + Math.round(0.0105 * sr), 0.09);
  return finish(out, sr);
}

/**
 * Robot-arm nutrunner driving an M2.5 Ti screw: BLDC whine (rpm × pole pairs) + planetary gear mesh,
 * thread friction pulsing at spindle rotation, rpm sag as torque builds, mechanical clutch double-click, spin-down.
 */
export function renderNutrunnerV2(sr, opts = {}, seed = 3) {
  const r = rng(seed);
  const tRun = opts.tRun ?? 0.62, dur = tRun + 0.28, out = new Float32Array(Math.ceil(dur * sr));
  const poles = 4, Zs = 13, Zr = 47, ratio = 1 + Zr / Zs, rpmMax = 15000, rpmEnd = 11800;   // planetary stage
  let phM = 0, phG = 0, phS = 0;
  const fric = biquad(biquad(Float32Array.from({ length: out.length }, () => r() * 2 - 1), sr, 'bp', 1300, 1.4), sr, 'bp', 1300, 1.4);
  for (let i = 0; i < out.length; i++) {
    const t = i / sr;
    let rpm;
    if (t < 0.07) rpm = rpmMax * (1 - Math.exp(-t / 0.018));
    else if (t < tRun) rpm = rpmMax - (rpmMax - rpmEnd) * ((t - 0.07) / (tRun - 0.07)) ** 1.6;
    else rpm = rpmEnd * Math.exp(-(t - tRun) / 0.05);
    const load = t < tRun ? Math.min(1, (t / tRun) ** 2) : 0;
    const fm = rpm / 60 * poles, fg = rpm / 60 * Zs * Zr / (Zs + Zr), fs = rpm / 60 / ratio;   // mesh = f_sun · Zs·Zr/(Zs+Zr)
    phM += 2 * Math.PI * fm / sr; phG += 2 * Math.PI * fg / sr; phS += 2 * Math.PI * fs / sr;
    const env = Math.min(1, t / 0.01) * (t < tRun ? 1 : Math.exp(-(t - tRun) / 0.06));
    const motor = 0.32 * Math.sin(phM) + 0.12 * Math.sin(2 * phM) + 0.06 * Math.sin(3 * phM);
    const gear = (0.16 + 0.22 * load) * Math.sin(phG) * (1 + 0.35 * Math.sin(phS * 3));      // mesh, modulated by planet carrier
    const thread = (0.05 + 0.25 * load) * fric[i] * (0.6 + 0.4 * Math.max(0, Math.sin(phS)));
    const pwm = 0.012 * Math.sin(2 * Math.PI * 9200 * t);
    out[i] += env * (motor + gear + thread + pwm) * 0.45;
  }
  // clutch release: characteristic double click
  const click = [2250, 3820, 5640, 7900].map((f, i) => ({ f, a: [1, 0.7, 0.5, 0.3][i], tau: [0.016, 0.012, 0.009, 0.007][i] }));
  for (const [dt, g] of [[0, 1], [0.024, 0.65]]) {
    const i0 = Math.round((tRun + dt) * sr);
    addModes(out, sr, i0, click, 0.00007, 0.9 * g, r);
    addNoise(out, sr, i0, 0.0007, 0.8 * g, r, 'decay', ['hp', 2000]);
  }
  return finish(out, sr);
}

/**
 * ADOPTED (Doha, P0 listening 3: "v2 is better"). Hydraulic actuator stroke: solenoid valve opens (poppet on seat), internal-gear pump ripple
 * (rpm × teeth + harmonics), flow hiss ∝ velocity, cavitation fizz, rod-seal rumble, valve close + settle.
 */
export function renderHydraulic(sr, opts = {}, seed = 5) {
  const r = rng(seed);
  const stroke = opts.stroke ?? 0.75, dur = stroke + 0.35, out = new Float32Array(Math.ceil(dur * sr));
  const pumpF = 3600 / 60 * 11;  // 660 Hz
  const white = Float32Array.from({ length: out.length }, () => r() * 2 - 1);
  const hiss = biquad(biquad(white, sr, 'bp', 3400, 0.8), sr, 'bp', 3400, 0.8), fizz = biquad(white, sr, 'hp', 7000), seal = biquad(white, sr, 'bp', 240, 1.2);
  const t0 = 0.03;
  for (let i = 0; i < out.length; i++) {
    const t = i / sr - t0;
    if (t < 0) continue;
    const x = Math.min(1, Math.max(0, t / stroke));
    const vel = t < stroke ? Math.sin(Math.PI * x) ** 1.5 : 0;                 // smooth accel/decel
    const pump = Math.min(1, t / 0.05) * (t < stroke + 0.05 ? 1 : Math.exp(-(t - stroke - 0.05) / 0.08));
    const ripple = pump * (0.22 * Math.sin(2 * Math.PI * pumpF * t) + 0.1 * Math.sin(2 * Math.PI * 2 * pumpF * t) + 0.05 * Math.sin(2 * Math.PI * 3 * pumpF * t)) * (1 + 0.1 * Math.sin(2 * Math.PI * 60 * t));
    out[i] += ripple * 0.75 + vel * (0.5 * hiss[i] + 0.025 * fizz[i] + 0.3 * seal[i]);
  }
  const poppet = [2600, 4100, 6300].map((f, i) => ({ f, a: [1, 0.6, 0.35][i], tau: [0.009, 0.007, 0.005][i] }));
  const valve = (time, g) => {
    const i0 = Math.round(time * sr);
    addModes(out, sr, i0, poppet, 0.0001, 0.8 * g, r);
    addModes(out, sr, i0, [{ f: 180, a: 1, tau: 0.016 }], 0.0004, 0.4 * g, r);
  };
  valve(t0, 1);
  valve(t0 + stroke + 0.02, 0.85);
  addModes(out, sr, Math.round((t0 + stroke + 0.025) * sr), [{ f: 120, a: 1, tau: 0.045 }, { f: 880, a: 0.4, tau: 0.02 }], 0.0005, 0.5, r); // settle against stop
  return finish(out, sr);
}

/** the P0 v4 sound (for A/B comparison) */
export function renderLockV1(sr, seed = 1) {
  const r = rng(seed), out = new Float32Array(Math.ceil(0.8 * sr));
  const modes = plateModes(0.16, 0.10, 0.001).filter((p) => p.m <= 4 && p.n <= 4 && p.f < 12000).map((p) => ({ f: p.f, a: 0.5 / (p.m * p.n), tau: 0.06 * Math.pow(800 / p.f, 0.6) }));
  addModes(out, sr, 0, modes, 0, 1, r);
  addNoise(out, sr, 0, 0.002, 0.35, r);
  addModes(out, sr, Math.round(0.03 * sr), [4200, 6900, 9100].map((f, i) => ({ f, a: 0.25 / (i + 1), tau: 0.012 })), 0, 0.7, r);
  return finish(out, sr, false);
}

/* =====================================================================================
 * v3 — "rougher by layering" (Doha, P0 listening 2): keep each sound's pitch, add layers
 * that make it rough: amplitude modulation in the 20–150 Hz roughness band, dense
 * inharmonic partials that beat, and stochastic micro-impacts (rattle, grit, crackle).
 * ===================================================================================== */

// Poisson micro-impacts: each excites a few small-part modes with random strength (grit, rattle, crackle)
function addRattle(out, sr, i0, dur, ratePerSec, amp, r, modes, tc = 0.00008, densityEnv = () => 1) {
  const n = Math.min(out.length - i0, Math.ceil(dur * sr));
  let t = 0;
  while (true) {
    t += -Math.log(1 - r()) / ratePerSec;
    if (t * sr >= n) break;
    const d = densityEnv(t / dur);
    if (r() > d) continue;
    const g = amp * (0.25 + 0.75 * r() ** 2);
    const jit = 1 + (r() - 0.5) * 0.12;
    addModes(out, sr, i0 + Math.round(t * sr), modes.map((m) => ({ ...m, f: m.f * jit })), tc, g, r);
  }
}

// smooth random signal (for turbulence / jitter), value roughly in [-1, 1]
function smoothNoise(n, sr, rateHz, r) {
  const y = new Float32Array(n), step = Math.max(1, Math.round(sr / rateHz));
  let a = r() * 2 - 1, b = r() * 2 - 1;
  for (let i = 0; i < n; i++) {
    if (i % step === 0) { a = b; b = r() * 2 - 1; }
    const u = (i % step) / step, w = u * u * (3 - 2 * u);
    y[i] = a + (b - a) * w;
  }
  return y;
}

export function renderLock(sr, part = { a: 0.16, b: 0.10, h: 0.001, massG: 70 }, seed = 1) {
  const r = rng(seed ^ 0x5a5a);
  const out = renderLockV2(sr, part, seed);                       // the approved "철컥" stays the core
  const heavy = Math.min(1, Math.max(0, Math.log10(part.massG / 20) / Math.log10(30)));
  const t1 = Math.round(0.06 * sr), t2 = t1 + Math.round((0.038 + 0.012 * heavy) * sr);
  // layer: stick-slip grit while the panel slides along its guide (instead of a smooth hiss)
  const grit = [1900, 3300, 5200].map((f, i) => ({ f, a: [1, 0.6, 0.35][i], tau: 0.004 }));
  addRattle(out, sr, 0, 0.058, 260, 0.05, r, grit, 0.00012, (u) => u);
  // layer: the second latch of the panel engages 2–5 ms later, slightly detuned → a thicker, rougher "철"
  const pawl2 = [3150, 4870, 6620, 8930].map((f, i) => ({ f: f * (1.035 + r() * 0.03), a: [1, 0.7, 0.5, 0.3][i], tau: [0.02, 0.016, 0.012, 0.009][i] }));
  addModes(out, sr, t1 + Math.round((0.002 + r() * 0.003) * sr), pawl2, 0.00007, 0.32, r);
  // layer: loose clip / washer rattle after the seat
  const clip = [2700, 4400, 6900].map((f, i) => ({ f, a: [1, 0.6, 0.3][i], tau: 0.006 }));
  addRattle(out, sr, t2 + Math.round(0.006 * sr), 0.07, 140, 0.11 + 0.06 * heavy, r, clip, 0.0001, (u) => (1 - u) ** 2);
  return finish(out, sr, false);
}

export function renderNutrunner(sr, opts = {}, seed = 3) {
  const r = rng(seed);
  const tRun = opts.tRun ?? 0.62, dur = tRun + 0.28, N = Math.ceil(dur * sr), out = new Float32Array(N);
  const poles = 4, Zs = 13, Zr = 47, ratio = 1 + Zr / Zs, rpmMax = 15000, rpmEnd = 11800;
  const white = Float32Array.from({ length: N }, () => r() * 2 - 1);
  const fric = biquad(biquad(white, sr, 'bp', 1300, 1.4), sr, 'bp', 1300, 1.4);
  const brush = biquad(biquad(white.map((v, i) => white[(i * 7919) % N]), sr, 'hp', 2500), sr, 'lp', 9000);   // decorrelated copy
  const jitter = smoothNoise(N, sr, 35, r), rough = smoothNoise(N, sr, 140, r);
  const rpmAt = (t) => t < 0.07 ? rpmMax * (1 - Math.exp(-t / 0.018))
    : t < tRun ? rpmMax - (rpmMax - rpmEnd) * ((t - 0.07) / (tRun - 0.07)) ** 1.6
    : rpmEnd * Math.exp(-(t - tRun) / 0.05);
  const ph = new Float64Array(8);
  for (let i = 0; i < N; i++) {
    const t = i / sr, rpm = rpmAt(t) * (1 + 0.004 * jitter[i]);       // slight speed wander, same pitch centre
    const load = t < tRun ? Math.min(1, (t / tRun) ** 2) : 0;
    const fm = rpm / 60 * poles, fg = rpm / 60 * Zs * Zr / (Zs + Zr), fs = rpm / 60 / ratio;
    const freqs = [fm, fm * 1.031, fm * 0.966, fg, fg * 1.047, fs, fm * 2, rpm / 60];   // detuned layers beat at 30–120 Hz → roughness
    for (let k = 0; k < freqs.length; k++) ph[k] += 2 * Math.PI * freqs[k] / sr;
    const env = Math.min(1, t / 0.01) * (t < tRun ? 1 : Math.exp(-(t - tRun) / 0.06));
    // whine: core + two detuned layers, amplitude-modulated near 70 Hz (peak of perceived roughness)
    const am = 1 - 0.35 * (0.5 + 0.5 * Math.sin(2 * Math.PI * 68 * t + 3 * jitter[i]));
    const whine = (0.26 * Math.sin(ph[0]) + 0.13 * Math.sin(ph[1]) + 0.12 * Math.sin(ph[2]) + 0.09 * Math.sin(ph[6])) * am;
    // gear mesh with tooth-impact harshness (clipped sine ~ square-ish) and its detuned partner
    const gm = Math.tanh(2.2 * Math.sin(ph[3])) * 0.6 + 0.4 * Math.sin(ph[4]);
    const gear = (0.13 + 0.2 * load) * gm * (1 + 0.35 * Math.sin(ph[5] * 3));
    const thread = (0.05 + 0.25 * load) * fric[i] * (0.6 + 0.4 * Math.max(0, Math.sin(ph[5])));
    const brushes = 0.07 * brush[i] * (0.6 + 0.4 * Math.sin(ph[7] * 2)) * (0.7 + 0.3 * rough[i]);
    const pwm = 0.012 * Math.sin(2 * Math.PI * 9200 * t);
    out[i] += env * (whine + gear + thread + brushes + pwm) * 0.42;
  }
  // gear backlash rattle grows with load
  const tooth = [1800, 3100, 4700].map((f, i) => ({ f, a: [1, 0.55, 0.3][i], tau: 0.003 }));
  addRattle(out, sr, Math.round(0.08 * sr), tRun - 0.08, 320, 0.07, r, tooth, 0.0001, (u) => 0.25 + 0.75 * u);
  // clutch release double click (+ a faint third ratchet tick)
  const click = [2250, 3820, 5640, 7900].map((f, i) => ({ f, a: [1, 0.7, 0.5, 0.3][i], tau: [0.016, 0.012, 0.009, 0.007][i] }));
  for (const [dt, g] of [[0, 1], [0.024, 0.65], [0.041, 0.2]]) {
    const i0 = Math.round((tRun + dt) * sr);
    addModes(out, sr, i0, click, 0.00007, 0.9 * g, r);
    addNoise(out, sr, i0, 0.0007, 0.8 * g, r, 'decay', ['hp', 2000]);
  }
  return finish(out, sr);
}

/**
 * Hydraulic "슉": no tonal pump whine (the pump lives in the HPU, far from the joint).
 * At the actuator you hear oil rushing through the valve and lines: layered turbulent noise bands with
 * independent random modulation, cavitation crackle, a body "chuff", and (optionally) soft valve ticks.
 */
export function renderHydraulicV3(sr, opts = {}, seed = 5) {
  const r = rng(seed);
  const stroke = opts.stroke ?? 0.42, withValve = opts.valve ?? true, dur = stroke + 0.22, N = Math.ceil(dur * sr), out = new Float32Array(N);
  const w1 = Float32Array.from({ length: N }, () => r() * 2 - 1), w2 = Float32Array.from({ length: N }, () => r() * 2 - 1);
  const bands = [
    [biquad(biquad(w1, sr, 'bp', 900, 0.9), sr, 'bp', 900, 0.9), 0.55, smoothNoise(N, sr, 18, r)],    // body
    [biquad(biquad(w2, sr, 'bp', 2400, 0.8), sr, 'bp', 2400, 0.8), 0.85, smoothNoise(N, sr, 26, r)],  // main rush
    [biquad(biquad(w1, sr, 'bp', 5200, 0.9), sr, 'bp', 5200, 0.9), 0.45, smoothNoise(N, sr, 40, r)],  // edge
  ];
  const grain = smoothNoise(N, sr, 90, r), grain2 = smoothNoise(N, sr, 55, r);   // fast random modulation (40–150 Hz) → rough, not smooth
  const t0 = 0.012;
  for (let i = 0; i < N; i++) {
    const t = i / sr - t0;
    if (t < 0) continue;
    const x = t / stroke;
    // "슉": fast onset, a short swell, then decay as the rod decelerates
    const env = t < stroke ? Math.min(1, t / 0.018) * (1 - 0.55 * x) * (0.85 + 0.15 * Math.sin(Math.PI * Math.min(1, x * 1.6)))
                           : (1 - 0.55) * Math.exp(-(t - stroke) / 0.035);
    let v = 0;
    for (const [b, g, mod] of bands) v += b[i] * g * (0.75 + 0.25 * mod[i]);
    out[i] += v * env * (0.62 + 0.24 * grain[i] + 0.14 * grain2[i]);
  }
  const bubble = [3800, 6100, 8800].map((f, i) => ({ f, a: [1, 0.6, 0.35][i], tau: 0.0018 }));
  addRattle(out, sr, Math.round(t0 * sr), stroke, 900, 0.07, r, bubble, 0.00005, (u) => (1 - u) * 0.9 + 0.1);
  if (withValve) {
    const tick = [2600, 4100].map((f, i) => ({ f, a: [1, 0.5][i], tau: 0.005 }));
    addModes(out, sr, 0, tick, 0.0001, 0.18, r);
    addModes(out, sr, Math.round((t0 + stroke + 0.015) * sr), [{ f: 140, a: 1, tau: 0.03 }, ...tick], 0.0004, 0.22, r);
  }
  return finish(out, sr);
}
