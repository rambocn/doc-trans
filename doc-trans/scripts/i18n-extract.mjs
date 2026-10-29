#!/usr/bin/env node
/**
 * i18n 提取与体检脚本（2026-10-28，界面翻译插件 P0）。
 *
 * 三件事：
 * 1. 扫描 `t('key', '源文')` 调用，产出「key → 源文」清单（导入运营后台用）；
 * 2. 体检：key 重复但源文不一致（同一个 key 两种说法，必然是复制粘贴出错）、
 *    key 格式非法（必须 `[a-z0-9_.]`）、缺少源文（空字符串）；
 * 3. 统计仍然硬编码的中文行（未走 `t()`），给出文件维度 Top N，作为分批改造的派单依据。
 *
 * 用法：
 *   node scripts/i18n-extract.mjs                      # 只打印体检报告
 *   node scripts/i18n-extract.mjs --json out.json      # 落 key→源文 清单
 *   node scripts/i18n-extract.mjs --ts baseline/zh-CN.ts  # 生成前端内置基线模块
 *   node scripts/i18n-extract.mjs --strict             # 有冲突/非法 key 时退出码 1（CI 用）
 *
 * 约定（与方案 §3.1 一致）：key 必须是静态字面量，禁止字符串拼接；
 * `web.menu.*` / `web.dict.*` 是运行期拼接的覆盖类 key，**不在**本脚本范围内。
 */

