"""
Enhanced Literature Review Skill Tests

Tests for:
- Document analysis (TXT, PDF)
- PDF text extraction
- Citation extraction
- Research gap detection
- Cross-verification
- BibTeX generation
- Error handling for empty/non-existent files
- Windows compatibility (encoding, paths)
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import (
    DocumentAnalyzer,
    CrossVerifier,
    BibTeXGenerator,
    AnalysisResult,
    Citation,
    compute_content_hash
)


def test_basic_document_analysis():
    """Test basic document analysis functionality"""
    print("[TEST] Basic Document Analysis")
    analyzer = DocumentAnalyzer()

    # Test key points extraction
    test_text = "这是一个重要的发现。研究显示AI具有巨大潜力。关键在于数据质量。结论是需要加强合作。"
    key_points = analyzer.extract_key_points(test_text)

    assert len(key_points) > 0, "Should extract key points"
    assert all('content' in p for p in key_points), "Key points should have content"
    print(f"[OK] Extracted {len(key_points)} key points")

    # Test structure extraction
    structure = analyzer.extract_structure(test_text)
    assert 'total_words' in structure, "Structure should have total_words"
    assert structure['total_words'] > 0, "Should count words"
    print(f"[OK] Structure: {len(test_text)} characters")

    # Test summary generation
    summary = analyzer._generate_summary(test_text)
    assert len(summary) > 0, "Should generate summary"
    print(f"[OK] Summary: {len(summary)} characters")


def test_citation_extraction():
    """Test citation extraction from text"""
    print("\n[TEST] Citation Extraction")
    analyzer = DocumentAnalyzer()

    # Test with embedded citation
    text_with_citation = """
    Smith, John (2024). This is a research paper about AI.
    The findings show significant improvements in accuracy.
    """
    citation = analyzer.extract_citations(text_with_citation, "test.pdf")

    assert citation.source == "test.pdf", "Citation should have correct source"
    print(f"[OK] Citation author: {citation.author}")
    print(f"[OK] Citation year: {citation.year}")
    print(f"[OK] Citation key: {citation.citation_key}")


def test_research_gap_detection():
    """Test research gap detection"""
    print("\n[TEST] Research Gap Detection")
    analyzer = DocumentAnalyzer()

    # Text with research gaps
    gap_text = """
    This study has several limitations.
    Further research is needed to validate these findings.
    However, there is a lack of data in certain areas.
    Future work should address the open problems.
    """

    key_points = analyzer.extract_key_points(gap_text)
    gaps = analyzer.detect_research_gaps(gap_text, key_points)

    assert len(gaps) > 0, "Should detect research gaps"
    print(f"[OK] Detected {len(gaps)} research gaps")
    for gap in gaps:
        print(f"     - {gap[:50]}...")


def test_cross_verification_consensus():
    """Test cross-verification consensus detection"""
    print("\n[TEST] Cross-Verification (Consensus)")
    verifier = CrossVerifier()

    # Create mock results with similar content
    result1 = AnalysisResult(
        source="doc1.txt",
        type=".txt",
        structure={'total_words': 100},
        summary="Test",
        key_points=[
            {'content': 'AI shows significant potential in healthcare.', 'score': 2, 'source': '[Smith, 2024]'}
        ],
        citation=Citation(source="doc1.txt", author="Smith", year="2024"),
        research_gaps=[],
        content_hash="abc"
    )

    result2 = AnalysisResult(
        source="doc2.txt",
        type=".txt",
        structure={'total_words': 100},
        summary="Test",
        key_points=[
            {'content': 'AI demonstrates great potential for medical applications.', 'score': 2, 'source': '[Jones, 2024]'}
        ],
        citation=Citation(source="doc2.txt", author="Jones", year="2024"),
        research_gaps=[],
        content_hash="def"
    )

    verification = verifier.analyze_consensus([result1, result2])

    assert 'consensus' in verification, "Should have consensus field"
    print(f"[OK] Consensus rate: {verification['consensus_rate']:.1f}%")
    print(f"[OK] Found {len(verification['consensus'])} consensus points")


def test_cross_verification_disagreement():
    """Test cross-verification disagreement detection"""
    print("\n[TEST] Cross-Verification (Disagreement)")
    verifier = CrossVerifier()

    # Create mock results with conflicting views
    result1 = AnalysisResult(
        source="doc1.txt",
        type=".txt",
        structure={'total_words': 100},
        summary="Test",
        key_points=[
            {'content': 'The approach is highly effective for improving accuracy.', 'score': 2, 'source': '[Smith, 2024]'}
        ],
        citation=Citation(source="doc1.txt", author="Smith", year="2024"),
        research_gaps=[],
        content_hash="abc"
    )

    result2 = AnalysisResult(
        source="doc2.txt",
        type=".txt",
        structure={'total_words': 100},
        summary="Test",
        key_points=[
            {'content': 'The method is ineffective and reduces performance.', 'score': 2, 'source': '[Jones, 2024]'}
        ],
        citation=Citation(source="doc2.txt", author="Jones", year="2024"),
        research_gaps=[],
        content_hash="def"
    )

    verification = verifier.analyze_consensus([result1, result2])

    assert 'disagreements' in verification, "Should have disagreements field"
    print(f"[OK] Found {len(verification['disagreements'])} disagreements")
    if verification['disagreements']:
        print(f"     - {verification['disagreements'][0]['view1'][:50]}...")
        print(f"     - {verification['disagreements'][0]['view2'][:50]}...")


def test_bibtex_generation():
    """Test BibTeX generation"""
    print("\n[TEST] BibTeX Generation")

    results = [
        AnalysisResult(
            source="doc1.pdf",
            type=".pdf",
            structure={'total_words': 100},
            summary="Test summary",
            key_points=[],
            citation=Citation(source="doc1.pdf", author="Smith, John", year="2024", title="AI in Healthcare"),
            research_gaps=[],
            content_hash="abc"
        ),
        AnalysisResult(
            source="doc2.txt",
            type=".txt",
            structure={'total_words': 100},
            summary="Test summary",
            key_points=[],
            citation=Citation(source="doc2.txt", author="Jones, Mary", year="2023", title="ML Applications"),
            research_gaps=[],
            content_hash="def"
        )
    ]

    bibtex = BibTeXGenerator.generate_from_results(results)

    assert '@misc{ref1' in bibtex, "Should contain first reference"
    assert '@misc{ref2' in bibtex, "Should contain second reference"
    assert 'author' in bibtex, "Should have author field"
    assert 'year' in bibtex, "Should have year field"
    print(f"[OK] Generated BibTeX with {len(results)} entries")


def test_content_hash():
    """Test content hash computation"""
    print("\n[TEST] Content Hash Computation")

    text1 = "This is test content."
    text2 = "This is test content."
    text3 = "Different content."

    hash1 = compute_content_hash(text1)
    hash2 = compute_content_hash(text2)
    hash3 = compute_content_hash(text3)

    assert hash1 == hash2, "Same content should have same hash"
    assert hash1 != hash3, "Different content should have different hash"
    print(f"[OK] Hash function working correctly")


def test_empty_directory_handling():
    """Test handling of non-existent and empty files"""
    print("\n[TEST] Error Handling")

    analyzer = DocumentAnalyzer()

    # Test non-existent file
    try:
        analyzer.analyze_file("non_existent_file.txt")
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError:
        print("[OK] Correctly raised FileNotFoundError for non-existent file")

    # Test empty text
    empty_text = ""
    key_points = analyzer.extract_key_points(empty_text)
    assert len(key_points) == 0, "Should return empty list for empty text"
    print("[OK] Handled empty text correctly")


def test_file_analysis_with_encoding():
    """Test file analysis with different encodings"""
    print("\n[TEST] File Encoding Handling")

    analyzer = DocumentAnalyzer()

    # Create test file with UTF-8 content
    test_file = Path(__file__).parent / "test_encoding.txt"

    try:
        # Test UTF-8 encoding
        test_file.write_text("测试内容Test Content", encoding='utf-8')
        result = analyzer.analyze_file(str(test_file))
        assert '测试内容' in result.summary or 'Test Content' in result.summary, "Should read UTF-8 file"
        print("[OK] UTF-8 encoding handled correctly")

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_citation_key_format():
    """Test citation key format generation"""
    print("\n[TEST] Citation Key Format")

    # Test with year
    citation1 = Citation(source="test.pdf", author="Smith", year="2024", page="15")
    expected1 = "[Smith, 2024, 15]"
    assert citation1.citation_key == expected1, f"Expected {expected1}, got {citation1.citation_key}"
    print(f"[OK] Citation with year and page: {citation1.citation_key}")

    # Test without year
    citation2 = Citation(source="test.pdf", author="Unknown", year="", page="")
    expected2 = "[Unknown]"
    assert citation2.citation_key == expected2, f"Expected {expected2}, got {citation2.citation_key}"
    print(f"[OK] Citation without year: {citation2.citation_key}")


def test_similarity_computation():
    """Test text similarity computation"""
    print("\n[TEST] Similarity Computation")
    verifier = CrossVerifier()

    # Test identical texts
    text1 = "AI shows great potential in healthcare applications."
    text2 = "AI shows great potential in healthcare applications."

    similarity = verifier.compute_similarity(text1, text2)
    assert similarity > 0.5, "Similar texts should have high similarity"
    print(f"[OK] Similar texts similarity: {similarity:.2f}")

    # Test different texts
    text3 = "Machine learning is widely used in finance."
    similarity2 = verifier.compute_similarity(text1, text3)
    assert similarity2 < 0.5, "Different texts should have low similarity"
    print(f"[OK] Different texts similarity: {similarity2:.2f}")


def test_pdf_extraction():
    """Test PDF text extraction (if pypdf is available)"""
    print("\n[TEST] PDF Extraction")

    try:
        from main import PDF_AVAILABLE

        if not PDF_AVAILABLE:
            print("[SKIP] pypdf not available - install with: pip install pypdf")
            return

        # Check if PDF analyzer has the method
        analyzer = DocumentAnalyzer()
        assert hasattr(analyzer, '_extract_pdf_text'), "Should have PDF extraction method"
        print("[OK] PDF extraction method available")

        # Note: Actual PDF file testing would require a test PDF
        # This verifies the method exists and structure is correct

    except ImportError as e:
        print(f"[SKIP] Cannot import PDF_AVAILABLE: {e}")


def test_integration_full_workflow():
    """Test full workflow from file analysis to review generation"""
    print("\n[TEST] Full Workflow Integration")

    from main import ReviewGenerator

    # Create temporary test files
    test_dir = Path(__file__).parent / "temp_test"
    test_dir.mkdir(exist_ok=True)

    try:
        # Create test files
        file1 = test_dir / "test1.txt"
        file2 = test_dir / "test2.txt"

        file1.write_text("""
        Research on AI in Healthcare
        Background: AI technology is transforming healthcare.
        Key findings: AI improves diagnostic accuracy significantly.
        Conclusion: Further research is needed in clinical validation.
        """, encoding='utf-8')

        file2.write_text("""
        Machine Learning in Medical Applications
        Background: ML algorithms help analyze medical data.
        Key findings: Deep learning models achieve 95% accuracy.
        Limitation: Data privacy concerns remain unresolved.
        """, encoding='utf-8')

        # Run full workflow
        generator = ReviewGenerator(language="zh")
        review, bibtex_path = generator.generate_review(
            topic="AI Healthcare Research",
            files=[str(file1), str(file2)],
            web_search=False,
            output_bibtex=True
        )

        assert len(review) > 0, "Should generate review"
        assert "AI Healthcare Research" in review, "Review should contain topic"
        assert "交叉验证" in review or "Cross-Verification" in review, "Review should contain cross-verification"
        print(f"[OK] Generated review: {len(review)} characters")

        if bibtex_path:
            assert Path(bibtex_path).exists(), "BibTeX file should be created"
            print(f"[OK] BibTeX file created: {bibtex_path}")

    finally:
        # Cleanup
        if test_dir.exists():
            for f in test_dir.glob("*"):
                f.unlink()
            test_dir.rmdir()


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("LITERATURE REVIEW SKILL - ENHANCED TESTS")
    print("=" * 60)

    tests = [
        test_basic_document_analysis,
        test_citation_extraction,
        test_research_gap_detection,
        test_cross_verification_consensus,
        test_cross_verification_disagreement,
        test_bibtex_generation,
        test_content_hash,
        test_empty_directory_handling,
        test_file_analysis_with_encoding,
        test_citation_key_format,
        test_similarity_computation,
        test_pdf_extraction,
        test_integration_full_workflow,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append(f"{test_func.__name__}: {e}")
        except Exception as e:
            failed += 1
            errors.append(f"{test_func.__name__}: Unexpected error - {e}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if errors:
        print("\n[FAILED] Errors:")
        for error in errors:
            print(f"  - {error}")

    print(f"\nSuccess Rate: {passed / len(tests) * 100:.1f}%")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(run_all_tests())
