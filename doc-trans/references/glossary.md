# 跨境物流单证领域术语词典（Glossary）

> **本文件的角色**：领域「词义词典」，供 AI 翻译界面文案时**确认概念边界与含义**，避免望文生义、把近似词翻错。
>
> **它不是翻译表**。界面 8 语种的最终译文以 `terminology.md`（锁定表）与 `apps/api/data/i18n_seed.json`（生产词表）为准；本文件只负责"这个词到底指什么"。
>
> **使用顺序（见 SKILL.md「文件关系」）**：
> 1. 看到界面文案里出现某个业务词 → 先查本文件确认它是什么、和哪个词容易混；
> 2. 再到 `terminology.md` 取该概念的锁定 8 语译文；
> 3. 遵守 `languages.md` 的语种专属规则；
> 4. 用 `scripts/validate_ui_strings.py` 校验。
>
> **别乱改原则**：本文件与 `terminology.md` 都是只读参考。词义确认后**只引用锁定译文**，绝不自己编 8 语译法；遇到本词典与锁定表冲突或本词典未覆盖的概念，标 `TERM-CANDIDATE` 或调跨境本地化翻译专家（`lingua-translator`）复核，不要静默改 `i18n_seed.json`。

---

## 1. 核心单据与文件

- **订舱号（Booking Number）**：订舱成功后船公司给的编号，用于提柜、报关、追踪。
- **提单号（B/L Number）**：提单上的唯一编号，用于提货、转让货权、结算。
- **提单（B/L，Bill of Lading）**：海运物权凭证，兼货物收据、运输合同证明。
- **订舱单（S/O，Shipping Order）**：船公司确认订舱后的操作文件，用于提柜、报关。⚠️ 注意：**S/O 即装货单/订舱单**，不是「订舱委托书」。
- **订舱确认书（Booking Confirmation）**：与 S/O 本质相同，不同地区叫法。
- **订舱委托书（Booking Note）**：发货人/货代向船公司**申请舱位**的委托文件（需求方填写，≠ 船公司回发的 S/O）。
- **主提单（MBL，Master Bill of Lading）**：船公司签发，可直接换 D/O 提货。
- **货代提单（HBL，House Bill of Lading）**：货代签发，需换 MBL 才能提货。
- **提货单（D/O，Delivery Order）**：目的港凭提单换取的提货指令。
- **补料（SI，Shipping Instructions）**：发货人给船公司的**提单内容确认文件**。
- **配载单（Stowage Plan / Manifest）**：船公司/码头内部货物装载明细清单。
- **报关资料（Customs Declaration Documents）**：出口报关所需全套文件。
- **出口货物报关单（Customs Declaration）**：向中国海关申报出口的核心单据。
- **商业发票（Commercial Invoice）**：报关、清关、结算用货物价值证明。
- **装箱单（Packing List）**：列明件数、毛重、净重、体积等。
- **外贸合同（Contract）**：买卖双方交易合同，报关随附。
- **报关委托书（Customs Power of Attorney）**：委托报关行报关的授权文件。
- **出境货物通关单**：法检商品出口所需。
- **出口许可证**：管制商品出口所需。
- **放行条（Customs Release Notice）**：海关放行后允许装船的凭证。
- **装货单（Shipping Order）**：船公司指示码头装货的单据（即 S/O）。
- **大副收单（Mate's Receipt）**：装船后大副签发，用于换提单。
- **场站收据**：货物交到场站后出具的收据。
- **提单草稿（Draft B/L）**：船公司根据 SI 出具的提单确认稿。
- **设备交接单（EIR，Equipment Interchange Receipt）**：提柜/还柜时箱体交接凭证。
- **采购订单（PO，Purchase Order）**：客户下单文件。
- **形式发票（PI，Proforma Invoice）**：卖方给买方的确认/报价文件。
- **销售确认书（S/C，Sales Confirmation）**：确认订单细节的销售文件。
- **VGM 申报表（VGM Submission Form）**：提交集装箱验证总重的表格。
- **ISF 申报表**：美国进口商安全申报表。
- **AMS 申报表**：美国反恐舱单申报表。
- **ACI 申报表**：加拿大预申报表。
- **ENS 申报表**：欧洲入境摘要申报表。
- **进口货物报关单（Import Declaration）**：目的港清关核心单据。
- **查验通知单**：海关要求查验的通知。
- **税单（Customs Duty Memo）**：关税/增值税缴纳凭证。
- **海关放行通知（Customs Release Notice）**：目的港海关放行凭证。
- **海运单（Sea Waybill）**：非物权凭证，收货人凭身份提货。
- **电子提单（EBL，Electronic Bill of Lading）**：电子化提单，可在线转让。
- **电放（Telex Release）**：电子放货，无需正本提单。
- **目的港出单**：正本提单在目的港签发。
- **报关代理开**：由报关代理开具/操作放货。
- **BOL（Bill of Lading）**：海外仓自提中的提单/交接合同。
- **航空主运单（MAWB，Master Air Waybill）**：航空公司签发的空运主单。
- **航空分运单（HAWB，House Air Waybill）**：货代签发的空运分单。
- **航空运单（AWB，Air Waybill）**：空运总称，非物权凭证。
- **托运委托书（Shipper's Letter of Instruction）**：空运发货人委托书。
- **订舱申请单（Booking Request）**：空运向航空公司申请舱位。
- **舱位确认书（Booking Confirmation）**：空运舱位确认。
- **入仓单（Warehouse Receipt）**：空运货物入仓交接单。
- **安检放行单**：空运安检通过凭证。
- **集装器装配清单（ULD Build-up Sheet）**：空运打板/组板清单。
- **装载舱单（Load Sheet）**：航班装载明细。

