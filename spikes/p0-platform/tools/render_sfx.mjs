// Offline render of src/sfx.js to WAV (48 kHz, 16-bit) for spectral inspection.
import { writeFileSync, mkdirSync } from 'node:fs';
import { renderLock, renderNutrunner, renderHydraulic, renderLockV1 } from '../src/sfx.js';
const sr = 48000; mkdirSync('build_tmp/sfx', { recursive: true });
const wav = (name, x) => {
  const b = Buffer.alloc(44 + x.length * 2);
  b.write('RIFF', 0); b.writeUInt32LE(36 + x.length * 2, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22);
  b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(x.length * 2, 40);
  x.forEach((v, i) => b.writeInt16LE(Math.max(-32767, Math.min(32767, Math.round(v * 32767))), 44 + i * 2));
  writeFileSync(`build_tmp/sfx/${name}.wav`, b);
};
const t = performance.now();
wav('lock_v1_old', renderLockV1(sr));
wav('lock_small_20g', renderLock(sr, { a: 0.05, b: 0.03, h: 0.0008, massG: 20 }, 11));
wav('lock_panel_70g', renderLock(sr, { a: 0.16, b: 0.10, h: 0.001, massG: 70 }, 12));
wav('lock_pec_600g', renderLock(sr, { a: 0.24, b: 0.18, h: 0.0012, massG: 600 }, 13));
wav('nutrunner', renderNutrunner(sr));
wav('hydraulic', renderHydraulic(sr));
console.log('rendered in', Math.round(performance.now() - t), 'ms');
