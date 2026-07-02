# 报告数据 JSON 格式规范

> 模型收集完分析数据后，按此格式写入 JSON 文件，然后执行 `python3 scripts/build_report.py <data.json>` 生成 HTML。

## 完整结构

```json
{
  "meta": {
    "skill_name": "职场关系地图",
    "version": "2.6.0",
    "case_title": "一句话总结困局",
    "page_title": "页面标题（可选，默认取 case_title）",
    "scene_tag": "场景标签（如"老黄牛困境""空降兵生存"，用于 Header badge）",
    "key_people_count": 3
  },
  "xingfa": {
    "tag": "反脆弱心法（塔勒布）",
    "quote": "风会熄灭蜡烛，却能让火越烧越旺",
    "source": "塔勒布《反脆弱》"
  },
  "diagnosis": {
    "title": "一句话定性困局",
    "description": "2-3句话展开说明，诊断而非复述用户描述",
    "alt_view": "可能没注意到的是…（指出盲点，禁止"你以为""其实是"句式）"
  },
  "relations": [
    {
      "name": "人物代号",
      "tag": "角色标签（如'NPD上司''决策者''旁观者'，显示在权力图节点上）",
      "surface": "他表面上的立场/行为",
      "motive": "真实动机/深层需求",
      "leverage": "你的杠杆点（你最可能影响他的角度）"
    }
  ],
  "power_structure": [
    {
      "from": "施加影响的人",
      "to": "被影响的人",
      "desc": "谁用什么方式影响谁——不是复述解码表，是串起来说"这个局怎么转的"",
      "tag": "关系短标签（如'控制''收编''报喜''试探'，显示在权力图连线上）"
    }
  ],
  "leverage": [
    {
      "point": "杠杆点名称（一种意识、一种哲学、一种生存之道，不是某条关系的问题）",
      "why": "发现逻辑：为什么这是你的破局关键——不是'某人的弱点'，而是'你的机会/这个结构的裂缝'",
      "how": "行动路径：怎么用这个意识来行动，动词开头，2-3句",
      "risk": "误判风险：时机不对或方式错误会怎样，1-2句"
    }
  ],
  "strategies": [
    {
      "name": "策略名（关系操作，非哲学标签）",
      "source": "人名·书名",
      "action": "具体动作，动词开头，2-3句话",
      "target": "具体人名/角色",
      "script": "可直接复制的完整话术，不少于2句",
      "timing": "具体时间点（如"明天例会前"，非"找机会"）",
      "followup": {
        "option_a": "选项A：具体可回答的问题",
        "option_b": "选项B：另一个角度",
        "round2_a": "如果选A的追问",
        "round2_b": "如果选B的追问"
      }
    }
  ],
  "checklist": {
    "tomorrow": "明天第一步：具体的可执行行动",
    "this_week": "本周必须跟谁谈、谈什么",
    "two_weeks": "两周后检查什么信号"
  },
  "danger": "绝对不要做的具体坑（不是"注意沟通方式"这种废话）"
}
```

## 字段约束

| 字段 | 约束 |
|------|------|
| `meta.scene_tag` | 场景中文标签，用于 Header badge（如"老黄牛困境"） |
| `meta.key_people_count` | 整数，关键人物数量，用于 Header badge |
| `relations` | 2-5 个，每人必填 name/surface/motive/leverage，tag 可选 |
| `relations[].tag` | 角色短标签（2-4字），显示在权力图节点上方，如"NPD上司""决策者" |
| `power_structure` | 1-5 条关系链，`from`/`to` 中用户一律写 `"我"`（脚本自动归一化"你"/"自己"等变体）；`tag` 可选，用于权力图连线标注 |
| `power_structure[].tag` | 关系短标签（1-3字），显示在权力图连线上，如"控制""收编""试探" |
| `leverage` | 0-3 个顶层杠杆点，每个必填 point/why/how/risk；无杠杆数据时整个区块隐藏 |
| `leverage[].point` | 杠杆点名称：一种意识/哲学/生存之道，禁止写成"某人的弱点"（如"老板对上级交付的焦虑"→错，"信息差是你的护城河"→对） |
| `leverage[].why` | 发现逻辑：为什么这是破局关键，2-3 句，指向"你的机会/结构裂缝"而非"他的弱点" |
| `leverage[].how` | 行动路径：动词开头的具体动作，2-3 句，禁止"加强沟通"等废话 |
| `leverage[].risk` | 误判风险：时机/方式错误会怎样，1-2 句 |
| `strategies` | 1-3 条，每条必须含 `followup` |
| `xingfa.tag` | 必须包含人名，如"反脆弱心法（塔勒布）""斯多葛心法（爱比克泰德）""NVC心法（卢森堡）" |
| `xingfa.source` | 人名+书名，如"塔勒布《反脆弱》""爱比克泰德《手册》""马可·奥勒留《沉思录》""塞涅卡《致卢齐利乌斯的信》""卢森堡《非暴力沟通》" |
| `xingfa.quote` | 必须与 source 的哲学内核有真实关联，禁止通用鸡汤贴标签。当 source 为《黑神话：悟空》时，quote 必须从以下主题之一 authentically derive：执念、天命之问、金箍悖论、兵解、六根与五毒、佛魔同体、轮回之力。参考 `references/wukong-xingfa-guide.md` |
| `diagnosis.alt_view` | 以"可能没注意到的是…"或"另一个角度是…"开头 |
| `strategies[].name` | 关系操作名（如"先拿筹码再谈底线"），禁止哲学标签（如"杠铃策略"） |

## 格式规则

- 所有字符串字段禁止留空——没有就说"暂无"
- `script` 字段的话术必须可直接复制使用
- JSON 必须是合法的 UTF-8 编码
