#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨境单证界面词条校验器（doc-trans 技能自带）。

对齐仓库真实契约，不是通用 i18n 检查器：

* 结构与语义门禁对齐 `apps/api/services/i18n.py::validate_publish`
  （key 格式 / 空值 / 占位符集合 / 孤儿 key）；
* 长度阈值改用**布局口径**（各语种实测中位数，见 references/languages.md §0），
  服务端固定的 1.8× 只做兜底（`--ratio-profile server`）；
* 补齐服务端没有的语种专属检查：阿语数字与混排、日语简体词、繁体大陆用词、
  越南语降调、西语变体、泰语未译、拉丁语系夹中文。

用法示例：

    # 全量校验仓库词表
    python validate_ui_strings.py --seed apps/api/data/i18n_seed.json

    # 只校验本次新增的语种 + 句柄术语表做一致性巡检，阻断项非零则退出码 1
    python validate_ui_strings.py --seed apps/api/data/i18n_seed.json \
        --terms references/terminology.md --locales ar,ja,zh-Hant --strict

    # 校验外部译员交来的 9 列长表（表头 key,zh-CN,en,zh-Hant,ar,ja,es,vi,th）
    python validate_ui_strings.py --rows batch.tsv --json report.json

    # 逐条自检
    python validate_ui_strings.py --check-pair "保存" "บันทึก" --locale th

退出码：0 通过（或仅告警）；1 存在阻断项（`--strict` 之外也返回 1，便于脚本串联）。
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SOURCE = 'zh-CN'
ALL_LOCALES = ['zh-CN', 'en', 'zh-Hant', 'ar', 'ja', 'es', 'vi', 'th']

KEY_RE = re.compile(r'^[a-z0-9_]+(\.[a-z0-9_]+)+$')
PLACEHOLDER_RE = re.compile(r'\{\{\s*([A-Za-z0-9_]+)\s*\}\}')
HTML_RE = re.compile(r'</?[a-zA-Z][^>]*>|&(?:[a-z]+|#\d+);')
CJK_RE = re.compile(r'[\u3400-\u9fff]')
KANA_RE = re.compile(r'[\u3040-\u30ff]')
THAI_RE = re.compile(r'[\u0e00-\u0e7f]')
ARABIC_RE = re.compile(r'[\u0600-\u06ff]')
ARABIC_DIGITS_RE = re.compile(r'[\u0660-\u0669\u06f0-\u06f9]')
LATIN_RUN_RE = re.compile(r'[A-Za-z]{2,}')

#: 布局口径长度上限（译文/源文字符数比），数据来自 i18n_seed.json 实测
RATIO_LIMIT = {'zh-Hant': 1.3, 'ja': 2.4, 'ar': 4.4, 'th': 4.4, 'en': 4.4, 'vi': 4.7, 'es': 5.6}
#: 短标签的绝对长度豁免（取实测短标签 p95）：纯比例判据会把「取消→Cancelar」判超长
LENGTH_FLOOR = {'zh-Hant': 6, 'ja': 11, 'ar': 21, 'th': 21, 'en': 21, 'vi': 23, 'es': 26}
SERVER_RATIO = 1.8

