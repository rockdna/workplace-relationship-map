#!/usr/bin/env python3
"""职场关系地图 HTML 报告生成器 v2.6.0

用法: python3 scripts/build_report.py <data.json> [output.html]

v2.6.0 变更:
- 杠杆点从 power_structure 边属性 → 顶层独立概念（意识/哲学/生存之道）
- 权力图从线性流布局 → SVG 辐射关系图（我居中，每人只出现一次）
- 关系边支持 tag 短标签（如"控制""收编"），用于图上标注
- 人物支持 tag 角色标签（如"NPD上司""决策者"），显示在节点上
- 关系线颜色区分类型：控制(红) / 信任(橙虚线) / 协作(绿) / 对立(玫红虚线)

v2.5.0 变更:
- 杠杆点发现与解析：power_structure 每条边可选 leverage 对象（point/why/how/risk）（已废弃，改为顶层）

v2.4.5 变更:
- 阿德勒策略场景路由：4 个子策略（设立边界/不接情绪/不卷入/角色重置）
- 行为识别：动作子类型细分（拖延/模糊/挡卡/施压/越界/庇护）
- 话术骨架差异化：每种动作类型对应独立话术模板
- 策略名差异化：不再统一叫"课题分离：把别人的课题还回去"
- 修复"施压"中的"压"被 blocker 误命中的优先级问题

v2.4.4 变更:
- 用户自称归一化：_is_me() 兼容"你"/"自己"/"本人"
- 权力结构"我"节点不再重复

v2.4.0 变更:
- 权力结构: 线性链 → 独立流向图（每条关系一行 From→desc→To）
- 关系解码: 纯文字行 → 信息图卡片（图标+标签+杠杆高亮块）
- 策略区: 增加编号+图标行、追一问实色边框升级
- 三件事: 修复时间线圆点数字对齐
- Header: 增加场景标签+关键人数徽章
- 稀疏模式: ≤2条权力关系自动居中降级
"""

import json, sys, os, re, math

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

# ═══════════════════════════════════════════════════════════
# 权力结构 · SVG 辐射图生成 (v2.6.0)
# ═══════════════════════════════════════════════════════════

def _classify_edge_type(desc: str) -> str:
    """从 desc 推断关系类型，用于 SVG 连线颜色"""
    control_kws = ['控制', '施压', '越界', '催', '逼', '收编', '庇护', '包庇', '纵容']
    trust_kws = ['信任', '盟友', '依靠', '自己人', '旧信任']
    collab_kws = ['协作', '合作', '帮', '传帮带', '配合', '试探', '靠近', '同盟']
    conflict_kws = ['对立', '冲突', '对抗', '矛盾', '争']
    if any(kw in desc for kw in control_kws):
        return 'control'
    if any(kw in desc for kw in trust_kws):
        return 'trust'
    if any(kw in desc for kw in collab_kws):
        return 'collab'
    if any(kw in desc for kw in conflict_kws):
        return 'conflict'
    return 'default'


