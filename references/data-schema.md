# 报告数据 JSON 格式规范

> 模型收集完分析数据后，按此格式写入 JSON 文件，然后执行 `python3 scripts/build_report.py <data.json>` 生成 HTML。

## 完整结构

```json
{
  "meta": {
    "skill_name": "职场关系地图",
    "version": "2.4.0",
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
      "surface": "他表面上的立场/行为",
      "motive": "真实动机/深层需求",
      "leverage": "你的杠杆点（你最可能影响他的角度）"
    }
  ],
  "power_structure": [
    {
      "from": "施加影响的人",
      "to": "被影响的人",
      "desc": "谁用什么方式影响谁，你的杠杆在哪里——不是复述解码表，是串起来说"这个局怎么转的""
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
| `relations` | 2-5 个，每人 4 字段必填 |
| `power_structure` | 1-5 条关系链 |
| `strategies` | 1-3 条，每条必须含 `followup` |
| `xingfa.tag` | 必须包含人名，如"反脆弱心法（塔勒布）" |
| `xingfa.source` | 人名+书名，如"塔勒布《反脆弱》" |
| `diagnosis.alt_view` | 以"可能没注意到的是…"或"另一个角度是…"开头 |
| `strategies[].name` | 关系操作名（如"先拿筹码再谈底线"），禁止哲学标签（如"杠铃策略"） |

## 格式规则

- 所有字符串字段禁止留空——没有就说"暂无"
- `script` 字段的话术必须可直接复制使用
- JSON 必须是合法的 UTF-8 编码
