import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { extname, join } from 'node:path';
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.wasm': 'application/wasm' };
const srv = createServer((req, res) => { const u = decodeURIComponent(req.url.split('?')[0]); const p = join('dist', u === '/' ? 'index.html' : u);
  if (!existsSync(p)) { res.writeHead(404); return res.end(); } res.writeHead(200, { 'content-type': types[extname(p)] || 'application/octet-stream', 'content-security-policy': "default-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com data:; connect-src 'self'; worker-src 'self' blob:" }); res.end(readFileSync(p)); }).listen(5179);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--autoplay-policy=no-user-gesture-required'] });
const page = await browser.newPage(); const logs = [];
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') logs.push(m.type() + ': ' + m.text()); }); page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
await page.goto('http://localhost:5179/'); await page.waitForTimeout(6000);
for (const k of ['lock-s', 'lock-m', 'lock-l', 'nut', 'hyd', 'old']) { await page.click(`[data-sfx="${k}"]`); await page.waitForTimeout(400); }
await page.click('[data-rate="good"]'); await page.click('#rebench'); await page.waitForTimeout(500);
console.log(await page.$eval('#t-audio [data-s]', (e) => e.textContent), logs.filter((l) => !/CERT|fonts|GPU stall|404/.test(l)).slice(0, 10));
await browser.close(); srv.close();
