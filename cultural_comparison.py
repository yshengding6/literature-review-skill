# -*- coding: utf-8 -*-
"""
文化比较核心模块 (Cultural Comparison Module)
literature-review-skill v4.1.2

功能：诸子百家观点 vs 西方哲学观点的比较分析
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


# ========================================
# 诸子百家核心观点库（精简版）
# ========================================

ZHUZI_DB = {
    "孔子": {
        "core": {"仁": "爱人克己", "礼": "和为贵", "义": "喻于义", "忠恕": "己所不欲"},
        "人性": "性相近", "方法": "启发因材", "政治": "为政以德"
    },
    "孟子": {
        "core": {"性善": "水就下", "仁政": "民贵君轻", "四端": "恻隐羞恶", "王道": "以德王"},
        "人性": "性善论", "方法": "推己及人", "政治": "民本"
    },
    "荀子": {
        "core": {"性恶": "其善伪也", "礼法": "隆礼重法", "天人之分": "制天命用之"},
        "人性": "性恶论", "方法": "解蔽积伪", "政治": "礼法兼治"
    },
    "老子": {
        "core": {"道": "道法自然", "无为": "无不为", "柔弱": "胜刚强", "自然": "人法天地"},
        "人性": "自然素朴", "方法": "致虚守静", "政治": "无为而治"
    },
    "庄子": {
        "core": {"逍遥": "乘天地正", "齐物": "万物一马", "天籁": "吹万不同"},
        "人性": "天性完整", "方法": "寓言重言", "政治": "不刻意"
    },
    "墨子": {
        "core": {"兼爱": "爱无差等", "非攻": "兴天下利", "尚贤": "政之本", "节用": "民用则止"},
        "人性": "性可善", "方法": "三表法", "政治": "兼爱尚同"
    },
    "韩非子": {
        "core": {"法": "国之权衡", "术": "循名责实", "势": "胜者王", "耕战": "农战兴国"},
        "人性": "性恶自为", "方法": "参验功用", "政治": "法治集权"
    },
}

# 西方哲学核心观点库（精简版）
WESTERN_DB = {
    "苏格拉底": {
        "core": {"美德知识": "无人有意作恶", "产婆术": "问答引导", "认识自己": "未经省察的人生不值得过"},
        "方法": "反诘法", "政治": "德性治国"
    },
    "柏拉图": {
        "core": {"理念论": "现实是影子", "哲学王": "哲人王统治", "洞穴隐喻": "走出洞穴看阳光", "正义": "各安其位"},
        "方法": "辩证法", "政治": "理想国"
    },
    "亚里士多德": {
        "core": {"中道": "两极端之间", "目的论": "幸福是终极目的", "友爱": "生活的必需品", "实体": "个别事物"},
        "方法": "经验归纳", "政治": "混合政体"
    },
    "康德": {
        "core": {"绝对命令": "愿成为普遍法则", "人是目的": "不止视为手段", "物自体": "不可知", "理性": "有界限"},
        "方法": "先验演绎", "政治": "永久和平"
    },
    "尼采": {
        "core": {"权力意志": "生命追求超越", "超人": "大地之意义", "虚无主义": "上帝死了", "永恒轮回": "热爱命运"},
        "方法": "谱系学", "政治": "批判民主"
    },
    "萨特": {
        "core": {"存在先于本质": "人先存在后成什么", "自由": "命中注定", "责任": "选择即责任", "他人地狱": "他人是异化"},
        "方法": "现象学", "政治": "介入承担"
    },
    "边沁/密尔": {
        "core": {"功利": "最大幸福", "伤害原则": "不伤害他人", "自由": "个性发展", "质量": "高质量快乐"},
        "方法": "效益计算", "政治": "代议民主"
    },
    "斯多葛派": {
        "core": {"自然": "按自然生活", "自足": "内在自由", "区分": "可控与不可控"},
        "方法": "哲学实践", "政治": "世界公民"
    },
}

# 概念对应映射
CONCEPT_MAP = {
    "仁": {
        "zh": ["孔子仁", "孟子仁政"],
        "confucian": {"孔子": "克己复礼，忠恕爱人", "孟子": "恻隐之心，仁之端"},
        "western": {
            "亚里士多德": "phronesis(实践智慧)/agape(博爱)",
            "康德": "善意(good will)，人是目的",
            "边沁/密尔": "最大幸福原则",
        },
        "similar": "都关注人际道德，都强调利他",
        "diff": "儒家仁是情感发用，西方是理性原则；儒家重推恩，西方重契约"
    },
    "义": {
        "zh": ["孔子义", "孟子义", "荀子礼法"],
        "western": {
            "康德": "定言命令，道德律令",
            "柏拉图": "正义(dikaiosyne)",
            "亚里士多德": "justice，中道",
        },
        "similar": "都强调道德正当性，都反对唯利是图",
        "diff": "儒家义侧重内在情感外发，西方义侧重外在规范"
    },
    "礼": {
        "zh": ["周礼", "孔子礼", "荀子礼法"],
        "western": {
            "亚里士多德": "中道，仪式美德",
            "柏拉图": "秩序，和谐",
            "康德": "道德法则",
        },
        "similar": "都规范行为，都维护秩序",
        "diff": "儒家礼是情感化规范（礼乐教化），西方是理性规范"
    },
    "天命": {
        "zh": ["孔子天命", "孟子尽心知命"],
        "western": {
            "柏拉图": "理念，永恒真理",
            "康德": "物自体，绝对命令",
            "基督教": "上帝旨意",
        },
        "similar": "都承认超越性存在，都认为人应服从更高法则",
        "diff": "儒家天命内化为人性，西方超越外在"
    },
    "君子": {
        "zh": ["孔子君子", "孟子大人"],
        "western": {
            "亚里士多德": "有德之人",
            "柏拉图": "哲学家王",
            "康德": "道德行动者",
        },
        "similar": "都追求完美人格，都强调道德修养",
        "diff": "儒家君子重社会角色，西方哲人重理性卓越"
    },
    "无为": {
        "zh": ["老子无为", "庄子逍遥"],
        "western": {
            "斯多葛派": "顺其自然",
            "爱比克泰德": "区分可控/不可控",
            "第欧根尼": "按自然生活",
        },
        "similar": "都反对过度干预，都追求自然",
        "diff": "道家无为是退隐超越，斯多葛是理性接纳"
    },
    "性善": {
        "zh": ["孟子性善", "荀子性恶", "董仲舒性三品"],
        "western": {
            "柏拉图": "灵魂回忆",
            "卢梭": "高贵的野蛮人",
            "康德": "善意内在于理性",
        },
        "similar": "都认为人有向善可能",
        "diff": "孟子是情感四端，西方多是理性本质"
    },
}


# ========================================
# 数据类
# ========================================

@dataclass
class ComparisonResult:
    chapter_id: str
    source_text: str
    confucian: Dict[str, Any]
    western: Dict[str, Any]
    similarities: List[str]
    differences: List[str]
    cold_knowledge: str
    timestamp: str


# ========================================
# 文化比较器
# ========================================

class CulturalComparator:
    """文化比较器"""

    def __init__(self):
        self.zhuzi = ZHUZI_DB
        self.western = WESTERN_DB
        self.concepts = CONCEPT_MAP

    def extract_concepts(self, text: str) -> List[str]:
        """提取文本中的核心概念"""
        found = []
        for concept in self.concepts:
            if concept in text:
                found.append(concept)
        if not found:
            for k in ["仁", "义", "礼", "智", "信", "忠", "孝"]:
                if k in text:
                    found.append(k)
        return found

    def analyze_confucian(self, text: str, chapter: str = "") -> Dict[str, Any]:
        """分析儒家内部分歧"""
        concepts = self.extract_concepts(text)
        results = {
            "intra_confucian": [],
            "zhuzi_vs_dao": [],
            "zhuzi_vs_mo": [],
            "zhuzi_vs_fa": []
        }

        for concept in concepts:
            if concept in self.concepts:
                mapping = self.concepts[concept]
                for philosopher, view in mapping.get("confucian", {}).items():
                    results["intra_confucian"].append({
                        "concept": concept,
                        "philosopher": philosopher,
                        "view": view
                    })

        daoists = ["老子", "庄子"]
        mo = ["墨子"]
        legalists = ["韩非子"]

        for p, data in self.zhuzi.items():
            if p in daoists:
                results["zhuzi_vs_dao"].append({
                    "philosopher": p,
                    "view": f"人性:{data['人性']}, 政治:{data['政治']}"
                })
            if p in mo:
                results["zhuzi_vs_mo"].append({
                    "philosopher": p,
                    "view": f"核心:{list(data['core'].keys())}, 政治:{data['政治']}"
                })
            if p in legalists:
                results["zhuzi_vs_fa"].append({
                    "philosopher": p,
                    "view": f"核心:{list(data['core'].keys())}, 政治:{data['政治']}"
                })

        return results

    def analyze_western(self, text: str, chapter: str = "") -> Dict[str, Any]:
        """分析中西概念对应"""
        concepts = self.extract_concepts(text)
        results = {
            "concept_mapping": [],
            "traditions": [],
            "method_diff": [],
            "values_diff": []
        }

        for concept in concepts:
            if concept in self.concepts:
                mapping = self.concepts[concept]
                for trad, equiv in mapping.get("western", {}).items():
                    results["concept_mapping"].append({
                        "chinese_concept": concept,
                        "western_tradition": trad,
                        "equivalent": equiv
                    })
                    if trad not in results["traditions"]:
                        results["traditions"].append(trad)

                results["method_diff"].append({
                    "concept": concept,
                    "similar": mapping.get("similar", ""),
                    "diff": mapping.get("diff", "")
                })

        results["traditions"] = list(set(results["traditions"]))
        return results

    def compare(self, text: str, chapter_id: str = "") -> ComparisonResult:
        """执行完整文化比较"""
        concepts = self.extract_concepts(text)
        confucian = self.analyze_confucian(text, chapter_id)
        western = self.analyze_western(text, chapter_id)

        similarities = []
        differences = []

        for concept in concepts:
            if concept in self.concepts:
                mapping = self.concepts[concept]
                if mapping.get("similar"):
                    similarities.append(f"{concept}：{mapping['similar']}")
                if mapping.get("diff"):
                    differences.append(f"{concept}：{mapping['diff']}")

        cold_knowledge = self._generate_cold_knowledge(text, concepts, confucian, western)

        return ComparisonResult(
            chapter_id=chapter_id,
            source_text=text,
            confucian=confucian,
            western=western,
            similarities=similarities,
            differences=differences,
            cold_knowledge=cold_knowledge,
            timestamp=datetime.now().isoformat()
        )

    def _generate_cold_knowledge(self, text: str, concepts: List[str],
                                 confucian: Dict, western: Dict) -> str:
        """生成冷知识命题"""
        if not concepts:
            return '【冷知识】儒家"仁"与斯多葛派"顺应自然"看似相近，实则前者是情感发用，后者是理性接纳，方向相反。'

        c = concepts[0]
        if c in self.concepts:
            diff = self.concepts[c].get("diff", "")
            if "情感" in diff and "理性" in diff:
                return f"【冷知识】{c}的中西理解：表面都强调利他，但儒家是情感推恩，西方是理性原则，本质不同。"

        return "【冷知识】诸子百家与西方哲学的最大差异不在于答案，而在于问题意识：儒家问如何成圣，西方问如何获得真理。"

    def generate_report(self, result: ComparisonResult) -> str:
        """生成文化比较报告（Markdown格式）"""
        lines = [
            f"# 文化比较分析报告",
            f"",
            f"**章节**: {result.chapter_id}",
            f"**生成时间**: {result.timestamp}",
            f"",
            f"---",
            f"",
            f"## 原始章句",
            f"",
            f"{result.source_text}",
            f"",
            f"---",
            f"",
            f"## 一、儒家内部分析",
            f"",
        ]

        if result.confucian.get("intra_confucian"):
            lines.append("### 1.1 孔孟荀观点差异")
            for item in result.confucian["intra_confucian"][:6]:
                lines.append(f"- **{item['philosopher']}** 论{item['concept']}：{item['view']}")

        if result.confucian.get("zhuzi_vs_dao"):
            lines.append("\n### 1.2 儒道分歧")
            for item in result.confucian["zhuzi_vs_dao"][:2]:
                lines.append(f"- {item['philosopher']}：{item['view']}")

        if result.confucian.get("zhuzi_vs_mo"):
            lines.append("\n### 1.3 儒墨分歧")
            for item in result.confucian["zhuzi_vs_mo"][:2]:
                lines.append(f"- {item['philosopher']}：{item['view']}")

        if result.confucian.get("zhuzi_vs_fa"):
            lines.append("\n### 1.4 儒法分歧")
            for item in result.confucian["zhuzi_vs_fa"][:2]:
                lines.append(f"- {item['philosopher']}：{item['view']}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 二、中西哲学比较",
            f"",
        ])

        if result.western.get("concept_mapping"):
            lines.append("### 2.1 概念对应")
            for item in result.western["concept_mapping"][:6]:
                lines.append(
                    f"- **{item['chinese_concept']}** → **{item['western_tradition']}**：{item['equivalent']}"
                )

        if result.western.get("traditions"):
            lines.append(f"\n### 2.2 涉及西方传统")
            lines.append(f"{'、'.join(result.western['traditions'])}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 三、异同分析",
            f"",
            f"### 3.1 相同点",
        ])
        for s in result.similarities[:5]:
            lines.append(f"- {s}")

        lines.extend([
            f"",
            f"### 3.2 根本差异",
        ])
        for d in result.differences[:5]:
            lines.append(f"- {d}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 四、冷知识命题",
            f"",
            f"{result.cold_knowledge}",
            f"",
            f"---",
            f"",
            f"*本报告由 literature-review-skill v4.1.2 自动生成*",
        ])

        return "\n".join(lines)


# ========================================
# 入口函数（供外部调用）
# ========================================

def run_cultural_comparison(text: str, chapter_id: str = "") -> ComparisonResult:
    """执行文化比较分析"""
    comparator = CulturalComparator()
    return comparator.compare(text, chapter_id)


def generate_comparison_report(result: ComparisonResult) -> str:
    """生成文化比较报告"""
    comparator = CulturalComparator()
    return comparator.generate_report(result)


if __name__ == "__main__":
    # 测试
    test_text = "子曰：仁者爱人，克己复礼为仁。"
    result = run_cultural_comparison(test_text, "论语·颜渊12.1")
    report = generate_comparison_report(result)
    print(report)
