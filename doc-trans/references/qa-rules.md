# 界面翻译质量检查规则

> 校验分两级：**阻断**（不得标记 `TRANSLATED`，不得发布）与**告警**（可发，但必须进复核清单）。
> 服务端发布门禁 `apps/api/services/i18n.py::validate_publish` 只覆盖 R1/R3/R4 的稳定子集；R5–R9 由本技能脚本与人工复核承担。
> 每条规则都对应 `scripts/validate_ui_strings.py` 输出的 `code`，便于对账。

## R1 占位符完整性 — `PLACEHOLDER_MISMATCH`（阻断）

`{{name}}` 占位符集合必须与 zh-CN **完全相等**（多、少、拼错、改变大小写都算错）。

- 只允许具名参数 `{{count}}`，不支持 `{0}` / `%s` / `${x}` —— 出现即视为占位符不一致。
- 纯占位符行（值等于 `{{count}}`）不翻译，标 `SKIP-PLACEHOLDER`。
- 顺序可以按目标语序调整，但集合必须一致；数量不能变。
- 丢一个占位符 = 运行期少传一个变量，界面会显示空串或 `undefined`，属功能性缺陷。

## R2 长度约束 — `TOO_LONG`（告警）

以字符数比判阈值，**比例上限 + 短标签绝对豁免**双判据（见 `languages.md` §0 实测表）：`len(译文) > max(比例上限 × len(源文), 豁免字数)`。

- 比例上限取各语种 p95：zh-Hant 1.3× / ja 2.4× / ar·th·en 4.4× / vi 4.7× / es 5.6×；豁免字数 6/11/21/21/21/23/26。
- 加豁免的原因：纯比例会把「取消 → Cancelar」（4 倍、8 字）判超长，实测噪音 2255 条。
- 服务端的 `> 1.8×` 是**兜底异常检测**，不适合当布局判断（拉丁语种中位数本就 2.7–3.8 倍）。用 `--ratio-profile server` 可复现该口径。
- 控件硬边界用 `--max-len ar=40` 显式传，别指望比例判据。
- 超限先缩短：换短词 → 去冗余量词 → 拆句。**禁止硬截断、禁止省略号糊弄**。

## R3 术语一致性 — `TERM_DRIFT`（告警，红线级）

同一锁定术语在全表目标语言列中只允许一种译法。校验分两级，因为「源文相同」不等于「语义相同」：

| 范围 | 判定 | 级别 |
|---|---|---|
| 规范条目（`common.field.shipper` ↔ 术语 `field.shipper`） | 译文必须等于锁定译法（忽略大小写/必填星号） | WARN |
| 同业务域其它 key（`web.grouping.tag.suggest` 的「建议归集」） | 可能是刻意的短标签 | INFO |
| 跨域同源（单证状态的「已确认」vs 差异确认的「已确认」） | **不比对**，语义不同（Confirmed vs Corrected/Explained） | 跳过 |

不用「术语 `in` 长句」的写法：阿拉伯语前缀、西语复数、越语语序会让子串比对误报（实测 1471 条噪音）。

巡检发现漂移 → 统一回术语表译法 → 变更记入 `i18n_entries.remark` 与变更日志。同一 zh-CN 源文在不同 key 下出现两种译文时另报 `INCONSISTENT_TRANSLATION`（INFO），按「哪个更贴行业」统一。状态词与动作词不得互换：`ยกเลิก`（取消，按钮）≠ `ยกเลิกแล้ว`（已取消，状态）。

## R4 空译文 — `EMPTY_VALUE` / `MISSING_LOCALE`（阻断）

空串、纯空白、只有标点、复制了 key 本身，一律视为未翻译。

- 8 个语种必须都有非空值（`i18n_batch_util.py` 与发布门禁双重强制）。
- 确实无法翻译（如纯占位符）→ 源文原样透传并标 `SKIP-PLACEHOLDER`，不要留空。
- 覆盖率看板把空值计为未翻译，留空会一直挂在待办里。

## R5 不可译项 — `TRANSLATED_CODE`（阻断）

