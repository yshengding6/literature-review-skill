# -*- coding: utf-8 -*-
"""测试保存到 Get笔记"""

import sys
import io

# 重定向输出到文件
output = io.StringIO()
sys.stdout = output
sys.stderr = output

from getnote_integration import save_note, add_tags_to_note, add_note_to_knowledge_base

# 测试保存
result = save_note(
    title='【v4.1.2测试】仁者爱人 - 文化比较分析',
    content='''# 仁者爱人 - 文化比较分析

## 原始章句
子曰：仁者爱人，克己复礼为仁。

## 儒家内部分析
- 孔子：克己复礼，忠恕爱人
- 孟子：恻隐之心，仁之端

## 中西比较
- 仁 → 亚里士多德：实践智慧/博爱
- 礼 → 柏拉图：秩序，和谐

## 冷知识
儒家"仁"与西方"博爱"表面相似，但前者是情感推恩，后者是理性原则。

---
*本报告由 literature-review-skill v4.1.2 自动生成*
''',
    tags=['论语研究', '文化比较', 'v4.1.2', '注疏解读']
)

output.write(f"\n保存结果: {result}\n")

if result.get('success'):
    note_id = result.get('note_id')
    output.write(f"笔记ID: {note_id}\n")
    
    # 添加到知识库
    kb_result = add_note_to_knowledge_base(note_id, 'QYA1qm4Y')
    output.write(f"知识库添加结果: {kb_result}\n")
else:
    output.write("保存失败！\n")

# 写入文件
with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write(output.getvalue())

print("结果已保存到 test_output.txt")
