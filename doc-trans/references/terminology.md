# 跨境物流单证界面术语约束表

> **权威源与更新规则**
> 1. 生产词表：`apps/api/data/i18n_seed.json`（1429 key × 8 语）。
> 2. 字段唯一事实源：`apps/api/services/doc_fields.py::FIELD_SPECS`（75 个字段 key）。
> 3. 本文件是「锁定口径」，冲突时以本文件为准并回头修词表——本文的**字段名与时态词已由跨境本地化翻译专家逐条复核**，带 `⚠️` 的行是「现网词表与建议口径不一致、待修」项，见 §8。
> 4. 下表所有 `key` 型表格（9 列）会被 `scripts/validate_ui_strings.py --terms` 解析为**锁定术语**做一致性巡检；其它表格不参与机器校验。

## 1. 单证类型（最高频、最易错）

| key | zh-CN | en | zh-Hant | ja | th | es | ar | vi |
|---|---|---|---|---|---|---|---|---|
| doc_type.bl | 提单 | Bill of lading | 提單 | 船荷証券 | ใบตราส่ง | Conocimiento de embarque | بوليصة الشحن | Vận đơn |
| doc_type.invoice | 发票 | Invoice | 發票 | インボイス | ใบแจ้งหนี้ | Factura | فاتورة | Hóa đơn |
| doc_type.packing_list | 装箱单 | Packing list | 裝箱單 | パッキングリスト | ใบรายการบรรจุหีบห่อ | Lista de empaque | قائمة التعبئة | Bảng kê đóng gói |
| doc_type.customs | 报关单 | Customs declaration | 報關單 | 通関申告書 | ใบขนสินค้า | Declaración aduanera | بيان جمركي | Tờ khai hải quan |
| doc_type.booking | 订舱单 | Booking note | 訂艙單 | ブッキングノート（B/N） | ใบจองระวาง | Nota de reserva | إشعار الحجز | Đơn đặt chỗ |

要点：

- 泰语「报关单」必须是 `ใบขนสินค้า`（泰国海关法定名称），`ใบศุลกากร` 是"海关的表格"泛称，会被操作员误解成别的表。
- 泰语「装箱单」要带量词 `ใบ`，缺了就成了描述短语而不是单证名。
- 日语「订舱单」不是 `ブッキング`（那是订舱这个动作/记录），单证名是 `ブッキングノート`。
- 越南语「装箱单」用 `Bảng kê đóng gói`，`Phiếu đóng gói` 是电商打包单。

## 2. 单证字段名（按 B/L 与报关单两组）

### 2.1 当事人与运输段

| key | zh-CN | en | zh-Hant | ja | th | es | ar | vi |
|---|---|---|---|---|---|---|---|---|
| field.shipper | 发货人 | Shipper | 發貨人 | 荷送人 | ผู้ส่งสินค้า | Cargador | الشاحن | Người gửi hàng |
| field.consignee | 收货人 | Consignee | 收貨人 | 荷受人 | ผู้รับสินค้า | Consignatario | المرسل إليه | Người nhận hàng |
| field.notify_party | 通知人 | Notify party | 通知人 | 通知先 | ผู้รับแจ้ง | Parte a notificar | الطرف المُخطَر | Bên thông báo |
| field.forwarding_agent | 转运代理 / Apply To | Forwarding agent / Apply To | 轉運代理 / Apply To | 転送代理 / Apply To | ตัวแทนขนส่ง / Apply To | Agente de tránsito / Apply To | وكيل الشحن / Apply To | Đại lý chuyển tải / Apply To |
| field.vessel_voyage | 船名航次 | Vessel and voyage | 船名航次 | 船名・航海番号 | ชื่อเรือและเที่ยวเรือ | Buque y viaje | السفينة والرحلة | Tên tàu và chuyến |
| field.port_of_loading | 装货港 | Port of loading | 裝貨港 | 積出港 | ท่าเรือต้นทาง | Puerto de carga | ميناء التحميل | Cảng xếp hàng |
| field.port_of_discharge | 卸货港 | Port of discharge | 卸貨港 | 揚陸港 | ท่าเรือปลายทาง | Puerto de descarga | ميناء التفريغ | Cảng dỡ hàng |
| field.place_of_receipt | 装货地 / 收货地 | Place of receipt | 裝貨地 / 收貨地 | 受取地 | สถานที่รับสินค้า | Lugar de recepción | مكان الاستلام | Nơi nhận hàng |
| field.place_of_delivery | 交货地 | Place of delivery | 交貨地 | 引渡地 | สถานที่ส่งมอบ | Lugar de entrega | مكان التسليم | Nơi giao hàng |
| field.final_destination | 最终目的港 | Final destination | 最終目的港 | 最終仕向地 | ปลายทางสุดท้าย | Destino final | الوجهة النهائية | Đích cuối cùng |
| field.carrier_name | 船公司 / 承运人 | Carrier | 船公司 / 承運人 | 船会社 / 運送人 | สายเรือ / ผู้ขนส่ง | Naviera / transportista | الناقل | Hãng tàu / người vận chuyển |

