---
name: doc-trans
description: "跨境物流单证智能体系统界面多语言翻译技能。支持简体中文、繁体中文、英文、越南语、泰语、日语、阿拉伯语、西班牙语共 8 种语言互译。锁定单证术语（单证类型、字段名、状态词、Incoterms、HS 编码、港口代码），保留 {{name}} 占位符与 key 契约，处理阿拉伯语 RTL/双向文本，执行各语种专属规则（简繁术语替换、日语惯用语、泰语无词间空格、越南语声调、西语变体），校验界面长度与发布门禁，输出可直接回填 i18n_seed.json 的译文表。触发关键词：界面翻译、单证系统翻译、UI string 翻译、泰文界面、日文界面、阿拉伯语界面、越南语界面、西班牙语界面、简繁转换、物流系统本地化、词条翻译。"
allowed-tools: Read,Write,Bash
agent_created: true
---

# 跨境物流单证界面翻译

## 概述

把跨境物流单证智能体系统的界面文案在 **zh-CN（源）/ en / zh-Hant / vi / th / ja / ar / es** 八语种之间互译，并产出可直接回填 `apps/api/data/i18n_seed.json` 的词条。

单证界面不是普通文案。术语不一致会让操作员把「通知人」和「收货人」看混；占位符丢一个 `{{count}}` 会让页面显示 `undefined`；阿拉伯语不加隔离会让单号 `OOLU8882850350` 重排成乱码；繁简出现「字形繁体 + 用词大陆」的混合体等于交了一份假繁体。本技能把「术语锁定 → 结构保真 → 语种专属规则 → 长度与门禁校验 → 合规复核」五道关卡固化进流程。

**术语与规则的唯一事实源是本仓库**，不是本文件：词表 `apps/api/data/i18n_seed.json`、字段名 `apps/api/services/doc_fields.py::FIELD_SPECS`、发布门禁 `apps/api/services/i18n.py::validate_publish`。`references/` 下的四份文件是从这些源头提炼的快照与规则，冲突时以仓库代码与词表为准，并回头修正参考文献：

- `references/terminology.md`——**锁定译文表**（8 语字段/状态/动作 + 保留原文项 + 现网待修清单）；被校验脚本 `validate_ui_strings.py --terms` 解析为一致性巡检基准。
- `references/glossary.md`——**领域词义词典**（单证/费用/海关/箱务等全部业务专有词汇的英文全称、中文含义、使用场景）。只给 AI 翻译时确认"词义与边界"用，**脚本不解析**，也不用于产出译文——译文以 terminology.md 为准。
- `references/languages.md`——各语种专属规则（阿拉伯 RTL、简繁术语替换、日语惯用语、泰语无词间空格、越南语声调、西语变体）。
- `references/qa-rules.md`——QA 规则与脚本 `code` 对照表，便于对账。

## 文件关系与调用链

```
SKILL.md  ← 总调度：AI 翻译时读它，它指示 AI 去读下面三份参考 + 跑脚本
   ├─ references/glossary.md      （AI 翻译前查"词义"，只读，脚本不解析）
   ├─ references/terminology.md   （AI 取"锁定 8 语译文"；校验脚本用 load_terms() 解析）
   ├─ references/languages.md     （AI 翻译时遵守的语种规则）
   └─ references/qa-rules.md      （QA 规则 ↔ 脚本 code 对照）

scripts/validate_ui_strings.py  ← 校验器（CLI，独立跑）
   --seed  apps/api/data/i18n_seed.json   （读真实词表）
   --terms references/terminology.md      （读锁定表，做一致性巡检）
   ⚠️ 校验器只调用 terminology.md，不读 glossary.md
```

**哪一个文件在"调用" glossary.md？** 是 `SKILL.md`——它指令 AI 在翻译前先查 `glossary.md` 确认概念边界，再去 `terminology.md` 取锁定译文。**校验脚本不调用它**（词典是给理解用的，不是机器校验用的）。职责分离：词典管"懂不懂"，锁定表管"翻得对不对"，脚本管"有没有违规"。

