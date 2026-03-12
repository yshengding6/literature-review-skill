"""
文献调研综述 Skill 测试文件
"""

import sys
import io
from pathlib import Path

# 设置标准输出为 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import DocumentAnalyzer, WebSearcher, ReviewGenerator


def test_document_analyzer():
    """测试文档分析器"""
    print("测试文档分析器...")
    analyzer = DocumentAnalyzer()

    # 测试关键点提取
    test_text = "这是一个重要的发现。研究显示AI具有巨大潜力。关键在于数据质量。结论是需要加强合作。"
    key_points = analyzer.extract_key_points(test_text)

    assert len(key_points) > 0, "应该提取到关键点"
    assert all('content' in p for p in key_points), "关键点应该包含content字段"

    print(f"[OK] 提取到 {len(key_points)} 个关键点")


def test_structure_extraction():
    """测试结构提取"""
    print("测试结构提取...")
    analyzer = DocumentAnalyzer()

    test_text = """
    # 背景
    这是研究背景内容。

    ## 方法
    这是研究方法描述。

    ## 结论
    这是研究结论。
    """

    structure = analyzer.extract_structure(test_text)

    assert structure['total_words'] > 0, "应该统计字数"
    print(f"[OK] 文档字数: {structure['total_words']}")


def test_file_analysis():
    """测试文件分析"""
    print("测试文件分析...")
    analyzer = DocumentAnalyzer()

    # 使用示例文件
    sample_file = Path(__file__).parent.parent / "examples" / "sample_document.txt"

    if sample_file.exists():
        result = analyzer.analyze_file(str(sample_file))

        assert 'source' in result, "结果应该包含source"
        assert 'key_points' in result, "结果应该包含key_points"
        print(f"[OK] 文件分析完成: {result['source']}")
    else:
        print("[WARN] 示例文件不存在，跳过文件分析测试")


def test_web_searcher():
    """测试网络搜索器"""
    print("测试网络搜索器...")
    searcher = WebSearcher()

    results = searcher.search("人工智能医疗", depth="basic")

    assert len(results) > 0, "应该返回搜索结果"
    print(f"[OK] 搜索返回 {len(results)} 条结果")

    searcher.close()


def test_review_generation():
    """测试综述生成"""
    print("测试综述生成...")
    generator = ReviewGenerator()

    # 使用示例文件
    sample_file1 = Path(__file__).parent.parent / "examples" / "sample_document.txt"
    sample_file2 = Path(__file__).parent.parent / "examples" / "sample_document2.txt"

    files = []
    if sample_file1.exists():
        files.append(str(sample_file1))
    if sample_file2.exists():
        files.append(str(sample_file2))

    review = generator.generate_review(
        topic="人工智能医疗",
        files=files if files else None,
        web_search=False
    )

    assert len(review) > 0, "应该生成综述内容"
    assert "人工智能医疗" in review, "综述应该包含主题"
    print(f"[OK] 生成综述成功，长度: {len(review)} 字符")

    # 保存生成的综述
    output_file = Path(__file__).parent / "generated_review.md"
    output_file.write_text(review, encoding="utf-8")
    print(f"[OK] 综述已保存到: {output_file}")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始运行测试...")
    print("=" * 50)

    try:
        test_document_analyzer()
        test_structure_extraction()
        test_file_analysis()
        test_web_searcher()
        test_review_generation()

        print("=" * 50)
        print("[OK] 所有测试通过！")
        print("=" * 50)
    except AssertionError as e:
        print(f"[FAIL] 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(run_all_tests())
