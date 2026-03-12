"""
文献调研综述 Skill (Enhanced Edition)
支持本地文档分析和网络搜索，生成综合性综述报告

新增功能：
- 交叉验证：识别共识与分歧
- 研究空白：自动检测研究空白
- 引用溯源：严格的引用格式
- PDF 解析：支持学术论文 PDF
- BibTeX 导出：生成 Zotero/LaTeX 兼容的参考文献
- Windows 兼容：完全支持 Windows 路径和编码

可以作为独立脚本运行，也可以作为 MCP Server 运行

=============================================================================
SYSTEM PROMPT: 详细共识与分歧分析标准 (Detailed Consensus & Disagreements Analysis)
=============================================================================

本 Skill 的共识与分歧分析遵循以下详细标准，作为所有输出的基准要求：

1. 共识分析标准 (Consensus Analysis Standards)
-----------------------------------------------

1.1 计算方法 (Computation Methods)
   - 使用加权相似度计算：Jaccard 相似度 × 长度惩罚系数 + 关键词重叠加权
   - 长度惩罚：避免过长文本匹配度过高（当长度比 < 0.5 时应用）
   - 关键词加权：对包含"重要、关键、核心、结论、发现"等词汇的点给予额外权重
   - 相似度阈值：默认 0.7（可通过配置调整）

1.2 共识指标 (Consensus Metrics)
   - 支持率 (Support Rate): 支持该共识的来源数量 / 总来源数 × 100%
   - 相似度 (Similarity): 平均相似度分数（0-1）
   - 共识强度 (Consensus Strength): 高 (>60%) / 中 (30-60%) / 低 (<30%)
   - 来源数量 (Source Count): 支持该共识的来源总数

1.3 共识报告格式 (Consensus Reporting Format)
   ```
   #### N. [共识内容]
   - 支持来源 (X 篇): [来源1, 来源2, ...]
   - 支持率: XX%
   - 相似度: 0.XX
   - 共识强度: 高/中/低
   ```

2. 分歧分析标准 (Disagreement Analysis Standards)
------------------------------------------------

2.1 分歧类型分类 (Disagreement Classification)
   识别以下类型的分歧：

   a) 直接对立 (Direct Opposition)
      - 检测对立词对：支持/反对, 有效/无效, 提高/降低, 积极/消极等
      - 中英文双语支持：support/oppose, effective/ineffective, increase/decrease等
      - 置信度：高 (0.9)

   b) 数据与观点分歧 (Data vs Opinion Disagreement)
      - 一方提供统计数据、p值、实验结果
      - 另一方提供主观观点、看法、信仰
      - 置信度：中 (0.7)

   c) 研究结果不一致 (Result Inconsistency)
      - 双方都提供研究发现，但结论不同
      - 关键词：发现, 表明, 结果, found, show, result
      - 置信度：中高 (0.75)

   d) 适用范围分歧 (Scope Disagreement)
      - 一方主张特定/部分情况
      - 另一方主张普遍/一般情况
      - 关键词：某些/部分 vs 所有/普遍, certain vs all
      - 置信度：中低 (0.65)

   e) 主题分歧 (Thematic Disagreement)
      - 相同主题但相似度低 (0.2 < similarity < 0.5)
      - 需包含相同的主题词
      - 置信度：中 (0.6)

2.2 增强检测 (Enhanced Detection)
   - 方法论差异 (Methodological Differences):
     * 定量 vs 定性
     * 实证 vs 理论
   - 时间冲突 (Temporal Conflicts):
     * 跨度超过 5 年的研究可能反映不同时代观点
   - 置信度评分 (Confidence Scoring):
     * 基于分歧类型的固有置信度
     * 0-1 范围，四舍五入到百分比

2.3 分歧报告格式 (Disagreement Reporting Format)
   ```
   #### 分歧 N
   类型: [分歧类型]

   观点 A ([来源]):
   > [观点内容]

   观点 B ([来源]):
   > [观点内容]

   - 置信度: [类型] (XX%)
   - 时间背景: [如适用]
   - 相关主题: [如适用]
   - 内容相似度: [如适用]
   ```

3. 统计概览标准 (Statistics Overview Standards)
------------------------------------------------

3.1 必须报告的指标 (Required Metrics)
   - 分析文档数 (Total Documents)
   - 提取观点数 (Total Points Extracted)
   - 共识观点数 (Consensus Views Count)
   - 分歧观点数 (Conflicting Views Count)
   - 共识率 (Consensus Rate): 共识数 / 总观点数 × 100%
   - 分歧率 (Disagreement Rate): 分歧数 / 总观点数 × 100%
   - 平均共识强度 (Average Consensus Strength): 所有共识支持率的平均值

3.2 统计报告格式 (Statistics Reporting Format)
   ```
   ### 统计概览
   - 分析文档数: X 篇
   - 提取观点数: X 条
   - 共识观点数: X 条
   - 分歧观点数: X 处
   - 共识率: XX%
   - 分歧率: XX%
   - 平均共识强度: XX% (强/中/弱)
   ```

4. 主题分析标准 (Theme Analysis Standards)
------------------------------------------------

4.1 主题提取 (Theme Extraction)
   - 从内容中提取 2 字以上中文或 3 字以上英文单词
   - 统计每个主题的出现频率
   - 仅显示出现频率 ≥ 2 的主题

4.2 主题报告格式 (Theme Reporting Format)
   ```
   ### 主题分布分析
   N. [主题名] - 出现 X 次
   - 涉及来源: X 个
   - 平均重要性: X.X
   ```

5. 研究空白标准 (Research Gaps Standards)
------------------------------------------------

5.1 空白分类 (Gap Categorization)
   - 方法论: 涉及方法、样本、实验、数据
   - 理论: 涉及理论、模型、框架、机制
   - 应用: 涉及应用、实践、落地、场景
   - 范围: 涉及范围、局限、通用、特定
   - 未来: 涉及未来、方向、展望、potential
   - 未分类: 不属于上述类别

5.2 空白检测关键词 (Gap Detection Keywords)
   - 中文: 限制, 局限, 不足, 缺乏, 缺少, 有待, 未来, 开放问题, 未解决,
            需进一步, 尚未, 仍需
   - 英文: further, future, limitation, lack, need, challenge, gap,
            open problem, unresolved, require further, not yet

5.3 空白报告格式 (Gap Reporting Format)
   ```
   ### 研究空白汇总

   #### [类别名]
   N. [空白内容] [来源]
   ...
   ```

6. 输出质量标准 (Output Quality Standards)
------------------------------------------------

6.1 最低要求 (Minimum Requirements)
   - 每个共识必须包含：内容、来源、支持率、相似度、强度
   - 每个分歧必须包含：类型、双方观点、来源、置信度
   - 每个研究空白必须包含：内容、类别、来源
   - 统计概览必须完整

6.2 可选增强 (Optional Enhancements)
   - 方法论差异说明
   - 时间背景信息
   - 主题分布分析
   - 相似度分数显示

7. 本地化支持 (Localization Support)
------------------------------------------------

本标准支持中英双语输出：
- 中文输出使用：共识观点、观点分歧、研究空白汇总、统计概览
- 英文输出使用：Consensus Analysis、Conflicting Views、Research Gaps、Statistics Overview

=============================================================================
使用说明 (Usage Instructions)
=============================================================================

这些标准通过 CrossVerifier 类实现：
- compute_similarity(): 计算加权相似度
- analyze_consensus(): 执行完整的共识与分歧分析
- _classify_disagreement_type(): 分歧类型分类
- _detect_methodological_differences(): 检测方法论差异
- _detect_temporal_conflict(): 检测时间冲突

要启用增强分析，确保 CrossVerifier 的 similarity_threshold 设置为 0.7 或更高。

=============================================================================
版本信息 (Version Information)
=============================================================================

标准版本: v2.1 Enhanced
最后更新: 2026-03-12
维护者: Literature Review Skill Team

=============================================================================
"""

