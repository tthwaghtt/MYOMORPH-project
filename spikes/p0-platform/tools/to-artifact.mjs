// Vite's dist/index.html is a full document; the Artifact publisher wraps the page in its own skeleton.
// Strip doctype/html/head/body so the published page is content-only (title, links, styles, scripts, body markup).
import { readFileSync, writeFileSync } from 'node:fs';
let h = readFileSync('dist/index.html', 'utf8');
h = h.replace(/<!doctype html>/i, '').replace(/<\/?html[^>]*>/gi, '').replace(/<\/?head>/gi, '').replace(/<\/?body>/gi, '')
     .replace(/<meta charset[^>]*>\s*/i, '').replace(/<meta name="viewport"[^>]*>\s*/i, '');
const title = h.match(/<title>[\s\S]*?<\/title>/)[0];
h = title + '\n' + h.replace(title, '');
writeFileSync('dist/index.html', h.trim() + '\n');
console.log('artifact page ready', h.length, 'chars');
