import * as THREE from 'three/webgpu';
import { pass, float, log2, max, clamp, texture3D, vec4 } from 'three/tsl';
import { lut3D } from 'three/addons/tsl/display/Lut3DNode.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { noBlobTextures } from './gltf-noblob.js';

const $ = (id) => document.getElementById(id);
const BASE = new URL('./', document.baseURI);   // published files are served next to the page
const url = (p) => new URL(p, BASE).href;

/* ---------------- results + persistence ---------------- */
const results = { started: new Date().toISOString(), page: 'p0-platform v3', auto: {}, manual: {}, memo: '' };
const rows = {};
function setAuto(key, label, status, detail) {
  results.auto[key] = { status, detail };
  let tr = rows[key];
  if (!tr) {
    tr = document.createElement('tr');
    tr.innerHTML = '<td></td><td></td><td class="v"></td>';
    tr.children[0].textContent = label;
    $('auto').appendChild(tr); rows[key] = tr;
  }
  const names = { ok: '정상', warn: '부분', bad: '실패', wait: '측정 중', info: '정보' };
  tr.children[1].innerHTML = `<span class="pill ${status}">${names[status]}</span>`;
  tr.children[2].textContent = typeof detail === 'string' ? detail : JSON.stringify(detail);
  queueSave();
}
function setManual(id, status, detail) {
  results.manual[id] = { status, detail, at: new Date().toISOString() };
  const pill = $(id).querySelector('[data-s]');
  const names = { ok: '정상', warn: '부분', bad: '안 됨', wait: '대기', info: '확인 필요' };
  pill.className = `pill ${status}`; pill.textContent = names[status];
  queueSave();
}

let db = null, docRef = null, saveTimer = null, saving = false, dirty = false;
function queueSave() { dirty = true; clearTimeout(saveTimer); saveTimer = setTimeout(save, 800); }
async function save() {
  if (!db || saving || !dirty) return;
  saving = true; dirty = false;
  try {
    const data = JSON.parse(JSON.stringify(results));
    data.updated = new Date().toISOString();
    if (!docRef) docRef = await db.collection('p0_runs').add(data);
    else await docRef.set(data);
    $('save').textContent = `저장됨 · ${new Date().toLocaleTimeString()}`; $('save').classList.add('on');
  } catch (e) {
    $('save').textContent = `저장 실패: ${e.code || e.message}`; $('save').classList.remove('on');
  } finally { saving = false; if (dirty) queueSave(); }
}
(async () => {
  const use = window.claude?.use;
  db = use ? await use('db') : null;
  if (!db) { $('save').textContent = '저장 불가 (로그인된 claude.ai 뷰어에서만 저장됩니다). 결과는 화면에 표시됩니다.'; return; }
  const user = await use('user');
  results.viewer = user ? { owner: user.isOwner?.() ?? null, id: await user.id?.().catch(() => null) } : null;
  queueSave();
})();

/* ---------------- console capture (diagnostics) ---------------- */
results.logs = [];
for (const lvl of ['warn', 'error']) {
  const orig = console[lvl].bind(console);
  console[lvl] = (...a) => { if (results.logs.length < 40) results.logs.push(`${lvl}: ${a.map(String).join(' ').slice(0, 300)}`); queueSave(); orig(...a); };
}
addEventListener('error', (e) => { results.logs.push(`onerror: ${e.message}`); queueSave(); });
addEventListener('unhandledrejection', (e) => { results.logs.push(`rejection: ${String(e.reason).slice(0, 300)}`); queueSave(); });

/* ---------------- environment ---------------- */
const nav = navigator;
setAuto('env', '기기', 'info', {
  ua: nav.userAgent, platform: nav.userAgentData?.platform || nav.platform, mobile: nav.userAgentData?.mobile ?? /Mobi/.test(nav.userAgent),
  dpr: devicePixelRatio, screen: `${screen.width}x${screen.height}`, viewport: `${innerWidth}x${innerHeight}`,
  cores: nav.hardwareConcurrency, memoryGB: nav.deviceMemory ?? null, inIframe: window.top !== window,
});