def _build_power_svg(relations: list, power_structure: list) -> str:
    """生成以「我」为中心的辐射关系图 SVG

    设计原则：
    - 每个人只出现一次，我居中辐射
    - 角色标签（tag）标注在人物节点上
    - 关系线颜色区分类型（控制/信任/协作/对立）
    - 边标签（tag）标注在关系线上
    """
    # 1. 收集所有人名（排除"我"变体）
    people = []
    people_tags = {}
    for r in relations:
        name = r.get('name', '')
        if name and not _is_me(name):
            if name not in people:
                people.append(name)
            people_tags[name] = r.get('tag', '')

    # 补充 power_structure 中出现但不在 relations 中的人
    for p in power_structure:
        for key in ('from', 'to'):
            name = p.get(key, '')
            if name and not _is_me(name) and name not in people:
                people.append(name)
                people_tags[name] = ''

    n = len(people)
    if n == 0:
        return '<div class="pf-empty" style="text-align:center;color:rgba(255,255,255,.4);padding:40px">暂无权力关系数据</div>'

    # 2. 计算节点位置
    cx, cy = 450, 350
    radius = 240 if n <= 4 else 260

    positions = {'我': (cx, cy)}
    for i, name in enumerate(people):
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions[name] = (x, y)

    # 3. 构建 SVG（分层：边线在底层，节点在上层）
    parts = []
    parts.append('<svg viewBox="0 0 900 700" class="pf-svg" xmlns="http://www.w3.org/2000/svg">')

    # 箭头标记定义
    parts.append('''<defs>
      <marker id="pf-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,1 L10,5 L0,9" fill="rgba(255,255,255,.3)"/></marker>
      <marker id="pf-arr-c" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,1 L10,5 L0,9" fill="#e74c3c"/></marker>
      <marker id="pf-arr-t" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,1 L10,5 L0,9" fill="#E8923C"/></marker>
      <marker id="pf-arr-g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,1 L10,5 L0,9" fill="#27ae60"/></marker>
    </defs>''')

    # ── 第一层：边线（最底层） ──
    parts.append('<g class="pf-svg-edges">')
    for p in power_structure:
        from_name = '我' if _is_me(p.get('from', '')) else p.get('from', '')
        to_name = '我' if _is_me(p.get('to', '')) else p.get('to', '')

        if from_name not in positions or to_name not in positions:
            continue

        x1, y1 = positions[from_name]
        x2, y2 = positions[to_name]

        edge_type = _classify_edge_type(p.get('desc', ''))
        edge_tag = p.get('tag', '')

        # 缩短线段避免与节点重叠
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            shrink = 90
            ratio = shrink / length
            sx, sy = x1 + dx * ratio, y1 + dy * ratio
            ex, ey = x2 - dx * ratio, y2 - dy * ratio
        else:
            sx, sy, ex, ey = x1, y1, x2, y2

        # 选择箭头标记
        marker_map = {'control': 'pf-arr-c', 'trust': 'pf-arr-t', 'collab': 'pf-arr-g'}
        marker_id = marker_map.get(edge_type, 'pf-arr')

        parts.append(f'<line class="pf-svg-edge pf-svg-edge-{edge_type}" '
                     f'x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
                     f'marker-end="url(#{marker_id})" />')

        # 边标签（加权定位，避开中心「我」节点）
        label = edge_tag
        if not label:
            desc = p.get('desc', '')
            label = desc[:6] + '…' if len(desc) > 6 else desc
        if label:
            is_from_me = (from_name == '我')
            is_to_me = (to_name == '我')
            if is_from_me:
                # 从我出发：标签靠向对方（0.65处）
                t = 0.65
                lx = x1 + dx * t
                ly = y1 + dy * t
            elif is_to_me:
                # 指向我：标签靠向对方（0.35处）
                t = 0.35
                lx = x1 + dx * t
                ly = y1 + dy * t
            else:
                # 两端都是外围节点：标签放1/3处，远离中心
                # 选离中心更远的那个端点，标签靠近它
                d1 = math.sqrt((x1 - cx) ** 2 + (y1 - cy) ** 2)
                d2 = math.sqrt((x2 - cx) ** 2 + (y2 - cy) ** 2)
                if d1 >= d2:
                    lx, ly = x1 + dx * 0.3, y1 + dy * 0.3
                else:
                    lx, ly = x1 + dx * 0.7, y1 + dy * 0.7
            # 垂直于线段方向偏移 18px
            if length > 0:
                nx, ny = -dy / length * 18, dx / length * 18
            else:
                nx, ny = 0, -18
            parts.append(f'<text class="pf-svg-elabel" x="{lx + nx:.1f}" y="{ly + ny:.1f}">{label}</text>')
    parts.append('</g>')

    # ── 第二层：节点（最顶层，覆盖边线） ──
    parts.append('<g class="pf-svg-nodes">')

    # 「我」节点（中心）
    parts.append(f'''<g class="pf-svg-node pf-svg-me" transform="translate({cx},{cy})">
      <rect x="-65" y="-30" width="130" height="60" rx="12"/>
      <text class="pf-svg-nname">我</text>
    </g>''')

    # 其他人物节点
    for name in people:
        x, y = positions[name]
        tag = people_tags.get(name, '')
        if tag:
            tag_line = f'<text class="pf-svg-ntag" y="-16">{tag}</text>'
            name_y = 12
            rect_y, rect_h = -40, 80
        else:
            tag_line = ''
            name_y = 0
            rect_y, rect_h = -32, 64
        parts.append(f'''<g class="pf-svg-node pf-svg-other" transform="translate({x:.1f},{y:.1f})">
      <rect x="-76" y="{rect_y}" width="152" height="{rect_h}" rx="12"/>
      {tag_line}
      <text class="pf-svg-nname" y="{name_y}">{name}</text>
    </g>''')

    parts.append('</g>')
    parts.append('</svg>')
    return '\n'.join(parts)