#: 简体专用字（日语里永不出现，出现即说明混入了简体中文）
SIMPLIFIED_ONLY = (
    '单证报关编导删储认设选显类总输页签账说请员级纯组质贸检验优发货运归据间时过还为对应开门问题图标确录项额价费'
)
#: 中文专有词（字面可能是共用字，但整词不是日语说法）
JA_BAD_WORDS = [
    '阻断', '单证', '报关', '装箱单', '发票', '订舱', '收货人', '发货人', '通知人',
    '体积', '校验', '归集', '作废', '单号', '提单', '箱型箱量', '待确认', '已确认',
]
#: 繁体里不该出现的简体词 → 港台对应写法（缺一即判定）
HANT_MAINLAND = {
    '保存': '儲存', '字段': '欄位', '导出': '匯出', '导入': '匯入',
    '设置': '設定', '信息': '資訊', '默认': '預設', '数据': '資料', '打印': '列印',
    '刷新': '重新整理', '审计': '稽核', '创建': '建立', '添加': '新增', '搜索': '搜尋',
    '加载': '載入', '支持': '支援', '菜单': '選單', '登录': '登入',
    '网络': '網路', '软件': '軟體', '服务器': '伺服器', '上传': '上傳', '下载': '下載',
}
#: 语境相关的软用词（港台也用，只是本项目偏好另一种）→ 只告警不阻断
HANT_SOFT = {'文件': '檔案', '批量': '批次'}
#: 结尾是这些分隔符时，尾随空格是拼接用的，不算脏数据
SEPARATOR_TAIL = ('·', '：', ':', '，', ',', '—', '-', '/', '|', '、')
#: 简体列里不该出现的繁体词
ZHCN_TRAD_WORDS = ['資訊', '檔案', '設定', '儲存', '匯出', '匯入', '欄位', '選單', '稽核', '重新整理']
ES_VARIANT_PAIRS = [('ordenador', 'computadora'), ('fichero', 'archivo'), ('móvil', 'celular')]
VI_DIACRITIC_BASE = 'ăâđêôơưĂÂĐÊÔƠƯ'
BLOCK, WARN, INFO = 'BLOCK', 'WARN', 'INFO'


# --------------------------------------------------------------------------- 读取

def load_seed(path: Path) -> dict[str, dict[str, str]]:
    """读仓库词表：{_comment,_batch,entries:{key:{locale:value}}}。"""
    payload = json.loads(path.read_text(encoding='utf-8'))
    entries = payload.get('entries')
    if not isinstance(entries, dict):
        raise SystemExit(f'[i18n-validate] 不是仓库词表结构（缺 entries）：{path}')
    return {str(k): {str(loc): str(val) for loc, val in (v or {}).items()} for k, v in entries.items()}


def load_rows(path: Path) -> dict[str, dict[str, str]]:
    """读外部 9 列长表（TSV/CSV，表头必须含 key 与 zh-CN）。"""
    delimiter = '\t' if path.suffix.lower() in ('.tsv', '.txt') else ','
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if reader.fieldnames is None:
            raise SystemExit(f'[i18n-validate] 空表：{path}')
        fields = [name.strip() for name in reader.fieldnames]
        if 'key' not in fields or SOURCE not in fields:
            raise SystemExit(f'[i18n-validate] 表头需含 key 与 {SOURCE}，实际：{fields}')
        reader.fieldnames = fields
        rows: dict[str, dict[str, str]] = {}
        for raw in reader:
            key = (raw.get('key') or '').strip()
            if not key:
                continue
            rows[key] = {
                name: (raw.get(name) or '').strip()
                for name in fields
                if name != 'key'
            }
    return rows


def load_terms(path: Path) -> list[dict[str, str]]:
    """从 terminology.md 解析锁定术语：表头首列必须是 key、且含 8 语种列。"""
    header: list[str] | None = None
    terms: list[dict[str, str]] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped.startswith('|'):
            header = None if not stripped else header
            continue
        cells = [cell.strip() for cell in stripped.strip('|').split('|')]
        if header is None:
            if cells and cells[0] == 'key' and SOURCE in cells:
                header = cells
            continue
        if set(''.join(cells)) <= set('-: '):
            continue  # 分隔行
        if len(cells) != len(header):
            continue
        row = dict(zip(header, cells, strict=False))
        if row.get('key') and row.get(SOURCE):
            terms.append(row)
    return terms


# --------------------------------------------------------------------------- 检查

def placeholders(text: str) -> set[str]:
    return set(PLACEHOLDER_RE.findall(text or ''))


def is_latin_word_char(ch: str) -> bool:
    return ch.isascii() and ch.isalnum()


def has_vietnamese_marks(text: str) -> bool:
    if any(ch in VI_DIACRITIC_BASE for ch in text):
        return True
    return any('\u00c0' <= ch <= '\u1ef9' for ch in text)


