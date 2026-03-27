"""
文献调研综述 Skill (Socratic Roundtable Edition v3.0.0)
支持本地文档分析和网络搜索，生成综合性综述报告

v3.0.0 新增功能：
- 四把手术刀方法论（政治史探针、六维解剖、异常检测、变量替换）
- 苏格拉底圆桌会议系统（冲突点将 + 逻辑清洗）
- 交互式检查点机制
- 证据分级协议（[实证]/[推论]/[缺失]）
- 老丁因子（非共识观察点、冷知识命题）
- 多格式输出（md/pdf/docx）

v2.2.1 功能：
- MCP 输入验证
- 增强引用提取（支持中文格式）
- Feishu 重试机制（指数退避）

v2.1.0 功能：
- 交叉验证：识别共识与分歧
- 研究空白：自动检测研究空白
- 引用溯源：严格的引用格式
- PDF 解析：支持学术论文 PDF
- BibTeX 导出：生成 Zotero/LaTeX 兼容的参考文献
- Windows 兼容：完全支持 Windows 路径和编码

v2.0.0 功能：
- 飞书数据集成：从飞书多维表格/电子表格获取数据
- 基础文献分析功能
- 模拟网络搜索实现
- Markdown 综述报告生成
- 文件编码自动检测（UTF-8、GBK、Latin-1）

可以作为独立脚本运行，也可以作为 MCP Server 运行
"""

