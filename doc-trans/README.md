# doc-trans

> 跨境物流单证系统的**界面**多语言翻译技能。8 语种、术语锁定、占位符保真、长度与发布门禁校验，产出可直接回填词表的译文。

---

## 它是什么

一个给 AI 用的翻译工作流技能（Skill）。它把「跨境物流单证系统界面文案」的翻译，从"翻一遍就交"变成一条**带关卡的流水线**：

```
术语锁定 → 结构保真 → 语种专属规则 → 长度与门禁校验 → 合规复核
```

**它不是通用翻译器。** 单证界面不同于普通文案：术语不一致会让操作员把「通知人」和「收货人」看混；丢一个 `{{count}}` 占位符会让页面显示 `undefined`；阿拉伯语不加隔离会让集装箱号 `OOLU8882850350` 重排成乱码；简繁产出"繁体字形 + 大陆用词"等于交了一份假繁体。

**术语库来自真实上线系统**，不是示例数据：从一套跨境物流单证智能体（提单 / 发票 / 装箱单 / 报关单 / 订舱单的识别与一致性校验）的现网词表 **1429 key × 8 语**中提炼，并经跨境本地化专家逐条复核。

### 支持语种

| 语种 | code | 专属红线 |
|---|---|---|
| 简体中文 | `zh-CN` | 源语言；`t('key','源文')` 第二参必须与代码字面量一字不差 |
| 英文 | `en` | 长度基准与缩写宿主；Incoterms 不译不扩写 |
| 繁体中文 | `zh-Hant` | **术语替换，不是字形映射**；禁止「繁体字形 + 大陆用词」 |
| 越南语 | `vi` | 声调符号完整保留，禁止降级为无调 ASCII |
| 泰语 | `th` | 无词间空格，禁止按空格断行 |
| 日语 | `ja` | 按钮用惯用 UI 语（送信/保存/戻る）；禁止混入简体中文词 |
| 阿拉伯语 | `ar` | RTL 双向文本；西方数字；单号/金额强制 `direction:ltr` |
| 西班牙语 | `es` | 锁定变体（es-ES / es-419），禁止混用 |

---

## 目录结构

```
doc-trans/
├── SKILL.md                      # 总调度：8 步流程、语种红线、边界与自检
├── README.md                     # 本文件
├── scripts/
│   └── validate_ui_strings.py    # 校验器（CLI，可直接跑）
└── references/
    ├── terminology.md            # 锁定译文表（8 语字段/状态/动作 + 保留原文项 + 待修清单）
    ├── glossary.md               # 领域词义词典（业务词汇的英文全称/中文含义/使用场景）
    ├── languages.md              # 各语种专属规则
    └── qa-rules.md               # QA 规则 ↔ 脚本 code 对照表
```

**调用关系**（谁读谁）：

```
SKILL.md  ← 总调度，指示 AI 去读下面四份 + 跑脚本
   ├─ glossary.md      （AI 翻译前查"词义边界"，只读）
   ├─ terminology.md   （AI 取"锁定译文"；校验脚本解析它做一致性巡检）
   ├─ languages.md     （语种规则）
   └─ qa-rules.md      （规则 ↔ code 对照）

scripts/validate_ui_strings.py  ← 独立 CLI，只解析 terminology.md，不读 glossary.md
```

> 词典管"懂不懂"，锁定表管"翻得对不对"，脚本管"有没有违规"。三者职责分离。

---

## 快速开始

### 安装

把整个文件夹拷到用户级技能目录即可全局生效：

```bash
cp -r doc-trans ~/.workbuddy/skills/
```

之后在对话里说「翻译界面」「UI string 翻译」「泰文/日文/阿拉伯语界面」「简繁转换」「单证系统词条翻译」即可触发。

### 最小用法

```bash
# 1) 校验一份已有词表
python scripts/validate_ui_strings.py --seed path/to/i18n_seed.json

# 2) 顺带做术语一致性巡检
python scripts/validate_ui_strings.py --seed path/to/i18n_seed.json \
                                      --terms references/terminology.md

# 3) 单条自检（改某一条译文时最快）
python scripts/validate_ui_strings.py --check-pair "共 {{count}} 个文件" "{{count}} ไฟล์" --locale th
```

退出码：有阻断项即为 `1`，可直接接 CI。

---

## 怎么用

### 三种输入方式

| 方式 | 命令 | 用途 |
|---|---|---|
| 仓库词表 | `--seed i18n_seed.json` | 结构 `{entries:{key:{locale:value}}}`，最常用 |
| 外部长表 | `--rows table.tsv` | 9 列 `key / zh-CN / en / zh-Hant / ja / th / es / ar / vi`，外部译员协作 |
| 单条 | `--check-pair "源" "译" --locale xx` | 改一条查一条 |

### 常用参数

```
--terms <md>          术语表，做一致性巡检
--locales en,ja       只校验指定语种
--ratio-profile       长度口径：layout（默认，p95 实测）| server（1.8× 服务端门禁）
--max-len en=24       按语种设绝对字符上限
--json <out.json>     导出全量报告（给 CI / 给人工复核清单）
--max-detail N        终端最多打印 N 条明细
--no-dupes            跳过"同源多译"统计
--strict              阻断项非零即退出码 1
```

### 长度判据（这是本技能最反直觉的一点）

界面长度**不能按 1.8× 判**。实测拉丁语系与泰/阿/越语种的中位数就在 2.7–3.8 倍，按 1.8× 会把 80% 以上的正常译文标红。