async function probeWebGPU() {
  if (!('gpu' in nav)) return setAuto('webgpu', 'WebGPU', 'bad', 'navigator.gpu 없음');
  try {
    const ad = await nav.gpu.requestAdapter({ powerPreference: 'high-performance' });
    if (!ad) return setAuto('webgpu', 'WebGPU', 'bad', 'requestAdapter → null (iframe 정책 또는 GPU 차단 가능)');
    const info = ad.info || {};
    setAuto('webgpu', 'WebGPU', 'ok', {
      vendor: info.vendor, arch: info.architecture, device: info.device, desc: info.description,
      features: [...ad.features].filter((f) => /texture-compression|float32|timestamp|shader-f16/.test(f)),
      maxTex2D: ad.limits.maxTextureDimension2D, maxBuf: ad.limits.maxBufferSize,
    });
  } catch (e) { setAuto('webgpu', 'WebGPU', 'bad', String(e)); }
}
function probeWebGL2() {
  const gl = document.createElement('canvas').getContext('webgl2');
  if (!gl) return setAuto('webgl2', 'WebGL2 (폴백)', 'bad', '컨텍스트 없음');
  const dbg = gl.getExtension('WEBGL_debug_renderer_info');
  setAuto('webgl2', 'WebGL2 (폴백)', 'ok', {
    renderer: dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
    maxTex: gl.getParameter(gl.MAX_TEXTURE_SIZE),
    astc: !!gl.getExtension('WEBGL_compressed_texture_astc'), bptc: !!gl.getExtension('EXT_texture_compression_bptc'),
    etc: !!gl.getExtension('WEBGL_compressed_texture_etc'), s3tc: !!gl.getExtension('WEBGL_compressed_texture_s3tc'),
  });
}
async function probeFetch() {
  const t0 = performance.now();
  try {
    const r = await fetch(url('decoders/basis_transcoder.wasm'));
    const ct = r.headers.get('content-type');
    const buf = await r.arrayBuffer();
    let compiled = false; try { await WebAssembly.compile(buf); compiled = true; } catch {}
    setAuto('wasm', 'wasm 파일 배포', r.ok && compiled ? 'ok' : 'bad', { status: r.status, contentType: ct, bytes: buf.byteLength, compiled, ms: Math.round(performance.now() - t0) });
  } catch (e) { setAuto('wasm', 'wasm 파일 배포', 'bad', String(e)); }
}
probeWebGPU(); probeWebGL2(); probeFetch();
setAuto('apis', '브라우저 API 유무', 'info', {
  vibrate: 'vibrate' in nav, pointerLock: 'requestPointerLock' in Element.prototype, fullscreen: !!document.fullscreenEnabled,
  deviceOrientation: 'DeviceOrientationEvent' in window, orientationNeedsPermission: typeof DeviceOrientationEvent?.requestPermission === 'function',
  audioWorklet: typeof AudioWorkletNode !== 'undefined', gamepad: 'getGamepads' in nav, reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
});

/* ---------------- 3D ---------------- */
const canvas = $('c');
const canvasRef = { el: canvas };
let renderer = new THREE.WebGPURenderer({ canvas, antialias: true });
let fallbackReason = null;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0b0c);
const camera = new THREE.PerspectiveCamera(30, 16 / 9, 0.01, 10);
camera.position.set(0.05, 0.08, 0.42);
let controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.target.set(0, 0.0, 0.0);
let lutPipe, threePipe, pipe, mode = 'lut';

function resize() {
  const w = canvasRef.el.clientWidth, h = canvasRef.el.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
}