import re
import json
import logging
from typing import Optional, List, Dict, Any, Set, Tuple
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('literature_review.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        # 改进的引用提取模式，支持更多格式
        self.citation_patterns = [
            # 标准学术格式：Author, Year
            r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,\s*\d{4})',  # Smith, 2023
            r'\((\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,\s*\d{4})\)',  # (Smith, 2023)
            # et al. 格式：Author et al., Year
            r'(\b[A-Z][a-z]+\s+et\s+al\.?\s*,\s*\d{4})',  # et al., 2023
            # 带页码格式：Author, Year, p. N
            r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,\s*\d{4}\s*,\s*p\.\s*\d+\s*)',  # Smith, 2023, p. 25
            # 中文格式：作者[年份]
            r'([\u4e00-\u9fa5]+)\[(\d{4})\]',  # 张[2023]
            r'([\u4e00-\u9fa5]+)\[(\d{4})\s*,\s*p\.\s*\d+\s*)\]',  # 张[2023], p. 25
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

        # 尝试中文引用格式：作者[年份]
        chinese_citation_pattern = r'([\u4e00-\u9fa5]+)\[(\d{4})\]'
        chinese_matches = re.findall(chinese_citation_pattern, text)
        if chinese_matches:
            # 使用中文引用格式
            match = chinese_matches[0]
            if isinstance(match, tuple):
                match = match[0]
            citation.author = match.group(1)
            citation.year = match.group(2)
            # 中文引用优先于英文引用
            logger.debug(f"检测到中文引用: {citation.author}[{citation.year}]")

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
        logger.info(f"开始分析文件: {file_path}")
        path = Path(file_path)
        content = self.extract_text_from_file(path)

        # 提取引用信息
        citation = self.extract_citations(content, path.name)
        logger.info(f"引用信息: 作者={citation.author}, 年份={citation.year}")

        # 提取关键点并标记来源
        key_points = self.extract_key_points(content)
        for point in key_points:
            point['source'] = citation.citation_key

        # 提取结构
        structure = self.extract_structure(content)

        # 检测研究空白
        research_gaps = self.detect_research_gaps(content, key_points)
        logger.info(f"检测到研究空白数量: {len(research_gaps)}")

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
    """交叉验证器 - 识别共识与分歧"""

    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold

    def compute_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        # 简单的词重叠相似度
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0

    def analyze_consensus(
        self,
        results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """分析多篇文献的共识与分歧"""
        # 收集所有关键点
        all_points = []
        for result in results:
            for point in result.key_points:
                all_points.append({
                    'content': point['content'],
                    'source': result.citation.citation_key,
                    'score': point.get('score', 0)
                })

        # 按分数排序
        all_points.sort(key=lambda x: x['score'], reverse=True)

        # 识别共识（相似度高）
        consensus = []
        processed_indices = set()

        for i, point1 in enumerate(all_points[:30]):
            if i in processed_indices:
                continue

            agreement_points = [point1]
            for j, point2 in enumerate(all_points[i+1:50], i+1):
                if j in processed_indices:
                    continue

                similarity = self.compute_similarity(point1['content'], point2['content'])
                if similarity >= self.similarity_threshold:
                    agreement_points.append(point2)
                    processed_indices.add(j)

            if len(agreement_points) >= 2:
                processed_indices.add(i)
                consensus.append({
                    'content': point1['content'],
                    'sources': [p['source'] for p in agreement_points],
                    'count': len(agreement_points)
                })

        # 识别分歧（观点冲突）
        disagreements = []
        # 检测对立观点
        opposition_pairs = [
            ('支持', '反对', 'support', 'oppose', 'agree', 'disagree'),
            ('有效', '无效', 'effective', 'ineffective'),
            ('提高', '降低', 'increase', 'decrease', 'improve', 'worsen'),
            ('积极', '消极', 'positive', 'negative')
        ]

        for point1 in all_points[:20]:
            if any(opp in point1['content'].lower() for opp in sum(opposition_pairs, ())):
                # 查找对立观点
                for point2 in all_points:
                    content1 = point1['content'].lower()
                    content2 = point2['content'].lower()

                    for pair in opposition_pairs:
                        if (pair[0] in content1 and pair[1] in content2) or \
                           (pair[2] in content1 and pair[3] in content2):
                            disagreements.append({
                                'view1': point1['content'],
                                'view2': point2['content'],
                                'source1': point1['source'],
                                'source2': point2['source']
                            })
                            break

        # 提取研究空白汇总
        all_gaps = []
        for result in results:
            all_gaps.extend(result.research_gaps)

        # 去重研究空白
        seen_gaps = set()
        unique_gaps = []
        for gap in all_gaps:
            normalized = re.sub(r'[^\w\u4e00-\u9fff]', '', gap).lower()
            if normalized and normalized not in seen_gaps:
                seen_gaps.add(normalized)
                unique_gaps.append(gap)

        return {
            'consensus': consensus[:5],
            'disagreements': disagreements[:3],
            'research_gaps': unique_gaps[:5],
            'total_documents': len(results),
            'consensus_rate': len(consensus) / len(all_points) * 100 if all_points else 0
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
        logger.info(f"生成综述报告: 主题='{topic}'")
        review = self._format_review(topic, all_sources, verification)

        # 生成 BibTeX
        bibtex = None
        if output_bibtex and analysis_results:
            bibtex_path = f"{topic.replace(' ', '_')}_references.bib"
            logger.info(f"生成 BibTeX 文件: {bibtex_path}")
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

            # 共识
            if verification['consensus']:
                review += "### " + ("共识观点" if self.language == "zh" else "Consensus Views") + "\n\n"
                for i, consensus in enumerate(verification['consensus'], 1):
                    sources_str = ", ".join(consensus['sources'])
                    review += f"{i}. **{consensus['content']}**\n   - 来源: {sources_str} (共 {consensus['count']} 篇)\n\n"

            # 分歧
            if verification['disagreements']:
                review += "### " + ("观点分歧" if self.language == "zh" else "Conflicting Views") + "\n\n"
                for i, disagreement in enumerate(verification['disagreements'], 1):
                    review += f"{i}. **分歧 {i}:**\n"
                    review += f"   - 观点 A ({disagreement['source1']}): {disagreement['view1']}\n"
                    review += f"   - 观点 B ({disagreement['source2']}): {disagreement['view2']}\n\n"

            # 研究空白
            if verification['research_gaps']:
                review += "### " + ("研究空白" if self.language == "zh" else "Research Gaps") + "\n\n"
                for i, gap in enumerate(verification['research_gaps'], 1):
                    review += f"{i}. {gap}\n"
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
        # 输入验证
        if not topic or not topic.strip():
            raise ValueError("研究主题不能为空")
        if search_depth not in ["basic", "medium", "deep"]:
            raise ValueError(f"search_depth 必须是 'basic'、'medium' 或 'deep'，当前值为: {search_depth}")
        if language not in ["zh", "en"]:
            raise ValueError(f"language 必须是 'zh' 或 'en'，当前值为: {language}")
        if files:
            valid_extensions = {".txt", ".md", ".pdf", ".py", ".js", ".json", ".csv"}
            for file_path in files:
                path = Path(file_path)
                if not path.exists():
                    logger.warning(f"文件不存在: {file_path}")
                    continue
                if path.suffix.lower() not in valid_extensions:
                    logger.warning(f"不支持的文件类型: {file_path}")
                    continue
        logger.info(f"输入验证通过: 主题='{topic}', 文件数={len(files) if files else 0}, 语言={language}, 搜索深度={search_depth}")

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
                simple_read = "--simple-read" in sys.argv  # 简单读取模式

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
                print(f"简单读取模式: {simple_read}")
                print()

                # 简单读取模式：只读取文件内容，不进行完整分析
                if simple_read:
                    print("简单读取模式：仅读取文件内容...")
                    for file_path in files:
                        try:
                            analyzer = DocumentAnalyzer()
                            result = analyzer.analyze_file(file_path)
                            print(f"\n=== {Path(file_path).name} ===")
                            print(f"类型: {result.type}")
                            print(f"摘要: {result.summary}")
                            print(f"作者: {result.citation.author}")
                            print(f"年份: {result.citation.year}")
                            print(f"关键点数量: {len(result.key_points)}")
                            for i, point in enumerate(result.key_points[:5], 1):
                                print(f"  {i+1}. {point['content']}")
                        except Exception as e:
                            print(f"错误: {e}")
                    print("\n简单读取完成。")
                    return

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