> 西语 `Shipper` 栏位行业固定用 `Cargador`（拉美也用 `Embarcador`）；`Remitente` 是快递寄件人，货代场景会被读错。
> 西语 `Notify party` 是 `Parte a notificar`；`Parte notificada` 是"已被通知的一方"，语感被动错位。
> 阿拉伯语 `Consignee` 锁 `المرسل إليه`，不要再混用 `جهة الاستلام`。

### 2.2 货物、集装箱与金额

| key | zh-CN | en | zh-Hant | ja | th | es | ar | vi |
|---|---|---|---|---|---|---|---|---|
| field.goods | 品名描述 | Goods description | 品名描述 | 品名説明 | คำอธิบายสินค้า | Descripción de mercancía | وصف البضاعة | Mô tả hàng hóa |
| field.marks_and_numbers | 唛头 | Marks and numbers | 嘜頭 | 荷印・番号 | เครื่องหมายและหมายเลข | Marcas y números | العلامات والأرقام | Ký mã hiệu và số hiệu |
| field.packages | 件数 | Packages | 件數 | 個数 | จำนวนหีบห่อ | Bultos | عدد الطرود | Số kiện |
| field.packages_in_words | 大写件数 | Packages in words | 大寫件數 | 個数（英字） | จำนวนหีบห่อเป็นตัวอักษร | Bultos en letras | عدد الطرود كتابةً | Số kiện bằng chữ |
| field.gross_weight | 毛重 | Gross weight | 毛重 | グロス重量 | น้ำหนักรวม | Peso bruto | الوزن الإجمالي | Trọng lượng cả bì |
| field.total_gross_weight | 合计毛重 | Total gross weight | 合計毛重 | 合計総重量 | น้ำหนักรวมทั้งหมด | Peso bruto total | إجمالي الوزن | Tổng trọng lượng cả bì |
| field.net_weight | 净重 | Net weight | 淨重 | 正味重量 | น้ำหนักสุทธิ | Peso neto | الوزن الصافي | Trọng lượng tịnh |
| field.measurement | 体积 | Volume | 體積 | 容積 | ปริมาตร | Volumen | الحجم | Thể tích |
| field.total_measurement | 合计体积 | Total volume | 合計體積 | 合計容積 | ปริมาตรรวม | Volumen total | الحجم الإجمالي | Tổng thể tích |
| field.container_no | 集装箱号 | Container No. | 貨櫃號 | コンテナ番号 | หมายเลขตู้คอนเทนเนอร์ | N.º de contenedor | رقم الحاوية | Số container |
| field.seal_no | 封条号 | Seal No. | 封條號 | シール番号 | หมายเลขซีล | N.º de precinto | رقم الختم | Số niêm phong |
| field.container_type_qty | 箱型箱量 | Container type and quantity | 箱型箱量 | コンテナ種別・本数 | ประเภทและจำนวนตู้ | Tipo y número de contenedores | نوع الحاوية وعددها | Loại và số lượng container |
| field.hs_code | HS编码 | HS code | HS 編碼 | HS コード | รหัส HS | Código HS | رمز HS | Mã HS |
| field.quantity | 数量 | Quantity | 數量 | 数量 | ปริมาณ | Cantidad | الكمية | Số lượng |
| field.unit | 单位 | Unit | 單位 | 単位 | หน่วย | Unidad | الوحدة | Đơn vị |
| field.unit_price | 单价 | Unit price | 單價 | 単価 | ราคาต่อหน่วย | Precio unitario | سعر الوحدة | Đơn giá |
| field.amount | 发票金额 | Invoice amount | 發票金額 | 請求書金額 | จำนวนเงินใบแจ้งหนี้ | Importe de factura | مبلغ الفاتورة | Số tiền hóa đơn |
| field.currency | 币制 | Currency | 幣制 | 通貨 | สกุลเงิน | Moneda | العملة | Đồng tiền |
| field.total_amount | 总金额 | Total amount | 總金額 | 合計金額 | จำนวนเงินรวม | Importe total | المبلغ الإجمالي | Tổng số tiền |

