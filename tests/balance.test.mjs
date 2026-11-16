// Регрессия баланса: жадный бот проходит все 5 арен по 5 волн.
// Ловит то, что ломается при правке TUNE, волн или цен — то есть смысл игры.
import path from 'node:path';
import { serve, launchBrowser, root, assert, SEED } from './lib/harness.mjs';

// Скорость врагов в игре зависит от Math.random, поэтому баланс не единое число,
// а коридор. Замер по восьми зёрнам после переделки путей (ломаные 0/30/45/90,
// скругления, серпантин) дал: Трава 18–19, Лес 16–17, Пустыня 13–14,
// Острова 9–13, Вулканы 4–11. В CI ГПСЧ зафиксирован, поэтому прогон
// детерминирован и даёт ровно EXPECTED_SEEDED. Диапазоны ловят сдвиг баланса.
const EXPECTED_SEEDED = [18, 17, 14, 10, 6];
const RANGE = [[18, 19], [16, 17], [13, 14], [9, 13], [4, 11]];
const TOLERANCE = 1;

const { server, url } = await serve(path.join(root, 'index.html'));
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
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'load' });
  // Глушим игровой цикл: баланс должен зависеть только от update(),
  // иначе rAF подмешивает реальное время и прогон плавает между машинами.
  await page.evaluate(() => { window.requestAnimationFrame = () => 0; });
  await page.addScriptTag({ content: SEED });
  await page.waitForTimeout(300);

  const result = await page.evaluate(() => {
    const out = [];
    for (let pi = 0; pi < 5; pi++) {
      setPolygon(pi);
      S.screen = 'game';
      const slots = POLYGONS[pi].slots.slice();
      let wavesDone = 0;
      for (let w = 0; w < 5; w++) {
        // Жадная закупка: самый дорогой доступный тип на каждый свободный слот.
        for (const s of slots) {
          if (S.towers.some((t) => t.sx === s[0] && t.sy === s[1])) continue;
          for (let ti = TOWERS.length - 1; ti >= 0; ti--) {
            if (S.gold >= TOWERS[ti].cost) {
              const d = TOWERS[ti];
              S.gold -= d.cost;
              S.towers.push({
                sx: s[0], sy: s[1], x: s[0], y: s[1], ti,
                range: RANGE, dmg: d.dmg, rate: d.rate, splash: d.splash, burn: d.burn,
                timer: 0, level: 1, angle: 0, spr: d.spr, burnTick: 0,
              });
              break;
            }
          }
        }
        // Остаток кассы — в апгрейды до L4.
        for (const tw of S.towers) {
          while (tw.level < 4) {
            const c = TOWERS[tw.ti].up[tw.level - 1];
            if (S.gold < c) break;
            S.gold -= c;
            tw.level++;
          }
        }
        startWave();
        let cleared = false;
        for (let i = 0; i < 9000; i++) {
          update(0.05);
          if (!S.waveActive && S.spawnQueue.length === 0 && S.enemies.length === 0) { cleared = true; break; }
          if (S.lives <= 0) break;
        }
        if (cleared) wavesDone++;
        S.betweenTimer = 0;
        if (S.lives <= 0) break;
      }
      out.push({ name: POLYGONS[pi].name, lives: S.lives, wavesDone, gold: Math.round(S.gold) });
    }
    return out;
  });

  await run('все 5 арен проходят 5 волн', async () => {
    const bad = result.filter((r) => r.wavesDone !== 5);
    assert(bad.length === 0, bad.map((r) => `${r.name}: ${r.wavesDone}/5`).join(', '));
    return result.map((r) => `${r.name} ${r.wavesDone}/5`).join(' · ');
  });

  await run('сложность нарастает монотонно', async () => {
    for (let i = 1; i < result.length; i++) {
      assert(
        result[i].lives <= result[i - 1].lives + TOLERANCE,
        `${result[i].name} (${result[i].lives}) легче ${result[i - 1].name} (${result[i - 1].lives})`
      );
    }
    return result.map((r) => r.lives).join(' · ');
  });

  await run('ни одна арена не на грани смерти', async () => {
    const thin = result.filter((r) => r.lives <= 2);
    assert(thin.length === 0, thin.map((r) => `${r.name}: ${r.lives}`).join(', '));
    return `минимум ${Math.min(...result.map((r) => r.lives))} жизней`;
  });

  await run('жизни внутри допустимого коридора', async () => {
    const got = result.map((r) => r.lives);
    const bad = got.map((v, i) => (v < RANGE[i][0] || v > RANGE[i][1]
      ? `${result[i].name} ${v} вне ${RANGE[i][0]}–${RANGE[i][1]}` : null)).filter(Boolean);
    assert(bad.length === 0, bad.join('; ') + '. Если баланс изменён намеренно, обновите RANGE в tests/balance.test.mjs.');
    return got.join(' · ');
  });

  await run('детерминированный прогон совпадает с эталоном', async () => {
    const got = result.map((r) => r.lives);
    const drift = got.map((v, i) => Math.abs(v - EXPECTED_SEEDED[i]));
    const worst = Math.max(...drift);
    assert(
      worst <= TOLERANCE,
      `жизни ${got.join('/')} против эталона ${EXPECTED_SEEDED.join('/')} — сдвиг ${worst}. `
      + 'Если баланс изменён намеренно, обновите EXPECTED_SEEDED в tests/balance.test.mjs.'
    );
    return `${got.join(' · ')} (эталон ${EXPECTED_SEEDED.join(' · ')})`;
  });

  await run('золото не упирается в потолок', async () => {
    // Касса в конце не должна течь мимо игрока: иначе экономика не работает.
    const rich = result.filter((r) => r.gold > 2500);
    assert(rich.length === 0, rich.map((r) => `${r.name}: ${r.gold}`).join(', '));
    return `максимум ${Math.max(...result.map((r) => r.gold))} золота на финише`;
  });

  await page.close();
} finally {
  await browser.close();
  server.close();
}

console.log(failed ? `\n${failed} проверок провалено` : '\nрегрессия баланса пройдена');
process.exit(failed ? 1 : 0);