> **易混点**：订舱委托书（Booking Note，申请用）≠ 订舱单/装货单（S/O，船公司回发）；MBL/HBL 是提单层级，D/O 是提货凭证；EBL 保留物权，Sea Waybill 不保留。

## 2. 时间节点与截止时间

- **截 VGM（VGM Cut-off）**：提交集装箱验证总重的截止时间，最早。
- **截单（SI Cut-off）**：提交补料、确认提单的截止时间，中间。
- **截关（Customs Cut-off）**：报关放行的截止时间，最晚。
- **CY Closing**：码头截关时间。
- **DOC Closing**：文件截单时间。
- **ETD（Estimated Time of Departure）**：预计开船时间。
- **装船前 24 小时**：AMS/ISF/ENS 等安全申报截止。
- **截 VGM 时间前 / 截单时间前 / 截关时间前**：必须分别完成 VGM 提交 / SI 提交 / 报关放行。

> 界面常把三者合成一个标签或分三条状态，翻译时要保持「VGM / 单 / 关」三者的区分，不要合并成一个"截止"。

## 3. 费用、付款与贸易术语

- **Prepaid（预付）**：运费预付，发货人在起运港支付。
- **Collect（到付）**：运费到付，收货人在目的港支付。
- **FREIGHT PREPAID / FREIGHT COLLECT / FREIGHT PAYABLE AT**：提单/配载单上运费支付状态的显示。
- **Incoterms（International Commercial Terms）**：国际贸易术语解释通则。
- **FOB（Free On Board）**：装运港船上交货，买方订舱，运费到付。
- **CIF（Cost, Insurance and Freight）**：卖方负责成本+保险+运费，运费预付。
- **CFR（Cost and Freight）**：卖方负责成本+运费，不含保险。
- **EXW（Ex Works）**：工厂交货，买方全权安排。
- **FCA（Free Carrier）**：货交承运人。
- **CIP（Carriage and Insurance Paid To）**：运费+保险付至目的地。
- **CPT（Carriage Paid To）**：运费付至目的地。
- **DAP（Delivered At Place）**：目的地交货。
- **DPU（Delivered at Place Unloaded）**：目的地卸货后交货。
- **DDP（Delivered Duty Paid）**：完税后交货。
- **PSS（Peak Season Surcharge）**：旺季附加费。
- **改单费 / 漏装费 / 滞箱费 / 仓储费 / 掏箱费 / 等候费**：截单后改单、错过截关、超期用箱、港/仓超期、查验掏箱、卡车等待等产生的费用。
- **第三方支付 / 别处支付**：运费由第三方 / 在起运港或目的港以外地点支付。

> **Incoterms 一律保留英文缩写，不译不扩写**（见 `terminology.md` §6）。

## 4. 放货方式

- **正本**：凭纸质正本提单提货。
- **电放（Telex Release）**：电子放货，无需正本；电放时需在正本背面背书并交回船公司。
- **SEAWAY BILL（海运单）**：非物权凭证，凭身份提货。
- **EBL（电子提单）**：保留物权凭证功能。
- **目的港出单 / 报关代理开**：在目的港签发正本 / 由报关代理操作放货。

## 5. 安全申报与海关系统

