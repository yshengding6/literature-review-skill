"""
文献调研综述 Skill
支持本地文档分析和网络搜索，生成综合性综述报告

可以作为独立脚本运行，也可以作为 MCP Server 运行
"""

import re
from typing import Optional, List, Dict, Any
from pathlib import Path
from collections import defaultdict

# 尝试导入 MCP 相关依赖（可选）
try:
    from fastmcp import FastMCP
    import httpx
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    httpx = None

# 如果 MCP 可用，初始化 MCP 服务器
if MCP_AVAILABLE:
    mcp = FastMCP("literature-review")
else:
    mcp = None


class DocumentAnalyzer:
    """文档分析器"""

    def __init__(self):
        self.sections = defaultdict(list)

    def extract_key_points(self, text: str, max_points: int = 10) -> List[Dict[str, str]]:
        """提取关键点"""
        # 按句子分割
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s) > 10]

        # 简单的关键词提取和重要性评分
        key_words = [
            '重要', '关键', '核心', '主要', '结论', '发现', '研究', '表明', '显示',
            '结果', '方法', '目的', '背景', '意义', '影响', '优势', '缺点', '问题',
            'solution', 'result', 'conclusion', 'finding', 'key', 'major', 'important'
        ]

        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = sum(1 for word in key_words if word.lower() in sentence.lower())
            if score > 0:
                scored_sentences.append({
                    'content': sentence,
                    'score': score,
                    'position': i
                })

        # 按分数排序并取前 N 个
        scored_sentences.sort(key=lambda x: (-x['score'], x['position']))
        return scored_sentences[:max_points]

    def extract_structure(self, text: str) -> Dict[str, Any]:
        """提取文档结构"""
        structure = {
            'background': '',
            'methodology': '',
            'key_findings': [],
            'conclusion': '',
            'total_words': len(text)
        }

        # 简单的章节识别
        if '背景' in text or 'background' in text.lower():
            structure['background'] = '包含背景说明'
        if '方法' in text or 'method' in text.lower():
            structure['methodology'] = '包含方法论'
        if '结论' in text or 'conclusion' in text.lower():
            structure['conclusion'] = '包含结论'

        structure['key_findings'] = self.extract_key_points(text)

        return structure

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 读取文件内容
        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = path.read_text(encoding='gbk')

        return {
            'source': str(path),
            'type': path.suffix,
            'structure': self.extract_structure(content),
            'summary': self._generate_summary(content),
            'key_points': self.extract_key_points(content)
        }

    def _generate_summary(self, text: str) -> str:
        """生成摘要"""
        # 取前 200 个字符作为简单摘要
        return text[:500] + ('...' if len(text) > 500 else '')


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
                'source': '网络搜索'
            })

        return results

    def close(self):
        """关闭客户端"""
        if self.client:
            self.client.close()


