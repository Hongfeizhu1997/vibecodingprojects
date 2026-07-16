# Dynamic Pricing Phase 2 KUT-LBPi — 分析摘要

**来源：** LBP IT Team (Yihang) — KUT 会议 PPT  
**日期：** 2026-07-16 接收  
**文件：** `Dynamic Pricing Phase 2 KUT-LBPi.pptx`

---

## 范围

| 维度 | 值 |
|------|-----|
| GEO | WW |
| BU | ISG Only |
| Quote Type | LBPi（SC & MC, Indirect & Direct, Standard quote） |

---

## 4 个核心交付

### DYPC2-3: Pen-Rate Delegation 表
LBP Admin → Pricing Grid → Pen Rate Delegation：
- 增删改查委派记录
- 附件上传/下载、操作历史
- Delta Upload / Full Upload / Export / Download Template
- 删除后进入 Grid Archive

### DYPC2-4: Pen-Rate Adjustment 表
LBP Admin → Pricing Grid → Pen Rate Adjustment：
- 按 HW Unit Sales Price 分档调整 Pen-Rate%
- Delta/Full Upload、Change History、Export

### DYPC2-5: Pen-Rate 优先级逻辑（核心引擎）

**映射链：**
1. Quote 中 Service PN → Brand Mapping 表查找 PN 的 Branding
2. Branding → 匹配 Pen Rate Delegation 表的 Brand Mapping 字段
3. PN 未命中 → fallback 到 PC（重复步骤 1-2）

**5 个匹配字段：** Brand Mapping / SDF Code / Base Warranty / RAD / GTM Sub-Segmentation

**优先级：** BU ＞ Country ＞ EU ID list ＞ GTM sub-segmentation ＞ RAD

**计算：**
```
Adjusted Pen Rate = Standard Pen Rate × Adjustment to Pen-Rate%
Pen Rate Delegation Price = HW Unit Sales Price × Adjusted Pen Rate
Final Delegation = compare(Original LBP Delegation, Pen Rate Delegation) → 取 Floor
```

### DYPC2-12: 传递给 LUDP/Magellan
将以下信息同步给 LUDP 和 Magellan：
- Pen Rate Delegation 表数据
- Pen-Rate Adjustment 表数据
- Base Warranty / SDF Code / Final Delegation + PN 信息

---

## 关键认知

1. **Pen Rate 非固定：** ISG 的 Pen Rate 有 Adjustment 机制，按 HW 单价分档调整比例
2. **Brand Mapping 是桥接：** PN/PC 通过 Branding Mapping 表间接匹配到 Pen Rate Delegation
3. **双体系比较：** Final Delegation = 原 LBP Delegation vs Pen Rate Delegation 取 Floor，不是单一来源
4. **测试参考文件：** `Dynamic Pricing Phase 2- Testing Reference.xlsx`