| 语种 | 中位数区间 | 脚本阈值（p95 硬限） |
|---|---|---|
| `zh-Hant` | 100%–110% | 1.3× |
| `ja` | 100%–130% | 2.4× |
| `en` / `th` / `ar` | 150%–200% | 4.4× |
| `vi` | 150%–200% | 4.7× |
| `es` | 150%–200% | 5.6× |

超限时**优先给缩短方案**（换短词、去冗余量词、拆句），不硬截断、不用省略号糊弄。物理约束（按钮固定宽、列宽）优先于规则。

### 校验规则速查

| 级别 | code | 含义 |
|---|---|---|
| 阻断 | `EMPTY_VALUE` | 译文为空 / 是 key 本身 |
| 阻断 | `PLACEHOLDER_MISMATCH` | `{{}}` 占位符集合与源文不一致 |
| 阻断 | `HTML_TAG` / `NEWLINE_IN_VALUE` | 译文含 HTML 或换行 |
| 阻断 | `CJK_IN_LATIN` | 拉丁语系译文里夹汉字（漏译） |
| 阻断 | `TH_NO_THAI` | 泰语列不含泰文字符 |
| 阻断 | `AR_ARABIC_DIGITS` | 阿语用了 `٠١٢` 而非西方数字 |
| 阻断 | `JA_SIMPLIFIED_WORD` | 日文混入简体中文词 |
| 阻断 | `HANT_MAINLAND_WORD` | 繁体出现大陆用词（保存→儲存、信息→資訊…） |
| 告警 | `TOO_LONG` | 超过语种长度阈值 |
| 告警 | `TERM_DRIFT` | 术语未按锁定表译 |
| 告警 | `INCONSISTENT_TRANSLATION` | 同一源文出现两种译法 |
| 告警 | `AR_BIDI_RISK` / `VI_NO_DIACRITICS` / `ES_VARIANT_MIX` | 语种专属风险 |

---

## 什么场景用

### 适用

- 新增界面文案的八语种译法生成
- 已有译文的**术语一致性巡检与漂移修正**
- 简繁中文术语库对齐（**禁止 OpenCC 自动转换**）
- 单证模板固定字段名的多语言对齐
- Excel / CSV 词条表的外部译员协作与回表校验
- 接 CI：阻断项非零即失败

### 不适用

- 整段法律条款的认证翻译（需持证译员签章）→ 标 `LEGAL-REVIEW` 停下
- 营销文案的创意本地化
- 单证原件内容与 OCR 原文（属「不翻译」边界）
- **商务文本**（订舱邮件、报价单、合同、信用证、海外仓 SOP、平台 Listing）→ 用配套的 **crossborder-trade-translator（贸译通）** 商务翻译 Agent（独立文件，与本技能同仓库 `docs/agents/` 目录，安装到 `~/.workbuddy/skills/crossborder-trade-translator/` 即可调用）

### 与商务翻译 Agent 的分工

| | 本技能（界面词条） | 商务翻译 Agent（商贸文本） |
|---|---|---|
| 对象 | UI 字符串（按钮/表头/Toast/菜单） | 邮件、单证、合同、SOP、Listing |
| 单位 | 一条一个 key，8 语对齐 | 段落/篇章，保留条款结构 |
| 语域 | 简洁、术语固定、惯用 UI 语 | 按场景分档（正式/商务/指令/口语/本地化） |
| 产出 | 回填词表的 9 列行 | 译文 + 术语表 + 风险标注 |

---

## 边界与红线

- 不翻译单证编号、HS 编码、港口代码、金额数值、日期固定部分、API Key、代码块。
- 信用证条款、法律声明标 `LEGAL-REVIEW` 并停下等人工。
- 不擅自缩写 Incoterms 或监管证件名称；不把占位符"翻译"成目标语言词汇。
- 阿拉伯语数字必须是西方数字 `0-9`；**不手动插 U+2068/U+2069**（隔离交给容器 `direction:ltr; unicode-bidi:isolate`，手动插会污染复制粘贴与导出），仅纯文本通道例外。
- 简繁互转产出「繁体字形 + 大陆用词」视为失败。
- 术语表未定义且无法从官方来源确认的术语 → 标 `TERM-CANDIDATE`，不进交付译文。
- 本技能只产出词条与校验，**不改业务逻辑、不动 props/state/请求/校验流程**。

---

## 维护

### 换成你自己的术语库

`references/terminology.md` 的锁定表是从真实项目抽的快照。**换成你项目的官方术语库时，`SKILL.md` 主流程无需改动**——脚本按 markdown 表格解析，列头保持 `key / zh-CN / en / zh-Hant / ja / th / es / ar / vi` 即可。

### 扩展语种

1. `languages.md` 增一节（专属规则 + 长度基准）
2. `SKILL.md` 语种表加一行
3. `qa-rules.md` 的 R7 补一句
4. 脚本的 `RATIO_LIMIT`、`LOCALES` 加一项

主流程保持稳定。

### 已知待办

`terminology.md` §8 记录了一批**现网真实错译**（如阿语「封条号」误译为"绳号"、西语「发货人」用了快递口径、泰语「报关单」用了泛称、「拼柜」被译成 Pallet），已定位但未修改源词表——按 P0/P1/P2 排期处理，修改走批量合并脚本，不手改 JSON。

---

## 许可与来源

从真实跨境物流单证 SaaS 项目的界面本地化工程提炼，术语与阈值均来自实测数据（1429 key × 8 语）。可自由 Fork 改造，建议替换 `references/terminology.md` 为你自己的术语库后再投入生产。