LEVERAGE_CARD = '''      <div class="lev-card">
        <div class="lev-title">
          <span class="lev-icon">🔑</span>
          {point}
        </div>
        <div class="lev-row">
          <span class="lev-label">发现逻辑</span>
          <span class="lev-val">{why}</span>
        </div>
        <div class="lev-row">
          <span class="lev-label">怎么撬</span>
          <span class="lev-val">{how}</span>
        </div>
        <div class="lev-risk">
          <div class="lev-risk-label">⚠️ 风险</div>
          {risk}
        </div>
      </div>'''

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
# 阿德勒心理学策略生成 (v2.4.5)
# ═══════════════════════════════════════════════════════════

# 行为识别关键词（v2.4.5 优化：先 pressurer 后 blocker，避免"施压"中的"压"被 blocker 误命中）
_BLOCKER_KWS = {
    'drag':   ['拖延', '再等等', '再看看', '再调调', '观望', '敷衍', '打太极', '不拒不接', '不接', '缓一缓'],
    'fuzzy':  ['需求模糊', '反复改', '需求反复', '还没定', '没说', '没定', '还在调', '反复变', '改需求', '漂'],
    'block':  ['挡', '卡', '拦', '堵', '不配合', '甩', '不推', '推不动', '踢皮球', '甩锅'],
}
_PRESSURER_KWS = {
    'push':     ['施压', '催', '逼进度', '追进度', '追你', '急', '逼'],
    'overstep': ['越界', '替你', '替你做主', '替你跟', '替你对接', '指手画脚', '直接找', '直接对接', '绕过'],
}
_PROTECTOR_KWS = ['庇护', '包庇', '纵容', '袒护', '靠山', '保护伞', '罩着']

def _classify_action(desc: str) -> str:
    """从 desc 文本识别行为子类型（顺序：protector > pressurer > blocker）"""
    for kw in _PROTECTOR_KWS:
        if kw in desc:
            return 'protector'
    for sub, kws in _PRESSURER_KWS.items():
        if any(kw in desc for kw in kws):
            return f'pressurer:{sub}'
    for sub, kws in _BLOCKER_KWS.items():
        if any(kw in desc for kw in kws):
            return f'blocker:{sub}'
    return 'unknown'


def _scan_edges(power_structure: list) -> dict:
    """扫描 power_structure 边，按行为类型分组"""
    groups = {
        'blocker_drag': [],    # 拖延/观望
        'blocker_fuzzy': [],   # 模糊/反复
        'blocker_block': [],   # 挡/卡
        'pressurer_push': [],  # 施压
        'pressurer_overstep': [],  # 越界
        'protector': [],       # 庇护
        'unknown': [],         # 未识别（指向我的边）
    }
    for p in power_structure:
        desc = p.get('desc', '')
        to_who, from_who = p.get('to', ''), p.get('from', '')

        kind = _classify_action(desc)
        if _is_me(to_who):
            # 指向我的边 → blocker / pressurer
            if kind.startswith('blocker:'):
                groups[f'blocker_{kind.split(":", 1)[1]}'].append((from_who, desc))
            elif kind.startswith('pressurer:'):
                groups[f'pressurer_{kind.split(":", 1)[1]}'].append((from_who, desc))
            else:
                groups['unknown'].append((from_who, desc))
        elif not _is_me(to_who) and not _is_me(from_who):
            if kind == 'protector':
                groups['protector'].append((from_who, to_who, desc))
    return groups


