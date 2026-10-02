import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { extname, join } from 'node:path';
const types = { '.html': 'text/html', '.js': 'text/javascript', '.wasm': 'application/wasm', '.glb': 'model/gltf-binary', '.bin': 'application/octet-stream' };
const srv = createServer((req, res) => {
  const p = join('dist', decodeURIComponent(req.url.split('?')[0]) === '/' ? 'index.html' : decodeURIComponent(req.url.split('?')[0]));
  if (!existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': (types[extname(p)] || 'application/octet-stream') + (extname(p) === '.html' ? '; charset=utf-8' : ''), 'content-security-policy': "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com https://fonts.gstatic.com data:; connect-src 'self'; worker-src 'self' blob:" }); res.end(readFileSync(p));
}).listen(5178);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--enable-unsafe-webgpu', '--enable-features=Vulkan', '--use-vulkan=swiftshader', '--use-webgpu-adapter=swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
const logs = []; page.on('console', (m) => logs.push(`${m.type()}: ${m.text()}`)); page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
await page.goto('http://localhost:5178/');
await page.waitForTimeout(25000);
await page.screenshot({ path: 'build_tmp/local.png', fullPage: false });
const rows = await page.$$eval('#auto tr', (trs) => trs.map((t) => [...t.children].map((c) => c.textContent)));
console.log(JSON.stringify(rows, null, 1)); console.log(logs.slice(0, 15).join('\n'));
await browser.close(); srv.close();
