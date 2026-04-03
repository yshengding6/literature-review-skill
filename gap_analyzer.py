"""
研究空白检测器（增强版 v2.0）
使用更 sophisticated NLP 技术进行语义分析和上下文理解
支持中英文双语，具有 Analects 级深度分析能力
"""

import re
import logging
from typing import List, Dict, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class GapAnalyzer:
    """研究空白检测器 - Analects 级深度分析"""

    def __init__(self, language: str = "zh"):
        """
        初始化空白检测器

        Args:
            language: 默认语言 "zh" 或 "en"
        """
        self.language = language

        # 扩展的关键词库 - 包含近义词和变体
        self.gap_keywords_enhanced = {
            # 中文关键词
            'zh': [
                # 原始关键词
                '限制', '局限', '不足', '缺乏', '缺少', '有待', '未来',
                # 瓶颈类
                '瓶颈', '难点', '约束', '障碍', '缺陷', '弱点', '不够', '有限', '难以',
                # 未解决类
                '未解答', '待探索', '需研究', '待分析', '待验证', '需进一步', '尚未', '仍需',
                # 否定和转折
                '无法', '不能', '不确定', '未定', '未知',
                '然而', '但是', '不过', '相反',
                # 肯定性表达（表示建议而非结论）
                '建议', '提议', '可能', '或许', '考虑', '应该',
                # 研究空白指示词
                '空白', '未研究', '研究空间', '机会', '方向', '领域',
                # 特定领域关键词
                '需要改进', '有待完善', '尚不明确', '仍不清楚', '有待进一步研究',
                '局限性', '约束条件', '数据不足', '样本有限', '实验限制',
            ],
            # 英文关键词
            'en': [
                # Original keywords
                'further', 'future', 'limitation', 'lack', 'need', 'challenge',
                # Bottleneck class
                'bottleneck', 'difficulty', 'difficult', 'challenge', 'constraint',
                'obstacle', 'deficiency', 'weakness', 'insufficient', 'limited', 'inadequate',
                # Unresolved class
                'unanswered', 'unresolved', 'to be explored', 'needs research',
                'needs analysis', 'needs verification', 'needs further study', 'yet to be',
                # Negative and transition
                'cannot', 'unable', 'unclear', 'uncertain', 'undefined', 'unknown',
                'however', 'but', 'nevertheless', 'in contrast', 'on the other hand',
                # Suggestive expressions
                'suggested', 'proposed', 'possibly', 'perhaps', 'consider', 'should',
                # Research gap indicators
                'gap', 'unexplored', 'opportunity for', 'research direction', 'area',
                # Specific domain keywords
                'needs improvement', 'remains unclear', 'still unclear', 'requires further investigation',
                'limitations', 'constrained by', 'data shortage', 'limited sample', 'experimental constraints',
            ]
        }

        # 空白类型分类系统
        self.gap_categories = {
            'zh': {
                'methodological': ['方法', '理论', '模型', '框架', '机制', '依据', '证明', '算法', '范式'],
                'practical': ['实验', '数据', '样本', '案例', '应用', '实现', '技术', '系统', '平台', '效果', '结果'],
                'theoretical': ['假设', '推导', '前提', '基础', '原理', '定理', '公理'],
                'scope': ['范围', '领域', '跨领域', '多模态', '综合', '覆盖面', '广度'],
                'data': ['数据', '样本', '质量', '完整性', '代表性', '偏差', '噪音', '数据集'],
                'technical': ['架构', '性能', '效率', '可扩展', '兼容', '实现', '部署', '优化'],
                'temporal': ['目前', '现在', '近期', '未来', '长期', '短期', '当前', '以前', '时间'],
            },
            'en': {
                'methodological': ['method', 'theory', 'model', 'framework', 'mechanism', 'basis', 'proof', 'algorithm', 'paradigm'],
                'practical': ['experiment', 'data', 'sample', 'case', 'application', 'implementation', 'technical', 'system', 'platform', 'result'],
                'theoretical': ['hypothesis', 'assumption', 'deduction', 'proof', 'premise', 'basis', 'evidence', 'principle', 'theorem', 'axiom'],
                'scope': ['scope', 'domain', 'intra-domain', 'cross-domain', 'multi-modal', 'comprehensive', 'coverage', 'breadth'],
                'data': ['data', 'sample', 'dataset', 'quality', 'representative', 'bias', 'noise'],
                'technical': ['architecture', 'performance', 'efficiency', 'scalability', 'compatibility', 'deployment', 'optimization'],
                'temporal': ['current', 'now', 'recent', 'future', 'long-term', 'short-term', 'present', 'past', 'time'],
            }
        }

        # 严重性评分系统（基于关键词权重）
        self.severity_weights = {
            'zh': {
                'critical': ['致命', '根本性', '重大', '严重', '关键', '核心'],
                'high': ['不足', '缺乏', '局限', '缺陷', '弱点', '需要', '有待', '有待完善'],
                'medium': ['难以', '不确定', '未定', '尚不明确', '仍不清楚'],
                'low': ['可能', '或许', '考虑', '建议', '提议'],
            },
            'en': {
                'critical': ['critical', 'fundamental', 'major', 'severe', 'significant', 'key', 'essential'],
                'high': ['insufficient', 'limited', 'inadequate', 'deficiency', 'weakness', 'needs', 'requires'],
                'medium': ['difficult', 'unclear', 'uncertain', 'remains unclear', 'challenging'],
                'low': ['possibly', 'perhaps', 'consider', 'suggested', 'proposed'],
            }
        }

    def detect_research_gaps(
        self,
        text: str,
        key_points: Optional[List[Dict[str, str]]] = None,
        max_gaps: int = 10
    ) -> List[Dict[str, Any]]:
        """
        检测研究空白 - Analects 级增强版

        Args:
            text: 文本内容
            key_points: 关键点列表（可选，用于上下文理解）
            max_gaps: 返回的最大空白数量

        Returns:
            研究空白列表，每个空白包含：
            - text: 空白描述
            - type: 空白类型（methodological/practical/theoretical/scope/data/technical/temporal）
            - category: 详细分类
            - severity: 严重性评分（1-5）
            - keywords: 匹配的关键词
            - confidence: 置信度评分（0-1）
        """
        gaps = []

        # 按句子分割（支持中英文标点）
        sentences = re.split(r'[。！？.!?]', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue

            # 提取空白信息
            gap_info = self._extract_gap_info(sentence)
            if gap_info:
                # 计算置信度
                gap_info['confidence'] = self._calculate_confidence(sentence, gap_info)
                gaps.append(gap_info)
                logger.debug(f"检测到空白: {gap_info['text'][:50]}")

        logger.info(f"共检测到研究空白数量: {len(gaps)}")

        # 按严重性和置信度综合排序（取前 N 个）
        gaps.sort(key=lambda x: (x['severity'] * 0.7 + x['confidence'] * 0.3), reverse=True)

        return gaps[:max_gaps]

    def _extract_gap_info(self, sentence: str) -> Optional[Dict[str, Any]]:
        """从句子中提取空白信息"""
        sentence_lower = sentence.lower()

        # 检测空白类型
        gap_type = self._classify_gap_type(sentence_lower)
        if gap_type == 'other':
            return None  # 不是有效的空白

        # 严重性评分
        severity = self._score_gap_severity(sentence_lower)

        # 提取相关关键词
        keywords = self._extract_gap_keywords(sentence_lower)

        # 构建空白信息
        return {
            'text': sentence,
            'type': gap_type,
            'severity': severity,
            'keywords': keywords,
            'category': gap_type,
        }

    def _classify_gap_type(self, sentence: str) -> str:
        """分类空白类型"""
        lang_keywords = self.gap_categories.get(self.language, {})
        for gap_type, keywords in lang_keywords.items():
            if any(keyword in sentence for keyword in keywords):
                return gap_type
        return 'other'

    def _calculate_confidence(self, sentence: str, gap_info: Dict[str, Any]) -> float:
        """
        计算检测置信度

        Args:
            sentence: 原始句子
            gap_info: 已提取的空白信息

        Returns:
            置信度评分（0-1），越高表示越确定是研究空白
        """
        sentence_lower = sentence.lower()
        keywords = gap_info.get('keywords', [])

        if not keywords:
            return 0.3  # 基础置信度

        # 基础分：每个匹配关键词
        base_score = min(0.6, len(keywords) * 0.2)

        # 上下文加分：多个空白关键词出现在同一句子
        context_bonus = 0.1 if len(keywords) >= 2 else 0.0

        # 否定词加分：包含明确的否定或限制表达
        negation_bonus = 0.1 if any(kw in sentence_lower for kw in ['缺乏', '不足', 'lack', 'insufficient']) else 0.0

        # 未来指向加分：明确指向未来工作
        future_bonus = 0.1 if '未来' in sentence_lower or 'future' in sentence_lower else 0.0

        # 句子长度惩罚：过长的句子可能不是明确的空白表达
        length_penalty = max(0, (len(sentence) - 100) / 500) * 0.1

        # 总置信度
        confidence = base_score + context_bonus + negation_bonus + future_bonus - length_penalty

        return max(0.3, min(0.95, confidence))  # 限制在合理范围内

    def _extract_gap_keywords(self, sentence: str) -> List[str]:
        """提取空白相关关键词"""
        keywords = []
        lang_keywords = self.gap_keywords_enhanced.get(self.language, [])

        for keyword in lang_keywords:
            if keyword in sentence:
                keywords.append(keyword)

        return keywords

    def _score_gap_severity(self, sentence: str) -> int:
        """
        对空白严重性进行评分（1-5 分）

        Args:
            sentence: 句子内容

        Returns:
            severity score (1-5), 越高越严重
        """
        severity_weights = self.severity_weights.get(self.language, {})

        # 默认中等严重性
        severity = 3

        # 根据关键词调整严重性
        for level, keywords in severity_weights.items():
            if any(keyword in sentence for keyword in keywords):
                if level == 'critical':
                    severity = 5
                elif level == 'high':
                    severity = max(severity, 4)
                elif level == 'medium':
                    severity = max(severity, 3)
                elif level == 'low':
                    severity = max(severity, 2)

        # 基于上下文调整
        # 短句降低权重（可能是描述性而非实际空白）
        if len(sentence) < 30:
            severity = max(1, severity - 1)

        # 包含多个严重性关键词则提高评分
        critical_count = sum(1 for kw in severity_weights.get('critical', []) if kw in sentence)
        if critical_count >= 2:
            severity = 5

        return min(5, max(1, severity))


# 测试函数
def test_gap_analyzer():
    """测试空白分析器"""
    # 中文测试
    print("=== 中文测试 ===")
    analyzer_zh = GapAnalyzer(language="zh")

    # 测试1：方法论空白
    text1 = "本研究样本量有限，需要扩大数据集规模。实验环境较为复杂。"
    result1 = analyzer_zh.detect_research_gaps(text1)
    print(f"测试1 - 检测到 {len(result1)} 个空白:")
    for gap in result1:
        print(f"  - {gap['text']}: {gap['category']}, 严重性: {gap['severity']}, 置信度: {gap['confidence']:.2f}")

    # 测试2：理论空白
    text2 = "当前方法基于简化假设，未来工作需要更严格的理论基础。"
    result2 = analyzer_zh.detect_research_gaps(text2)
    print(f"\n测试2 - 检测到 {len(result2)} 个空白:")
    for gap in result2:
        print(f"  - {gap['text']}: {gap['category']}, 严重性: {gap['severity']}, 置信度: {gap['confidence']:.2f}")

    # 测试3：技术空白
    text3 = "算法在处理大规模数据时效率较低，需要优化或更换算法。"
    result3 = analyzer_zh.detect_research_gaps(text3)
    print(f"\n测试3 - 检测到 {len(result3)} 个空白:")
    for gap in result3:
        print(f"  - {gap['text']}: {gap['category']}, 严重性: {gap['severity']}, 置信度: {gap['confidence']:.2f}")

    # 英文测试
    print("\n=== English Tests ===")
    analyzer_en = GapAnalyzer(language="en")

    # Test 1: Methodological gap
    text_en1 = "The study has limited sample size and requires expansion of the dataset."
    result_en1 = analyzer_en.detect_research_gaps(text_en1)
    print(f"Test 1 - Detected {len(result_en1)} gaps:")
    for gap in result_en1:
        print(f"  - {gap['text']}: {gap['category']}, severity: {gap['severity']}, confidence: {gap['confidence']:.2f}")

    # Test 2: Theoretical gap
    text_en2 = "The current method relies on simplified assumptions, requiring a more rigorous theoretical foundation."
    result_en2 = analyzer_en.detect_research_gaps(text_en2)
    print(f"\nTest 2 - Detected {len(result_en2)} gaps:")
    for gap in result_en2:
        print(f"  - {gap['text']}: {gap['category']}, severity: {gap['severity']}, confidence: {gap['confidence']:.2f}")


if __name__ == "__main__":
    test_gap_analyzer()