import { existsSync, readdirSync, readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * 定位宿主项目根（含 `apps/web/src` 的那一层）。
 * 本文件是项目 `scripts/` 的同步副本，技能包里层级不同，因此三级探测：
 * 环境变量 I18N_PROJECT_ROOT → 自身向上 → 当前目录向上。
 * 在原位运行时命中的就是原来的 `..`，行为不变。
 */
function resolveProjectRoot() {
  const candidates = [];
  const explicit = process.env.I18N_PROJECT_ROOT;
  if (explicit) {
    candidates.push(resolve(explicit));
  }
  let dir = dirname(fileURLToPath(import.meta.url));
  for (let i = 0; i < 6; i += 1) {
    candidates.push(dir);
    dir = resolve(dir, '..');
  }
  dir = process.cwd();
  for (let i = 0; i < 4; i += 1) {
    candidates.push(dir);
    dir = resolve(dir, '..');
  }
  for (const base of candidates) {
    if (existsSync(join(base, 'apps', 'web', 'src'))) {
      return base;
    }
  }
  return resolve(dirname(fileURLToPath(import.meta.url)), '..');
}

const ROOT = resolveProjectRoot();
const SCAN_DIRS = ['apps/web/src', 'apps/ops/src', 'apps/shared/src'];
const EXTENSIONS = new Set(['.ts', '.tsx']);
const SKIP_DIRS = new Set(['node_modules', 'dist']);

/** 覆盖类 key 前缀：运行期由 code 拼出来，源码里没有字面量。 */
const OVERLAY_PREFIXES = ['web.menu.', 'web.dict.'];

/** 已走字典的行：`t('key',` / `translate('key',`，用于剔除硬编码统计。 */
const I18N_CALL = /\b(?:t|translate)\(\s*(['"])[A-Za-z0-9_.]+\1\s*,/;

const KEY_PATTERN = /^[a-z0-9_]+(\.[a-z0-9_]+)+$/;
const CJK = /[\u4e00-\u9fa5]/;

// t( 'key' , '源文' ...)  /  t("key", "源文")  /  translate('key', '源文')
// 业务组件里常把 `t` 具名为 `translate`（避免与局部变量撞名），两者都要提取
const CALL_PATTERN =
  /\b(?:t|translate)\(\s*(['"])([A-Za-z0-9_.]+)\1\s*,\s*(?:'((?:\\.|[^'\\])*)'|"((?:\\.|[^"\\])*)"|`((?:\\.|[^`\\])*)`)/g;

function walk(dir, out) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (!SKIP_DIRS.has(entry.name)) {
        walk(join(dir, entry.name), out);
      }
      continue;
    }
    const dot = entry.name.lastIndexOf('.');
    if (dot > 0 && EXTENSIONS.has(entry.name.slice(dot))) {
      out.push(join(dir, entry.name));
    }
  }
}

/** 去掉行注释与块注释内容，避免注释里的 `t('a','b')` 被误统计。 */
function stripComments(source) {
  return source
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .split('\n')
    .map((line) => {
      const index = line.indexOf('//');
      if (index < 0) {
        return line;
      }
      // 粗略判断：`//` 前面的引号数为偶数才认为进入注释（避免砍掉 URL 里的 //）
      const before = line.slice(0, index);
      const quotes = (before.match(/'|"|`/g) || []).length;
      return quotes % 2 === 0 ? before : line;
    })
    .join('\n');
}

function main() {
  const args = process.argv.slice(2);
  const flag = (name) => {
    const index = args.indexOf(name);
    return index >= 0 ? args[index + 1] : undefined;
  };
  const strict = args.includes('--strict');
  const jsonOut = flag('--json');
  const tsOut = flag('--ts');
  const hardcodedOut = flag('--hardcoded');

  const files = [];
  const missingDirs = SCAN_DIRS.filter((dir) => !existsSync(join(ROOT, dir)));
  for (const dir of SCAN_DIRS) {
    walk(join(ROOT, dir), files);
  }
  if (files.length === 0) {
    process.stdout.write(
      `\n未扫描到任何文件：项目根判定为 ${ROOT}\n` +
        `可用 I18N_PROJECT_ROOT=<项目根> 指定，` +
        `或确认目录存在：${missingDirs.join(', ') || '（目录均在，但无 .ts/.tsx）'}\n`,
    );
    process.exit(2);
  }

  /** @type {Map<string, {text: string, files: Set<string>}>} */
  const entries = new Map();
  const invalidKeys = [];
  const emptyText = [];
  let callCount = 0;

  /** 文件 → 硬编码中文行数 */
  const hardcoded = new Map();

  for (const file of files) {
    let source;
    try {
      source = readFileSync(file, 'utf8');
    } catch {
      continue;
    }
    const cleaned = stripComments(source);
    const rel = relative(ROOT, file).replace(/\\/g, '/');

    CALL_PATTERN.lastIndex = 0;
    let match = CALL_PATTERN.exec(cleaned);
    while (match !== null) {
      callCount += 1;
      const key = match[2];
      const text = match[3] ?? match[4] ?? match[5] ?? '';
      if (!KEY_PATTERN.test(key)) {
        invalidKeys.push({ file: rel, key });
      } else if (text.trim() === '') {
        emptyText.push({ file: rel, key });
      } else {
        const existing = entries.get(key);
        if (existing === undefined) {
          entries.set(key, { text, files: new Set([rel]) });
        } else {
          existing.files.add(rel);
          if (existing.text !== text) {
            // 同一个 key 两种源文：以先出现的为准，记冲突
            invalidKeys.push({ file: rel, key, reason: `源文冲突：${existing.text} / ${text}` });
          }
        }
      }
      match = CALL_PATTERN.exec(cleaned);
    }

    // 硬编码中文体检：跳过注释行、导入行、纯类型行
    for (const line of cleaned.split('\n')) {
      const trimmed = line.trim();
      if (trimmed === '' || trimmed.startsWith('import ') || trimmed.startsWith('export type')) {
        continue;
      }
      if (!CJK.test(trimmed)) {
        continue;
      }
      // 已 key 化的行不算硬编码。原来只判 `t(` —— `translate(` 这个常见具名写法
      // 不含 "t(" 子串，导致翻译过的行被误统计成硬编码，批次进度看不出来。
      if (I18N_CALL.test(trimmed) || trimmed.startsWith('*') || trimmed.startsWith('/*')) {
        continue;
      }
      hardcoded.set(rel, (hardcoded.get(rel) || 0) + 1);
    }
  }

  const sortedKeys = [...entries.keys()].sort();
  const hardcodedTotal = [...hardcoded.values()].reduce((sum, n) => sum + n, 0);
  const topHardcoded = [...hardcoded.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12);

  process.stdout.write(`\n=== i18n 体检 ${new Date().toISOString().slice(0, 19)} ===\n`);
  process.stdout.write(`扫描文件        ${files.length}\n`);
  process.stdout.write(`t() 调用点      ${callCount}\n`);
  process.stdout.write(`唯一 key        ${sortedKeys.length}\n`);
  process.stdout.write(`非法/冲突 key   ${invalidKeys.length}\n`);
  process.stdout.write(`空源文          ${emptyText.length}\n`);
  process.stdout.write(`硬编码中文行    ${hardcodedTotal}（涉及 ${hardcoded.size} 个文件）\n`);

  if (invalidKeys.length > 0) {
    process.stdout.write('\n-- 非法 / 冲突 key --\n');
    for (const item of invalidKeys.slice(0, 20)) {
      process.stdout.write(`  ${item.file}  ${item.key}${item.reason ? `  ${item.reason}` : ''}\n`);
    }
    if (invalidKeys.length > 20) {
      process.stdout.write(`  … 另有 ${invalidKeys.length - 20} 条\n`);
    }
  }
  if (topHardcoded.length > 0) {
    process.stdout.write('\n-- 硬编码中文最多的文件（分批改造派单用）--\n');
    for (const [file, count] of topHardcoded) {
      process.stdout.write(`  ${String(count).padStart(4)}  ${file}\n`);
    }
  }

  if (hardcodedOut !== undefined) {
    // 派单用：按文件给出「还没走 t() 的中文行数」，按数量降序
    const report = [...hardcoded.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([file, count]) => ({ file, lines: count }));
    mkdirSync(dirname(resolve(hardcodedOut)), { recursive: true });
    writeFileSync(resolve(hardcodedOut), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
    process.stdout.write(`\n已写出硬编码清单 ${report.length} 个文件 → ${hardcodedOut}\n`);
  }

  if (jsonOut !== undefined) {
    const payload = {};
    for (const key of sortedKeys) {
      payload[key] = entries.get(key).text;
    }
    mkdirSync(dirname(resolve(jsonOut)), { recursive: true });
    writeFileSync(resolve(jsonOut), `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
    process.stdout.write(`\n已写出 ${sortedKeys.length} 条 → ${jsonOut}\n`);
  }

  if (tsOut !== undefined) {
    const lines = [
      '/**',
      ' * 界面翻译插件 · 内置基线包（自动生成，勿手改）。',
      ' *',
      ` * 生成：node scripts/i18n-extract.mjs --ts ${relative(ROOT, resolve(tsOut)).replace(/\\/g, '/')}`,
      ` * 生成时间：${new Date().toISOString().slice(0, 10)} / 条目数：${sortedKeys.length}`,
      ' */',
      '',
      'const baseline: Record<string, string> = {',
      ...sortedKeys.map((key) => `  ${JSON.stringify(key)}: ${JSON.stringify(entries.get(key).text)},`),
      '};',
      '',
      'export default baseline;',
      '',
    ];
    mkdirSync(dirname(resolve(tsOut)), { recursive: true });
    writeFileSync(resolve(tsOut), lines.join('\n'), 'utf8');
    process.stdout.write(`已写出基线模块 → ${tsOut}\n`);
  }

  const overlay = [...entries.keys()].filter((key) => OVERLAY_PREFIXES.some((p) => key.startsWith(p)));
  if (overlay.length > 0) {
    process.stdout.write(`\n注意：检测到 ${overlay.length} 个覆盖类 key 被静态书写，确认是否应改为动态拼接。\n`);
  }

  if (strict && invalidKeys.length > 0) {
    process.stdout.write('\n--strict：存在非法 / 冲突 key，退出码 1\n');
    process.exit(1);
  }
}

main();