def check_value(key: str, locale: str, source: str, value: str, ratio_limit: float,
                max_len: int | None) -> list[tuple[str, str, str]]:
    """单条译文校验，返回 [(level, code, message)]；消息带语种前缀，便于定位。"""
    issues: list[tuple[str, str, str]] = []

    def add(level: str, code: str, message: str) -> None:
        issues.append((level, code, f'[{locale}] {message}'))

    if not value.strip():
        add(BLOCK, 'EMPTY_VALUE', '译文为空')
        return issues
    if value.strip() == key:
        add(BLOCK, 'EMPTY_VALUE', '译文是 key 本身')
    if '\n' in value or '\r' in value:
        add(BLOCK, 'NEWLINE_IN_VALUE', '译文含换行符')
    if HTML_RE.search(value):
        add(BLOCK, 'HTML_TAG', f'译文含 HTML：{HTML_RE.search(value).group()}')
    if value != value.strip():
        # 拼接用的尾分隔符（“…核对 · ”）不算脏数据
        if not value.strip().endswith(SEPARATOR_TAIL):
            add(WARN, 'WS_EDGE', '译文首尾有空白')
    if '  ' in value:
        add(WARN, 'WS_DOUBLE', '译文中含连续空格')

    # R1 占位符（源文为空时不判，避免拿孤立译文误报）
    if source.strip() and placeholders(value) != placeholders(source):
        add(BLOCK, 'PLACEHOLDER_MISMATCH',
            f'占位符不一致 源{sorted(placeholders(source))} / 译{sorted(placeholders(value))}')

    if locale == SOURCE:
        # 源文列只查「夹了繁体词」这类自身问题
        for word in ZHCN_TRAD_WORDS:
            if word in value:
                add(WARN, 'ZHCN_TRAD_CHAR', f'简体源文里出现繁体词「{word}」')
        return issues

    # 繁体与部分无 CJK 的词条（API / PDF / Logo）本来就该同形，不算未翻译；
    # 日语里「一致/操作/数量/保存」这类汉字词与中文同形是正常的，只在夹假名时才算漏译
    if source.strip() and value == source and locale != 'zh-Hant' and CJK_RE.search(source):
        if locale == 'ja' and not KANA_RE.search(value):
            add(INFO, 'SAME_AS_SOURCE', '日文与中文同形（共用汉字词，属正常）')
        else:
            add(WARN, 'SAME_AS_SOURCE', '与源文完全相同（疑似未翻译）')

    # R2 长度：比例 + 短标签绝对豁免，避免「取消→Cancelar」这类正常译文被误报
    if source.strip():
        ratio = len(value) / max(1, len(source))
        allowed = max(ratio_limit * len(source), LENGTH_FLOOR.get(locale, 0))
        if len(value) > allowed:
            add(WARN, 'TOO_LONG', f'{ratio:.1f}× 源文，{len(value)} 字 > 预算 {allowed:.0f} 字')
    if max_len and len(value) > max_len:
        add(WARN, 'MAX_LEN_EXCEEDED', f'{len(value)} 字 > 控件上限 {max_len}')

    # 拉丁语系夹中文
    if locale in ('en', 'es', 'vi', 'th', 'ar') and CJK_RE.search(value):
        add(BLOCK, 'CJK_IN_LATIN', '译文里夹了汉字（漏译）')

    if locale == 'ar':
        if ARABIC_DIGITS_RE.search(value):
            add(BLOCK, 'AR_ARABIC_DIGITS', '用了阿拉伯-印度数字，应改西方数字 0-9')
        stripped = value.strip()
        edge = bool(stripped) and (is_latin_word_char(stripped[0]) or is_latin_word_char(stripped[-1]))
        if edge and ARABIC_RE.search(value) and ('{{' in value or LATIN_RUN_RE.search(value)):
            add(WARN, 'AR_BIDI_RISK',
                '拉丁/数字贴着 RTL 边界，交由容器 dir/unicode-bidi 隔离，勿手插 FSI')

    if locale == 'ja':
        bad_chars = sorted({ch for ch in value if ch in SIMPLIFIED_ONLY})
        bad_words = [word for word in JA_BAD_WORDS if word in value]
        if bad_chars or bad_words:
            detail = []
            if bad_chars:
                detail.append(f'简体字 {"".join(bad_chars)}')
            if bad_words:
                detail.append(f'中文词 {"、".join(bad_words)}')
            add(BLOCK, 'JA_SIMPLIFIED_WORD', '混入' + '；'.join(detail))

    if locale == 'zh-Hant':
        for simple, trad in HANT_MAINLAND.items():
            if simple in value and trad not in value:
                add(BLOCK, 'HANT_MAINLAND_WORD', f'大陆用词「{simple}」应为「{trad}」')
        for simple, trad in HANT_SOFT.items():
            if simple in value and trad not in value:
                add(WARN, 'HANT_MAINLAND_WORD', f'大陆用词「{simple}」，本项目口径为「{trad}」')

    if locale == 'vi':
        latin = sum(1 for ch in value if ch.isascii() and ch.isalpha())
        if latin >= 12 and len(value.split()) >= 4 and not has_vietnamese_marks(value):
            add(WARN, 'VI_NO_DIACRITICS', '越南语无任何声调符号（疑似降调为 ASCII）')

    if locale == 'th' and not THAI_RE.search(value):
        # 品牌（WeChat Pay）、代码（G-{{id}}）、纯占位符模板属正常；成句的拉丁短语才是漏译
        if CJK_RE.search(value):
            add(BLOCK, 'TH_NO_THAI', '泰语列夹了汉字，未翻译')
        elif len(LATIN_RUN_RE.findall(value)) >= 2:
            add(WARN, 'TH_NO_THAI', '泰语列无泰文，疑未翻译（拉丁短语）')
        else:
            add(INFO, 'TH_NO_THAI', '泰语列无泰文（品牌/代码/纯占位符，可接受）')

    return issues


