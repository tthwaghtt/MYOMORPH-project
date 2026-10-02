// P0 asset pipeline: Blender GLB -> + AO texture (KTX2 UASTC via basisu CLI) -> meshopt -> public/models
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, KHRTextureBasisu } from '@gltf-transform/extensions';
import { dedup, prune, weld, quantize, meshopt } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { execFileSync } from 'node:child_process';
import { readFileSync, statSync, mkdirSync } from 'node:fs';

const BASISU = 'node_modules/basisu/bin/linux/x64_sse/basisu';
mkdirSync('public/models', { recursive: true });
mkdirSync('build_tmp', { recursive: true });
await MeshoptEncoder.ready; await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });

function ktx2(png, mode) {
  const out = `build_tmp/${png.split('/').pop().replace('.png', '')}_${mode}.ktx2`;
  const args = mode === 'uastc' ? ['-ktx2', '-uastc', '-uastc_level', '2', '-uastc_rdo_l', '1.0', '-linear', '-mipmap', png, '-output_file', out]
                                : ['-ktx2', '-comp_level', '2', '-q', '255', '-mipmap', png, '-output_file', out];
  execFileSync(BASISU, args, { stdio: 'pipe' });
  return out;
}

const t0 = Date.now();
const doc = await io.read('assets_src/test_panel.glb');
const root = doc.getRoot();
const uastc = ktx2('assets_src/panel_ao.png', 'uastc');
const etc1s = ktx2('assets_src/panel_ao.png', 'etc1s');
doc.createExtension(KHRTextureBasisu).setRequired(true);
const tex = doc.createTexture('IM-MM1-TEST-PANEL-ao').setMimeType('image/ktx2').setImage(readFileSync(uastc)).setURI('panel_ao.ktx2');
const ti = root.listMaterials().find(m => m.getName() === 'MA-ti64_beadblast');
ti.setOcclusionTexture(tex);
await doc.transform(dedup(), prune(), weld(), quantize(), meshopt({ encoder: MeshoptEncoder, level: 'medium' }));
await io.write('public/models/test_panel.glb', doc);
const sz = f => statSync(f).size;
console.log(JSON.stringify({
  ms: Date.now() - t0,
  blender_glb: sz('assets_src/test_panel.glb'),
  ao_png: sz('assets_src/panel_ao.png'), ao_uastc_ktx2: sz(uastc), ao_etc1s_ktx2: sz(etc1s),
  final_glb_meshopt_ktx2: sz('public/models/test_panel.glb'),
  extensions: root.listExtensionsUsed().map(e => e.extensionName),
}, null, 1));
