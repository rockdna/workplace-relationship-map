#!/usr/bin/env python3
"""职场关系地图 HTML 报告生成器 v2.5.0

用法: python3 scripts/build_report.py <data.json> [output.html]

v2.5.0 变更:
- 内置阿德勒课题分离策略自动生成

v2.4.0 变更:
- 权力结构: 线性链 → 独立流向图（每条关系一行 From→desc→To）
- 关系解码: 纯文字行 → 信息图卡片（图标+标签+杠杆高亮块）
- 策略区: 增加编号+图标行、追一问实色边框升级
- 三件事: 修复时间线圆点数字对齐
- Header: 增加场景标签+关键人数徽章
- 稀疏模式: ≤2条权力关系自动居中降级
"""

import json, sys, os, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
TEMPLATE_PATH = os.path.join(SKILL_DIR, 'templates', 'report.html')

# 用户自称归一化：模型可能生成"你"/"自己"/"本人"等，统一当"我"处理
_ME_VARIANTS = {'我', '你', '自己', '本人', '用户'}

def _is_me(name: str) -> bool:
    """判断 from/to 字段是否指代用户本人"""
    return name.strip() in _ME_VARIANTS

# ═══════════════════════════════════════════════════════════
# HTML 片段模板
# ═══════════════════════════════════════════════════════════

RELATION_CARD = '''      <details class="rel-card {avatar_shape}"{open_attr}>
        <summary class="rel-head">
          <div class="rel-head-info">
            <span class="rel-name">{name}</span>
            <span class="rel-hint">{surface}</span>
          </div>
          <span class="fold-btn"></span>
        </summary>
        <div class="rel-body">
          <div class="rel-row">
            <span class="rel-icon">🎯</span>
            <span class="rel-label">动机</span>
            <span class="rel-val">{motive}</span>
          </div>
          <div class="rel-leverage">
            <span class="rel-icon">🔑</span>
            <span class="rel-label">杠杆</span>
            <span class="rel-val">{leverage}</span>
          </div>
        </div>
      </details>'''

TRI_ANCHOR_NODE_TOP = '''      <div class="pf-node">
        <div class="pf-name">{name}</div>
      </div>
      <div class="pf-arrow-down"><span class="pf-line"></span>{edge_label}</div>'''

TRI_ANCHOR_NODE_ROW = '''      <div class="pf-node {extra_class}"><div class="pf-name">{name}</div></div>
      <div class="pf-arrow-{arrow_dir}">{edge_label}</div>'''

TRI_ANCHOR_NODE_ME = '''      <div class="pf-node pf-me"><div class="pf-name">我</div></div>'''

STRATEGY_BLOCK = '''    <details class="strategy-block"{open_attr}>
      <summary class="st-summary">
        <span class="st-num-big">{num_big}</span>
        <div class="st-summary-text">
          <div class="st-name">{name}</div>
          <div class="st-source">{source}</div>
        </div>
        <span class="fold-btn"></span>
      </summary>
      <div class="st-body">
      <div class="strategy-duo">
        <div class="strategy-info">
          <div class="si-row">
            <span class="si-icon">🎯</span>
            <span class="si-label">做什么</span>
            <span class="si-content">{action}</span>
          </div>
          <div class="si-row">
            <span class="si-icon">👤</span>
            <span class="si-label">找谁</span>
            <span class="si-content">{target}</span>
          </div>
          <div class="si-row">
            <span class="si-icon">⏱</span>
            <span class="si-label">时机</span>
            <span class="si-content">{timing}</span>
          </div>
        </div>
        <div class="strategy-script">
          <div class="ss-label">💬 话术</div>
          <div class="ss-text">{script}</div>
        </div>
      </div>
      <div class="followup">
        <div class="fu-label">🧭 追一问</div>
        <ul class="fu-options">
          <li><strong>A.</strong> {opt_a}</li>
          <li><strong>B.</strong> {opt_b}</li>
        </ul>
        <div class="fu-skip">C. 跳过，继续往下看</div>
        <div class="fu-round2">
          选A：{round2_a}<br>
          选B：{round2_b}
        </div>
      </div>
      </div>
    </details>'''

TIMELINE_ITEM = '''      <div class="tl-item">
        <div class="tl-dot"><span class="tl-num">{num}</span></div>
        <div class="tl-content">
          <div class="tl-title">{title}</div>
          <div class="tl-desc">{desc}</div>
        </div>
      </div>'''


# ═══════════════════════════════════════════════════════════
# 阿德勒心理学策略生成 (v2.5.0)
# ═══════════════════════════════════════════════════════════