async function init3D() {
  const t0 = performance.now();
  try {
    await renderer.init();
    await probeRender();
  } catch (e) {
    // WebGPU path failed (old browser, blocked adapter, unsupported feature) -> same code on the WebGL2 backend
    fallbackReason = String(e.message || e).slice(0, 240);
    try { renderer.dispose(); } catch {}
    const fresh = canvas.cloneNode(); canvas.replaceWith(fresh); canvasRef.el = fresh;
    renderer = new THREE.WebGPURenderer({ canvas: fresh, antialias: true, forceWebGL: true });
    await renderer.init();
  }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  resize(); addEventListener('resize', resize);
  const backend = renderer.backend.isWebGPUBackend ? 'WebGPU' : 'WebGL2';
  setAuto('renderer', 'three.js 렌더러', backend === 'WebGPU' ? 'ok' : 'warn', { backend, three: THREE.REVISION, initMs: Math.round(performance.now() - t0), fallbackReason });
  controls.dispose(); controls = new OrbitControls(camera, canvasRef.el); controls.enableDamping = true;

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.02).texture;
  const key = new THREE.DirectionalLight(0xffffff, 2.5); key.position.set(0.4, 0.6, 0.5); scene.add(key);

  // AgX LUT (Blender 5.2.1, 48^3, log2 shaper)
  try {
    const t1 = performance.now();
    const r = await fetch(url('lut/agx_48.bin'));
    const buf = await r.arrayBuffer();
    const N = 48, tex = new THREE.Data3DTexture(new Uint16Array(buf), N, N, N);
    tex.type = THREE.HalfFloatType; tex.format = THREE.RGBAFormat;
    tex.minFilter = tex.magFilter = THREE.LinearFilter; tex.wrapS = tex.wrapT = tex.wrapR = THREE.ClampToEdgeWrapping;
    tex.colorSpace = THREE.NoColorSpace; tex.unpackAlignment = 1; tex.needsUpdate = true;
    const LO = -12.47393, HI = 12.5260688117;
    const scenePass = pass(scene, camera);
    const shaped = clamp(log2(max(scenePass.rgb, float(2 ** LO))).sub(LO).div(HI - LO), 0, 1);
    lutPipe = new THREE.RenderPipeline(renderer);
    lutPipe.outputColorTransform = false;
    lutPipe.outputNode = lut3D(vec4(shaped, 1), texture3D(tex), N, float(1));
    setAuto('lut', 'AgX LUT (.bin 파일)', r.ok ? 'ok' : 'bad', { status: r.status, contentType: r.headers.get('content-type'), bytes: buf.byteLength, ms: Math.round(performance.now() - t1) });
  } catch (e) { setAuto('lut', 'AgX LUT (.bin 파일)', 'bad', String(e)); }
  threePipe = new THREE.RenderPipeline(renderer);
  threePipe.outputNode = pass(scene, camera);
  setMode('lut');

  // asset: meshopt geometry + KTX2 (UASTC) texture + KHR_materials_anisotropy
  try {
    const t2 = performance.now();
    const ktx2 = new KTX2Loader().setTranscoderPath(url('decoders/')).detectSupport(renderer);
    const gltf = await new GLTFLoader().register(noBlobTextures).setMeshoptDecoder(MeshoptDecoder).setKTX2Loader(ktx2).loadAsync(url('models/test_panel.glb'));
    const root = gltf.scene; scene.add(root);
    const box = new THREE.Box3().setFromObject(root); const c = box.getCenter(new THREE.Vector3());
    root.position.sub(c);
    let aniso = null, aoFormat = null, meshes = 0, parts = [], mats = {};
    root.traverse((o) => {
      if (!o.isMesh) return;
      meshes++;
      if (o.userData?.mm1_part_id) parts.push(o.userData.mm1_part_id);
      const m = o.material;
      if (m.anisotropy) aniso = m.anisotropy;
      if (m.aoMap) aoFormat = m.aoMap.format;
      mats[m.name] = Object.keys(m).filter((k) => /Map$/.test(k) && m[k]).map((k) => `${k}:${m[k].isCompressedTexture ? 'compressed' : 'plain'}:${m[k].format}`);
    });
    setAuto('asset', 'glTF (meshopt + KTX2 + 이방성)', aniso && aoFormat != null ? 'ok' : 'warn', {
      ms: Math.round(performance.now() - t2), meshes, extras: parts.length, anisotropy: aniso, ktx2GpuFormat: aoFormat, maps: mats, gltfTextures: gltf.parser.json.textures?.length ?? 0,
    });
  } catch (e) { setAuto('asset', 'glTF (meshopt + KTX2 + 이방성)', 'bad', String(e)); }

  // frame-time benchmark: 120 frames after warm-up
  const times = []; let last = performance.now(), frame = 0;
  renderer.setAnimationLoop(() => {
    const now = performance.now(); const dt = now - last; last = now;
    controls.update(); pipe.render();
    frame++;
    if (frame > 30 && times.length < 120) times.push(dt);
    if (times.length === 120) {
      times.sort((a, b) => a - b);
      const med = times[60], p95 = times[114];
      setAuto('bench', '렌더 성능 (프레임 시간)', med < 17.5 ? 'ok' : med < 34 ? 'warn' : 'bad',
        { medianMs: +med.toFixed(2), p95Ms: +p95.toFixed(2), px: `${renderer.domElement.width}x${renderer.domElement.height}`, mode });
      times.push(0);
    }
    if (frame % 15 === 0) $('fps').textContent = `${dt.toFixed(1)} ms · ${renderer.backend.isWebGPUBackend ? 'WebGPU' : 'WebGL2'}`;
  });
}
async function probeRender() {
  const pm = new THREE.PMREMGenerator(renderer);
  const rt = pm.fromScene(new RoomEnvironment(), 0.02);
  const t = new THREE.Data3DTexture(new Uint16Array(4 * 8), 2, 2, 2); t.type = THREE.HalfFloatType; t.needsUpdate = true;
  const m = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshStandardMaterial());
  const s = new THREE.Scene(); s.environment = rt.texture; s.add(m);
  const p = new THREE.RenderPipeline(renderer); p.outputNode = pass(s, camera);
  p.render();
  if (renderer.backend.device) { const err = await renderer.backend.device.popErrorScope?.().catch(() => null); }
  rt.dispose(); pm.dispose();
}
function setMode(m) {
  mode = m;
  if (m === 'lut') { renderer.toneMapping = THREE.NoToneMapping; pipe = lutPipe || threePipe; }
  else { renderer.toneMapping = THREE.AgXToneMapping; pipe = threePipe; }
  $('tm-lut').setAttribute('aria-pressed', String(m === 'lut')); $('tm-three').setAttribute('aria-pressed', String(m === 'three'));
}
$('tm-lut').onclick = () => setMode('lut');
$('tm-three').onclick = () => setMode('three');
init3D().catch((e) => setAuto('renderer', 'three.js 렌더러', 'bad', String(e)));