- **AMS（Automated Manifest System）**：美国自动舱单系统，装船前 24 小时申报。
- **ISF（Importer Security Filing）**：美国进口商安全申报，俗称"10+2"。
- **ACI（Advance Commercial Information）**：加拿大预申报。
- **ENS（Entry Summary Declaration）**：欧洲入境摘要申报。
- **10+2**：ISF 的 10 项进口商信息 + 2 项船公司信息。
- **1Y / 3Z / S1**：AMS 匹配成功回执 / ISF 与 AMS 匹配成功回执 / ISF 申报完成状态。
- **CBP（U.S. Customs and Border Protection）**：美国海关与边境保护局。
- **CBSA（Canada Border Services Agency）**：加拿大边境服务局。
- **EORI（Economic Operators Registration and Identification）**：欧盟经济运营商注册识别号。
- **EIN（Employer Identification Number）**：美国雇主识别号。
- **Bond（保证金）**：美国进口商保证金。
- **SCAC Code（Standard Carrier Alpha Code）**：承运人标准数字代码。
- **HTS 编码（Harmonized Tariff Schedule）**：美国协调关税表编码。
- **HS 编码（Harmonized System）**：国际协调制度编码。
- **海关 10 位编码**：中国海关商品编码。
- **SOLAS（International Convention for the Safety of Life at Sea）**：国际海上人命安全公约，VGM 依据。
- **NVOCC（Non-Vessel Operating Common Carrier）**：无船承运人。
- **报关行 / 海关 / 清关申报 / 清关放行 / 出口报关 / 目的港清关**：代理报关企业 / 进出境监管机关 / 目的港进口申报 / 目的港海关放行 / 中国出口申报 / 进口国清关。

> **HS 编码、UN/LOCODE、SCAC、EORI、EIN、AMS/ISF/ACI/ENS 缩写均保留原文不译**（见 `terminology.md` §6）。

## 6. 集装箱、重量与设备

- **柜号（Container No.）**：集装箱唯一编号，如 `MSDU6467076`。
- **封号 / 铅封号（Seal No.）**：锁在箱门上的一次性锁扣编号，如 `FJ28430244`。
- **柜重（Tare Weight）**：集装箱皮重。
- **柜型**：20GP / 40GP / 40HQ(40HC) 等。
- **VGM（Verified Gross Mass）**：集装箱验证总重。
- **整体称重法（Method 1）/ 累加计算法（Method 2）**：整柜过磅 / 货物+包装+皮重累加。
- **误差 ±5% / 1 吨**：VGM 允许误差 / 绝对误差上限。
- **重出空回 / 重出重回**：重柜出去空柜回来 / 重柜出去再装重柜回来。
- **提空柜 / 装柜 / 还柜 / 做柜时间 / 装货地点**：提取空箱 / 装货入箱 / 归还空箱 / 装柜作业时间 / 装柜地点。
- **工厂名称 / 客户编号 / 车牌 / 司机 / 司机手机号**：拖车相关主体信息。

> 柜号、封号、VGM 数值**原样透传不译**；阿语等 RTL 环境靠容器 `direction:ltr; unicode-bidi:isolate` 防重排。

## 7. 流程与操作术语

- **订舱 / 配舱 / 配载 / 提柜 / 装船 / 开船 / 签发提单**：向船公司申请舱位 / 预订舱位 / 安排装载位置 / 提取集装箱 / 货物装上船 / 船舶离港 / 船公司出具提单。
- **目的港提柜 / 补料 / 报关 / 清关 / 放行**：收货人目的港提箱 / 提交 SI / 向中国海关申报出口 / 目的港进口申报 / 海关允许装船或提货。
- **截单 / 截关 / 截 VGM**：SI 截止 / 报关放行截止 / VGM 截止。
- **预配舱单 / 清洁舱单**：装船前预申报舱单 / 装船后最终舱单。
- **装机单 / 打板·组板 / 安检**：空运装载计划 / 货物装入 ULD / 空运必检。
- **体积重 / 计费重量**：空运计费重（长×宽×高/6000）/ 体积重与实际毛重取大值。
- **FTL（Full Truck Load）/ LTL（Less Than Truck Load）**：整车 / 零担。
- **拼箱（LCL）/ 整箱（FCL）**：不足整箱拼箱运输 / 整箱运输。
- **LA/LB（Los Angeles / Long Beach）/ 美西 / 美东**：洛杉矶港/长滩港 / 美国西海岸 / 美国东海岸。
- **旺季 / 夏秋旺季（7–10 月）/ 春节前旺季（1–2 月）**：货运高峰期。

## 8. 空运特有术语

