// E2E смоук: игра реально запускается, принимает ввод и убивает врагов.
// Проверяет цикл, а не пиксели: меню → арена → башня → волна → урон.
import path from 'node:path';
import { serve, launchBrowser, root, assert } from './lib/harness.mjs';

const htmlPath = path.join(root, 'index.html');
const { server, url } = await serve(htmlPath);
const browser = await launchBrowser();
let failed = 0;

async function run(name, fn) {
  try {
    const detail = await fn();
    console.log(`ok   ${name}${detail ? ' — ' + detail : ''}`);
  } catch (e) {
    failed++;
    console.log(`FAIL ${name} — ${e.message}`);
  }
}

try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });

  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(600);

  // 1. Игра поднялась в меню, канвас отрисован.
  await run('страница грузится, меню на экране', async () => {
    const st = await page.evaluate(() => ({
      screen: S.screen,
      canvas: !!document.getElementById('c'),
      w: cv.width, h: cv.height,
    }));
    assert(st.canvas, 'нет канваса');
    assert(st.screen === 'menu', `ожидалось меню, получено ${st.screen}`);
    assert(st.w === 900 && st.h === 500, `размер канваса ${st.w}x${st.h}`);
    return `экран=${st.screen} канвас=${st.w}x${st.h}`;
  });

  // 2. Вход на арену через кнопку — как это делает человек.
  await run('кнопка «Играть» вводит на арену', async () => {
    await page.click('#playmenu');
    await page.waitForTimeout(300);
    const st = await page.evaluate(() => ({
      screen: S.screen,
      name: document.getElementById('poly').textContent,
      gold: S.gold, lives: S.lives, slots: POLYGONS[S.pi].slots.length,
    }));
    assert(st.screen === 'game', `экран ${st.screen}`);
    assert(st.gold > 0, `золото ${st.gold}`);
    assert(st.lives === 20, `жизни ${st.lives}`);
    assert(st.slots === 6, `слотов ${st.slots}`);
    return `${st.name}: ${st.gold} золота, ${st.lives} жизней, ${st.slots} слотов`;
  });

  // 3. Постройка башни кликом по площадке.
  await run('клик по площадке строит башню', async () => {
    const info = await page.evaluate(() => {
      const s = POLYGONS[S.pi].slots[0];
      const r = cv.getBoundingClientRect();
      return { sx: s[0], sy: s[1], rx: r.left, ry: r.top, kx: r.width / 900, ky: r.height / 500, gold: S.gold };
    });
    await page.mouse.click(info.rx + info.sx * info.kx, info.ry + info.sy * info.ky);
    await page.waitForTimeout(250);
    const st = await page.evaluate(() => ({ towers: S.towers.length, gold: S.gold }));
    assert(st.towers === 1, `башен ${st.towers}`);
    assert(st.gold < info.gold, 'золото не списалось');
    return `1 башня, золото ${info.gold} → ${st.gold}`;
  });

  // 4. Волна запускается и враги идут.
  await run('волна запускается, враги появляются', async () => {
    await page.click('#nextwave');
    await page.waitForTimeout(1200);
    const st = await page.evaluate(() => ({
      active: S.waveActive, wave: S.wave,
      enemies: S.enemies.length, queued: S.spawnQueue.length,
    }));
    assert(st.wave === 1, `волна ${st.wave}`);
    assert(st.active || st.enemies > 0 || st.queued > 0, 'волна не пошла');
    return `волна ${st.wave}, врагов ${st.enemies}, в очереди ${st.queued}`;
  });

  // 5. Башня наносит урон: враги умирают, золото приходит.
  await run('башня убивает врагов, доход идёт', async () => {
    const st = await page.evaluate(() => {
      const gold0 = S.gold;
      for (let i = 0; i < 600 && (S.waveActive || S.enemies.length || S.spawnQueue.length); i++) {
        update(0.05);
      }
      return { gold0, gold: S.gold, alive: S.enemies.length, wave: S.wave };
    });
    assert(st.gold > st.gold0, `доход не вырос: ${st.gold0} → ${st.gold}`);
    return `золото ${st.gold0} → ${st.gold}, осталось врагов ${st.alive}`;
  });

  // 6. Апгрейд по клику на башню.
  await run('клик по башне поднимает уровень', async () => {
    const st = await page.evaluate(async () => {
      S.gold = 5000;
      const t = S.towers[0];
      const r = cv.getBoundingClientRect();
      const before = t.level;
      cv.dispatchEvent(new MouseEvent('click', {
        clientX: r.left + t.x * (r.width / 900),
        clientY: r.top + t.y * (r.height / 500),
        bubbles: true,
      }));
      await new Promise((res) => setTimeout(res, 150));
      return { before, after: S.towers[0].level };
    });
    assert(st.after > st.before, `уровень не вырос: ${st.before} → ${st.after}`);
    return `L${st.before} → L${st.after}`;
  });

  // 7. Все пять арен открываются без падения.
  await run('все 5 полигонов инициализируются', async () => {
    const info = await page.evaluate(() => {
      const out = [];
      for (let i = 0; i < 5; i++) {
        setPolygon(i);
        out.push({ name: POLYGONS[i].name, slots: POLYGONS[i].slots.length, gold: S.gold });
      }
      return out;
    });
    assert(info.length === 5, `полигонов ${info.length}`);
    assert(info.every((p) => p.slots === 6), 'у арены не 6 слотов');
    assert(info.every((p) => p.gold > 0), 'арена без стартового золота');
    return info.map((p) => p.name).join(' · ');
  });

  // 8. Ни одной ошибки в консоли за весь прогон.
  await run('консоль без ошибок', async () => {
    assert(errors.length === 0, errors.slice(0, 3).join(' | '));
    return 'чисто';
  });

  await page.close();
} finally {
  await browser.close();
  server.close();
}

console.log(failed ? `\n${failed} проверок провалено` : '\nвсе e2e проверки пройдены');
process.exit(failed ? 1 : 0);