/* ---------------- manual tests ---------------- */
function ask(id, onYes, onNo) {
  const el = $(id).querySelector('[data-ask]'); el.classList.add('on');
  el.querySelector('[data-yes]').onclick = () => { onYes(); el.classList.remove('on'); };
  el.querySelector('[data-no]').onclick = () => { onNo(); el.classList.remove('on'); };
}

// Ti panel plate modes: f_mn = (pi/2) sqrt(D/(rho h)) ((m/a)^2 + (n/b)^2), D = E h^3 / (12 (1 - nu^2))
const Ti = { E: 113.8e9, rho: 4430, nu: 0.34 };
function plateModes(a, b, h) {
  const D = Ti.E * h ** 3 / (12 * (1 - Ti.nu ** 2)), k = (Math.PI / 2) * Math.sqrt(D / (Ti.rho * h));
  const modes = [];
  for (let m = 1; m <= 4; m++) for (let n = 1; n <= 4; n++) {
    const f = k * ((m / a) ** 2 + (n / b) ** 2);
    if (f < 12000) modes.push({ f, a: 0.5 / (m * n), tau: 0.06 * Math.pow(800 / f, 0.6), ph: Math.random() * 6.28 });
  }
  return modes;
}
let actx = null, node = null;
async function audioInit() {
  if (actx) return;
  const t0 = performance.now();
  actx = new AudioContext({ latencyHint: 'interactive' });
  await actx.audioWorklet.addModule(url('worklets/modal-processor.js'));
  node = new AudioWorkletNode(actx, 'modal-processor', { outputChannelCount: [2] });
  const comp = actx.createDynamicsCompressor(); comp.threshold.value = -6; comp.ratio.value = 8;
  node.connect(comp).connect(actx.destination);
  results.manual.audioEngine = { sampleRate: actx.sampleRate, baseLatencyMs: +(actx.baseLatency * 1000).toFixed(1), outputLatencyMs: actx.outputLatency ? +(actx.outputLatency * 1000).toFixed(1) : null, initMs: Math.round(performance.now() - t0) };
}
function strike(delay = 0, gain = 0.5) {
  const panel = plateModes(0.16, 0.10, 0.001);           // the test panel
  const latch = [4200, 6900, 9100].map((f, i) => ({ f, a: 0.25 / (i + 1), tau: 0.012, ph: 0 }));
  node.port.postMessage({ type: 'strike', modes: panel, noise: 0.35, gain, delay, life: 8 * Math.max(...panel.map((m) => m.tau)) });   // ~ -70 dB before the voice ends: no truncation click
  node.port.postMessage({ type: 'strike', modes: latch, noise: 0.15, gain: gain * 0.7, delay: delay + 0.03, life: 0.1 });
  if (nav.vibrate) nav.vibrate([10, 24, 14]);
}
$('b-audio').onclick = async () => {
  try {
    await audioInit(); await actx.resume(); strike();
    setManual('t-audio', 'info', { ...results.manual.audioEngine, firstModesHz: plateModes(0.16, 0.10, 0.001).slice(0, 4).map((m) => Math.round(m.f)) });
    ask('t-audio', () => setManual('t-audio', 'ok', { heard: true, ...results.manual.audioEngine }), () => setManual('t-audio', 'bad', { heard: false, state: actx.state, ...results.manual.audioEngine }));
  } catch (e) { setManual('t-audio', 'bad', String(e)); }
};
$('b-audio2').onclick = async () => { try { await audioInit(); await actx.resume(); for (let i = 0; i < 5; i++) strike(i * 0.16, 0.45 + Math.random() * 0.1); } catch (e) { setManual('t-audio', 'bad', String(e)); } };

