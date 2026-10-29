#!/usr/bin/env python
"""界面翻译插件 · 首批译文灌库脚本（2026-10-28）。

把 `apps/api/data/i18n_seed.json` 里的「key → 各语言译文」写入 `i18n_entries`，
然后调用服务层 `publish()` 生成一个发布版本，客户端即可拉到。

为什么用脚本而不是塞进迁移：
译文是**内容**，会反复变；塞进迁移会让迁移链变成文案变更日志，
且每次改字都要写一个迁移。迁移只负责表结构与语言清单（结构），内容走这里。

用法（项目根目录，PG 已起）：
    .venv/Scripts/python.exe scripts/seed_i18n.py            # 写入并发布
    .venv/Scripts/python.exe scripts/seed_i18n.py --dry-run  # 只看差异不写库
    .venv/Scripts/python.exe scripts/seed_i18n.py --no-publish  # 只写草稿

幂等性：按 (locale, key) upsert，重复执行不会产生重复行；但每次执行都会
**新增一个发布版本**（version 只增不减，这是客户端缓存判等的前提）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _resolve_project_root() -> Path:
    """定位宿主项目根（含 `apps/api/data/i18n_seed.json` 的那一层）。

    本文件是项目 `scripts/` 的同步副本，技能包里层级不同，因此三级探测：
    环境变量 I18N_PROJECT_ROOT → 自身向上 → 当前目录向上。原位运行时命中
    原来的 parent.parent，行为不变。
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
sys.path.insert(0, str(ROOT))

import models_registry  # noqa: E402,F401  注册全部 ORM 模型
from sqlalchemy import select  # noqa: E402

from agent_core.config.database import SessionLocal  # noqa: E402
from apps.api.models_i18n import I18nEntry  # noqa: E402
from apps.api.services import i18n as service  # noqa: E402

SEED_FILE = ROOT / 'apps' / 'api' / 'data' / 'i18n_seed.json'
ACTOR = 'seed:i18n'


def main() -> int:
    parser = argparse.ArgumentParser(description='灌入首批界面译文并发布')
    parser.add_argument('--file', default=str(SEED_FILE), help='译文 JSON 路径')
    parser.add_argument('--dry-run', action='store_true', help='只统计差异，不写库')
    parser.add_argument('--no-publish', action='store_true', help='只写草稿，不发布')
    args = parser.parse_args()

    payload = json.loads(Path(args.file).read_text(encoding='utf-8'))
    entries: dict[str, dict[str, str]] = payload['entries']
    batch = payload.get('_batch', 'seed')

    locales: set[str] = set()
    for table in entries.values():
        locales.update(table.keys())
    ordered = ['zh-CN'] + sorted(locales - {'zh-CN'})

    created = updated = unchanged = 0
    with SessionLocal() as db:
        for key, table in entries.items():
            for locale, value in table.items():
                row = db.scalar(
                    select(I18nEntry)
                    .where(I18nEntry.locale == locale)
                    .where(I18nEntry.key == key)
                )
                if row is None:
                    created += 1
                    if not args.dry_run:
                        db.add(I18nEntry(
                            locale=locale,
                            key=key,
                            draft_value=value,
                            published_value=value,
                            status='active',
                            updated_by=ACTOR,
                        ))
                    continue
                if row.draft_value == value and row.published_value == value:
                    unchanged += 1
                    continue
                updated += 1
                if not args.dry_run:
                    row.draft_value = value
                    row.published_value = value
                    row.status = 'active'
                    row.updated_by = ACTOR
        if args.dry_run:
            print(f'[dry-run] 新增 {created} / 更新 {updated} / 无变化 {unchanged}，'
                  f'语言 {ordered}')
            return 0
        db.commit()

        version = service.current_version(db)
        if args.no_publish:
            print(f'[no-publish] 新增 {created} / 更新 {updated} / 无变化 {unchanged}；'
                  f'当前版本 v{version}')
            return 0
        release = service.publish(db, ordered, f'seed:{batch}', ACTOR)
        print(f'新增 {created} / 更新 {updated} / 无变化 {unchanged}')
        print(f'已发布 v{release.version}（条目 {release.item_count}，语言 {ordered}）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