def _normalize_label(text: str) -> str:
    """去掉必填星号、尾部标点，便于「源文 == 术语本身」的严格比对。"""
    return text.strip().rstrip('*＊:：').strip()


def _term_scope(entry_key: str, term_key: str) -> str | None:
    """术语与词条的匹配范围。

    `exact`  = 词条就是该术语的规范条目（如 `common.field.shipper` ↔ `field.shipper`）；
    `family` = 同业务域下源文相同但 key 不同（如 `web.grouping.tag.suggest` 的「建议归集」）；
    None     = 不比对（避免「已确认」在单证状态与差异确认里语义不同却互相报错）。
    """
    if entry_key == f'common.{term_key}' or entry_key.endswith(f'.{term_key}'):
        return 'exact'
    parts = term_key.split('.')
    if len(parts) < 2:
        return None
    segment = parts[1] if parts[0] == 'status' else parts[0]
    return 'family' if segment in entry_key.split('.') else None


def check_terms(rows: dict[str, dict[str, str]], terms: list[dict[str, str]],
                locales: list[str]) -> list[tuple[str, str, str]]:
    """R3 术语一致性。

    不是拿术语去 `in` 长句（阿拉伯语前缀/西语复数/越语语序都会误报，实测 1471 条噪音），
    而是「源文整体等于术语」时才比对，并按 key 归属分两级：
    规范条目命中 → WARN；同域其它 key → INFO（可能是刻意的短标签）。
    """
    issues: list[tuple[str, str, str]] = []
    by_source = {_normalize_label(term[SOURCE]): term for term in terms}
    for key, values in rows.items():
        source = _normalize_label(values.get(SOURCE, ''))
        term = by_source.get(source)
        if term is None:
            continue
        scope = _term_scope(key, term['key'])
        if scope is None:
            continue
        level = WARN if scope == 'exact' else INFO
        for locale in locales:
            expected = _normalize_label(term.get(locale, ''))
            actual = _normalize_label(values.get(locale, ''))
            if not expected or not actual:
                continue
            if actual.casefold() != expected.casefold():
                issues.append((level, 'TERM_DRIFT',
                               f'[{locale}] 术语「{source}」应为「{expected}」，实际「{actual}」'))
    return issues