> 日语 `体積` 是物理用语，日本提单/报关的货物体积一律写 `容積`（m³）。
> **毛重与合计毛重必须能区分**：两栏都写 `総重量` 是功能性缺陷，校验报错定位会指错行——单条用 `グロス重量`，合计用 `合計総重量`。
> 泰语毛重 `น้ำหนักรวม` 已含"合计"义，再写 `ทั้งหมด`（全部）属语义重复。
> 越南语 `Trọng lượng` 系列必须带 `cả bì / tịnh` 后缀，否则毛重与净重在跨单证校验提示里无法区分。
> 阿拉伯语封条号是 `رقم الختم`；`رقم الحبل`（绳号）是明显的机翻错误（现网词表待修）。

### 2.3 报关单专用

| key | zh-CN | en | zh-Hant | ja | th | es | ar | vi |
|---|---|---|---|---|---|---|---|---|
| field.terms_of_delivery | 成交方式 | Terms of delivery | 成交方式 | 貿易条件（インコタームズ） | เงื่อนไขการส่งมอบ | Condiciones de entrega | شروط التسليم | Điều kiện giao hàng |
| field.trade_mode_name | 贸易方式名称 | Trade mode name | 貿易方式名稱 | 貿易方式名 | ชื่อวิธีการค้า | Nombre del modo comercial | اسم طريقة التجارة | Tên phương thức thương mại |
| field.transport_mode_name | 运输方式名称 | Transport mode name | 運輸方式名稱 | 輸送方法名 | ชื่อวิธีการขนส่ง | Nombre del modo de transporte | اسم وسيلة النقل | Tên phương thức vận chuyển |
| field.declarant_name | 申报单位名称 | Declarant name | 申報單位名稱 | 申告者名 | ชื่อผู้สำแดง | Nombre del declarante | اسم المصرّح | Tên đơn vị khai báo |
| field.export_port_code | 出口口岸关区代码 | Export customs port code | 出口口岸關區代碼 | 輸出税関コード | รหัสศุลกากรท่าเรือส่งออก | Código de aduana del puerto de exportación | رمز المنطقة الجمركية لميناء التصدير | Mã hải quan cảng xuất khẩu |
| field.trade_terms | 成交方式 | Trade terms | 成交方式 | 貿易条件 | เงื่อนไขการค้า | Términos comerciales | شروط التجارة | Điều kiện thương mại |

> 「成交方式（Incoterms）」与「贸易方式（海关监管方式）」是两个概念，日语必须分成 `貿易条件` 与 `取引形態`，西语必须分成 `Condiciones de entrega` 与 `Modalidad comercial`；共用一个词会让报关页两个下拉看起来一样。

