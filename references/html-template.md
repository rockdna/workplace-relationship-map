# HTML 报告输出硬模板（v2.3.7）

> **这是输出 HTML 报告的唯一合法结构。** 生成 HTML 时必须严格按此模板，只替换占位内容，不可增、删、改区块顺序。
> 所有 CSS 已预定义——生成时复制完整模板，把 `{{占位符}}` 替换为实际内容即可。
> **字体大小和间距已锁定，禁止调整。**

---

## 硬模板（完整复制，替换占位符）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{页面标题}}</title>
<style>
  :root {
    --bg: #F8F9FB;
    --card: #FFFFFF;
    --border: #E4E7EC;
    --text: #1A1D23;
    --text-secondary: #5F6B7A;
    --accent: #2563EB;
    --accent-light: #EEF2FF;
    --success: #059669;
    --success-light: #ECFDF5;
    --warning: #D97706;
    --warning-light: #FFFBEB;
    --purple: #7C3AED;
    --purple-light: #F5F3FF;
    --rose: #E11D48;
    --rose-light: #FFF1F2;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif; background: var(--bg); color: var(--text); line-height: 1.65; font-size: 16px; }
  .container { max-width: 720px; margin: 0 auto; padding: 40px 20px; }

  /* 标题区 */
  .header { margin-bottom: 28px; }
  .header h1 { font-size: 26px; font-weight: 700; margin-bottom: 6px; }
  .header .meta { font-size: 14px; color: var(--text-secondary); }

  /* 心法区 */
  .quote-card { background: linear-gradient(135deg, #1E293B 0%, #334155 100%); color: #F1F5F9; padding: 24px 28px; border-radius: 14px; margin-bottom: 24px; }
  .quote-card .quote-label { font-size: 12px; font-weight: 600; color: #F59E0B; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; }
  .quote-card .quote-text { font-size: 17px; line-height: 1.75; }
  .quote-card .quote-source { font-size: 13px; color: #94A3B8; margin-top: 10px; }

  /* 卡片通用 */
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 28px; margin-bottom: 20px; }
  .card h2 { font-size: 20px; font-weight: 700; margin-bottom: 16px; }
  .card h3 { font-size: 17px; font-weight: 600; margin-bottom: 10px; }

  /* 困局诊断 */
  .diagnosis-label { display: inline-block; font-size: 12px; font-weight: 600; color: var(--accent); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; background: var(--accent-light); padding: 3px 10px; border-radius: 4px; }
  .diagnosis-title { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
  .diagnosis-text { font-size: 16px; color: var(--text-secondary); margin-bottom: 16px; }
  .alternative-view { background: var(--purple-light); border-left: 4px solid var(--purple); padding: 16px 20px; border-radius: 0 8px 8px 0; margin-top: 12px; }
  .alternative-view .alt-label { font-size: 12px; font-weight: 600; color: var(--purple); margin-bottom: 6px; }
  .alternative-view .alt-text { font-size: 15px; color: #4C1D95; }

  /* 权力结构 */
  .power-flow { display:flex; flex-direction:column; gap:16px; }
  .power-flow .pf-item { display:flex; align-items:flex-start; gap:14px; padding:14px 0; border-bottom:1px solid var(--border); }
  .power-flow .pf-item:last-child { border-bottom:none; }
  .power-flow .pf-arrow { flex-shrink:0; color:var(--accent); font-weight:700; font-size:18px; min-width:80px; }
  .power-flow .pf-text { font-size:15px; }
  .power-flow .pf-text strong { color:var(--text); }

  /* 关系解码表 */
  .relation-table { width: 100%; border-collapse: collapse; font-size: 15px; }
  .relation-table th { text-align: left; padding: 12px 16px; border-bottom: 2px solid var(--border); font-weight: 600; color: var(--text-secondary); font-size: 13px; }
  .relation-table td { padding: 14px 16px; border-bottom: 1px solid var(--border); vertical-align: top; }
  .relation-table .person-name { font-weight: 600; }
  .relation-table .leverage { color: var(--accent); font-weight: 600; }

  /* 策略卡片 */
  .strategy-card { border: 1px solid var(--success); background: var(--success-light); border-radius: 14px; padding: 28px; margin-bottom: 20px; }
  .strategy-card .strategy-name { font-size: 19px; font-weight: 700; color: #065F46; margin-bottom: 4px; }
  .strategy-card .strategy-source { font-size: 12px; color: #92400E; font-style: italic; margin-bottom: 20px; }
  .strategy-card .strategy-block { margin-bottom: 16px; }
  .strategy-card .strategy-block-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
  .strategy-card .strategy-block-content { font-size: 16px; }
  .strategy-card .script-block { background: #fff; border: 1px solid #A7F3D0; border-radius: 8px; padding: 16px 20px; margin-top: 8px; font-size: 15px; line-height: 1.7; }

  /* 追一问 */
  .followup { margin-top: 20px; padding: 20px; background: #fff; border: 1px dashed var(--success); border-radius: 10px; }
  .followup .followup-label { font-size: 12px; font-weight: 600; color: var(--success); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }
  .followup .followup-options { list-style: none; padding: 0; }
  .followup .followup-options li { font-size: 16px; padding: 8px 0; }
  .followup .followup-options li:last-child { color: var(--text-secondary); font-size: 14px; }
  .followup .followup-round2 { margin-top: 14px; padding-top: 14px; border-top: 1px solid #D1FAE5; font-size: 14px; color: var(--text-secondary); }

  /* 三件事清单 */
  .checklist { counter-reset: item; }
  .checklist .checklist-item { counter-increment: item; display: flex; align-items: flex-start; gap: 14px; padding: 16px 0; border-bottom: 1px solid var(--border); }
  .checklist .checklist-item:last-child { border-bottom: none; }
  .checklist .checklist-num { flex-shrink: 0; width: 32px; height: 32px; background: var(--accent); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; }
  .checklist .checklist-content { font-size: 16px; }
  .checklist .checklist-content .checklist-title { font-weight: 600; margin-bottom: 2px; }
  .checklist .checklist-content .checklist-detail { font-size: 14px; color: var(--text-secondary); }

  /* 绝对不要做 */
  .danger-zone { background: var(--rose-light); border: 1px solid #FECDD3; border-radius: 14px; padding: 28px; margin-bottom: 20px; }
  .danger-zone h2 { font-size: 20px; font-weight: 700; color: #9F1239; margin-bottom: 12px; }
  .danger-zone p { font-size: 16px; color: #9F1239; }
</style>
</head>
<body>
<div class="container">

  <!-- ========== 1. 标题区 ========== -->
  <div class="header">
    <h1>{{技能名称}}<span style="font-size:15px;font-weight:400;color:var(--text-secondary);margin-left:10px;">v{{版本号}}</span></h1>
    <div class="meta">{{困局一句话定性}}</div>
  </div>

  <!-- ========== 2. 心法区 ========== -->
  <div class="quote-card">
    <div class="quote-label">{{心法标签：如"反脆弱心法（塔勒布）"}}</div>
    <div class="quote-text">"{{核心心法引用句}}"</div>
    <div class="quote-source">——{{来源：人名+书名}}</div>
  </div>

  <!-- ========== 3. 困局诊断 ========== -->
  <div class="card">
    <div class="diagnosis-label">你的困局</div>
    <div class="diagnosis-title">{{困局一句话定性}}</div>
    <div class="diagnosis-text">{{困局展开说明，2-3句话，诊断而非复述}}</div>
    <div class="alternative-view">
      <div class="alt-label">🔍 换个视角</div>
      <div class="alt-text">{{用"可能没注意到的是…"或"另一个角度是…"开头，指出盲点。禁止"你以为""其实是"句式。}}</div>
    </div>
  </div>

  <!-- ========== 4. 关系解码表 ========== -->
  <div class="card">
    <h2>关系解码</h2>
    <table class="relation-table">
      <thead>
        <tr><th>关键人</th><th>表面立场</th><th>真实动机</th><th>杠杆点</th></tr>
      </thead>
      <tbody>
        {{对每个关键人生成一行：
        <tr>
          <td class="person-name">{{人物代号}}</td>
          <td>{{表面立场}}</td>
          <td>{{真实动机}}</td>
          <td class="leverage">{{杠杆点}}</td>
        </tr>
        }}
      </tbody>
    </table>
  </div>

  <!-- ========== 5. 权力结构 ========== -->
  <div class="card">
    <h2>权力结构</h2>
    <div class="power-flow">
      {{对每条关系链生成一行：
      <div class="pf-item">
        <div class="pf-arrow">{{A}} → {{B}}</div>
        <div class="pf-text">{{关系链描述：谁用什么方式影响谁，你的杠杆在哪里。不是复述解码表内容，是串起来说"这个局怎么转的"。}}</div>
      </div>
      }}
    </div>
  </div>

  <!-- ========== 6. 策略区 ========== -->
  <div class="card">
    <h2>策略组合</h2>
    
    {{每条策略一张 strategy-card，至少1条，最多3条。每条策略必须包含追一问。}}

    <div class="strategy-card">
      <div class="strategy-name">{{策略名}}</div>
      <div class="strategy-source">{{来源：人名·书名}}</div>

      <div class="strategy-block">
        <div class="strategy-block-label">做什么</div>
        <div class="strategy-block-content">{{具体动作，动词开头，2-3句话}}</div>
      </div>
      <div class="strategy-block">
        <div class="strategy-block-label">找谁</div>
        <div class="strategy-block-content">{{具体人名/角色}}</div>
      </div>
      <div class="strategy-block">
        <div class="strategy-block-label">说什么</div>
        <div class="script-block">{{可直接复制的完整话术，不少于2句}}</div>
      </div>
      <div class="strategy-block">
        <div class="strategy-block-label">时机</div>
        <div class="strategy-block-content">{{具体时间点，如"明天例会前"而非"找机会"}}</div>
      </div>

      <!-- 追一问（每条策略必须） -->
      <div class="followup">
        <div class="followup-label">🧭 追一问</div>
        <div>第一轮 — 选方向：</div>
        <ul class="followup-options">
          <li>A. {{选项A：具体可回答的问题}}</li>
          <li>B. {{选项B：另一个角度，与A不重复}}</li>
          <li>C. 跳过，继续往下看</li>
        </ul>
        <div class="followup-round2">
          第二轮 — 如果选A：{{基于A的追问}}<br>
          如果选B：{{基于B的追问}}
        </div>
      </div>
    </div>

    {{更多策略卡片同上格式}}
  </div>

  <!-- ========== 7. 三件事清单 ========== -->
  <div class="card">
    <h2>三件事清单</h2>
    <div class="checklist">
      <div class="checklist-item">
        <div class="checklist-num">①</div>
        <div class="checklist-content">
          <div class="checklist-title">明天第一步</div>
          <div class="checklist-detail">{{具体的、明天就能做的第一步行动}}</div>
        </div>
      </div>
      <div class="checklist-item">
        <div class="checklist-num">②</div>
        <div class="checklist-content">
          <div class="checklist-title">本周关键对话</div>
          <div class="checklist-detail">{{本周必须跟谁谈、谈什么、为什么重要}}</div>
        </div>
      </div>
      <div class="checklist-item">
        <div class="checklist-num">③</div>
        <div class="checklist-content">
          <div class="checklist-title">两周后回头看</div>
          <div class="checklist-detail">{{2周后要检查什么、什么信号说明策略有效/无效}}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- ========== 8. 绝对不要做 ========== -->
  <div class="danger-zone">
    <h2>⛔ 绝对不要做</h2>
    <p>{{一个具体的坑，不是"注意沟通方式"这种废话}}</p>
  </div>

</div>
</body>
</html>
```

---

## 模板使用规则（必须遵守）

### 区块顺序（不可增删改）

1. 标题区 → 2. 心法区 → 3. 困局诊断 → 4. 关系解码表 → 5. 权力结构 → 6. 策略区（每条含追一问）→ 7. 三件事清单 → 8. 绝对不要做

**禁止出现的区块：**
- ❌ 14天复盘（已废弃，用三件事清单替代）
- ❌ 修行路径图（心猿/火眼等西游术语，用户看不懂）
- ❌ SVG 雷达图（技术不稳定，用文字表格替代）
- ❌ 绝对定位的局势图（depth不足，用关系解码表替代）

### 措辞红线

- **"换个视角"区**：必须用"可能没注意到的是…""另一个角度是…""如果倒过来看…"开头。严禁"你以为…""其实是…""你错了…"等审判句式
- **心法引用**：必须标注具体人名+书名（如"塔勒布《反脆弱》"），禁止只写库名
- **追一问**：每条策略必须有，选项A/B/C格式，C永远是"跳过"
- **所有占位符**：必须替换为具体内容，不允许留 `{{xxx}}` 在最终输出中

### 策略数量

- 最少 1 条，最多 3 条
- 策略必须从对应策略库中选取（反脆弱/悟空/存在主义）
- 备用策略同样必须包含追一问

### 字体与排版

- body 16px，h1 26px，h2 20px — **禁止调小**
- 卡片间距 20px，内边距 28px — **禁止压缩**
- 颜色已预定义，**禁止使用内联样式覆盖**
</parameter>