def check_hant_ratio(rows: dict[str, dict[str, str]]) -> list[tuple[str, str, str]]:
    """R7 繁体与简体同形率过高 → 疑似直接贴简体。"""
    pairs = [(v.get(SOURCE, ''), v.get('zh-Hant', '')) for v in rows.values()
             if v.get(SOURCE, '').strip() and v.get('zh-Hant', '').strip()]
    if len(pairs) < 20:
        return []
    same = sum(1 for source, hant in pairs if source == hant)
    ratio = same / len(pairs)
    if ratio > 0.95:
        return [(WARN, 'HANT_LOOKS_SIMPLIFIED', f'繁体与简体同形率 {ratio:.0%}（{same}/{len(pairs)}）')]
    return []


def check_es_variant(rows: dict[str, dict[str, str]], locale: str = 'es') -> list[tuple[str, str, str]]:
    blob = ' '.join((v.get(locale) or '').lower() for v in rows.values())
    issues = []
    for left, right in ES_VARIANT_PAIRS:
        if left in blob and right in blob:
            issues.append((WARN, 'ES_VARIANT_MIX', f'同时出现「{left}」与「{right}」，变体混用'))
    return issues


def check_duplicate_sources(rows: dict[str, dict[str, str]], locale: str) -> list[tuple[str, str, str]]:
    """同一源文在不同 key 下译文不同 → INFO（可能合理，但值得看一眼）。"""
    buckets: dict[str, set[str]] = defaultdict(set)
    for values in rows.values():
        source, target = values.get(SOURCE, '').strip(), (values.get(locale) or '').strip()
        if len(source) >= 4 and target:
            buckets[source].add(target)
    drift = [(source, targets) for source, targets in buckets.items() if len(targets) > 1]
    if not drift:
        return []
    sample = '；'.join(f'「{source}」→{len(targets)} 种' for source, targets in drift[:3])
    return [(INFO, 'INCONSISTENT_TRANSLATION', f'{len(drift)} 组同源多译（{sample}）')]


# --------------------------------------------------------------------------- 输出

def run(args: argparse.Namespace) -> int:
    if args.check_pair:
        source, value = args.check_pair
        locale = args.locale or 'th'
        issues = check_value('manual.check', locale, source, value,
                             SERVER_RATIO if args.ratio_profile == 'server' else RATIO_LIMIT.get(locale, SERVER_RATIO),
                             args.max_len_map.get(locale))
        if not issues:
            print(f'[i18n-validate] {locale} OK：{value}')
        for level, code, message in issues:
            print(f'{level:5s} {code:22s} {message}')
        return 1 if any(level == BLOCK for level, _, _ in issues) else 0

    if not args.seed and not args.rows:
        raise SystemExit('[i18n-validate] 需要 --seed 或 --rows（或用 --check-pair 逐条自检）')

    rows = load_seed(Path(args.seed)) if args.seed else load_rows(Path(args.rows))
    terms = load_terms(Path(args.terms)) if args.terms else []
    present = {loc for values in rows.values() for loc in values}
    locales = ([item.strip() for item in args.locales.split(',') if item.strip()]
               if args.locales else [loc for loc in ALL_LOCALES if loc in present and loc != SOURCE])
    unknown = [loc for loc in locales if loc not in ALL_LOCALES]
    if unknown:
        raise SystemExit(f'[i18n-validate] 未知语种：{unknown}（支持 {ALL_LOCALES}）')

    findings: dict[str, list[tuple[str, str, str]]] = {}
    for key, values in rows.items():
        if not KEY_RE.match(key):
            findings.setdefault(key, []).append((BLOCK, 'KEY_INVALID', 'key 格式非法，应为 [a-z0-9_.]+ 且至少两段'))
        for locale in locales:
            value = values.get(locale)
            if value is None:
                findings.setdefault(key, []).append((BLOCK, 'MISSING_LOCALE', f'{locale} 缺行'))
                continue
            limit = SERVER_RATIO if args.ratio_profile == 'server' else RATIO_LIMIT.get(locale, SERVER_RATIO)
            findings.setdefault(key, []).extend(
                check_value(key, locale, values.get(SOURCE, ''), value, limit, args.max_len_map.get(locale))
            )

    if terms:
        for level, code, message in check_terms(rows, terms, locales):
            findings.setdefault('(全局)', []).append((level, code, message))
    if 'zh-Hant' in locales:
        for level, code, message in check_hant_ratio(rows):
            findings.setdefault('(全局)', []).append((level, code, message))
    if 'es' in locales:
        for level, code, message in check_es_variant(rows):
            findings.setdefault('(全局)', []).append((level, code, message))
    if args.dupes:
        for locale in locales:
            for level, code, message in check_duplicate_sources(rows, locale):
                findings.setdefault('(全局)', []).append((level, code, f'{locale} {message}'))

    counter: Counter[tuple[str, str]] = Counter()
    for items in findings.values():
        for level, code, _ in items:
            counter[(level, code)] += 1
    total_block = sum(count for (level, _), count in counter.items() if level == BLOCK)
    total_warn = sum(count for (level, _), count in counter.items() if level == WARN)

    source_label = args.seed or args.rows
    print(f'[i18n-validate] {source_label}  entries={len(rows)}  locales={",".join(locales)}  '
          f'terms={len(terms)}  profile={args.ratio_profile}')
    print(f'[i18n-validate] 阻断 {total_block}  告警 {total_warn}  涉及 key {len(findings)}')
    for level in (BLOCK, WARN, INFO):
        for (lvl, code), count in sorted(counter.items(), key=lambda item: -item[1]):
            if lvl == level:
                print(f'  {lvl:5s} {code:26s} {count}')

    detail = [item for level in (BLOCK, WARN) for key, items in findings.items()
              for item in items if item[0] == level]
    shown = 0
    for key, items in findings.items():
        for level, code, message in items:
            if level in (BLOCK, WARN) and shown < args.max_detail:
                print(f'    {level:5s} {key} {code}: {message}')
                shown += 1
    if len(detail) > shown:
        print(f'    …另有 {len(detail) - shown} 条明细（--max-detail 调整，或用 --json 落盘全量）')

    if args.json:
        payload = {
            'source': source_label,
            'entries': len(rows),
            'locales': locales,
            'summary': {'blocking': total_block, 'warnings': total_warn, 'keys': len(findings)},
            'findings': {
                key: [{'level': level, 'code': code, 'message': message} for level, code, message in items]
                for key, items in findings.items()
            },
        }
        Path(args.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'[i18n-validate] 报告已写入 {args.json}')

    return 1 if total_block else 0