HS 编码、UN/LOCODE、船公司代码、单证编号、提单号、集装箱号、封条号、Incoterms 缩写、金额数字：原样透传，不进翻译队列。

- 八语种列里出现转写（`سي آي إف` 这种把 CIF 写成阿拉伯字母）即违规。
- 单号类值必须由容器强制 `direction: ltr; unicode-bidi: isolate`，防止 RTL 重排（`OOLU8882850350` 被读成 `8882850350OOLU`）。

## R6 低置信标记 — `CONFIDENCE: LOW`（进复核清单）

对译法不确定时：给译文 + `CONFIDENCE: LOW`，进人工复核，不静默交付。

- 禁止用「看起来合理」的译法硬填。
- 术语表未覆盖且无法从官方来源确认 → `TERM-CANDIDATE`，不写入交付译文。
- 复核结论必须回写 `terminology.md`，不要只在对话里说一次。

## R7 语种专属规则

| 规则 | code | 判据 | 级别 |
|---|---|---|---|
| 阿拉伯语数字 | `AR_ARABIC_DIGITS` | 出现 `٠-٩` / `۰-۹`（单证原件用西方数字） | 阻断 |
| 阿拉伯语混排 | `AR_BIDI_RISK` | 值以拉丁字母/数字开头或结尾（隔离边界），建议由容器 `dir`/`unicode-bidi` 处理，**不要默认插 FSI** | 告警 |
| 日语简体词 | `JA_SIMPLIFIED_WORD` | 日文值里出现简体专用字（`单/证/报/关/编/导/删/储/认/设/选/显/类/总/输/页/签/账/说/请/员/级/纯/组/质/贸/检/验/优/发/货/运/归/据/间/时/过/还/为/对/应/开/门/问/题/图/标/确/录/项/额/价/费`）或中文专有词（`阻断/单证/报关单/装箱单/发货人/收货人/通知人/体积/校验/归集/作废/单号/提单/箱型箱量/待确认/已确认`） | 阻断 |
| 繁体大陆用词 | `HANT_MAINLAND_WORD` | 硬表（`保存/字段/导出/导入/设置/信息/默认/数据/打印/刷新/审计/创建/添加/搜索/加载/支持/菜单/登录/上传/下载/网络/软件/服务器`）出现即阻断；软表（`文件/批量`）只告警（港台也用，只是本项目偏好 `檔案/批次`） | 阻断 / 告警 |
| 繁体疑似简体 | `HANT_LOOKS_SIMPLIFIED` | zh-Hant 与 zh-CN 同形率 > 95%（≥20 条样本） | 告警 |
| 简体夹繁体字 | `ZHCN_TRAD_CHAR` | zh-CN 值里出现繁体词（資訊/檔案/設定/儲存/匯出/匯入/欄位/選單/稽核/重新整理） | 告警 |
| 越南语降调 | `VI_NO_DIACRITICS` | vi 值含 ≥12 个拉丁字母、≥4 个词却零声调符号 | 告警 |
| 西语变体混用 | `ES_VARIANT_MIX` | 全表同时出现 `ordenador`+`computadora`、`fichero`+`archivo`、`móvil`+`celular` | 告警 |
| 泰语未译 | `TH_NO_THAI` | 三级：夹汉字→阻断；成句拉丁短语（≥2 个词）→告警；品牌/代码/纯占位符（`WeChat Pay`、`G-{{id}}`）→INFO 可接受 | 分级 |
| 拉丁语系夹中文 | `CJK_IN_LATIN` | en/es/vi/th/ar 值含 CJK 汉字（漏译） | 阻断 |
| 同形不必译 | `SAME_AS_SOURCE` | 与源文完全相同：zh-Hant 不判（本就同形）；ja 若无假名视为共用汉字词（`一致/操作/数量/保存`）→INFO；其余→告警 | 分级 |

> 现网实测（2026-10-29 全量 1429 key × 7 语）：`CJK_IN_LATIN` 抓到 3 条真实漏译——泰语值里混进「輸入」（`ช่อง輸入`），已进待修清单。

## R8 key 契约 — `KEY_INVALID`（阻断）