## 适用场景

- 新增界面文案的八语种译法生成（本仓库最常见的入口）
- 已有译文的术语一致性巡检与漂移修正（`i18n_seed.json` 已有 1429 key × 8 语）
- 简繁中文术语库对齐（**禁止 OpenCC 自动转换**）
- 单证模板固定字段名的多语言对齐（提单 / 发票 / 装箱单 / 报关单 / 订舱单）
- Excel/CSV 词条表的外部译员协作（导入导出走 9 列长表）

不适用：整段法律条款的认证翻译（需人工译员签章）、营销文案的创意本地化、单证原件内容与 OCR 原文（属「不翻译」边界）。

## 支持语种与专属红线

| 语种 | code | 专属红线 | 长度基准（相对 zh-CN） |
|---|---|---|---|
| 简体中文 | `zh-CN` | 源语言。`t('key','源文')` 第二参必须与代码字面量**一字不差** | 100%（基准） |
| 英文 | `en` | 长度基准与代码/缩写宿主；Incoterms 不译不扩写 | 150%–200%（拉丁语系最长基准） |
| 繁体中文 | `zh-Hant` | **术语替换，不是字形映射**；禁止「繁体字形 + 大陆用词」 | 100%–110% |
| 越南语 | `vi` | 声调符号完整保留，禁止降级为无调 ASCII；行高预留 | 150%–200% |
| 泰语 | `th` | 无词间空格，禁止按空格断行；`letter-spacing` 必须为 0 | 150%–200% |
| 日语 | `ja` | 按钮用惯用 UI 语（送信/保存/戻る/削除）；全半角统一；敬体常体不混用；**不得混入简体中文词** | 100%–130% |
| 阿拉伯语 | `ar` | RTL + 双向文本；数字用西方数字；单号/金额/代码强制 `direction:ltr; unicode-bidi:isolate`；括号与方向图标镜像规则见 `languages.md` | 90%–130% |
| 西班牙语 | `es` | 锁定变体（本仓库按中性/拉美口径，锁定后全表一致），禁止 ordenador/computadora 混用 | 150%–200% |

任一语种缺其专属规则检查，不得标记 `TRANSLATED`。

## 输入

执行前必须确认，缺失项向用户询问，不自行假设：

1. 源语言与目标语言（默认源 `zh-CN`，目标为其余 7 种）
2. 词条来源：本仓库 `apps/api/data/i18n_seed.json`（首选）/ 外部 Excel/CSV（需含 key 列与源文列）
3. 是否含 `{{name}}` 占位符、key 前缀归属（`common.*` / `web.*` / `ops.*`）
4. 界面约束：字符长度上限、是否允许换行、所在控件（按钮 / 表头 / 侧栏 / Toast）

## 执行步骤

### 第 1 步：诊断词条表，先不翻译

读出待处理词条，报告：总数、按命名空间分布（`common.field.*` / `web.documents.*` …）、占位符种类与出现次数、疑似超长源文、`zh-Hant` 与 `zh-CN` 同形率。

本仓库词条表就是 `apps/api/data/i18n_seed.json`（结构 `{_comment,_batch,entries:{key:{locale:value}}}`）。取新增 key 用：

```bash
node scripts/i18n-extract.mjs --json .tmp-i18n.json   # 静态 key → 源文清单
```

新增 key 必须先 key 化代码（`t('key','源文')`），再补译文——**顺序反了就会出现孤儿 key，发布被阻断**。

### 第 2 步：加载术语表，建立强制约束

先查 `references/glossary.md` 确认遇到的业务词**到底指什么、容易和哪个词混**（如「订舱委托书 Booking Note ≠ 订舱单 S/O」、「归集 ≠ 拼柜」），再去 `references/terminology.md` 取该概念的**锁定 8 语译文**。

