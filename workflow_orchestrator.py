# -*- coding: utf-8 -*-
"""
工作流编排器 (Workflow Orchestrator)
literature-review-skill v4.1.2

功能：
- 编排完整文化比较工作流
- 生成三种文档（注疏解读、圆桌会议纪要、文献综述）
- 自动保存到 Get笔记【论语研究】知识库
"""

import json
import sys
import io
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 设置编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 导入本地模块
from cultural_comparison import CulturalComparator, run_cultural_comparison, generate_comparison_report
from getnote_integration import save_document, check_credentials, load_credentials

# markdown_converter 是可选依赖（注意：文件名 markdown-converter.py 用hyphen，
# 但 Python import 不支持 hyphen，需用 importlib 或将文件重命名为 underscore）
try:
    import importlib
    _md_converter = importlib.import_module("markdown-converter")
    MarkdownConverter = getattr(_md_converter, 'MarkdownConverter', None)
    HAS_MARKDOWN_CONVERTER = MarkdownConverter is not None
except (ImportError, AttributeError):
    HAS_MARKDOWN_CONVERTER = False
    MarkdownConverter = None


# ========================================
# 文档模板
# ========================================

ANNOTATION_TEMPLATE = """# 注疏解读：{chapter_id}
## {source_title}

**生成时间**: {timestamp}
**版本**: v4.1.2
**标签**: 注疏解读、文化比较、诸子百家、西方哲学

---

## 一、原文

{original_text}

---

## 二、注疏解读

### 2.1 字词训诂

{philological_analysis}

### 2.2 历史语境

{historical_context}

### 2.3 文化比较分析

#### 儒家内部分析

{confucian_analysis}

#### 中西比较分析

{western_analysis}

---

## 三、异同分析

### 3.1 相同点

{similarities}

### 3.2 根本差异

{differences}

---

## 四、冷知识命题

{cold_knowledge}

---

## 五、参考文献

- [朱熹, 四书章句集注·论语集注]
- [刘宝楠, 论语正义]
- [钱穆, 论语新解]
- [柏拉图, 理想国]
- [亚里士多德, 尼各马可伦理学]
- [康德, 实践理性批判]

---

*本注疏解读由 literature-review-skill v4.1.2 自动生成*
*生成时间: {timestamp}*
"""

ROUNDTABLE_TEMPLATE = """# 圆桌会议纪要：{chapter_id}
## {source_title}

**生成时间**: {timestamp}
**版本**: v4.1.2
**标签**: 圆桌会议纪要、文化比较、诸子百家、西方哲学

---

## 一、会议背景

{background}

本圆桌会议汇聚诸子百家与西方哲学的代表人物，围绕"核心议题"展开深度对话。

---

## 二、参会学者

### 儒家代表
- **孔子**：仁者爱人，克己复礼
- **孟子**：性善论，民贵君轻
- **荀子**：性恶论，礼法兼治

### 道家代表
- **老子**：道法自然，无为而治
- **庄子**：逍遥齐物

### 西方哲学代表
- **柏拉图**：理念论，哲学王
- **亚里士多德**：中道，目的论
- **康德**：绝对命令，人是目的

---

## 三、核心议题讨论

### 议题一：{topic_1}

**诸子百家观点**：

- 孔子：{confucian_1}
- 孟子：{confucian_2}
- 老子：{daoist}

**西方哲学观点**：

- 柏拉图：{plato}
- 亚里士多德：{aristotle}
- 康德：{kant}

**交锋点**：

{conflict_1}

---

### 议题二：{topic_2}

**诸子百家观点**：

{zhuzi_view_2}

**西方哲学观点**：

{western_view_2}

**交锋点**：

{conflict_2}

---

## 四、异同总结

### 4.1 共识

{consensus}

### 4.2 分歧

{disagreements}

### 4.3 本质差异

{essential_diff}

---

## 五、冷知识发现

{cold_knowledge}

---

## 六、会议结论

{conclusion}

---

*本圆桌会议纪要由 literature-review-skill v4.1.2 自动生成*
*生成时间: {timestamp}*
"""