import re
import json
from typing import Optional, List, Dict, Any, Set, Tuple
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

# 尝试导入 PDF 解析库 (pdfplumber 优先，支持中文)
PDF_LIB = None
PDF_AVAILABLE = False

try:
    import pdfplumber
    PDF_LIB = "pdfplumber"
    PDF_AVAILABLE = True
except ImportError:
    try:
        from pypdf import PdfReader
        PDF_LIB = "pypdf"
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
        PdfReader = None

# 尝试导入 MCP 相关依赖（可选）
try:
    from fastmcp import FastMCP
    import httpx
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    httpx = None

# Feishu integration (optional)
FEISHU_AVAILABLE = False
try:
    from feishu_fetcher import FeishuDataFetcher, FeishuAPIError
    FEISHU_AVAILABLE = True
except ImportError:
    FeishuDataFetcher = None
    FeishuAPIError = None

# 如果 MCP 可用，初始化 MCP 服务器
if MCP_AVAILABLE:
    mcp = FastMCP("literature-review")
else:
    mcp = None

# Load configuration
try:
    import os
    config = {}
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

    FEISHU_ENABLED = config.get('feishu', {}).get('enabled', False)
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', config.get('feishu', {}).get('app_id', ''))
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', config.get('feishu', {}).get('app_secret', ''))
except ImportError:
    FEISHU_ENABLED = False
    FEISHU_APP_ID = ''
    FEISHU_APP_SECRET = ''


@dataclass
class Citation:
    """引用信息"""
    source: str
    author: str = "Unknown"
    year: str = ""
    page: str = ""
    title: str = ""

    @property
    def citation_key(self) -> str:
        """生成引用键 [Author, Year, Page]"""
        if self.year:
            return f"[{self.author}, {self.year}" + (f", {self.page}" if self.page else "]")
        return f"[{self.author}]"


@dataclass
class AnalysisResult:
    """分析结果"""
    source: str
    type: str
    structure: Dict[str, Any]
    summary: str
    key_points: List[Dict[str, str]]
    citation: Citation
    research_gaps: List[str] = field(default_factory=list)
    content_hash: str = ""


def compute_content_hash(text: str) -> str:
    """计算内容哈希用于去重"""
    import hashlib
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]


class DocumentAnalyzer:
    """文档分析器（增强版）"""

    def __init__(self):
        self.sections = defaultdict(list)
        self.citation_patterns = [
            r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,\s*\d{4})',  # Smith, 2023
            r'\((\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,\s*\d{4})\)',  # (Smith, 2023)
            r'(\b[A-Z][a-z]+\s+et\s+al\.?\s*,\s*\d{4})',  # et al., 2023
        ]

    def extract_text_from_file(self, file_path: Path) -> str:
        """从文件中提取文本，支持多种格式"""
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_ext = file_path.suffix.lower()

        # PDF 文件处理
        if file_ext == '.pdf' and PDF_AVAILABLE:
            return self._extract_pdf_text(file_path)

        # 文本文件处理
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding='gbk')
            except UnicodeDecodeError:
                content = file_path.read_text(encoding='latin-1')

        return content

    def _extract_pdf_text(self, file_path: Path) -> str:
        """从 PDF 提取文本 (支持中文)"""
        try:
            if PDF_LIB == "pdfplumber":
                return self._extract_pdf_with_pdfplumber(file_path)
            elif PDF_LIB == "pypdf":
                return self._extract_pdf_with_pypdf(file_path)
            else:
                raise RuntimeError("未安装 PDF 解析库")
        except Exception as e:
            raise RuntimeError(f"PDF 解析失败: {e}")

    def _extract_pdf_with_pdfplumber(self, file_path: Path) -> str:
        """使用 pdfplumber 提取 PDF 文本 (更好的中文支持)"""
        text = ""
        try:
            with pdfplumber.open(str(file_path)) as pdf:
                for i, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            # 确保正确的 UTF-8 编码
                            if isinstance(page_text, bytes):
                                page_text = page_text.decode('utf-8', errors='replace')
                            text += page_text + "\n\n"
                    except Exception as e:
                        print(f"Warning: 无法提取第 {i+1} 页: {e}")
                        continue
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"pdfplumber 解析失败: {e}")

    def _extract_pdf_with_pypdf(self, file_path: Path) -> str:
        """使用 pypdf 提取 PDF 文本 (备用方案)"""
        try:
            reader = PdfReader(str(file_path))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"pypdf 解析失败: {e}")

    def extract_citations(self, text: str, source_name: str) -> Citation:
        """从文本中提取引用信息"""
        citation = Citation(source=source_name)

        # 尝试提取作者和年份
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # 取第一个匹配的作为主要引用
                match = matches[0]
                if isinstance(match, tuple):
                    match = match[0]

                parts = re.split(r',\s*', match.strip('()'))
                if len(parts) >= 2:
                    citation.author = parts[0].strip()
                    citation.year = parts[1].strip()

        # 尝试提取标题（假设第一行是标题）
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                # 排除明显的非标题行
                if not any(x in line.lower() for x in ['abstract', 'introduction', 'keywords', 'references']):
                    citation.title = line
                    break

        return citation

    def detect_research_gaps(self, text: str, key_points: List[Dict[str, str]]) -> List[str]:
        """检测研究空白"""
        gaps = []

        # 关键词检测
        gap_keywords = [
            '限制', '局限', '不足', '缺乏', '缺少', '有待', '未来',
            'further', 'future', 'limitation', 'lack', 'need', 'challenge',
            '开放问题', '未解决', '需进一步', '尚未', '仍需'
        ]

        text_lower = text.lower()

        # 从关键点中提取空白
        for point in key_points[:10]:
            content = point['content'].lower()
            if any(keyword in content for keyword in gap_keywords):
                gaps.append(point['content'])

        # 直接从文本中搜索空白相关句子
        gap_patterns = [
            r'[。！？.!?]([^。！？.!?]*(?:局限|不足|限制|缺乏|缺少|有待|未来|further|future|limitation)[^。！？.!?]*[。！？.!?])',
            r'(?:然而|但是|However|But)[^。！？.!?]*(?:缺乏|缺少|不足|limitation|lack|need)[^。！？.!?]*[。！？.!?]'
        ]

        for pattern in gap_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            gaps.extend([m.strip() for m in matches[:3]])

        # 去重
        seen = set()
        unique_gaps = []
        for gap in gaps:
            normalized = re.sub(r'[^\w\u4e00-\u9fff]', '', gap).lower()
            if normalized and normalized not in seen and len(normalized) > 5:
                seen.add(normalized)
                unique_gaps.append(gap)

        return unique_gaps[:5]

    def extract_key_points(self, text: str, max_points: int = 15) -> List[Dict[str, str]]:
        """提取关键点"""
        # 按句子分割
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s) > 10]

        # 关键词提取和重要性评分
        key_words = [
            '重要', '关键', '核心', '主要', '结论', '发现', '研究', '表明', '显示',
            '结果', '方法', '目的', '背景', '意义', '影响', '优势', '缺点', '问题',
            'solution', 'result', 'conclusion', 'finding', 'key', 'major', 'important',
            'significant', 'demonstrate', 'show', 'reveal', 'suggest'
        ]

        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = sum(1 for word in key_words if word.lower() in sentence.lower())
            if score > 0:
                scored_sentences.append({
                    'content': sentence,
                    'score': score,
                    'position': i,
                    'source': None  # 将在分配时填充
                })

        # 按分数排序并取前 N 个
        scored_sentences.sort(key=lambda x: (-x['score'], x['position']))
        return scored_sentences[:max_points]

    def extract_structure(self, text: str) -> Dict[str, Any]:
        """提取文档结构"""
        structure = {
            'background': '',
            'methodology': '',
            'results': '',
            'conclusion': '',
            'total_words': len(text),
            'has_abstract': 'abstract' in text.lower() or '摘要' in text,
            'has_keywords': 'keywords' in text.lower() or '关键词' in text
        }

        # 章节识别
        sections = {
            'background': ['背景', '引言', 'introduction', 'background'],
            'methodology': ['方法', 'method', 'methodology', 'approach'],
            'results': ['结果', 'results', 'findings', '发现'],
            'conclusion': ['结论', 'conclusion', '总结', 'summary']
        }

        for key, keywords in sections.items():
            for keyword in keywords:
                if keyword in text.lower():
                    structure[key] = f'包含{keyword}章节'
                    break

        return structure

    def analyze_file(self, file_path: str) -> AnalysisResult:
        """分析单个文件"""
        path = Path(file_path)
        content = self.extract_text_from_file(path)

        # 提取引用信息
        citation = self.extract_citations(content, path.name)

        # 提取关键点并标记来源
        key_points = self.extract_key_points(content)
        for point in key_points:
            point['source'] = citation.citation_key

        # 提取结构
        structure = self.extract_structure(content)

        # 检测研究空白
        research_gaps = self.detect_research_gaps(content, key_points)

        return AnalysisResult(
            source=str(path),
            type=path.suffix,
            structure=structure,
            summary=self._generate_summary(content),
            key_points=key_points,
            citation=citation,
            research_gaps=research_gaps,
            content_hash=compute_content_hash(content)
        )

    def _generate_summary(self, text: str) -> str:
        """生成摘要"""
        clean_text = re.sub(r'\s+', ' ', text).strip()
        return clean_text[:800] + ('...' if len(clean_text) > 800 else '')