### 2.4 字段分组

| key | zh-CN | en | zh-Hant | ja | th | es | ar | vi |
|---|---|---|---|---|---|---|---|---|
| field_group.header | 抬头区 | Header | 抬頭區 | ヘッダー | ส่วนหัว | Encabezado | الترويسة | Phần đầu |
| field_group.parties | 当事人 | Parties | 當事人 | 当事者 | คู่สัญญา | Partes | الأطراف | Các bên |
| field_group.route | 运输段 | Route | 運輸段 | 輸送区間 | เส้นทาง | Ruta | المسار | Chặng vận chuyển |
| field_group.cargo | 货物区 | Cargo | 貨物區 | 貨物 | สินค้า | Carga | البضاعة | Hàng hóa |
| field_group.container | 集装箱区 | Container | 貨櫃區 | コンテナ | ตู้คอนเทนเนอร์ | Contenedor | الحاويات | Container |
| field_group.terms | 条款与备注 | Terms and remarks | 條款與備註 | 条件・備考 | เงื่อนไขและหมายเหตุ | Términos y notas | الشروط والملاحظات | Điều khoản và ghi chú |
| field_group.detail | 明细区 | Details | 明細區 | 明細 | รายละเอียด | Detalle | التفاصيل | Chi tiết |
| field_group.items | 商品明细 | Items | 商品明細 | 商品明細 | รายการสินค้า | Artículos | البنود | Mặt hàng |
| field_group.summary | 合计 | Summary | 合計 | 合計 | สรุป | Resumen | الإجمالي | Tổng cộng |
| field_group.unmapped | 未归类字段 | Unmapped fields | 未歸類欄位 | 未分類フィールド | ฟิลด์ที่ยังไม่จัดกลุ่ม | Campos sin clasificar | حقول غير مصنفة | Trường chưa phân loại |
| field_group.manual_added | 人工补录 | Manually added | 人工補錄 | 手動追加 | เพิ่มด้วยมือ | Añadidos manualmente | مضاف يدويًا | Bổ sung thủ công |

> 分组硬约束：后端返回 `header / parties / route / cargo / container / terms / detail / summary / items / other / unmapped / manual_added` 十二个 key，人工新增字段的分组回退显示 key 本身，**不猜译**。

## 3. 业务状态词（运行期拼接的覆盖类 key）

| key | zh-CN | en | zh-Hant | ja | th | es | ar | vi |
|---|---|---|---|---|---|---|---|---|
| status.business_doc.uploaded | 待识别 | Unrecognized | 待識別 | 未認識 | รอระบุ | Sin reconocer | بانتظار التعرّف | Chờ nhận dạng |
| status.business_doc.parsing | 识别中 | Recognizing | 識別中 | 認識中 | กำลังระบุ | Reconociendo | جارٍ التعرّف | Đang nhận dạng |
| status.business_doc.recognized | 待确认 | To confirm | 待確認 | 確認待ち | รอยืนยัน | Por confirmar | بانتظار التأكيد | Chờ xác nhận |
| status.business_doc.confirmed | 已确认 | Confirmed | 已確認 | 確認済み | ยืนยันแล้ว | Confirmado | مؤكّد | Đã xác nhận |
| status.business_doc.failed | 识别失败 | Failed | 識別失敗 | 認識失敗 | ระบุไม่สำเร็จ | Falló el reconocimiento | فشل التعرّف | Nhận dạng thất bại |
| status.business_doc.voided | 已作废 | Voided | 已作廢 | 無効 | ยกเลิกแล้ว | Anulado | ملغى | Đã hủy |
| status.batch.to_group | 待归集确认 | To group | 待歸集確認 | 集約確認待ち | รอยืนยันการจัดกลุ่ม | Por agrupar | بانتظار تأكيد التجميع | Chờ xác nhận gom nhóm |
| status.grouping.confirmed | 自动归集 | Auto-grouped | 自動歸集 | 自動集約 | จัดกลุ่มอัตโนมัติ | Agrupado automático | مجمّع تلقائيًا | Gom nhóm tự động |
| status.grouping.pending | 建议归集 | Suggested | 建議歸集 | 集約候補 | แนะนำให้จัดกลุ่ม | Sugerido | مقترح | Đề xuất gom |
| status.grouping.ungrouped | 未归集 | Not grouped | 未歸集 | 未集約 | ยังไม่จัดกลุ่ม | Sin agrupar | غير مجمّع | Chưa gom nhóm |