def generate_adler_strategy(relations: list, power_structure: list, diagnosis: dict) -> dict:
    """基于关系数据自动生成阿德勒课题分离策略"""
    blockers, pressurers, protectors = [], [], []

    for p in power_structure:
        desc = p.get('desc', '')
        to_who, from_who = p.get('to', ''), p.get('from', '')

        if _is_me(to_who):
            if any(kw in desc for kw in ['拖', '等', '慢', '不拒', '太极', '推']):
                blockers.append(from_who)
            if any(kw in desc for kw in ['施压', '追', '催', '逼', '急']):
                pressurers.append(from_who)
        elif not _is_me(to_who) and not _is_me(from_who):
            if any(kw in desc for kw in ['庇护', '保', '护', '罩']):
                protectors.append((from_who, to_who))

    parts = []
    if blockers:
        parts.append(f"{'、'.join(blockers)}的拖延——ta在惯性中选择了不动，拖延成本低于你的放弃成本。这是ta的课题，不是你的能力问题。")
    if pressurers:
        parts.append(f"{'、'.join(pressurers)}的焦虑——ta向上交付的压力。追你进度而不是帮你清障，因为碰元老比催你风险大。这是ta的课题。")
    if protectors:
        items = [f"{f}对{t}的庇护" for f, t in protectors]
        parts.append(f"{'、'.join(items)}——这是他们之间的课题，与你无关。你的战场不在这里。")
    if not parts:
        parts.append("厘清组织中的课题边界：哪些是你的结果，哪些是别人的情绪、惯性与权力博弈。把别人的课题还回去，你的课题才能浮出水面。")

    analysis = '；'.join(parts)
    b_name = blockers[0] if blockers else '对方'
    p_name = pressurers[0] if pressurers else '上级'

    script_b = (
        f"对{b_name}：「我理解您需要时间评估。我先把方案整理出来，周X前给到您。"
        f"如果届时没有反馈，我就按草案先推进一版，您看可以吗？」——无限等待→有限等待，设立时间边界。"
    )
    script_p = (
        f"对{p_name}：「目前的卡点在XX环节需要{b_name}确认。我已在推进，预计周X前有明确结论。"
        f"如果需要加快，建议您和{b_name}直接聊一下优先级。」——不接情绪，只接事实。"
    )

    return {
        "name": "课题分离：把别人的课题还回去",
        "source": "阿尔弗雷德·阿德勒《被讨厌的勇气》",
        "action": analysis,
        "target": f"{b_name}——设立时间边界；{p_name}——设立情绪边界",
        "timing": f"下次{b_name}说「再等等」的当场",
        "script": f"{script_b}\n\n{script_p}",
        "followup": {
            "option_a": f"如果{b_name}拒绝设立时间边界？",
            "option_b": f"如果{p_name}继续越界施压？",
            "round2_a": f"课题分离不是对抗。追问：「那您建议的时间节点是什么？」把球踢回去——设定时间是ta的课题。ta不给时间，你按自己节奏推进。",
            "round2_b": f"{p_name}的焦虑是ta的课题。回应：「我理解紧迫感。目前进度XX，下一步XX。如果不够快，一起看哪些环节可以简化。」不接情绪，只接事实。"
        }
    }


# ═══════════════════════════════════════════════════════════
# 构建函数
# ═══════════════════════════════════════════════════════════

