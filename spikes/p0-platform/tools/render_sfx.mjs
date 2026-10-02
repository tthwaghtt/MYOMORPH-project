import { writeFileSync, mkdirSync } from 'node:fs';
import * as S from '../src/sfx.js';
const sr = 48000; mkdirSync('build_tmp/sfx', { recursive: true });
const wav = (name, x) => {
  const b = Buffer.alloc(44 + x.length * 2);
  b.write('RIFF', 0); b.writeUInt32LE(36 + x.length * 2, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22);
  b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(x.length * 2, 40);
  x.forEach((v, i) => b.writeInt16LE(Math.max(-32767, Math.min(32767, Math.round(v * 32767))), 44 + i * 2));
  writeFileSync(`build_tmp/sfx/${name}.wav`, b);
};
const P = { a: 0.16, b: 0.10, h: 0.001, massG: 70 };
wav('lock_v2', S.renderLockV2(sr, P, 12)); wav('lock_v3', S.renderLock(sr, P, 12));
wav('nut_v2', S.renderNutrunnerV2(sr, {}, 3)); wav('nut_v3', S.renderNutrunner(sr, {}, 3));
wav('hyd_v2', S.renderHydraulicV2(sr, {}, 5)); wav('hyd_v3', S.renderHydraulic(sr, {}, 5)); wav('hyd_v3_novalve', S.renderHydraulic(sr, { valve: false }, 5));
console.log('ok');