从 `references/terminology.md` 加载锁定术语。以下类别必须按术语表执行，禁止自行推断：

- **Incoterms**（FOB、CIF、EXW、DDP…）：8 个语种列一律保留拉丁字母，不译、不扩写、不音译。
- **HS 编码、港口 UN/LOCODE、船公司代码、单证编号、提单号、集装箱号、封条号**：原样透传，不进「待翻译」队列。
- **单证类型名**（提单 / 发票 / 装箱单 / 报关单 / 订舱单）：按 `references/terminology.md` 的八语种锁定值，任何页面不得出现第二种说法。
- **单证字段名**：以后端 `FIELD_SPECS` 的 key 为锚点，走 `common.field.<key>`；同一字段在表头、详情、差异面板、复核工作区必须同译法。
- **监管证件缩写**（CIQ、AMS、ISF…）：检索官方译法，不自行创译。

术语表未覆盖的新术语 → 标 `TERM-CANDIDATE`，进待确认清单，**不直接写入译文**。判断不了的译法，调用跨境本地化翻译专家复核（见「外部复核」）。

### 第 3 步：加载目标语种专属规则

从 `references/languages.md` 读目标语种的专属规则，翻译时同步执行，不做事后补丁：

- `ar`：数字形式、双向混排、括号镜像、图标翻转、`dir` 作用域。
- `zh-Hant` / `zh-CN`：走术语替换；两岸用词差异按 `terminology.md` 实测对照表。
- `th` / `vi`：断行与声调符号风险、行高预留。
- `ja`：惯用 UI 语、全半角、敬体常体，**禁止混入简体中文词**（本项目真实事故：日文差异页出现「阻断」，应为「ブロック」）。
- `es`：变体锁定，同一概念全表只允许一种译法。

### 第 4 步：翻译，但只翻译「应该翻译的」

- 占位符 `{{name}}` **原样保留**：名称、数量、类型、顺序不变；插值只允许具名参数，译文里不得出现 HTML。
- 纯占位符行（如 `{{count}}` 单独成串）不翻译，标 `SKIP-PLACEHOLDER`。
- 界面短标签用目标语种惯用 UI 语而非直译：英文 "Submit" 在日文界面用「送信」、泰文界面用动词优先的短词。
- **本期不做复数/性/格**（项目决策 D2）：阿拉伯语 CLDR 六态靠**文案改写**规避（「3 个文件」→「文件数：3」），不要自创 `_plural` 变体。
- 不确定的模糊词：给出译文 + `CONFIDENCE: LOW`，进人工复核，不静默交付。
- 业务数据（客户名、单号、品名、差异规则 message、归集 reasonText）与 LLM 输出**不译**。

### 第 5 步：长度与结构校验（必须真跑，不许目测）

```bash
python docs/skills/doc-trans/scripts/validate_ui_strings.py \
  --seed apps/api/data/i18n_seed.json --strict
```

校验项与仓库发布门禁 `validate_publish` 同口径：

- 阻断：key 格式非法、8 语任一为空/空白、`{{}}` 占位符集合与源文不一致、译文含 HTML、目标语种混入源语言文字（`en`/`es`/`vi`/`th`/`ar` 出现 CJK）
- 告警：与源文完全相同、长度 > 源文 1.8 倍、繁简同形率 > 95%
- 语种专属：`ar` 阿拉伯-印度数字、RTL 混排未隔离；`ja` 简体中文词混入；`zh-Hant` 大陆用词；`vi` 无调降级；`es` 变体混用

超长行**优先给缩短方案**（换短词、去掉冗余量词），不硬截断。

### 第 6 步：术语一致性巡检

全部译文产出后，反向扫描 `terminology.md` 的锁定项：同一 zh-CN 术语在目标语言列中只允许一种译法。发现漂移 → 统一回术语表译法 → 记录到变更日志（`i18n_entries.remark` 同步留痕）。`validate_ui_strings.py --terms references/terminology.md` 可自动出漂移清单。