- **ULD（Unit Load Device）**：航空集装器（集装板/集装箱）。
- **MAWB / HAWB / AWB**：航空主运单 / 航空分运单 / 航空运单（非物权凭证）。
- **体积重 / 计费重量**：长×宽×高(cm)/6000 / 体积重 vs 实际毛重取大。
- **安检 / 打板·组板 / 航班截关时间**：空运必检 / 货物装入 ULD / 空运综合截止节点。
- **凭身份提货**：空运收货人凭身份证明提货，无需正本运单。

## 9. 角色、主体与代码

- **发货人（Shipper）/ 收货人（Consignee）/ 通知人（Notify Party）**：出口方 / 进口方 / 到货通知方。
- **承运人（Carrier）/ 货代（Freight Forwarder）/ 船公司 / 报关行 / 拖车公司**：海运/空运承运人 / 货运代理 / 海运承运人 / 代理报关企业 / 陆运承运人。
- **堆场 / 码头 / 美国进口商 / 美国海关（CBP）/ 加拿大 CBSA / 欧洲海关**：集装箱堆存场 / 港口作业区 / ISF 申报主体 / AMS·ISF 监管方 / ACI 监管方 / ENS 监管方。
- **NVOCC / 卡车公司 / 海外仓 / 亚马逊（Amazon）/ Wayfair**：无船承运人 / 海外仓自提承运人 / 境外仓储 / BOL 场景电商平台 / BOL 场景电商平台。
- **SCAC / EORI / EIN / Bond**：承运人标准代码 / 欧盟经营者注册号 / 美国雇主识别号 / 美国进口保证金。

> 当事人译法见 `terminology.md` §2.1（Shipper→Cargador、Consignee→Consignatario、Notify party→Parte a notificar 等已锁定）。

## 10. 其他缩写与概念速查

| 缩写 | 全称 / 含义 |
|---|---|
| Booking Confirmation = S/O | 同一文件不同叫法 |
| B/L Number = Bill of Lading Number | 提单号全称 |
| MBL / HBL | 主提单 / 货代提单 |
| D/O | 提货单 |
| SI | 补料（Shipping Instructions） |
| VGM | 核实总重（Verified Gross Mass） |
| ISF / AMS / ACI / ENS | 进口商安全申报 / 美国自动舱单 / 加拿大预申报 / 欧洲入境摘要 |
| EBL | 电子提单 |
| Sea Waybill | 海运单 |
| BOL | 提单（海外仓自提） |
| Prepaid / Collect | 预付 / 到付 |
| Incoterms | 国际贸易术语 |
| LA/LB | 洛杉矶 / 长滩港 |
| PSS | 旺季附加费 |
| SOLAS | 国际海上人命安全公约 |
| NVOCC | 无船承运人 |
| FTL / LTL | 整车 / 零担 |
| EIR | 设备交接单 |
| PO / PI / S/C | 采购订单 / 形式发票 / 销售确认书 |
| ULD | 航空集装器 |
| MAWB / HAWB / AWB | 空运主单 / 分单 / 运单 |
| HTS / HS | 关税编码 / 商品协调编码 |
| SCAC / EORI / EIN / Bond | 承运人标准代码 / 欧盟税号 / 美国税号 / 进口保证金 |
| 1Y / 3Z / S1 | AMS / ISF 匹配回执 |

---

## 11. 覆盖策略（如何"译得全、译得准、不乱改"）

1. **词义先确认**：遇到不确定的业务词，先查本词典 §1–§10 确认它指什么、与哪个词易混（如 Booking Note ≠ S/O）。
2. **译文取锁定值**：该概念若已在 `terminology.md` 有 8 语锁定值，**直接用**，不重新翻译；若只在 `i18n_seed.json` 有而 `terminology.md` 未列，以词表为准并补进 `terminology.md`。
3. **保留原文项不译**：Incoterms、HS/UN-LOCODE/SCAC/EORI/EIN、柜号/封号/单号、AMS/ISF/ACI/ENS 缩写、金额数字——全部原样透传（见 `terminology.md` §6）。
4. **撞车概念必分家**：归集 ≠ 拼柜、毛重 ≠ 合计毛重、成交方式 ≠ 贸易方式、单证 ≠ 附件——见 `terminology.md` §5，一个概念只锁一个 canonical 译法。
5. **拿不准就升级**：本词典与锁定表都未覆盖、或存在地区分歧 → 标 `TERM-CANDIDATE` 或调 `lingua-translator` 专家复核，结论回写 `terminology.md`，**绝不静默改词表**。
6. **只产出词条，不改业务**：本技能产出译文经 `i18n_batch_util.py` 合并进 `i18n_seed.json`，不手改 JSON、不动 props/state/请求/校验逻辑。