> **归票 ≠ 归集**：`未归票`（unlinked，单证还没挂到某票业务）与 `未归集`（ungrouped，还没归到某组）是本系统两个不同状态，八语种必须分开译，禁止合并成同一说法。
> 状态标签用**名词/完成态**，不要用祈使动词：泰语 `ยกเลิก`（取消）是按钮语，状态位必须 `ยกเลิกแล้ว`；英语 `To group` 作状态标签会被读成按钮，用 `Pending group confirmation`。

## 4. 动作词（按钮）

| key | zh-CN | en | zh-Hant | ja | th | es | ar | vi |
|---|---|---|---|---|---|---|---|---|
| action.save | 保存 | Save | 儲存 | 保存 | บันทึก | Guardar | حفظ | Lưu |
| action.cancel | 取消 | Cancel | 取消 | キャンセル | ยกเลิก | Cancelar | إلغاء | Hủy |
| action.confirm | 确认 | Confirm | 確認 | 確認 | ยืนยัน | Confirmar | تأكيد | Xác nhận |
| action.query | 查询 | Search | 查詢 | 検索 | ค้นหา | Buscar | بحث | Truy vấn |
| action.reset | 重置 | Reset | 重設 | リセット | รีเซ็ต | Restablecer | إعادة تعيين | Đặt lại |
| action.delete | 删除 | Delete | 刪除 | 削除 | ลบ | Eliminar | حذف | Xóa |
| action.export | 导出 | Export | 匯出 | エクスポート | ส่งออก | Exportar | تصدير | Xuất |
| action.retry | 重试 | Retry | 重試 | 再試行 | ลองใหม่ | Reintentar | إعادة المحاولة | Thử lại |
| action.grouping | 归集 | Grouping | 歸集 | グループ化 | การจัดกลุ่ม | Agrupación | التجميع | Gom nhóm |
| action.regroup | 重新归集 | Re-group | 重新歸集 | 再グルーピング | จัดกลุ่มใหม่ | Volver a agrupar | إعادة التجميع | Gom nhóm lại |

> 日语按钮一律用惯用 UI 语（`保存`/`削除`/`戻る`/`検索`），不要写「保存する」这类动词短语。

## 5. 易撞车概念（必须两两分开，不许共用一条词）

| 概念 A | 概念 B | 错误做法 | 正确口径 |
|---|---|---|---|
| 归集（Grouping，把多份单证归到一票） | 拼柜（Consolidation，LCL 集拼） | 现网把「拼柜」译成 Pallet（=托盘，语义错） | 归集 = Grouping / Agrupación / グループ化 / التجميع / Gom nhóm / การจัดกลุ่ม；拼柜 = Consolidation / Consolidación de carga / 混載 / توحيد الشحنات / Ghép hàng lẻ / การรวมตู้ |
| 毛重（行值） | 合计毛重（汇总值） | 日语两栏都写 総重量 | グロス重量 / 合計総重量 |
| 未归票（unlinked） | 未归集（ungrouped） | 合并为「未处理」 | 分别译，语义不可混 |
| 成交方式（Incoterms） | 贸易方式（海关监管方式） | 日语都用 取引条件 | 貿易条件 / 取引形態 |
| 单证（Documents） | 附件（Attachment） | 都用 File/文件 | 单证 = Documents/Chứng từ/書類；附件 = Attachment/Tệp đính kèm |
| 体积（Volume） | 件数（Packages） | 泰语都用数量词 | ปริมาตร (ลบ.ม.) / จำนวนหีบห่อ |