class ReviewGenerator:
    """综述生成器"""

    def __init__(self):
        self.analyzer = DocumentAnalyzer()
        self.searcher = WebSearcher()

    def generate_review(
        self,
        topic: str,
        files: Optional[List[str]] = None,
        web_search: bool = True,
        search_depth: str = 'medium'
    ) -> str:
        """生成综合综述"""

        # 收集所有资料
        all_sources = []

        # 分析本地文件
        if files:
            for file_path in files:
                try:
                    analysis = self.analyzer.analyze_file(file_path)
                    all_sources.append(analysis)
                except Exception as e:
                    all_sources.append({
                        'source': file_path,
                        'error': str(e)
                    })

        # 网络搜索
        if web_search:
            try:
                web_results = self.searcher.search(topic, search_depth)
                all_sources.extend(web_results)
            except Exception as e:
                all_sources.append({
                    'source': '网络搜索',
                    'error': str(e)
                })

        # 生成综述
        return self._format_review(topic, all_sources)

    def _format_review(self, topic: str, sources: List[Dict[str, Any]]) -> str:
        """格式化综述报告"""

        review = f"""# {topic} - 文献综述报告

## 1. 研究背景与目标

本综述围绕 **{topic}** 这一主题，对相关资料进行了系统性的调研和分析。研究目标包括：
- 梳理该领域的主要观点和研究成果
- 对比不同来源的资料，分析其异同
- 总结现有研究的发现和局限
- 提出未来的研究方向建议

## 2. 资料来源说明

本次调研共分析了 **{len(sources)}** 份资料，来源包括：

"""

        # 按来源类型统计
        file_count = sum(1 for s in sources if 'structure' in s)
        web_count = sum(1 for s in sources if 'source' in s and 'url' in s)

        review += f"""- 本地文档：{file_count} 份
- 网络资源：{web_count} 份

### 2.1 资料列表

"""

        for i, source in enumerate(sources, 1):
            if 'error' in source:
                review += f"{i}. ❌ {source['source']} - 处理失败: {source['error']}\n"
            elif 'structure' in source:
                review += f"{i}. 📄 [{Path(source['source']).name}]({source['source']}) - 本地文件\n"
            else:
                review += f"{i}. 🌐 [{source['title']}]({source['url']}) - {source.get('source', '网络')}\n"

        # 核心观点摘要
        review += """

## 3. 核心观点摘要

基于对上述资料的分析，该主题的主要观点如下：

"""

        # 提取所有关键点
        all_key_points = []
        for source in sources:
            if 'key_points' in source:
                all_key_points.extend(source['key_points'])
            elif 'snippet' in source:
                all_key_points.append({'content': source['snippet'], 'score': 1})

        # 按分数排序
        all_key_points.sort(key=lambda x: x.get('score', 0), reverse=True)
        unique_points = []
        seen = set()
        for point in all_key_points[:15]:
            content = point['content'][:100]
            if content not in seen:
                seen.add(content)
                unique_points.append(point['content'])

        for i, point in enumerate(unique_points, 1):
            review += f"{i}. {point}\n"

        # 详细分析
        review += """

## 4. 详细分析

### 4.1 本地文档分析

"""

        for source in sources:
            if 'structure' in source:
                review += f"""#### {Path(source['source']).name}

**文档类型：** {source['type']}

**内容摘要：**
{source['summary']}

**关键发现：**
"""
                for i, point in enumerate(source['key_points'][:5], 1):
                    review += f"- {point['content']}\n"
                review += "\n"

        # 网络资源分析
        review += """### 4.2 网络资源分析

"""

        for source in sources:
            if 'url' in source and 'error' not in source:
                review += f"""#### [{source['title']}]({source['url']})

**内容概要：**
{source['snippet']}

"""

        # 对比分析
        review += """## 5. 横向对比分析

### 5.1 观点一致性

通过对比不同资料，可以发现：

- **共同观点：** 大部分资料都支持该主题的基本概念和核心原理
- **关注重点：** 不同来源在细节层面有所侧重

### 5.2 资料质量评估

| 资料类型 | 数量 | 质量评级 | 主要优势 |
|---------|------|----------|----------|
| 本地文档 | {} | ⭐⭐⭐⭐ | 内容详实，可深度分析 |
| 网络资源 | {} | ⭐⭐⭐ | 信息更新快，覆盖面广 |

### 5.3 研究空白与局限

综合分析发现：
- 现有资料在理论层面较为完善
- 实践应用案例相对较少
- 部分细分领域研究不足

## 6. 结论与建议

### 6.1 主要结论

1. **{}** 是当前研究的热点领域
2. 相关理论体系相对成熟
3. 应用场景正在不断扩展

### 6.2 研究建议

1. **深化理论研究：** 进一步完善理论框架
2. **加强实践验证：** 收集更多实际应用案例
3. **拓展研究边界：** 探索与其他领域的结合点
4. **关注新兴趋势：** 跟踪最新技术发展

## 7. 参考资料列表

""".format(file_count, web_count, topic)

        # 参考资料列表
        for i, source in enumerate(sources, 1):
            if 'error' not in source:
                if 'url' in source:
                    review += f"{i}. [{source['title']}]({source['url']})\n"
                else:
                    review += f"{i}. {source['source']}\n"

        review += """
---

*本综述由 AI 自动生成，建议在使用前进行人工审核和补充。*
*生成时间：{timestamp}*
""".format(timestamp=str(__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return review


# MCP 工具定义（仅在 MCP 可用时注册）
if MCP_AVAILABLE and mcp:
    @mcp.tool()
    def generate_literature_review(
        topic: str,
        files: Optional[List[str]] = None,
        web_search: bool = True,
        search_depth: str = "medium"
    ) -> str:
        """
        生成文献综述报告

        Args:
            topic: 研究主题（必填）
            files: 本地文档文件路径列表（可选）
            web_search: 是否进行网络搜索（默认：true）
            search_depth: 网络搜索深度，可选值：basic/medium/deep（默认：medium）

        Returns:
            Markdown 格式的综述报告
        """
        generator = ReviewGenerator()
        try:
            review = generator.generate_review(topic, files, web_search, search_depth)
            return review
        finally:
            generator.searcher.close()


    @mcp.tool()
    def analyze_document(file_path: str) -> Dict[str, Any]:
        """
        分析单个文档

        Args:
            file_path: 文档文件路径

        Returns:
            文档分析结果，包含结构、摘要和关键点
        """
        analyzer = DocumentAnalyzer()
        return analyzer.analyze_file(file_path)


    @mcp.tool()
    def search_resources(topic: str, depth: str = "medium") -> List[Dict[str, str]]:
        """
        搜索网络资源

        Args:
            topic: 搜索主题
            depth: 搜索深度，可选值：basic/medium/deep

        Returns:
            搜索结果列表
        """
        searcher = WebSearcher()
        try:
            return searcher.search(topic, depth)
        finally:
            searcher.close()


# 命令行入口
def main():
    """命令行主函数"""
    import sys

    if MCP_AVAILABLE and mcp and len(sys.argv) == 1:
        # 默认运行 MCP 服务器
        mcp.run()
    else:
        # 独立运行模式
        print("=== 文献调研综述工具 ===")
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

                for arg in sys.argv:
                    if arg.startswith("--depth="):
                        search_depth = arg.split("=")[1]

                print(f"生成综述: {topic}")
                print(f"文件数量: {len(files)}")
                print(f"网络搜索: {web_search}")
                print()

                generator = ReviewGenerator()
                review = generator.generate_review(
                    topic=topic,
                    files=files if files else None,
                    web_search=web_search,
                    search_depth=search_depth
                )

                # 保存到文件
                output_file = f"{topic.replace(' ', '_')}_综述.md"
                Path(output_file).write_text(review, encoding="utf-8")
                print(f"综述已生成: {output_file}")
        else:
            print("请提供 --topic 参数")
            print("示例: python main.py --topic '人工智能在医疗中的应用' --files doc1.txt doc2.txt")


if __name__ == "__main__":
    main()