def _adler_boundary(groups: dict) -> dict:
    """子策略 A：拖延/模糊/挡卡 → 课题分离·设立边界"""
    blocker_actors = []
    blocker_descs = []
    for key, label in [('blocker_drag', '拖延'), ('blocker_fuzzy', '模糊'), ('blocker_block', '挡卡')]:
        for actor, desc in groups.get(key, []):
            blocker_actors.append(actor)
            blocker_descs.append(f"{actor}的「{desc}」——ta的课题是用{label}换安全，{label}成本低于'说不'的成本")

    # 加上配套的施压方描述
    press_descs = []
    for key, label in [('pressurer_push', '催你进度'), ('pressurer_overstep', '越界替你')]:
        for actor, desc in groups.get(key, []):
            press_descs.append(f"{actor}的「{desc}」——ta的课题是{label}，碰别人比碰你风险大")

    analysis_parts = blocker_descs + press_descs
    if analysis_parts:
        analysis = '；'.join(analysis_parts)
    else:
        analysis = "对方用拖延/模糊换安全——这是ta的课题，不是你的能力问题"

    # 选第一个 blocker 作为话术对象
    primary_actor = None
    primary_sub = None
    for sub in ('blocker_drag', 'blocker_fuzzy', 'blocker_block'):
        if groups.get(sub):
            primary_actor = groups[sub][0][0]
            primary_sub = sub
            break
    if not primary_actor:
        primary_actor = '对方'
        primary_sub = 'blocker_drag'

    # 按行为子类型选话术骨架
    scripts = {
        'blocker_drag': (
            f"对{primary_actor}：「我理解您需要时间评估。我先把方案整理出来，周X前给到您。"
            f"如果届时没有反馈，我就按草案先推进一版，您看可以吗？」——把'无限等待'变成'有限等待'。"
        ),
        'blocker_fuzzy': (
            f"对{primary_actor}：「我理解需求还在调。我把当前理解写到文档里，周X前给您确认。"
            f"届时未回我按此推进，有调整随时提。」——把'口头模糊'变成'有据可查的推进'。"
        ),
        'blocker_block': (
            f"对{primary_actor}：「我看到流程卡在XX环节。我先把能动的部分推进，"
            f"卡点处我写一版方案给您过目，麻烦您周X前给我反馈。」——把'卡住不动'变成'分段推进'。"
        ),
    }
    script_b = scripts[primary_sub]

    # 配套：pressurer 应对
    script_p = ""
    p_name = ""
    if groups.get('pressurer_push') or groups.get('pressurer_overstep'):
        p_name = (groups.get('pressurer_push') or groups.get('pressurer_overstep'))[0][0]
        if groups.get('pressurer_push'):
            script_p = (
                f"\n\n对{p_name}：「目前卡在XX需要{primary_actor}确认。我已在推进，预计周X前有结论。"
                f"如需加快，建议您和{primary_actor}直接对一下优先级。」——不接情绪，只接事实。"
            )
        else:
            script_p = (
                f"\n\n对{p_name}：「这块我接得住，给我X时间推进。完成后我会主动同步，"
                f"不劳您替我跟。」——把'替我做主'变成'我接得住'。"
            )

    target_parts = [f"{primary_actor}——把对方课题（{('拖延/模糊/挡卡'.split('/')[(['blocker_drag','blocker_fuzzy','blocker_block'].index(primary_sub))])}）还回去"]
    if p_name:
        target_parts.append(f"{p_name}——不接情绪")
    target = '；'.join(target_parts)

    timing_parts = []
    if primary_sub == 'blocker_drag':
        timing_parts.append(f"下次{primary_actor}说「再等等」「再看看」的当场")
    elif primary_sub == 'blocker_fuzzy':
        timing_parts.append(f"下次{primary_actor}说「再调调」「还没定」的当场")
    else:
        timing_parts.append(f"下次{primary_actor}把球踢回来的当场")
    if p_name:
        timing_parts.append(f"下次{p_name}在会议上点你名的当场")
    timing = '；'.join(timing_parts)

    return {
        "name": "课题分离·设立边界",
        "source": "阿尔弗雷德·阿德勒《被讨厌的勇气》",
        "action": analysis,
        "target": target,
        "timing": timing,
        "script": script_b + script_p,
        "followup": {
            "option_a": f"如果{primary_actor}拒绝定时间节点？",
            "option_b": f"如果{p_name or '上级'}继续越界施压？",
            "round2_a": "课题分离不是对抗。追问：「那您建议的时间节点是什么？」把球踢回去——设定时间是ta的课题。ta不给时间，你按自己节奏推进。",
            "round2_b": f"{p_name or '上级'}的焦虑是ta的课题。回应：「我理解紧迫感。目前进度XX，下一步XX。如果不够快，一起看哪些环节可以简化。」不接情绪，只接事实。"
        }
    }