**概念唯一化原则**：一个概念只允许一个 canonical 译法；同义说法只能进搜索别名，不得进界面。每个概念在词表里锁一行，组合标签（`A / B` 合成表头）单独建 key，不要把两个概念塞进一条值里——一旦后端把字段拆开显示，连接词就会变成多余的「y / و / และ」。

## 6. 保留原文项（禁止翻译）

- Incoterms：FOB、CIF、EXW、DDP、DAP、FCA、CPT、CIP、CFR、FAS、FTA、FOB Stowed、CIF Liner Terms（8 语列一律拉丁字母）
- HS 编码 / 商品编码（全数字段）
- 港口 UN/LOCODE（CNSHA、THLCH…）、港口英文名
- 船公司代码（MAEU、COSU…）、船名航次原文（MSC ISABELLA / 245E）
- 单证编号、提单号、集装箱号、封条号
- 监管证件缩写（CIQ、AMS、ISF、S.T.C.、S.L.&C.）
- 金额数值、币种代码（USD/CNY）、日期 ISO 部分、API Key、代码块

## 7. 简繁用词对照（本项目词表实测，非通用表）

不是字形映射。以下每对都在现网词表中验证过（命中率 = 该简体词出现时繁体列使用对应港台词的比例）：

| 简体（大陆） | 繁体（港台） | 实测 | 备注 |
|---|---|---|---|
| 保存 | 儲存 | 34/34 | 最易错，`保存` 在繁体里也通但项目统一 `儲存` |
| 字段 | 欄位 | 75/75 | 全表 100% |
| 文件 | 檔案 | 29/29 | `文件` 在港台偏"公文"，界面统一 `檔案` |
| 上传 / 下载 | 上傳 / 下載 | 30/30、11/11 | |
| 导出 / 导入 | 匯出 / 匯入 | 9/9、9/9 | `導出` 不是港台用法 |
| 设置 | 設定 | 7/7 | |
| 信息 | 資訊 | 13/13 | |
| 默认 | 預設 | 5/5 | |
| 数据 | 資料 | 11/11 | |
| 打印 | 列印 | 2/2 | |
| 登录 / 退出 | 登入 / 登出 | 7/8、— | |
| 创建 | 建立 | 18/18 | |
| 添加 | 新增 | 10/10 | |
| 搜索 | 搜尋 | 3/3 | |
| 加载 | 載入 | 22/22 | |
| 刷新 | 重新整理 | 8/8 | 不是 `刷新` |
| 支持 | 支援 | 10/10 | |
| 菜单 | 選單 | 4/4 | |
| 审计 | 稽核 | 9/9 | |
| 生成 | 產生 | 13/26 | 混用中，新词条统一 `產生` |
| 批量 | 批次 | 5/7 | 混用中 |
| 自定义 | 自訂 | 5/5 | |
| 账号 / 订单 / 账单 | 帳號 / 訂單 / 帳單 | 6/6、19/19、8/8 | |
| 归集 / 归票 | 歸集 / 歸票 | 48/48、— | 注意不是 `歸票` 通用 |
| 单证 / 提单 | 單證 / 提單 | 125/125、11/11 | |
| 支付 / 恢复 / 撤销 / 证据 | 支付 / 恢復 / 撤銷 / 證據 | — | 只换字形，不换词 |

高同形率（>95%）会被发布门禁告警，提示可能直接贴了简体。

## 8. 现网词表待修清单（专家复核产出，2026-10-29）

> 以下是**已上线词表里的错译**，本技能新产出一律按 §1–§4 的修正值，不再复制旧值。修词表需单独走一批（`scripts/i18n_batch_util.py` 不支持改值，得直接改 JSON 或走运营后台），不要混在翻译任务里静默改。