$('b-vib').onclick = () => {
  if (!nav.vibrate) return setManual('t-vib', 'bad', 'Vibration API 없음 (iPhone, 데스크톱에서는 정상)');
  const r = nav.vibrate([12, 30, 18, 30, 26]);
  setManual('t-vib', 'info', { returned: r });
  ask('t-vib', () => setManual('t-vib', 'ok', { felt: true, returned: r }), () => setManual('t-vib', 'bad', { felt: false, returned: r }));
};
$('ios-sw').addEventListener('change', () => {
  setManual('t-ios', 'info', 'switch toggled');
  ask('t-ios', () => setManual('t-ios', 'ok', { felt: true }), () => setManual('t-ios', 'bad', { felt: false }));
});
$('b-lock').onclick = async () => {
  try {
    await canvasRef.el.requestPointerLock();
    setTimeout(() => setManual('t-lock', document.pointerLockElement === canvasRef.el ? 'ok' : 'bad', { locked: document.pointerLockElement === canvasRef.el }), 300);
  } catch (e) { setManual('t-lock', 'bad', String(e.name || e)); }
};
$('b-fs').onclick = async () => {
  try {
    if (document.fullscreenElement) { await document.exitFullscreen(); return; }
    await $('vp').requestFullscreen();
    setManual('t-fs', document.fullscreenElement ? 'ok' : 'bad', { fullscreen: !!document.fullscreenElement });
  } catch (e) { setManual('t-fs', 'bad', String(e.name || e)); }
};
$('b-tilt').onclick = async () => {
  try {
    if (typeof DeviceOrientationEvent?.requestPermission === 'function') {
      const p = await DeviceOrientationEvent.requestPermission();
      if (p !== 'granted') return setManual('t-tilt', 'bad', { permission: p });
    }
    let got = false;
    const on = (e) => {
      if (e.beta == null) return;
      if (!got) { got = true; setManual('t-tilt', 'ok', { beta: Math.round(e.beta), gamma: Math.round(e.gamma) }); }
      const key = scene.children.find((c) => c.isDirectionalLight);
      if (key) key.position.set(Math.sin(e.gamma * Math.PI / 180) * 0.7, 0.6, Math.cos(e.beta * Math.PI / 180) * 0.6);
    };
    addEventListener('deviceorientation', on);
    setTimeout(() => { if (!got) setManual('t-tilt', 'bad', '3초 동안 센서 이벤트 없음 (데스크톱에서는 정상)'); }, 3000);
  } catch (e) { setManual('t-tilt', 'bad', String(e.name || e)); }
};
let memoTimer = null;
$('memo').addEventListener('input', () => { clearTimeout(memoTimer); memoTimer = setTimeout(() => { results.memo = $('memo').value; queueSave(); }, 1200); });