def _adler_emotion(groups: dict) -> dict:
    """子策略 B：施压/越界 → 课题分离·不接情绪"""
    p_actor = None
    p_sub = None
    for sub in ('pressurer_push', 'pressurer_overstep'):
        if groups.get(sub):
            p_actor = groups[sub][0][0]
            p_sub = sub
            break

    push_descs = [f"{a}的「{d}」" for a, d in groups.get('pressurer_push', [])]
    over_descs = [f"{a}的「{d}」" for a, d in groups.get('pressurer_overstep', [])]

    if push_descs:
        analysis = '；'.join(push_descs) + f"——ta的课题是向上交付的压力。追你进度而不帮你清障，因为碰别人比催你风险大。"
    elif over_descs:
        analysis = '；'.join(over_descs) + f"——ta的课题是'替你做主'带来的控制感。你接得住，是ta的焦虑；你接不住，也是ta的课题。"
    else:
        analysis = "对方的情绪是ta的课题，不是你的责任。"

    if p_sub == 'pressurer_push':
        script = (
            f"对{p_actor}：「我理解紧迫感。目前进度XX，下一步XX，需要相关方确认才能继续。"
            f"是否方便您直接和对方对一下优先级？我同步给您结论。」——不接情绪，只接事实，把协调成本推回上游。"
        )
        timing = f"下次{p_actor}在群里@你、当面追问、当众施压的当场"
    else:  # overstep
        script = (
            f"对{p_actor}：「这块我接得住，按我自己的节奏推进。有进展我主动同步，"
            f"不劳您替我跟。」——把'替我做主'变成'我接得住，你放手'。"
        )
        timing = f"下次{p_actor}绕过你直接对接你的下属/同事/客户的当场"

    return {
        "name": "课题分离·不接情绪",
        "source": "阿尔弗雷德·阿德勒《被讨厌的勇气》",
        "action": analysis,
        "target": f"{p_actor}——不接情绪，把协调/推进成本推回上游",
        "timing": timing,
        "script": script,
        "followup": {
            "option_a": f"如果{p_actor}当众给你难堪？",
            "option_b": f"如果{p_actor}越级指挥你的下属？",
            "round2_a": f"当场不接招。会后单独找{p_actor}：「刚才会议上的事我理解您是想推进，但我有自己的节奏。咱们对一下怎么协作更顺。」——把冲突从公开场拉回私下。",
            "round2_b": f"明确边界：「XX事归我管，对接请走我这边。」不卑不亢，{p_actor}知道你有边界，下次自然走流程。"
        }
    }


def _adler_uninvolved(groups: dict) -> dict:
    """子策略 C：派系/庇护 → 课题分离·不卷入"""
    items = []
    for f, t, d in groups.get('protector', []):
        items.append(f"{f}对{t}的「{d}」")
    analysis = '；'.join(items) + "——这是他们之间的课题。你的战场不在这里。"

    if groups.get('protector'):
        f0, t0, d0 = groups['protector'][0]
    else:
        f0, t0, d0 = '派系A', '派系B', '互为庇护'

    return {
        "name": "课题分离·不卷入",
        "source": "阿尔弗雷德·阿德勒《被讨厌的勇气》",
        "action": analysis,
        "target": f"不主动介入{f0}与{t0}的博弈，专注自己的事",
        "timing": "下次有人拉你站队、传闲话、要你表忠心的当场",
        "script": (
            f"回应拉拢：「我理解组织里有自己的格局。我的关注点是把XX事推进好，"
            f"{f0}和{t0}之间的事我先放一放。」——把'站队'变成'专注自己的课题'。"
        ),
        "followup": {
            "option_a": f"如果{f0}明示要你表态？",
            "option_b": f"如果同事传闲话逼你站队？",
            "round2_a": f"中性回应：「我两边都不站，按事办事。」然后走开——表态不是你的课题，专注把事做好才是。",
            "round2_b": "不接话：「这事我没参与过，不好评价。」把闲话挡回去——八卦是他们的课题，你的课题是把手上的活交出去。"
        }
    }