| 优先级 | key | 语种 | 现值 | 建议 | 理由 |
|---|---|---|---|---|---|
| P0 | `common.field.seal_no` | ar | رقم الحبل | رقم الختم | `الحبل` = 绳子，语义完全错（机翻 rope） |
| P0 | `common.field.shipper` | es | Remitente | Cargador | `Remitente` 是快递寄件人，提单栏位固定 Cargador |
| P0 | `common.status.doc_type.customs` | th | ใบศุลกากร | ใบขนสินค้า | 泰国海关申报单法定名称 |
| P0 | `web.grouping.*`（4 个 key，含 `action.pallet` / `pallet_tag` / `toast.pallet_marked` / `common.diff.rule.split_alloc`） | en/es/ja/ar/vi/th | 拼柜 → Pallet / Maestro de pallet / 混載マスター | Consolidation / Consolidación de carga / 混載 / توحيد الشحنات / Ghép hàng lẻ / การรวมตู้ | **Pallet = 托盘，语义错**；key 名保持不动，只改译文 |
| P1 | `common.field.marks_and_numbers` | vi | Nhãn hiệu và số | Ký mã hiệu và số hiệu | `Nhãn hiệu` = 品牌/商标 |
| P1 | `common.field.notify_party` | es | Parte notificada | Parte a notificar | 被动语感错位 |
| P1 | `common.status.doc_type.booking` | ja/es/ar/vi | ブッキング / Reserva de espacio / حجز الشحنة / Phiếu đặt chỗ | ブッキングノート / Nota de reserva / إشعار الحجز / Đơn đặt chỗ | 都是"订舱这件事"而非单证名 |
| P1 | `common.field.gross_weight` + `total_gross_weight` | ja | 两条同为 総重量 | グロス重量 / 合計総重量 | 功能缺陷：行值与合计无法区分 |
| P1 | `common.field.gross_weight` | th/vi | น้ำหนักรวม全部 / Tổng trọng lượng | น้ำหนักรวม / Tổng trọng lượng cả bì | 语义重复 / 与净重无法区分 |
| P1 | `common.field.measurement` | ja | 体積 | 容積 | 日本单证用 容積 |
| P2 | `common.status.doc_type.packing_list` | th/vi | รายการบรรจุหีบห่อ / Phiếu đóng gói | ใบรายการบรรจุหีบห่อ / Bảng kê đóng gói | 单证名要带量词 / 电商打包单混淆 |
| P2 | `common.field.vessel_voyage` | ja | 船名・航海 | 船名・航海番号 | 栏位填的是航次号 |
| P2 | `common.field.cargo_ready_date` | ja/th | 締切/出航日 / วันปิดรับสินค้า / ออกเรือ | カットオフ日／出航日 / วันปิดรับสินค้า / วันเรือออก | 缺"日"、动词短语作标签 |
| P2 | `common.field.container_type_qty` | es | Tipo y cantidad de contenedor | Tipo y número de contenedores | 单复数不一致 |
| P2 | `common.field.terms_of_delivery` | ja | 取引条件 | 貿易条件（インコタームズ） | 与「贸易方式」需分开 |
| P2 | `common.field.total_measurement` | ja | 合計体積 | 合計容積 | 与 measurement 同步改「容積」 |

## 9. 新术语入库流程

1. 判断归属：单证类型 → §1；字段名 → §2（先在 `doc_fields.py::FIELD_SPECS` 找 key）；状态 → §3；按钮 → §4。
2. 查本表 → 命中即锁定，禁止另起译法。
3. 未命中 → 查行业实物（提单/报关单样张、船公司网站、目的国海关官网），仍不确定则调跨境本地化翻译专家复核。
4. 复核通过才有资格进本表；进表时补一行、注明依据（来源链接或专家结论），同时确认不会与 §5 的任何概念撞车。
5. 仍无法确认 → 标 `TERM-CANDIDATE` 进复核清单，界面回退源文（不猜译）。