- 格式 `^[a-z0-9_]+(\.[a-z0-9_]+)+$`，至少两段，小写。
- 必须静态字面量，禁止 `t('web.documents.' + type)`；运行期拼接的覆盖类 key（`web.menu.*` / `web.dict.*` / `common.status.*`）不走提取脚本，但要遵守同样的命名规则（枚举值统一 `toLowerCase()`）。
- 一个 key 一个语义；同一中文词在不同语境必须拆 key。
- key 存在但源语言没有 → 孤儿 key，阻断；源语言有但某语种没有 → 也阻断（ORPHAN_KEY）。

## R9 结构安全 — `HTML_TAG` / `NEWLINE_IN_VALUE` / `WS_EDGE`（阻断 / 告警）

- 译文里出现 `<b>` `<br>` `&nbsp;` 等 HTML → 阻断（项目硬规则：词条不含 HTML）。
- 值内含换行符 `\n` → 阻断（DOM 里会被渲染成空格，看起来像译文被截断）。
- 值首尾有空格、值内有连续两个以上空格 → 告警。**例外**：值以 `·` `：` `:` `，` `,` `—` `-` `/` `|` `、` 结尾时，尾随空格是拼接用的（现网 70 处属此类，不应改）。

## R11 工具用法（`scripts/validate_ui_strings.py`）

```bash
# 全量巡检仓库词表（按语种实测阈值）
python docs/skills/crossborder-doc-ui-translator/scripts/validate_ui_strings.py \
  --seed apps/api/data/i18n_seed.json

# 带术语锁定巡检（输出即「待修清单」）+ 落 JSON 报告
python docs/skills/crossborder-doc-ui-translator/scripts/validate_ui_strings.py \
  --seed apps/api/data/i18n_seed.json \
  --terms docs/skills/crossborder-doc-ui-translator/references/terminology.md \
  --json .tmp-i18n-report.json

# 校验外部译员的 9 列长表，并指定控件硬上限
python docs/skills/crossborder-doc-ui-translator/scripts/validate_ui_strings.py \
  --rows batch.tsv --max-len ar=40 --max-len es=32

# 逐条自检（不给文件时最快的用法；只查结构，不查术语）
python docs/skills/crossborder-doc-ui-translator/scripts/validate_ui_strings.py \
  --check-pair "共 {{count}} 个文件" "{{count}} ไฟล์" --locale th
```

退出码：存在阻断项即 1（可直接串进脚本）。阻断口径与服务端 `validate_publish` 对齐，告警项不会挡发布，但必须逐条有结论。

## R10 落盘与发布 — 流程性检查（人工）

1. key 化代码与词表**必须同批**：先改代码再补词表，否则孤儿 key 阻断发布。
2. `python scripts/seed_i18n.py` 灌库后版本号单调递增（回滚也递增），不要手改 `i18n_releases`。
3. `npm run check:i18n` 与 `npm run build -w web` 必须绿（含字体门禁、RTL 静态检查）。
4. 阿语至少一张截图（RTL 问题在中文界面看不出来）。
5. 简繁必须独立维护，禁止 OpenCC。

## 复核清单该列什么

只列需要人看的行，不复制全表：

- `TERM-CANDIDATE`（术语候选，未定口径）
- `CONFIDENCE: LOW`（低置信译文）
- `TOO_LONG` 且没有收敛方案的
- `TERM_DRIFT` 修正记录（改了什么、改成什么、为什么）
- `AR_BIDI_RISK`（RTL 混排边界）
- `LEGAL-REVIEW`（法律/信用证条款，已停止处理）

## 通过标准（Definition of Done）

1. `validate_ui_strings.py --strict` 阻断项为 0；
2. 告警项全部有处置结论（改掉 / 缩短 / 进复核清单）；
3. 8 语种非空率 100%，覆盖率看板不倒退；
4. 术语巡检漂移为 0，或漂移已统一并在 `remark` 留痕；
5. 词表落盘后 `seed_i18n.py` 发布成功、`check:i18n` 与 `build -w web` 全绿。
