#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量写入 i18n_seed.json 的公共工具（2026-10-28，B1-b/B1-c 批次共用）。

每行固定 9 列：key + zh-CN + en + zh-Hant + ar + ja + es + vi + th。
写库前强校验：
1. key 格式 `[a-z0-9_.]+`，至少两段；
2. 8 个语种全部非空；
3. 各语种 `{{name}}` 占位符集合与 zh-CN 完全一致（发布门禁会阻断，早发现早改）；
4. 同一个 key 若已在词表里，源文必须一致（防止手滑覆盖已有译文）。

用法：在批次脚本里 `from i18n_batch_util import apply_rows`，传 ROWS 即可。
"""
from __future__ import annotations

import json
import os
import re
from collections import OrderedDict
from pathlib import Path


def _resolve_project_root() -> Path:
    """定位宿主项目根（含 `apps/api/data/i18n_seed.json` 的那一层）。

    本文件是项目 `scripts/` 的同步副本，在技能包里与项目不在同一层级，
    所以按「环境变量 I18N_PROJECT_ROOT → 自身向上 → 当前目录向上」三级探测。
    在原位（项目 scripts/）运行时，命中的就是原来的 parents[1]，行为不变。
    """
    seeds = ('apps', 'api', 'data', 'i18n_seed.json')
    candidates = []
    env = os.environ.get('I18N_PROJECT_ROOT')
    if env:
        candidates.append(Path(env))
    here = Path(__file__).resolve()
    candidates.extend(here.parents[:6])
    candidates.extend(Path.cwd().resolve().parents[:4])
    for base in candidates:
        if base.joinpath(*seeds).is_file():
            return base
    return here.parents[1]


ROOT = _resolve_project_root()
SEED = ROOT / 'apps' / 'api' / 'data' / 'i18n_seed.json'

LOCALES = ['zh-CN', 'en', 'zh-Hant', 'ar', 'ja', 'es', 'vi', 'th']
KEY_RE = re.compile(r'^[a-z0-9_]+(\.[a-z0-9_]+)+$')
PLACEHOLDER_RE = re.compile(r'\{\{\s*([A-Za-z0-9_]+)\s*\}\}')


def apply_rows(rows: list[tuple[str, ...]], batch: str) -> int:
    """把 ROWS 合并进词表并落盘；返回新增条数（已存在的 key 跳过）。"""
    if not SEED.is_file():
        raise SystemExit(f'[i18n-batch] 找不到词表：{SEED}（可设 I18N_PROJECT_ROOT 指向项目根）')
    raw = SEED.read_text(encoding='utf-8')
    eol = '\r\n' if '\r\n' in raw else '\n'
    payload = json.loads(raw, object_pairs_hook=OrderedDict)
    entries: OrderedDict[str, OrderedDict[str, str]] = payload['entries']

    errors: list[str] = []
    added = skipped = 0
    for row in rows:
        if len(row) != len(LOCALES) + 1:
            errors.append(f'列数应为 {len(LOCALES) + 1}，实际 {len(row)}：{row[:1]}')
            continue
        key = row[0]
        if not KEY_RE.match(key):
            errors.append(f'key 格式非法：{key}')
            continue
        values = dict(zip(LOCALES, row[1:], strict=True))
        source = values['zh-CN']
        if any(not str(value).strip() for value in values.values()):
            errors.append(f'存在空译文：{key}')
            continue
        source_placeholders = set(PLACEHOLDER_RE.findall(source))
        for locale, value in values.items():
            if set(PLACEHOLDER_RE.findall(value)) != source_placeholders:
                errors.append(f'占位符不一致：{key} / {locale}')
        if key in entries:
            existing = entries[key]
            if (existing.get('zh-CN') or '') != source:
                errors.append(f'源文冲突：{key} 已有「{existing.get("zh-CN")}」≠「{source}」')
            skipped += 1
            continue
        entries[key] = OrderedDict(values)
        added += 1

    if errors:
        raise SystemExit('\n'.join(f'[i18n-batch] {item}' for item in errors))

    payload['_batch'] = batch
    body = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
    SEED.write_text(body.replace('\n', eol), encoding='utf-8', newline='')
    print(f'[i18n-batch] {batch}：新增 {added}，跳过 {skipped}，词表合计 {len(entries)}')
    return added
