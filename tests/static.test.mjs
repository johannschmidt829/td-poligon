// Статические проверки: ноль зависимостей, ноль браузера.
// Ловят ровно то, что ломается при правке генератора или атласа.
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const index = path.join(root, 'index.html');
const md5 = (b) => createHash('md5').update(b).digest('hex');

let failed = 0;
function check(name, fn) {
  try {
    const detail = fn();
    console.log(`ok   ${name}${detail ? ' — ' + detail : ''}`);
  } catch (e) {
    failed++;
    console.log(`FAIL ${name} — ${e.message}`);
  }
}
const assert = (cond, msg) => { if (!cond) throw new Error(msg); };

const html = fs.readFileSync(index, 'utf8');

check('index.html существует и не пуст', () => {
  const n = fs.statSync(index).size;
  assert(n > 50_000 && n < 4_000_000, `подозрительный размер: ${n}`);
  return `${n} байт`;
});

check('JS парсится', () => {
  const m = html.match(/<script>([\s\S]*)<\/script>/);
  assert(m, 'нет <script> блока');
  new vm.Script(m[1]);
  return `${m[1].length} символов`;
});

check('нет внешних сетевых ссылок (игра обязана работать офлайн)', () => {
  const bad = [
    [/(?:src|href)\s*=\s*["']https?:/i, 'атрибут src/href на http'],
    [/url\(\s*["']?https?:/i, 'url() на http'],
    [/@import\s+["']?https?:/i, '@import на http'],
    [/fetch\(\s*["']https?:/i, 'fetch на http'],
  ].filter(([re]) => re.test(html)).map(([, why]) => why);
  assert(bad.length === 0, bad.join(', '));
  return 'все ассеты внутри файла';
});

check('атлас вшит base64', () => {
  const m = html.match(/data:image\/png;base64,([A-Za-z0-9+/=]+)/);
  assert(m, 'нет base64-картинки');
  assert(m[1].length > 20_000, `слишком короткий base64: ${m[1].length}`);
  return `${Math.round(m[1].length / 1024)} КБ base64`;
});

check('игровые данные на месте', () => {
  const towers = (html.match(/const TOWERS=\[[\s\S]*?\];/) || [''])[0];
  assert((towers.match(/\{name:"/g) || []).length === 5, 'ожидалось 5 башен');
  const polys = (html.match(/const POLYGONS=\[[\s\S]*?\n\];/) || [''])[0];
  assert((polys.match(/\{id:"/g) || []).length === 5, 'ожидалось 5 полигонов');
  assert(/const BASE_HP=44, BASE_SPD=36, RANGE=240, LIVES0=20;/.test(html), 'константы BASE_* изменились');
  return '5 башен, 5 полигонов, LIVES0=20';
});

check('TUNE в разумных пределах', () => {
  const m = html.match(/const TUNE=\{([^}]*)\}/);
  assert(m, 'нет TUNE');
  const o = Object.fromEntries(
    m[1].split(',').map((kv) => kv.split(':').map((s) => s.trim())).filter((p) => p.length === 2)
  );
  const num = (k) => { const v = Number(o[k]); assert(Number.isFinite(v), `TUNE.${k} не число`); return v; };
  const incExp = num('incExp'), waveBase = num('waveBase'), waveK = num('waveK'), repairCost = num('repairCost');
  assert(incExp >= 0 && incExp <= 1, `incExp вне [0,1]: ${incExp}`);
  assert(waveBase > 0 && waveBase < 5000, `waveBase вне разумного: ${waveBase}`);
  assert(waveK > 0 && waveK < 3, `waveK вне разумного: ${waveK}`);
  assert(repairCost > 0, `repairCost <= 0: ${repairCost}`);
  return `incExp=${incExp} waveBase=${waveBase} waveK=${waveK} repair=${repairCost}`;
});

check('сборка воспроизводима: генератор даёт байт в байт index.html', () => {
  const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'tdci-')), 'out.html');
  execFileSync('python3', [path.join(root, 'src', 'build_full.py'), tmp], { stdio: 'pipe' });
  const a = md5(fs.readFileSync(index));
  const b = md5(fs.readFileSync(tmp));
  assert(a === b, `md5 не совпал: index=${a} build=${b} — index.html не пересобран из src/`);
  return a;
});

console.log(failed ? `\n${failed} проверок провалено` : '\nвсе статические проверки пройдены');
process.exit(failed ? 1 : 0);