def build(data: dict) -> str:
    """从 JSON 数据生成完整 HTML"""
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    meta = data.get('meta', {})
    diag = data.get('diagnosis', {})

    # ── Header 简单占位符 ──
    html = html.replace('{{页面标题}}', meta.get('page_title', meta.get('case_title', '职场关系分析')))
    html = html.replace('{{版本号}}', meta.get('version', '2.4.4'))
    html = html.replace('{{场景标签}}', meta.get('scene_tag', '职场困局'))
    html = html.replace('{{关键人数}}', str(meta.get('key_people_count', len(data.get('relations', [])))))
    html = html.replace('{{用户背景概述}}', meta.get('background', diag.get('title', '')))

    # 心法区
    xf = data.get('xingfa', {})
    for ph, val in [
        ('{{心法标签}}', xf.get('tag', '')),
        ('{{核心心法引用句}}', xf.get('quote', '')),
        ('{{来源}}', xf.get('source', '')),
    ]:
        html = html.replace(ph, val)

    # 困局诊断
    for ph, val in [
        ('{{困局一句话定性}}', diag.get('title', '')),
        ('{{困局展开说明}}', diag.get('description', '')),
        ('{{换个视角文本}}', diag.get('alt_view', '')),
    ]:
        html = html.replace(ph, val)

    # ── 关系解码卡片 ──
    relations = data.get('relations', [])
    avatar_shapes = ['avatar-sq', 'avatar-di', 'avatar-ci']
    rel_cards = []
    for i, r in enumerate(relations):
        name = r.get('name', '')
        avatar_shape = avatar_shapes[i % len(avatar_shapes)]
        open_attr = ' open' if i == 0 else ''
        rel_cards.append(RELATION_CARD.format(
            avatar_shape=avatar_shape,
            open_attr=open_attr,
            name=name,
            surface=r.get('surface', ''),
            motive=r.get('motive', ''),
            leverage=r.get('leverage', '')
        ))
    html = html.replace('{{RELATION_CARDS}}', '\n'.join(rel_cards))

    # ── 权力结构纵向流 ──
    power = data.get('power_structure', [])
    tri_parts = []
    if power:
        # 分类边：指向我的、从我出发的、不涉及我的（归一化"你"/"自己"等变体）
        to_me = [p for p in power if _is_me(p.get('to', ''))]
        from_me = [p for p in power if _is_me(p.get('from', '')) and not _is_me(p.get('to', ''))]
        not_to_me = [p for p in power if not _is_me(p.get('to', '')) and not _is_me(p.get('from', ''))]

        # 第一步：不涉及我的边 = 上层关系，纵向展示
        for i, p in enumerate(not_to_me):
            f_name = p.get('from', '')
            t_name = p.get('to', '')
            desc = p.get('desc', '')
            # 上方节点
            tri_parts.append(TRI_ANCHOR_NODE_TOP.format(name=f_name, edge_label=desc))
            # 下方节点（不指向我的边的 target）
            tri_parts.append('<div class="pf-node"><div class="pf-name">{}</div></div>'.format(t_name))

        # 第二步：横向行 - 指向我的边（他人 → 我）
        if to_me:
            tri_parts.append('<div class="pf-row">')
            for i, p in enumerate(to_me):
                f_name = p.get('from', '')
                desc = p.get('desc', '')
                if i > 0:
                    tri_parts.append(TRI_ANCHOR_NODE_ME)
                tri_parts.append(TRI_ANCHOR_NODE_ROW.format(
                    name=f_name, extra_class='', arrow_dir='right', edge_label=desc
                ))
            tri_parts.append(TRI_ANCHOR_NODE_ME)
            tri_parts.append('</div>')

        # 第三步：横向行 - 从我出发的边（我 → 他人）
        if from_me:
            tri_parts.append('<div class="pf-row" style="margin-top:16px">')
            tri_parts.append(TRI_ANCHOR_NODE_ME)
            for i, p in enumerate(from_me):
                t_name = p.get('to', '')
                desc = p.get('desc', '')
                # 先箭头后节点（我 → 他人）
                tri_parts.append('      <div class="pf-arrow-right">{}</div>'.format(desc))
                tri_parts.append('      <div class="pf-node"><div class="pf-name">{}</div></div>'.format(t_name))
            tri_parts.append('</div>')

    html = html.replace('{{TRI_ANCHOR_NODES}}', '\n'.join(tri_parts))

    # ── 策略区块 ──
    strategies = list(data.get('strategies', []))
    # 内置阿德勒课题分离策略（v2.5.0）
    strategies.append(generate_adler_strategy(
        data.get('relations', []),
        data.get('power_structure', []),
        data.get('diagnosis', {})
    ))
    strategy_blocks = []
    for i, s in enumerate(strategies, 1):
        fu = s.get('followup', {})
        strategy_blocks.append(STRATEGY_BLOCK.format(
            open_attr=' open' if i == 1 else '',
            num_big=str(i).zfill(2),
            name=s.get('name', ''),
            source=s.get('source', ''),
            action=s.get('action', ''),
            target=s.get('target', ''),
            script=s.get('script', ''),
            timing=s.get('timing', ''),
            opt_a=fu.get('option_a', ''),
            opt_b=fu.get('option_b', ''),
            round2_a=fu.get('round2_a', ''),
            round2_b=fu.get('round2_b', '')
        ))
    html = html.replace('{{STRATEGY_BLOCKS}}', '\n'.join(strategy_blocks))

    # 清理空追一问 round2
    html = html.replace('<div class="fu-round2">\n          选A：<br>\n          选B：\n        </div>', '')

    # ── 三件事时间线 ──
    cl = data.get('checklist', {})
    timeline_items = []
    for idx, (key, title) in enumerate([
        ('tomorrow', '明天第一步'),
        ('this_week', '本周关键对话'),
        ('two_weeks', '两周后回头看'),
    ], 1):
        desc = cl.get(key, '')
        timeline_items.append(TIMELINE_ITEM.format(
            num=str(idx),
            title=title,
            desc=desc
        ))
    html = html.replace('{{TIMELINE_ITEMS}}', '\n'.join(timeline_items))

    # ── 绝对不要做 ──
    html = html.replace('{{危险动作}}', data.get('danger', ''))

    # ── 检查残留占位符 ──
    remaining = re.findall(r'\{\{[^}]+\}\}', html)
    if remaining:
        print(f"⚠️ 警告：{len(remaining)} 个占位符未替换: {remaining}", file=sys.stderr)

    return html


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 scripts/build_report.py <data.json> [output.html]", file=sys.stderr)
        sys.exit(1)

    data_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else data_path.replace('.json', '.html')

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html = build(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 报告已生成: {output_path} ({len(html)} 字节)")