REVIEW_TEMPLATE = """# 文献综述报告：{chapter_id}
## {source_title}——文化比较视角

**生成时间**: {timestamp}
**版本**: v4.1.2
**标签**: 文献综述、文化比较、诸子百家、西方哲学

---

## 一、研究概述

本综述从文化比较视角，对"核心议题"进行系统梳理，涵盖诸子百家与西方哲学的主要观点。

---

## 二、诸子百家文献综述

### 2.1 儒家文献

#### 2.1.1 孔子思想

孔子论"仁"：克己复礼为仁，一以贯之。
- 代表作：《论语》
- 核心观点：仁者爱人，礼之用和为贵

#### 2.1.2 孟子思想

孟子论"性善"：人性之善，犹水就下。
- 代表作：《孟子》
- 核心观点：四端说，仁政王道

#### 2.1.3 荀子思想

荀子论"性恶"：人之性恶，其善者伪也。
- 代表作：《荀子》
- 核心观点：礼法兼治，化性起伪

### 2.2 道家文献

#### 2.2.1 老子思想

老子论"道"：道可道，非常道。
- 代表作：《道德经》
- 核心观点：道法自然，无为无不为

#### 2.2.2 庄子思想

庄子论"逍遥"：若夫乘天地之正，而御六气之辩。
- 代表作：《庄子》
- 核心观点：齐物论，逍遥游

### 2.3 其他诸子

#### 墨家
- 墨子"兼爱"：爱无差等
- 代表作：《墨子》

#### 法家
- 韩非子"法治"：法者，国之权衡
- 代表作：《韩非子》

---

## 三、西方哲学文献综述

### 3.1 古希腊哲学

#### 柏拉图
- 理念论：现实世界是理念世界的影子
- 哲学王：除非哲学家成为国王
- 代表作：《理想国》

#### 亚里士多德
- 中道：德性是两极端的中道
- 目的论：幸福是人生的终极目的
- 代表作：《尼各马可伦理学》

### 3.2 康德哲学

- 绝对命令：只依据可成为普遍法则的行动准则
- 人是目的：永远把人视为目的
- 代表作：《实践理性批判》

### 3.3 其他西方传统

#### 斯多葛派
- 顺其自然：按自然生活
- 代表作：爱比克泰德《手册》

#### 功利主义
- 最大幸福：最大化最大多数人的最大幸福
- 代表作：边沁《道德与立法原理导论》

---

## 四、文化比较分析

### 4.1 概念对应

| 中国概念 | 西方对应 | 异同 |
|---------|---------|------|
{concept_table}

### 4.2 方法论比较

**儒家方法**：内省、推己及人、修身齐家
**道家方法**：致虚守静、反者道之动
**西方方法**：逻辑推理、经验归纳、先验分析

### 4.3 政治哲学比较

**儒家**：为政以德，贤人治国
**道家**：无为而治，小国寡民
**西方**：法治民主，契约政治

### 4.4 人性论比较

| 学派 | 人性观 |
|------|--------|
{ontology_table}

---

## 五、异同总结

### 5.1 相同点

{similarities}

### 5.2 根本差异

{differences}

---

## 六、冷知识与新发现

### 6.1 冷知识命题

{cold_knowledge}

### 6.2 研究空白

{research_gaps}

---

## 七、结论

{conclusion}

---

## 八、参考文献

### 诸子百家
1. 朱熹. 四书章句集注. 中华书局
2. 刘宝楠. 论语正义. 中华书局
3. 老子. 道德经
4. 庄子. 庄子
5. 墨子. 墨子
6. 韩非子. 韩非子

### 西方哲学
1. 柏拉图. 理想国
2. 亚里士多德. 尼各马可伦理学
3. 康德. 实践理性批判
4. 边沁. 道德与立法原理导论
5. 密尔. 论自由

---

*本文献综述由 literature-review-skill v4.1.2 自动生成*
*生成时间: {timestamp}*
"""


# ========================================
# 工作流编排器
# ========================================