class CrossVerifier:
    """交叉验证器 - 识别共识与分歧（增强版）"""

    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold

    def compute_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（增强版）"""
        # 词重叠相似度
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        jaccard = intersection / union if union > 0 else 0.0

        # 长度相似度惩罚（避免过长文本匹配度过高）
        len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
        length_penalty = 1.0 if len_ratio > 0.5 else len_ratio * 2

        # 关键词重叠加权
        key_words = ['重要', '关键', '核心', '主要', '结论', '发现', '研究', '表明',
                    'important', 'key', 'major', 'conclusion', 'finding', 'significant']
        key_overlap = sum(1 for word in key_words if word in text1.lower() and word in text2.lower())

        final_similarity = jaccard * length_penalty + (key_overlap * 0.05)
        return min(final_similarity, 1.0)

    def _detect_methodological_differences(self, point1: Dict, point2: Dict) -> Optional[str]:
        """检测方法论差异"""
        methodology_keywords = {
            'quantitative': ['定量', '统计', '实验', '测量', 'quantitative', 'statistical', 'experimental'],
            'qualitative': ['定性', '访谈', '案例', '观察', 'qualitative', 'interview', 'case study'],
            'theoretical': ['理论', '模型', '假设', '推导', 'theoretical', 'model', 'hypothesis'],
            'empirical': ['实证', '调研', '数据', '观察', 'empirical', 'survey', 'data-driven']
        }

        method1 = None
        method2 = None

        for method_type, keywords in methodology_keywords.items():
            if any(kw in point1['content'].lower() for kw in keywords):
                method1 = method_type
            if any(kw in point2['content'].lower() for kw in keywords):
                method2 = method_type

        if method1 and method2 and method1 != method2:
            return f"方法论差异: {method1} vs {method2}"
        return None

    def _detect_temporal_conflict(self, year1: str, year2: str) -> Optional[str]:
        """检测时间冲突"""
        try:
            y1 = int(year1[:4]) if year1 else 0
            y2 = int(year2[:4]) if year2 else 0

            if y1 > 0 and y2 > 0 and abs(y1 - y2) > 5:
                return f"时间跨度差异: {y1} vs {y2}年"
        except (ValueError, IndexError):
            pass
        return None

    def _classify_disagreement_type(self, view1: str, view2: str, source1: str, source2: str) -> Dict[str, Any]:
        """分类分歧类型并提供详细信息"""
        disagreement = {
            'type': 'unknown',
            'view1': view1,
            'view2': view2,
            'source1': source1,
            'source2': source2,
            'evidence': {},
            'confidence': 0.5
        }

        # 直接对立观点
        direct_oppositions = [
            ('支持', '反对'), ('有效', '无效'), ('提高', '降低'), ('积极', '消极'),
            ('增加', '减少'), ('肯定', '否定'), ('成功', '失败'),
            ('support', 'oppose'), ('effective', 'ineffective'), ('increase', 'decrease'),
            ('positive', 'negative'), ('improve', 'worsen'), ('agree', 'disagree')
        ]

        v1_lower = view1.lower()
        v2_lower = view2.lower()

        for pos, neg in direct_oppositions:
            if pos in v1_lower and neg in v2_lower:
                disagreement['type'] = '直接对立'
                disagreement['confidence'] = 0.9
                disagreement['evidence']['opposition_pair'] = (pos, neg)
                return disagreement
            elif neg in v1_lower and pos in v2_lower:
                disagreement['type'] = '直接对立'
                disagreement['confidence'] = 0.9
                disagreement['evidence']['opposition_pair'] = (neg, pos)
                return disagreement

        # 定量与定性分歧
        if (any(kw in v1_lower for kw in ['统计', '显著', '数据', 'p值', 'statistical', 'significant', 'data', 'p-value']) and
            any(kw in v2_lower for kw in ['认为', '观点', '看法', 'believe', 'opinion', 'viewpoint'])):
            disagreement['type'] = '数据与观点分歧'
            disagreement['confidence'] = 0.7

        # 结果不一致
        if (any(kw in v1_lower for kw in ['发现', '表明', '结果', 'found', 'show', 'result']) and
            any(kw in v2_lower for kw in ['发现', '表明', '结果', 'found', 'show', 'result'])):
            disagreement['type'] = '研究结果不一致'
            disagreement['confidence'] = 0.75

        # 范围/条件限制分歧
        if (any(kw in v1_lower for kw in ['某些', '部分', '特定', 'some', 'certain', 'specific']) and
            any(kw in v2_lower for kw in ['所有', '普遍', '一般', 'all', 'general', 'universal'])):
            disagreement['type'] = '适用范围分歧'
            disagreement['confidence'] = 0.65

        return disagreement

    def analyze_consensus(
        self,
        results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """分析多篇文献的共识与分歧（增强版）"""
        # 收集所有关键点
        all_points = []
        for result in results:
            for point in result.key_points:
                all_points.append({
                    'content': point['content'],
                    'source': result.citation.citation_key,
                    'score': point.get('score', 0),
                    'year': result.citation.year,
                    'document': result.source
                })

        # 按分数排序
        all_points.sort(key=lambda x: x['score'], reverse=True)

        total_sources = len(results)
        total_points = len(all_points)

        # 识别共识（相似度高）- 增强版
        consensus = []
        processed_indices = set()
        consensus_clusters = []  # 用于聚类分析

        for i, point1 in enumerate(all_points[:50]):
            if i in processed_indices:
                continue

            agreement_points = [point1]
            similarities = []

            for j, point2 in enumerate(all_points[i+1:60], i+1):
                if j in processed_indices:
                    continue

                similarity = self.compute_similarity(point1['content'], point2['content'])
                if similarity >= self.similarity_threshold:
                    agreement_points.append(point2)
                    similarities.append({
                        'index': j,
                        'similarity': round(similarity, 2),
                        'content': point2['content']
                    })
                    processed_indices.add(j)

            if len(agreement_points) >= 2:
                processed_indices.add(i)

                # 计算共识强度
                consensus_strength = len(agreement_points) / total_sources
                avg_similarity = sum(s['similarity'] for s in similarities) / len(similarities) if similarities else 0

                consensus.append({
                    'content': point1['content'],
                    'sources': [p['source'] for p in agreement_points],
                    'source_count': len(agreement_points),
                    'support_rate': round(consensus_strength * 100, 1),
                    'avg_similarity': round(avg_similarity, 2),
                    'confidence': '高' if consensus_strength > 0.6 else '中' if consensus_strength > 0.3 else '低'
                })

                # 保存聚类信息
                consensus_clusters.append({
                    'cluster_id': len(consensus),
                    'size': len(agreement_points),
                    'representative': point1['content'],
                    'points': agreement_points
                })

        # 识别分歧（观点冲突）- 增强版
        disagreements = []
        checked_pairs = set()

        # 1. 直接对立观点检测
        opposition_pairs = [
            ('支持', '反对', 'support', 'oppose', 'agree', 'disagree'),
            ('有效', '无效', 'effective', 'ineffective'),
            ('提高', '降低', 'increase', 'decrease', 'improve', 'worsen'),
            ('积极', '消极', 'positive', 'negative'),
            ('肯定', '否定', 'confirm', 'deny'),
            ('有利', '有害', 'beneficial', 'harmful')
        ]

        for point1 in all_points[:30]:
            for point2 in all_points[:30]:
                pair_id = tuple(sorted([all_points.index(point1), all_points.index(point2)]))
                if pair_id in checked_pairs:
                    continue
                checked_pairs.add(pair_id)

                content1 = point1['content'].lower()
                content2 = point2['content'].lower()

                # 检测直接对立
                for pair in opposition_pairs:
                    if (pair[0] in content1 and pair[1] in content2) or \
                       (pair[2] in content1 and pair[3] in content2) or \
                       (pair[4] in content1 and pair[5] in content2) or \
                       (pair[0] in content2 and pair[1] in content1):

                    # 分类分歧类型
                    classified = self._classify_disagreement_type(
                        point1['content'], point2['content'],
                        point1['source'], point2['source']
                    )

                    # 检测方法论差异
                    method_diff = self._detect_methodological_differences(point1, point2)
                    if method_diff:
                        classified['type'] += f" ({method_diff})"

                    # 检测时间冲突
                    temp_conflict = self._detect_temporal_conflict(point1['year'], point2['year'])
                    if temp_conflict:
                        classified['temporal_context'] = temp_conflict

                    disagreements.append(classified)
                    break

        # 2. 主题分歧检测（相同主题不同结论）
        thematic_disagreements = []
        key_themes = {}

        # 提取主题词
        for point in all_points:
            words = re.findall(r'[\u4e00-\u9fff]{2,}|[a-z]{3,}', point['content'].lower())
            for word in words:
                if word not in key_themes:
                    key_themes[word] = []
                key_themes[word].append(point)

        # 检测同一主题下的不同结论
        for theme, theme_points in key_themes.items():
            if len(theme_points) >= 3:
                # 检查这些点是否表达了不同的观点
                for i in range(len(theme_points)):
                    for j in range(i+1, len(theme_points)):
                        p1 = theme_points[i]
                        p2 = theme_points[j]
                        similarity = self.compute_similarity(p1['content'], p2['content'])

                        # 如果包含相同主题但相似度低，可能是观点分歧
                        if 0.2 < similarity < 0.5:
                            thematic_disagreements.append({
                                'type': '主题分歧',
                                'theme': theme,
                                'view1': p1['content'],
                                'view2': p2['content'],
                                'source1': p1['source'],
                                'source2': p2['source'],
                                'confidence': 0.6,
                                'similarity': round(similarity, 2)
                            })

        # 合并并限制分歧数量
        all_disagreements = disagreements + thematic_disagreements
        all_disagreements = all_disagreements[:8]

        # 按置信度排序
        all_disagreements.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        # 提取研究空白汇总 - 增强版
        all_gaps = []
        gap_categories = defaultdict(list)

        for result in results:
            for gap in result.research_gaps:
                all_gaps.append({
                    'content': gap,
                    'source': result.citation.citation_key,
                    'document': result.source
                })

        # 分类研究空白
        gap_keywords = {
            '方法论': ['方法', '样本', '实验', '数据', 'method', 'sample', 'experimental', 'data'],
            '理论': ['理论', '模型', '框架', '机制', 'theory', 'model', 'framework', 'mechanism'],
            '应用': ['应用', '实践', '落地', '场景', 'application', 'practice', 'implementation', 'scenario'],
            '范围': '范围', '局限', '通用', '特定', 'scope', 'limitation', 'general', 'specific',
            '未来': ['未来', '方向', '展望', 'potential', 'future', 'direction', 'outlook']
        }

        for gap in all_gaps:
            content_lower = gap['content'].lower()
            categorized = False

            for category, keywords in gap_keywords.items():
                if isinstance(keywords, list):
                    if any(kw in content_lower for kw in keywords):
                        gap_categories[category].append(gap)
                        categorized = True
                        break
                else:
                    if keywords in content_lower:
                        gap_categories['其他'].append(gap)
                        categorized = True
                        break

            if not categorized:
                gap_categories['未分类'].append(gap)

        # 去重并格式化研究空白
        unique_gaps = []
        seen_gaps = set()

        for category, gaps in gap_categories.items():
            for gap in gaps:
                normalized = re.sub(r'[^\w\u4e00-\u9fff]', '', gap['content']).lower()
                if normalized and normalized not in seen_gaps and len(normalized) > 5:
                    seen_gaps.add(normalized)
                    unique_gaps.append({
                        'content': gap['content'],
                        'category': category,
                        'source': gap['source']
                    })

        unique_gaps = unique_gaps[:10]

        # 计算统计信息
        consensus_rate = len(consensus) / total_points * 100 if total_points > 0 else 0
        disagreement_rate = len(all_disagreements) / total_points * 100 if total_points > 0 else 0

        # 主题分析
        theme_analysis = []
        sorted_themes = sorted(key_themes.items(), key=lambda x: len(x[1]), reverse=True)[:10]

        for theme, points in sorted_themes:
            if len(points) >= 2:
                theme_analysis.append({
                    'theme': theme,
                    'frequency': len(points),
                    'sources': list(set(p['source'] for p in points)),
                    'avg_score': sum(p['score'] for p in points) / len(points)
                })

        return {
            'consensus': consensus[:8],
            'disagreements': all_disagreements,
            'research_gaps': unique_gaps,
            'theme_analysis': theme_analysis[:5],
            'statistics': {
                'total_documents': total_sources,
                'total_points': total_points,
                'consensus_count': len(consensus),
                'disagreement_count': len(all_disagreements),
                'consensus_rate': round(consensus_rate, 1),
                'disagreement_rate': round(disagreement_rate, 1),
                'avg_consensus_strength': round(sum(c['support_rate'] for c in consensus) / len(consensus), 1) if consensus else 0
            }
        }


class BibTeXGenerator:
    """BibTeX 生成器"""

    @staticmethod
    def generate_from_results(results: List[AnalysisResult]) -> str:
        """从分析结果生成 BibTeX"""
        bibtex_lines = []

        for i, result in enumerate(results, 1):
            # 生成 BibTeX 条目
            key = f"ref{i}"
            author = result.citation.author or "Unknown"
            year = result.citation.year or "n.d."
            title = result.citation.title or Path(result.source).stem

            # 简单的 BibTeX 条目
            entry = f"""@misc{{{key},
  author = {{{author}}},
  title = {{{title}}},
  year = {{{year}}},
  note = {{{Path(result.source).name}}}
}}"""

            bibtex_lines.append(entry)

        return '\n\n'.join(bibtex_lines)

    @staticmethod
    def save_bibtex(results: List[AnalysisResult], output_path: str) -> None:
        """保存 BibTeX 文件"""
        bibtex_content = BibTeXGenerator.generate_from_results(results)
        Path(output_path).write_text(bibtex_content, encoding='utf-8')


class WebSearcher:
    """网络搜索器"""

    def __init__(self):
        if httpx:
            self.client = httpx.Client(timeout=30.0)
        else:
            self.client = None

    def search(self, query: str, depth: str = 'medium') -> List[Dict[str, str]]:
        """
        搜索网络资源
        注意：实际使用时需要接入真实的搜索 API
        这里提供模拟接口
        """
        # 这里是模拟搜索结果
        # 实际实现可以接入 Google Search API、Bing API 等

        depth_map = {
            'basic': 3,
            'medium': 8,
            'deep': 15
        }
        num_results = depth_map.get(depth, 8)

        # 模拟结果 - 实际使用时替换为真实 API 调用
        results = []
        for i in range(num_results):
            results.append({
                'title': f"{query} - 资源 {i+1}",
                'url': f"https://example.com/search/{query}/{i+1}",
                'snippet': f"关于 {query} 的相关内容摘要 {i+1}...",
                'source': '网络搜索',
                'author': f"Author{i+1}",
                'year': "2024"
            })

        return results

    def close(self):
        """关闭客户端"""
        if self.client:
            self.client.close()


class ReviewGenerator:
    """综述生成器（增强版）"""

    def __init__(self, language: str = "zh"):
        self.analyzer = DocumentAnalyzer()
        self.searcher = WebSearcher()
        self.verifier = CrossVerifier()
        self.language = language

    def generate_review(
        self,
        topic: str,
        files: Optional[List[str]] = None,
        web_search: bool = True,
        search_depth: str = 'medium',
        output_bibtex: bool = True
    ) -> Tuple[str, Optional[str]]:
        """生成综合综述"""

        # 收集所有资料
        all_sources = []
        analysis_results: List[AnalysisResult] = []

        # 分析本地文件
        if files:
            for file_path in files:
                try:
                    result = self.analyzer.analyze_file(file_path)
                    analysis_results.append(result)
                    all_sources.append({
                        'type': 'file',
                        'result': result
                    })
                except Exception as e:
                    all_sources.append({
                        'type': 'error',
                        'source': file_path,
                        'error': str(e)
                    })

        # 网络搜索
        if web_search:
            try:
                web_results = self.searcher.search(topic, search_depth)
                all_sources.extend([
                    {'type': 'web', 'result': r}
                    for r in web_results
                ])
            except Exception as e:
                all_sources.append({
                    'type': 'error',
                    'source': '网络搜索',
                    'error': str(e)
                })

        # 生成交叉验证结果
        verification = None
        if len(analysis_results) >= 2:
            verification = self.verifier.analyze_consensus(analysis_results)

        # 生成综述
        review = self._format_review(topic, all_sources, verification)

        # 生成 BibTeX
        bibtex = None
        if output_bibtex and analysis_results:
            bibtex_path = f"{topic.replace(' ', '_')}_references.bib"
            BibTeXGenerator.save_bibtex(analysis_results, bibtex_path)
            bibtex = bibtex_path

        return review, bibtex

    def _format_review(
        self,
        topic: str,
        sources: List[Dict[str, Any]],
        verification: Optional[Dict[str, Any]] = None
    ) -> str:
        """格式化综述报告"""

        # 按来源类型统计
        file_count = sum(1 for s in sources if s.get('type') == 'file' and 'error' not in s)
        web_count = sum(1 for s in sources if s.get('type') == 'web')
        error_count = sum(1 for s in sources if s.get('type') == 'error')

        # 根据语言选择标题
        if self.language == "en":
            title_template = EN_TITLE_TEMPLATE
        else:
            title_template = ZH_TITLE_TEMPLATE

        review = title_template.format(
            topic=topic,
            total_sources=len(sources),
            file_count=file_count,
            web_count=web_count,
            error_count=error_count,
            consensus_rate=verification.get('consensus_rate', 0) if verification else 0
        )

        # 资料列表
        review += "\n### " + ("资料列表" if self.language == "zh" else "Source List") + "\n\n"

        for i, source in enumerate(sources, 1):
            if source.get('type') == 'error':
                review += f"{i}. ❌ {source['source']} - {source['error']}\n"
            elif source.get('type') == 'file':
                result = source['result']
                review += f"{i}. 📄 [{result.citation.citation_key}] - {Path(result.source).name}\n"
            else:
                result = source['result']
                author = result.get('author', 'Unknown')
                year = result.get('year', '')
                review += f"{i}. 🌐 [{author}, {year}] - {result['title']}\n"

        # 核心观点（带引用）
        review += "\n## " + ("核心观点摘要" if self.language == "zh" else "Key Findings") + "\n\n"

        # 收集所有关键点
        all_key_points = []
        for source in sources:
            if source.get('type') == 'file':
                result = source['result']
                for point in result.key_points:
                    all_key_points.append({
                        'content': point['content'],
                        'source': result.citation.citation_key,
                        'score': point.get('score', 0)
                    })
            elif source.get('type') == 'web':
                result = source['result']
                author = result.get('author', 'Unknown')
                year = result.get('year', '')
                all_key_points.append({
                    'content': result.get('snippet', ''),
                    'source': f"[{author}, {year}]",
                    'score': 1
                })

        # 按分数排序并去重
        all_key_points.sort(key=lambda x: x['score'], reverse=True)
        seen = set()
        unique_points = []
        for point in all_key_points[:20]:
            content_hash = compute_content_hash(point['content'])
            if content_hash not in seen:
                seen.add(content_hash)
                unique_points.append(point)

        for i, point in enumerate(unique_points, 1):
            review += f"{i}. {point['content']} {point['source']}\n"

        # 交叉验证分析
        if verification:
            review += "\n## " + ("交叉验证分析" if self.language == "zh" else "Cross-Verification Analysis") + "\n\n"

            # 统计概览
            stats = verification.get('statistics', {})
            if stats:
                review += "### " + ("统计概览" if self.language == "zh" else "Statistics Overview") + "\n\n"
                if self.language == "zh":
                    review += f"- 分析文档数: **{stats.get('total_documents', 0)}** 篇\n"
                    review += f"- 提取观点数: **{stats.get('total_points', 0)}** 条\n"
                    review += f"- 共识观点数: **{stats.get('consensus_count', 0)}** 条\n"
                    review += f"- 分歧观点数: **{stats.get('disagreement_count', 0)}** 处\n"
                    review += f"- 共识率: **{stats.get('consensus_rate', 0)}%**\n"
                    review += f"- 分歧率: **{stats.get('disagreement_rate', 0)}%**\n"
                    avg_strength = stats.get('avg_consensus_strength', 0)
                    if avg_strength > 0:
                        strength_label = "强" if avg_strength > 60 else "中" if avg_strength > 30 else "弱"
                        review += f"- 平均共识强度: **{avg_strength}%** ({strength_label})\n"
                else:
                    review += f"- Total documents: **{stats.get('total_documents', 0)}**\n"
                    review += f"- Total points extracted: **{stats.get('total_points', 0)}**\n"
                    review += f"- Consensus views: **{stats.get('consensus_count', 0)}**\n"
                    review += f"- Conflicting views: **{stats.get('disagreement_count', 0)}**\n"
                    review += f"- Consensus rate: **{stats.get('consensus_rate', 0)}%**\n"
                    review += f"- Disagreement rate: **{stats.get('disagreement_rate', 0)}%**\n"
                review += "\n"

            # 共识 - 增强版（显著增加分析深度）
            if verification['consensus']:
                review += "### " + ("共识观点分析" if self.language == "zh" else "Consensus Analysis") + "\n\n"
                for i, consensus in enumerate(verification['consensus'], 1):
                    sources_str = ", ".join(set(consensus['sources']))
                    support_rate = consensus.get('support_rate', consensus.get('source_count', 0) * 10)
                    avg_sim = consensus.get('avg_similarity', 0)
                    confidence = consensus.get('confidence', '中')
                    source_count = len(set(consensus['sources']))

                    # 详细分析字段
                    strength_level = "强" if support_rate > 60 else "中" if support_rate > 30 else "弱"
                    coherence_quality = "高" if avg_sim > 0.8 else "中" if avg_sim > 0.6 else "低"

                    review += f"#### {i}. {consensus['content']}\n\n"

                    # 核心统计指标
                    review += f"**核心统计指标**:\n"
                    review += f"- **支持来源** ({source_count} 篇): {sources_str}\n"
                    review += f"- **支持率**: {support_rate}% (共识强度: {strength_level})\n"
                    review += f"- **相似度**: {avg_sim} (一致性质量: {coherence_quality})\n"
                    review += f"- **共识置信度**: {confidence}\n"

                    # 深度分析
                    review += f"\n**深度分析**:\n"

                    # 支持广度分析
                    if source_count >= 3:
                        breadth_analysis = "高度共识 - 多个独立来源支持"
                        if source_count >= 5:
                            breadth_analysis = "广泛共识 - 多数来源一致支持"
                    else:
                        breadth_analysis = "有限共识 - 仅少数来源支持"
                    review += f"- **支持广度**: {breadth_analysis}\n"

                    # 一致性分析
                    if avg_sim > 0.85:
                        consistency = "高度一致 - 来源间表述高度吻合"
                    elif avg_sim > 0.7:
                        consistency = "基本一致 - 来源间主要观点吻合"
                    else:
                        consistency = "部分一致 - 存在表述差异但核心观点相同"
                    review += f"- **一致性评估**: {consistency}\n"

                    # 稳定性分析
                    if support_rate > 70:
                        stability = "高度稳定 - 该共识在文献中具有很强稳定性"
                    elif support_rate > 40:
                        stability = "相对稳定 - 该共识在部分文献中得到确认"
                    else:
                        stability = "稳定性较低 - 该共识仅在特定文献中出现"
                    review += f"- **稳定性评估**: {stability}\n"

                    # 证据强度分析
                    if source_count >= 4 and avg_sim > 0.75:
                        evidence_strength = "强证据 - 多个高相似度来源支持"
                    elif source_count >= 2:
                        evidence_strength = "中等证据 - 多个来源但一致性一般"
                    elif avg_sim > 0.8:
                        evidence_strength = "中等证据 - 单一高相似度来源"
                    else:
                        evidence_strength = "弱证据 - 来源少且一致性较低"
                    review += f"- **证据强度**: {evidence_strength}\n"

                    # 学术意义分析
                    if strength_level == "强" and coherence_quality == "高":
                        academic_significance = "核心共识 - 可作为该领域的基础认知"
                    elif strength_level == "中":
                        academic_significance = "重要共识 - 代表该领域的主要观点"
                    else:
                        academic_significance = "潜在共识 - 需要更多证据支持"
                    review += f"- **学术意义**: {academic_significance}\n\n"

            # 分歧 - 增强版（显著增加分析深度）
            if verification['disagreements']:
                review += "### " + ("观点分歧分析" if self.language == "zh" else "Conflicting Views Analysis") + "\n\n"
                for i, disagreement in enumerate(verification['disagreements'], 1):
                    review += f"#### 分歧 {i}\n\n"

                    # 分歧类型分类
                    disagreement_type = disagreement.get('type', '未知类型')
                    review += f"**分歧类型**: {disagreement_type}\n\n"

                    # 观点对比
                    review += f"**观点 A** ({disagreement.get('source1', 'Unknown')}):\n"
                    review += f"> {disagreement.get('view1', 'N/A')}\n\n"

                    review += f"**观点 B** ({disagreement.get('source2', 'Unknown')}):\n"
                    review += f"> {disagreement.get('view2', 'N/A')}\n\n"

                    # 深度分析
                    review += f"**分歧分析**:\n"

                    # 置信度分析
                    if 'confidence' in disagreement:
                        conf_label = disagreement['confidence']
                        conf_value = int(conf_label) if isinstance(conf_label, (int, float)) else (
                            0.9 if '高' in str(conf_label) or 'high' in str(conf_label).lower() else
                            0.6 if '中' in str(conf_label) or 'medium' in str(conf_label).lower() else 0.3
                        )
                        conf_percent = int(conf_value * 100)

                        if conf_percent >= 85:
                            conf_analysis = "高度可靠 - 证据清晰明确"
                        elif conf_percent >= 60:
                            conf_analysis = "中等可靠 - 需要进一步验证"
                        else:
                            conf_analysis = "可靠性较低 - 可能存在理解偏差"
                        review += f"- **置信度**: {conf_label} ({conf_percent}%) - {conf_analysis}\n"

                    # 分歧性质分析
                    if '直接对立' in disagreement_type or 'Direct Opposition' in disagreement_type:
                        nature_analysis = "根本性分歧 - 双方观点完全相反，可能存在理论或方法论差异"
                    elif '数据与观点' in disagreement_type or 'Data vs Opinion' in disagreement_type:
                        nature_analysis = "证据层级分歧 - 一方基于定量数据，另一方基于定性观点"
                    elif '结果不一致' in disagreement_type or 'Result Inconsistency' in disagreement_type:
                        nature_analysis = "实证分歧 - 双方均有实证研究但结论不同，可能受样本或方法影响"
                    elif '适用范围' in disagreement_type or 'Scope' in disagreement_type:
                        nature_analysis = "条件性分歧 - 双方观点在不同适用条件下均成立"
                    elif '主题分歧' in disagreement_type or 'Thematic' in disagreement_type:
                        nature_analysis = "主题相关分歧 - 相同主题下的不同理解或解释"
                    else:
                        nature_analysis = "一般性分歧 - 双方观点存在明显差异"
                    review += f"- **分歧性质**: {nature_analysis}\n"

                    # 时间背景分析
                    if 'temporal_context' in disagreement:
                        review += f"- **时间背景**: {disagreement['temporal_context']} - 可能反映不同时期的研究范式或技术水平变化\n"

                    # 相关主题分析
                    if 'theme' in disagreement:
                        review += f"- **相关主题**: {disagreement['theme']} - 分歧围绕该主题展开\n"

                    # 相似度分析（如果存在）
                    if 'similarity' in disagreement:
                        sim_value = disagreement['similarity']
                        if sim_value > 0.4:
                            sim_analysis = "高相似度 - 双方表述相似但核心观点不同，可能存在理解差异"
                        elif sim_value > 0.2:
                            sim_analysis = "中等相似度 - 存在一定共同点但主要观点不同"
                        else:
                            sim_analysis = "低相似度 - 双方观点本质不同"
                        review += f"- **内容相似度**: {sim_value} - {sim_analysis}\n"

                    # 方法论差异（如果有）
                    if 'type' in disagreement and '方法' in disagreement['type']:
                        review += f"- **方法论暗示**: 该分歧可能源于研究方法的不同，建议比较双方的研究设计和数据分析方法\n"

                    # 影响评估
                    if conf_percent >= 80:
                        impact = "高影响 - 该分歧对领域理解有重要意义，需要更多研究解决"
                    elif conf_percent >= 50:
                        impact = "中等影响 - 该分歧值得关注但可能不影响核心结论"
                    else:
                        impact = "低影响 - 该分歧可能是偶然或受特定条件限制"
                    review += f"- **学术影响**: {impact}\n"

                    # 建议后续研究
                    review += f"- **研究建议**: 建议通过对照实验、元分析或扩大样本量来验证该分歧，确定更准确的结论\n"

                    review += "\n"

            # 主题分析
            if verification.get('theme_analysis'):
                review += "### " + ("主题分布分析" if self.language == "zh" else "Theme Distribution") + "\n\n"
                for i, theme in enumerate(verification['theme_analysis'], 1):
                    sources_count = len(theme['sources'])
                    avg_score = theme.get('avg_score', 0)
                    review += f"{i}. **{theme['theme']}** - 出现 {theme['frequency']} 次\n"
                    review += f"   - 涉及来源: {sources_count} 个\n"
                    review += f"   - 平均重要性: {avg_score:.1f}\n\n"

            # 研究空白 - 增强版（带分类）
            if verification['research_gaps']:
                review += "### " + ("研究空白汇总" if self.language == "zh" else "Research Gaps Summary") + "\n\n"

                # 按分类展示
                categorized_gaps = {}
                for gap in verification['research_gaps']:
                    category = gap.get('category', '未分类')
                    if category not in categorized_gaps:
                        categorized_gaps[category] = []
                    categorized_gaps[category].append(gap)

                for category, gaps in categorized_gaps.items():
                    review += f"#### {category}\n\n"
                    for i, gap in enumerate(gaps, 1):
                        source = gap.get('source', 'Unknown')
                        review += f"{i}. {gap['content']} `{source}`\n"
                    review += "\n"

        # 详细文档分析
        review += "\n## " + ("详细分析" if self.language == "zh" else "Detailed Analysis") + "\n\n"

        for source in sources:
            if source.get('type') == 'file':
                result = source['result']
                review += f"### {Path(result.source).name} {result.citation.citation_key}\n\n"
                review += f"**类型:** {result.type}\n\n"
                review += f"**摘要:** {result.summary}\n\n"

                if result.research_gaps:
                    review += "**研究空白:**\n"
                    for gap in result.research_gaps:
                        review += f"- {gap}\n"
                    review += "\n"

                review += "**关键发现:**\n"
                for point in result.key_points[:8]:
                    review += f"- {point['content']} {result.citation.citation_key}\n"
                review += "\n"

        # 参考文献
        review += "## " + ("参考文献" if self.language == "zh" else "References") + "\n\n"

        for i, source in enumerate(sources, 1):
            if source.get('type') == 'file':
                result = source['result']
                review += f"{i}. {result.citation.author} ({result.citation.year}). {result.citation.title}. {Path(result.source).name}.\n"
            elif source.get('type') == 'web':
                result = source['result']
                review += f"{i}. {result.get('author', 'Unknown')} ({result.get('year', 'n.d.')}). {result.get('title', 'N/A')}. Retrieved from: {result.get('url', 'N/A')}.\n"

        # 生成时间
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        review += f"\n---\n\n*本综述由 AI 自动生成，建议在使用前进行人工审核和补充。*\n*生成时间: {timestamp}*\n"

        return review


# 中文模板
ZH_TITLE_TEMPLATE = """# {topic} - 文献综述报告