def _adler_fallback(groups: dict) -> dict:
    """子策略 D：无明显课题信号 → 课题分离·角色重置"""
    unknown = groups.get('unknown', [])
    if unknown:
        actors = '、'.join(a for a, _ in unknown)
        descs = '；'.join(f"{a}的「{d}」" for a, d in unknown)
        analysis = f"{descs}——这些动作背后是ta自己的角色焦虑，不是你的边界问题。先看清，再分离。"
    else:
        analysis = "组织中每个人的动作背后都有一份'我的课题'。厘清哪些是你的结果、哪些是别人的情绪与惯性——把别人的课题还回去，你的课题才能浮出水面。"

    return {
        "name": "课题分离·角色重置",
        "source": "阿尔弗雷德·阿德勒《被讨厌的勇气》",
        "action": analysis,
        "target": "每个相关方——看清ta的课题，再决定你的回应",
        "timing": "下次感觉'好像都是我的事'的瞬间",
        "script": (
            "自问三件事：①这是谁的结果？（不是我的就还回去）②谁在为这个情绪买单？"
            "（是ta自己）③我能做的最小动作是什么？（只做最小，把剩下的留给他们）"
        ),
        "followup": {
            "option_a": "怎么判断'是不是我的课题'？",
            "option_b": "分离之后对方不接茬怎么办？",
            "round2_a": "阿德勒的判断标准很硬：'这件事的最终结果，由谁承担？'谁承担，谁就有课题决策权。不承担的人只有建议权，没有决策权。",
            "round2_b": "课题分离后，剩下的是'不接茬'的沉默——这是对方的课题。ta不接茬不是你的失败，是ta还在自己的节奏里。你按自己的节奏推进即可。"
        }
    }


def generate_adler_strategy(relations: list, power_structure: list, diagnosis: dict) -> dict:
    """基于关系数据自动生成阿德勒课题分离策略（v2.4.5 场景路由版）

    路由规则：
    1. 指向我的边含「拖/等/慢/模糊/反复/挡/卡」 → 课题分离·设立边界
    2. 指向我的边含「施压/催/越界/替」 → 课题分离·不接情绪
    3. 第三方之间含「庇护/保/护/罩」 → 课题分离·不卷入
    4. 其他 → 课题分离·角色重置（兜底）
    """
    groups = _scan_edges(power_structure)

    if groups.get('blocker_drag') or groups.get('blocker_fuzzy') or groups.get('blocker_block'):
        return _adler_boundary(groups)
    if groups.get('pressurer_push') or groups.get('pressurer_overstep'):
        return _adler_emotion(groups)
    if groups.get('protector'):
        return _adler_uninvolved(groups)
    return _adler_fallback(groups)


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
    html = html.replace('{{版本号}}', meta.get('version', '2.4.5'))
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

    # ── 权力结构 · 辐射关系图 ──
    power = data.get('power_structure', [])
    power_svg = _build_power_svg(relations, power)
    html = html.replace('{{POWER_DIAGRAM}}', power_svg)

    # ── 杠杆点解析区块（顶层独立概念） ──
    leverage_items = data.get('leverage', [])
    if leverage_items:
        lev_cards = []
        for lev in leverage_items:
            lev_cards.append(LEVERAGE_CARD.format(
                point=lev.get('point', ''),
                why=lev.get('why', ''),
                how=lev.get('how', ''),
                risk=lev.get('risk', '')
            ))
        leverage_section_html = '''<div class="sec-leverage">
  <div class="sec-head"><span class="num">04</span> 杠杆点解析</div>
  <div class="lev-grid">
{cards}
  </div>
</div>'''.format(cards='\n'.join(lev_cards))
    else:
        leverage_section_html = ''
    html = html.replace('{{LEVERAGE_SECTION}}', leverage_section_html)

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