class CulturalComparisonWorkflow:
    """文化比较工作流编排器"""

    def __init__(self):
        self.comparator = CulturalComparator()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_annotation(self, text: str, chapter_id: str, title: str = "") -> str:
        """生成注疏解读文档"""
        result = run_cultural_comparison(text, chapter_id)

        # 格式化输出
        confucian_text = ""
        if result.confucian.get("intra_confucian"):
            confucian_text = "\n".join([
                f"- **{item['philosopher']}** 论{item['concept']}：{item['view']}"
                for item in result.confucian["intra_confucian"][:5]
            ])
        else:
            confucian_text = "暂无详细内部分析"

        western_text = ""
        if result.western.get("concept_mapping"):
            western_text = "\n".join([
                f"- **{item['chinese_concept']}** → **{item['western_tradition']}**：{item['equivalent']}"
                for item in result.western["concept_mapping"][:5]
            ])
        else:
            western_text = "暂无中西比较分析"

        similarities = "\n".join([f"- {s}" for s in result.similarities[:5]]) or "- 暂无"
        differences = "\n".join([f"- {d}" for d in result.differences[:5]]) or "- 暂无"

        return ANNOTATION_TEMPLATE.format(
            chapter_id=chapter_id,
            source_title=title or f"论语·{chapter_id}",
            timestamp=self.timestamp,
            original_text=text,
            philological_analysis="【待补充具体训诂分析】",
            historical_context="【待补充历史语境分析】",
            confucian_analysis=confucian_text,
            western_analysis=western_text,
            similarities=similarities,
            differences=differences,
            cold_knowledge=result.cold_knowledge
        )

    def generate_roundtable(self, text: str, chapter_id: str, title: str = "") -> str:
        """生成圆桌会议纪要文档"""
        result = run_cultural_comparison(text, chapter_id)

        # 构建概念对应表格
        concept_table = ""
        if result.western.get("concept_mapping"):
            for item in result.western["concept_mapping"][:4]:
                concept_table += f"| {item['chinese_concept']} | {item['western_tradition']} | {item['equivalent']} |\n"
        else:
            concept_table = "| 仁 | 亚里士多德 | phronesis/agape |\n"

        return ROUNDTABLE_TEMPLATE.format(
            chapter_id=chapter_id,
            source_title=title or f"论语·{chapter_id}",
            timestamp=self.timestamp,
            background=f"本圆桌会议围绕「{chapter_id}」的核心议题，汇聚东西方哲学传统进行深度对话。",
            topic_1="仁与道德",
            topic_2="政治与治理",
            confucian_1="仁者爱人，克己复礼",
            confucian_2="恻隐之心，仁之端",
            daoist="道法自然，无为而治",
            plato="理念论，哲学王",
            aristotle="中道，幸福是目的",
            kant="绝对命令，人是目的",
            conflict_1="儒家仁是情感发用，西方是理性原则；儒家重推恩，西方重契约。",
            zhuzi_view_2="儒家主张德治，道家主张无为，墨家主张兼爱，法家主张法治。",
            western_view_2="柏拉图主张哲人王，亚里士多德主张混合政体，康德主张共和宪政。",
            conflict_2="在政治合法性来源上，儒家诉诸道德典范，西方诉诸理性论证。",
            consensus="\n".join([f"- {s}" for s in result.similarities[:3]]) or "- 都关注人类福祉",
            disagreements="\n".join([f"- {d}" for d in result.differences[:3]]) or "- 道德基础不同",
            essential_diff="根本差异在于问题意识：儒家问如何成圣，西方问如何获得真理。",
            cold_knowledge=result.cold_knowledge,
            conclusion="通过东西方哲学的对话，我们发现儒学与西方哲学在处理道德和政治问题时有各自独特的进路，值得进一步深入研究。"
        )

    def generate_review(self, text: str, chapter_id: str, title: str = "") -> str:
        """生成文献综述报告"""
        result = run_cultural_comparison(text, chapter_id)

        # 构建概念表格
        concept_table = ""
        if result.western.get("concept_mapping"):
            for item in result.western["concept_mapping"][:6]:
                sim = item.get('similar', '')[:20]
                concept_table += f"| {item['chinese_concept']} | {item['western_tradition']} | {sim}... |\n"
        else:
            concept_table = "| 仁 | 亚里士多德 | 都强调利他 |\n| 义 | 康德 | 都强调正当性 |\n"

        # 人性论表格
        ontology_table = "| 孟子 | 性善论，四端说 |\n| 荀子 | 性恶论，化性起伪 |\n| 柏拉图 | 灵魂回忆，理念先天 |\n| 康德 | 善意内在于理性 |\n"

        similarities = "\n".join([f"- {s}" for s in result.similarities[:5]]) or "- 都关注人际道德关系"
        differences = "\n".join([f"- {d}" for d in result.differences[:5]]) or "- 本质差异在于问题意识"

        return REVIEW_TEMPLATE.format(
            chapter_id=chapter_id,
            source_title=title or f"论语·{chapter_id}",
            timestamp=self.timestamp,
            concept_table=concept_table,
            ontology_table=ontology_table,
            similarities=similarities,
            differences=differences,
            cold_knowledge=result.cold_knowledge,
            research_gaps="1. 儒学与斯多葛派的系统性比较研究较少\n2. 中西人性论的深层结构差异待进一步探讨",
            conclusion="本综述梳理了诸子百家与西方哲学在核心议题上的主要观点，分析了异同，提出了值得进一步研究的问题。"
        )

    def run_full_workflow(self, text: str, chapter_id: str, title: str = "",
                         save_to_getnote: bool = True) -> Dict[str, Any]:
        """运行完整工作流：生成所有文档并保存

        Args:
            text: 原始章句
            chapter_id: 章节ID
            title: 文档标题
            save_to_getnote: 是否保存到Get笔记

        Returns:
            操作结果汇总
        """
        results = {
            "chapter_id": chapter_id,
            "timestamp": self.timestamp,
            "success": True,
            "documents": {},
            "getnote_results": {}
        }

        # 1. 生成注疏解读
        print("生成注疏解读...")
        annotation_content = self.generate_annotation(text, chapter_id, title)
        results["documents"]["annotation"] = annotation_content

        # 2. 生成圆桌会议纪要
        print("生成圆桌会议纪要...")
        roundtable_content = self.generate_roundtable(text, chapter_id, title)
        results["documents"]["roundtable"] = roundtable_content

        # 3. 生成文献综述
        print("生成文献综述...")
        review_content = self.generate_review(text, chapter_id, title)
        results["documents"]["review"] = review_content

        # 4. 保存到 Get笔记
        if save_to_getnote:
            print("保存到 Get笔记...")

            if not check_credentials():
                print("警告: Get笔记 API 未配置，跳过保存")
                results["getnote_results"] = {"warning": "API未配置"}
            else:
                # 保存注疏解读
                print("  - 保存注疏解读...")
                r1 = save_document(
                    title=f"【注疏解读】{chapter_id} {title}".strip(),
                    content=annotation_content,
                    doc_type="annotation",
                    school="confucian",
                    chapter=chapter_id
                )
                results["getnote_results"]["annotation"] = r1

                # 保存圆桌会议纪要
                print("  - 保存圆桌会议纪要...")
                r2 = save_document(
                    title=f"【圆桌纪要】{chapter_id} {title}".strip(),
                    content=roundtable_content,
                    doc_type="roundtable",
                    school="confucian",
                    chapter=chapter_id
                )
                results["getnote_results"]["roundtable"] = r2

                # 保存文献综述
                print("  - 保存文献综述...")
                r3 = save_document(
                    title=f"【文献综述】{chapter_id} {title}".strip(),
                    content=review_content,
                    doc_type="review",
                    school="confucian",
                    chapter=chapter_id
                )
                results["getnote_results"]["review"] = r3

        return results

    def save_docs_to_files(self, results: Dict[str, Any], output_dir: str = ".") -> Dict[str, str]:
        """将生成的文档保存为本地文件

        Args:
            results: run_full_workflow() 返回的结果字典
            output_dir: 输出目录

        Returns:
            文件路径字典
        """
        files = {}
        chapter_id = results.get("chapter_id", "unknown")
        timestamp = self.timestamp[:10]
        for doc_type, content in results.get("documents", {}).items():
            if content:
                filename = f"{doc_type}_{chapter_id}_{timestamp}.md"
                filepath = Path(output_dir) / filename
                filepath.write_text(content, encoding="utf-8")
                files[doc_type] = str(filepath)
        return files


# ========================================
# 入口函数
# ========================================

def run_workflow(text: str, chapter_id: str, title: str = "",
                save: bool = True) -> Dict[str, Any]:
    """运行文化比较完整工作流

    Args:
        text: 原始章句
        chapter_id: 章节ID
        title: 文档标题
        save: 是否保存到Get笔记

    Returns:
        操作结果
    """
    workflow = CulturalComparisonWorkflow()
    return workflow.run_full_workflow(text, chapter_id, title, save)


if __name__ == "__main__":
    # 测试
    test_text = "子曰：仁者爱人，克己复礼为仁。一以贯之，忠恕而已。"
    test_chapter = "论语·颜渊12.1"
    test_title = "仁者爱人"

    print("=== 文化比较工作流测试 ===")
    print()

    results = run_workflow(test_text, test_chapter, test_title, save=False)

    print()
    print(f"章节: {results['chapter_id']}")
    print(f"成功: {results['success']}")
    print(f"文档类型: {list(results['documents'].keys())}")
    print()

    # 显示摘要
    for doc_type, content in results["documents"].items():
        preview = content[:200] if content else ""
        print(f"--- {doc_type} 预览 ---")
        print(preview)
        print()
