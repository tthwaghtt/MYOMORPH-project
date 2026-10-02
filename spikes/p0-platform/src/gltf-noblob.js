// Artifact viewers block fetch() of blob: URLs (CSP), and GLTFLoader loads textures embedded in a GLB
// through blob: URLs. This plugin decodes embedded images straight from the buffer instead:
// KTX2 via KTX2Loader.parse(ArrayBuffer), PNG/JPEG/WebP via createImageBitmap(Blob) — no URL, no fetch.
import { Texture } from 'three/webgpu';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';

export function noBlobTextures(parser) {
  const orig = parser.loadImageSource.bind(parser);
  parser.loadImageSource = function (sourceIndex, loader) {
    const def = parser.json.images[sourceIndex];
    if (def.bufferView === undefined) return orig(sourceIndex, loader);
    if (parser.sourceCache[sourceIndex] !== undefined) return parser.sourceCache[sourceIndex].then((t) => t.clone());
    const p = parser.getDependency('bufferView', def.bufferView).then((buf) => {
      if (loader instanceof KTX2Loader) {
        return new Promise((resolve, reject) => loader.parse(buf.slice(0), resolve, reject));
      }
      return createImageBitmap(new Blob([buf], { type: def.mimeType }), { imageOrientation: 'flipY', premultiplyAlpha: 'none', colorSpaceConversion: 'none' })
        .then((bmp) => { const t = new Texture(bmp); t.needsUpdate = true; return t; });
    }).then((texture) => {
      texture.userData.mimeType = def.mimeType;
      return texture;
    }).catch((e) => { console.error('noBlobTextures: failed image', sourceIndex, String(e)); throw e; });
    parser.sourceCache[sourceIndex] = p;
    return p;
  };
  return { name: 'MM1_no_blob_textures' };
}