def parse_max_len(items: list[str] | None) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items or []:
        if '=' not in item:
            raise SystemExit(f'[i18n-validate] --max-len 需要 LOCALE=N，收到：{item}')
        locale, _, size = item.partition('=')
        result[locale.strip()] = int(size)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='跨境单证界面词条校验（占位符 / 长度 / 术语 / 语种专属规则）')
    parser.add_argument('--seed', help='仓库词表 JSON（apps/api/data/i18n_seed.json）')
    parser.add_argument('--rows', help='外部 9 列长表（TSV/CSV）')
    parser.add_argument('--terms', help='术语表 markdown（references/terminology.md）')
    parser.add_argument('--locales', help='只校验这些语种，逗号分隔（默认全部非源语种）')
    parser.add_argument('--ratio-profile', choices=['layout', 'server'], default='layout',
                        help='长度阈值口径：layout=各语种实测上限（默认），server=固定 1.8×')
    parser.add_argument('--max-len', dest='max_len', action='append',
                        help='控件硬上限，形如 ar=40，可重复')
    parser.add_argument('--json', help='把全量结果写成 JSON 报告')
    parser.add_argument('--max-detail', type=int, default=40, help='终端最多打印多少条明细')
    parser.add_argument('--no-dupes', dest='dupes', action='store_false', help='跳过同源多译统计')
    parser.add_argument('--strict', action='store_true', help='阻断项非零即退出码 1（默认行为亦如此）')
    parser.add_argument('--check-pair', nargs=2, metavar=('SOURCE', 'TARGET'), help='逐条自检一对源文/译文')
    parser.add_argument('--locale', help='配合 --check-pair 指定目标语种')
    args = parser.parse_args(argv)
    args.max_len_map = parse_max_len(args.max_len)
    for attr in ('seed', 'rows', 'terms'):
        value = getattr(args, attr)
        if value and not Path(value).exists():
            raise SystemExit(f'[i18n-validate] 文件不存在：{value}')
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
