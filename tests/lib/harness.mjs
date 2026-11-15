// Общая обвязка для браузерных тестов: локальный сервер + запуск Chromium.
// Ищет playwright в нескольких местах, чтобы работать и в CI, и локально.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

export function serve(htmlPath) {
  const body = fs.readFileSync(htmlPath);
  const server = http.createServer((req, res) => {
    if (req.url === '/' || req.url.startsWith('/index.html')) {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(body);
    } else {
      res.writeHead(404).end('not found');
    }
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      resolve({ server, url: `http://127.0.0.1:${port}/` });
    });
  });
}

function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const candidates = [
    root,
    path.join(root, 'tests'),
    process.env.PLAYWRIGHT_MODULE || '',
  ].filter(Boolean);
  for (const base of candidates) {
    for (const name of ['playwright', 'playwright-core']) {
      try {
        const mod = createRequire(path.join(base, 'noop.js'))(name);
        if (mod && mod.chromium) return mod;
      } catch { /* пробуем следующего кандидата */ }
    }
  }
  try { return require('playwright'); } catch { /* ниже */ }
  throw new Error('нет playwright/playwright-core — выполните npm i (или задайте PLAYWRIGHT_MODULE)');
}

export function launchBrowser() {
  const pw = loadPlaywright();
  const opts = {};
  let exe = '';
  try { exe = pw.chromium.executablePath(); } catch { /* нет пути — ищем сами */ }
  if (!exe || !fs.existsSync(exe)) {
    const cache = process.env.PLAYWRIGHT_BROWSERS_PATH
      || path.join(process.env.HOME || '', '.cache', 'ms-playwright');
    const found = fs.existsSync(cache)
      ? fs.readdirSync(cache)
        .filter((d) => d.startsWith('chromium-') && !d.includes('headless'))
        .sort().reverse()
        .map((d) => path.join(cache, d, 'chrome-linux64', 'chrome'))
        .find((p) => fs.existsSync(p))
      : null;
    if (found) opts.executablePath = found;
  }
  return pw.chromium.launch(opts);
}

// Детерминированный ГПСЧ вместо Math.random — иначе баланс «плавает» между прогонами.
export const SEED = `
(() => {
  let s = 0x2f6e2b1;
  Math.random = () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
})();
`;

export function report(name, fn) {
  try {
    const detail = fn();
    console.log(`ok   ${name}${detail ? ' — ' + detail : ''}`);
    return true;
  } catch (e) {
    console.log(`FAIL ${name} — ${e.message}`);
    return false;
  }
}

export const assert = (cond, msg) => { if (!cond) throw new Error(msg); };