### 第 7 步：输出

按用途二选一（或都给）：

1. **仓库落盘（首选）**：每行 9 列 `key, zh-CN, en, zh-Hant, ar, ja, es, vi, th`，交给
   `scripts/i18n_batch_util.py::apply_rows(rows, batch)` 合并进 `i18n_seed.json`——它会强校验 key 格式、8 语非空、占位符集合、源文冲突。**不要手改 JSON**。
2. **外部译员交付**：在原始词条表基础上加目标语言列 + `status` + `remark`，文件名 `{原文件名}_{目标语言}_translated.xlsx`。原始文件全程只读。

另附**人工复核清单**，只列需要人看的：`TERM-CANDIDATE`、`CONFIDENCE: LOW`、超长未解决项、术语漂移修正、RTL 混排异常、`LEGAL-REVIEW`。

### 第 8 步：落盘与发布

```bash
python scripts/seed_i18n.py            # 灌库并发布新版本（version 单调递增，可回滚）
npm run check:i18n                     # 提取校验 + RTL 静态检查
npm run build -w web                   # 字体门禁 + i18n 门禁 + vite build
```

三条硬提醒：

- **新增 zh-CN 源文会撞字体门禁**：代码里（不是词表里）多写一个 MiSans 子集外的汉字，`font-coverage` 直接构建失败。能改文案就改文案，必须新增就走 `FONT-NOTICE.md` 的子集重建流程，字符集与字体一起提交。
- **阿语至少截一张图**：RTL 问题在中文界面完全看不出来（`scripts/capture_i18n_*.mjs` 可复用）。
- **简繁不许 OpenCC**：两列独立维护，`zh-Hant` 与 `zh-CN` 同形率过高会被门禁告警。

## 边界与红线

- 不翻译单证编号、HS 编码、港口代码、金额数值、日期格式中的固定部分、API Key、代码块。
- 信用证条款、法律声明类文本不做「创造性」翻译：标 `LEGAL-REVIEW` 并停下等人工。
- 不擅自缩写 Incoterms 或监管证件名称，不把占位符「翻译」成目标语言词汇。
- 阿拉伯语数字必须是西方数字（`0-9`），禁用 `٠١٢`；单号类值不得因 RTL 被重排。
- 简繁互转产出「繁体字形 + 大陆用词」视为失败。
- 术语表未定义且无法从官方来源确认的术语，不进交付译文。
- **不改业务逻辑**：本技能只产出词条与校验，不动 props / state / 请求 / 校验流程。

## 外部复核（译法不准时的升级路径）

遇到以下情况，调用跨境本地化翻译专家（`lingua-translator`）复核，再落盘：

- 行业叫法存在地区分歧（如「归集」的英文用 Grouping 还是 Consolidation）
- 目标语种里同一概念有两种常用说法，且本项目未定口径
- 阿拉伯语、泰语等非通用语种的字面直译读起来生硬
- 单证字段名在该语种的海运单证实物上另有惯用写法

复核结论必须回写 `terminology.md`（连同依据），不要只在对话里说一次。

## 自检（输出前执行）

1. 每个 key 的 `{{}}` 占位符集合是否与 zh-CN 完全一致？
2. 8 个语种是否都非空、且没有一个是「复制源文」？
3. 锁定术语是否全部按 `terminology.md` 出现，没有第二种说法？
4. 每个目标语种是否都过了其专属规则（`ar` RTL、`zh-Hant` 用词、`ja` 简体词、`es` 变体、`vi` 声调、`th` 断行）？
5. 超长行是否都有缩短方案或进了复核清单？
6. key 是否静态字面量、符合 `[a-z0-9_.]+` 且至少两段？
7. 原始词条文件、代码文件是否未被本流程改动（除被点名的 `t()` 调用）？