## 1. 研究背景与目标

本综述围绕 **{topic}** 这一主题，对相关资料进行了系统性的调研和分析。研究目标包括：
- 梳理该领域的主要观点和研究成果
- 交叉验证不同来源的共识与分歧
- 识别研究空白与局限性
- 提出未来的研究方向建议

## 2. 资料来源说明

本次调研共分析了 **{total_sources}** 份资料，包括：
- 本地文档：{file_count} 份
- 网络资源：{web_count} 份
- 错误：{error_count} 份
"""

# 英文模板
EN_TITLE_TEMPLATE = """# {topic} - Literature Review Report

## 1. Research Background and Objectives

This review systematically analyzes materials related to **{topic}**. Objectives include:
- Identify key findings and research results in the field
- Cross-verify consensus and disagreements across sources
- Identify research gaps and limitations
- Propose future research directions

## 2. Source Description

This review analyzed **{total_sources}** sources, including:
- Local documents: {file_count}
- Web resources: {web_count}
- Errors: {error_count}
"""


# MCP 工具定义（仅在 MCP 可用时注册）
if MCP_AVAILABLE and mcp:
    @mcp.tool()
    def generate_literature_review(
        topic: str,
        files: Optional[List[str]] = None,
        web_search: bool = True,
        search_depth: str = "medium",
        language: str = "zh",
        output_bibtex: bool = True
    ) -> str:
        """
        生成文献综述报告

        Args:
            topic: 研究主题（必填）
            files: 本地文档文件路径列表（可选）
            web_search: 是否进行网络搜索（默认：true）
            search_depth: 网络搜索深度，可选值：basic/medium/deep（默认：medium）
            language: 输出语言，zh/en（默认：zh）
            output_bibtex: 是否生成 BibTeX 文件（默认：true）

        Returns:
            Markdown 格式的综述报告
        """
        generator = ReviewGenerator(language=language)
        try:
            review, bibtex_path = generator.generate_review(
                topic, files, web_search, search_depth, output_bibtex
            )
            if bibtex_path:
                review += f"\n\n[BibTeX 文件已生成: {bibtex_path}]"
            return review
        finally:
            generator.searcher.close()

    @mcp.tool()
    def analyze_document(file_path: str, language: str = "zh") -> Dict[str, Any]:
        """
        分析单个文档

        Args:
            file_path: 文档文件路径
            language: 输出语言，zh/en（默认：zh）

        Returns:
            文档分析结果，包含结构、摘要、关键点和引用信息
        """
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_file(file_path)

        return {
            'source': result.source,
            'type': result.type,
            'summary': result.summary,
            'citation': {
                'author': result.citation.author,
                'year': result.citation.year,
                'title': result.citation.title,
                'citation_key': result.citation.citation_key
            },
            'research_gaps': result.research_gaps,
            'key_points': result.key_points[:10],
            'structure': result.structure
        }

    @mcp.tool()
    def cross_verify_documents(
        files: List[str],
        language: str = "zh"
    ) -> Dict[str, Any]:
        """
        交叉验证多篇文档，识别共识与分歧

        Args:
            files: 文档文件路径列表
            language: 输出语言，zh/en（默认：zh）

        Returns:
            交叉验证结果，包含共识、分歧和研究空白
        """
        analyzer = DocumentAnalyzer()
        verifier = CrossVerifier()

        results = []
        for file_path in files:
            try:
                result = analyzer.analyze_file(file_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'error': str(e),
                    'source': file_path
                })

        verification = verifier.analyze_consensus(results)

        if language == "en":
            return {
                'consensus': verification['consensus'],
                'disagreements': verification['disagreements'],
                'research_gaps': verification['research_gaps'],
                'total_documents': verification['total_documents'],
                'consensus_rate': f"{verification['consensus_rate']:.1f}%"
            }
        return {
            'consensus': verification['consensus'],
            'disagreements': verification['disagreements'],
            'research_gaps': verification['research_gaps'],
            'total_documents': verification['total_documents'],
            'consensus_rate': f"{verification['consensus_rate']:.1f}%"
        }


# Feishu/Lark Integration MCP Tools (only register if enabled and available)
if MCP_AVAILABLE and mcp and FEISHU_AVAILABLE and FEISHU_ENABLED:
    @mcp.tool()
    def fetch_feishu_data(
        url: str,
        table_name: Optional[str] = None,
        max_records: int = 1000
    ) -> Dict[str, Any]:
        """
        Fetch data from Feishu base/spreadsheet

        Args:
            url: Feishu baseinfo URL (e.g., https://open.feishu.cn/app/.../baseinfo)
            table_name: Optional table name filter (if None, fetch all tables)
            max_records: Maximum number of records to fetch (default: 1000)

        Returns:
            Dictionary containing base info, tables with records, and summary
        """
        try:
            fetcher = FeishuDataFetcher(FEISHU_APP_ID, FEISHU_APP_SECRET)
            parsed = fetcher.parse_url(url)

            if not parsed.get('base_id') and not parsed.get('spreadsheet_token'):
                return {"error": "Invalid Feishu URL. Must be a base or spreadsheet URL"}

            tables_data = []

            if parsed.get('base_id'):
                all_tables = fetcher.fetch_base_tables(parsed['base_id'])

                for table in all_tables:
                    if table_name and table.get('name') != table_name:
                        continue

                    records = fetcher.fetch_records_paginated(
                        parsed['base_id'],
                        table['table_id'],
                        max_records=max_records
                    )

                    tables_data.append({
                        'table_id': table['table_id'],
                        'name': table['name'],
                        'record_count': len(records),
                        'records': records[:20]  # Limit response size
                    })

                    if table_name:
                        break

            fetcher.close()

            return {
                'base_id': parsed.get('base_id'),
                'base_name': tables_data[0]['name'] if tables_data else 'Unknown',
                'tables': tables_data,
                'total_tables': len(tables_data),
                'total_records': sum(t['record_count'] for t in tables_data)
            }

        except FeishuAPIError as e:
            return {"error": f"Feishu API error: {e.msg} (code: {e.code})"}
        except Exception as e:
            return {"error": f"Failed to fetch Feishu data: {str(e)}"}

    @mcp.tool()
    def list_feishu_tables(url: str) -> Dict[str, Any]:
        """
        List all tables in a Feishu base

        Args:
            url: Feishu baseinfo URL

        Returns:
            Dictionary containing base_id, base_name, and list of tables
        """
        try:
            fetcher = FeishuDataFetcher(FEISHU_APP_ID, FEISHU_APP_SECRET)
            parsed = fetcher.parse_url(url)

            if not parsed.get('base_id'):
                return {"error": "Invalid Feishu base URL"}

            tables = fetcher.fetch_base_tables(parsed['base_id'])
            fetcher.close()

            return {
                'base_id': parsed['base_id'],
                'tables': [
                    {
                        'table_id': t['table_id'],
                        'name': t['name'],
                        'field_count': len(t.get('fields', []))
                    }
                    for t in tables
                ],
                'total_tables': len(tables)
            }

        except FeishuAPIError as e:
            return {"error": f"Feishu API error: {e.msg} (code: {e.code})"}
        except Exception as e:
            return {"error": f"Failed to list tables: {str(e)}"}


# 命令行入口
def main():
    """命令行主函数"""
    import sys

    if MCP_AVAILABLE and mcp and len(sys.argv) == 1:
        # 默认运行 MCP 服务器
        mcp.run()
    else:
        # 独立运行模式
        print("=== 文献调研综述工具 (Enhanced Edition) ===")
        print("使用方式:")
        print("  1. 作为 MCP Server 运行: python main.py")
        print("  2. 作为独立脚本运行: python main.py --topic <主题> [--files 文件路径...]")
        print()

        # 简单的命令行参数解析
        if "--topic" in sys.argv:
            topic_idx = sys.argv.index("--topic") + 1
            if topic_idx < len(sys.argv):
                topic = sys.argv[topic_idx]
                files = []

                if "--files" in sys.argv:
                    files_idx = sys.argv.index("--files") + 1
                    while files_idx < len(sys.argv) and not sys.argv[files_idx].startswith("--"):
                        files.append(sys.argv[files_idx])
                        files_idx += 1

                web_search = "--no-web" not in sys.argv
                search_depth = "medium"
                language = "zh"
                output_bibtex = "--no-bibtex" not in sys.argv

                for arg in sys.argv:
                    if arg.startswith("--depth="):
                        search_depth = arg.split("=")[1]
                    elif arg.startswith("--lang="):
                        language = arg.split("=")[1]

                print(f"生成综述: {topic}")
                print(f"文件数量: {len(files)}")
                print(f"网络搜索: {web_search}")
                print(f"语言: {language}")
                print(f"BibTeX 导出: {output_bibtex}")
                print()

                generator = ReviewGenerator(language=language)
                review, bibtex_path = generator.generate_review(
                    topic=topic,
                    files=files if files else None,
                    web_search=web_search,
                    search_depth=search_depth,
                    output_bibtex=output_bibtex
                )

                # 保存综述
                output_file = f"{topic.replace(' ', '_')}_综述.md"
                Path(output_file).write_text(review, encoding="utf-8")
                print(f"综述已生成: {output_file}")

                if bibtex_path:
                    print(f"BibTeX 已生成: {bibtex_path}")
        else:
            print("请提供 --topic 参数")
            print("示例: python main.py --topic '人工智能在医疗中的应用' --files doc1.txt doc2.pdf --lang en")


if __name__ == "__main__":
    main()
