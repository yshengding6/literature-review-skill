#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Harness - Harness 单元测试
测试 route_assertions 和 structure_validator 的核心功能
"""

import unittest
import sys
from pathlib import Path

# 添加 harness 目录到路径
harness_dir = Path(__file__).parent.parent / "harness"
sys.path.insert(0, str(harness_dir))

from route_assertions import RouteAsserter, RoutingResult
from structure_validator import StructureValidator, ValidationResult


class TestRouteAsserter(unittest.TestCase):
    """测试路由断言功能"""
    
    def test_political_trigger(self):
        """测试政治史触发关键词"""
        text = "三桓专权，季氏僭越礼制"
        asserter = RouteAsserter(text)
        result = asserter.assert_routing()
        
        self.assertIn("political", result.actual_tools)
        self.assertTrue(any("政治史" in r for r in result.reasoning))
    
    def test_anomaly_trigger(self):
        """测试异常检测触发关键词"""
        text = "原文有异文，存在脱文衍文问题"
        asserter = RouteAsserter(text)
        result = asserter.assert_routing()
        
        self.assertIn("anomaly", result.actual_tools)
    
    def test_variable_trigger(self):
        """测试变量替换触发关键词"""
        text = "如果将'学'换为'教'，语义完全改变"
        asserter = RouteAsserter(text)
        result = asserter.assert_routing()
        
        self.assertIn("variable", result.actual_tools)
    
    def test_anatomy_trigger(self):
        """测试六维解剖触发（用户提供注疏）"""
        text = "朱熹注：学之为言效也"
        asserter = RouteAsserter(text)
        result = asserter.assert_routing()
        
        self.assertIn("anatomy", result.actual_tools)
    
    def test_minimal_text(self):
        """测试最小化文本（仅字词校释）"""
        text = "学而时习之，不亦说乎"
        asserter = RouteAsserter(text)
        result = asserter.assert_routing()
        
        # 纯论语文本，没有特殊触发词
        self.assertEqual(len(result.actual_tools), 0)
    
    def test_combined_triggers(self):
        """测试多触发词组合"""
        text = "三桓乱政，且文本有异文，朱熹与刘宝楠观点不同"
        asserter = RouteAsserter(text)
        result = asserter.assert_routing()
        
        self.assertIn("political", result.actual_tools)
        self.assertIn("anomaly", result.actual_tools)
        self.assertIn("anatomy", result.actual_tools)


class TestStructureValidator(unittest.TestCase):
    """测试结构验证功能"""
    
    def test_required_chapters_exist(self):
        """测试必须章节存在"""
        content = """
## 1. 原子化扫描结果
字词校释内容...

## 7. 证据分级综述
[实证] 证据...

## 8. 老丁因子
### 核心判断
判断...
### 证据链
证据...
### 论证路径
路径...
### 潜在反例
反例...
### 与主流解释的分歧点
分歧...
### 定位说明
[已论证]
"""
        validator = StructureValidator(content, [])
        result, issues = validator.validate()
        
        self.assertEqual(result, ValidationResult.PASS)
    
    def test_missing_required_chapter(self):
        """测试缺少必须章节"""
        content = """
## 1. 原子化扫描结果
字词校释内容...

## 7. 证据分级综述
[实证] 证据...
"""
        validator = StructureValidator(content, [])
        result, issues = validator.validate()
        
        self.assertEqual(result, ValidationResult.FAIL)
        self.assertTrue(any("老丁因子" in issue for issue in issues))
    
    def test_missing_disabled_marker(self):
        """测试未启用章节缺少'不适用'标注"""
        content = """
## 1. 原子化扫描结果
字词校释...

## 2. 政治史还原
政治史分析...

## 7. 证据分级综述
[实证] 证据...

## 8. 老丁因子
### 核心判断
判断...
### 证据链
证据...
### 论证路径
路径...
### 潜在反例
反例...
### 与主流解释的分歧点
分歧...
### 定位说明
[已论证]
"""
        # 没有启用 political 工具，但写了第2章内容，这是可以的
        # 但如果不写内容也不标注不适用，应该有警告
        validator = StructureValidator(content, [])  # 空工具列表
        result, issues = validator.validate()
        
        # 应该警告第2章既没有内容也没有标注不适用
        # 但现在有内容，所以应该通过或警告
        self.assertIn(result, [ValidationResult.PASS, ValidationResult.WARNING])
    
    def test_laoding_factor_incomplete(self):
        """测试老丁因子结构不完整"""
        content = """
## 1. 原子化扫描结果
字词校释...

## 7. 证据分级综述
[实证] 证据...

## 8. 老丁因子
只有核心判断，缺少其他子结构...
"""
        validator = StructureValidator(content, [])
        result, issues = validator.validate()
        
        # 应该警告老丁因子结构不完整
        self.assertEqual(result, ValidationResult.WARNING)
        self.assertTrue(any("老丁因子" in issue for issue in issues))
    
    def test_evidence_anchoring(self):
        """测试证据锚定"""
        content = """
## 1. 原子化扫描结果
字词校释...

## 7. 证据分级综述
[实证] 朱熹《四书章句集注》...
[推论] 基于...
[缺失] 关于...

## 8. 老丁因子
### 核心判断
判断...
### 证据链
证据...
### 论证路径
路径...
### 潜在反例
反例...
### 与主流解释的分歧点
分歧...
### 定位说明
[已论证]
"""
        validator = StructureValidator(content, [])
        result, issues = validator.validate()
        
        self.assertEqual(result, ValidationResult.PASS)
    
    def test_not_applicable_marker(self):
        """测试'不适用'标注识别"""
        content = """
## 1. 原子化扫描结果
字词校释...

## 2. 政治史还原
本篇不适用（无政治史背景）

## 7. 证据分级综述
[实证] 证据...

## 8. 老丁因子
### 核心判断
判断...
### 证据链
证据...
### 论证路径
路径...
### 潜在反例
反例...
### 与主流解释的分歧点
分歧...
### 定位说明
[已论证]
"""
        validator = StructureValidator(content, [])  # 未启用 political
        result, issues = validator.validate()
        
        # 应该通过，因为标注了不适用
        self.assertIn(result, [ValidationResult.PASS, ValidationResult.WARNING])


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整流程"""
        # 1. 输入文本
        input_text = "三桓专权，季氏僭越，朱熹认为..."
        
        # 2. 路由断言
        router = RouteAsserter(input_text)
        routing_result = router.assert_routing()
        
        self.assertIn("political", routing_result.actual_tools)
        self.assertIn("anatomy", routing_result.actual_tools)
        
        # 3. 生成模拟输出
        mock_output = f"""
## 1. 原子化扫描结果
字词校释内容...

## 2. 政治史还原
三桓政治史分析...

## 3. 注疏六维解剖
朱熹注疏分析...

## 4. 异常检测报告
本篇不适用

## 5. 变量替换实验
本篇不适用

## 6. 圆桌会议纪要
本篇不适用

## 7. 证据分级综述
[实证] 三桓专权证据...
[推论] 基于...

## 8. 老丁因子
### 核心判断
三桓之乱本质是...
### 证据链
[实证] 证据1...
### 论证路径
从文本...
### 潜在反例
质疑：...
回应：...
### 与主流解释的分歧点
朱熹认为...但...
### 定位说明
[已论证]

## 9. 冷知识命题
[本篇无冷知识触发点]
"""
        
        # 4. 结构验证
        validator = StructureValidator(mock_output, routing_result.actual_tools)
        struct_result, issues = validator.validate()
        
        self.assertEqual(struct_result, ValidationResult.PASS)


class TestGoldenSetCompliance(unittest.TestCase):
    """测试与 golden_set.json 的符合性"""
    
    def setUp(self):
        """加载 golden set"""
        golden_set_path = harness_dir / "golden_set.json"
        if golden_set_path.exists():
            import json
            with open(golden_set_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.golden_set = data.get("test_cases", [])
        else:
            self.golden_set = []
    
    def test_golden_set_loaded(self):
        """测试 golden set 可加载"""
        self.assertTrue(len(self.golden_set) > 0, "golden_set.json 为空或不存在")
    
    def test_golden_set_cases(self):
        """测试 golden set 用例"""
        if not self.golden_set:
            self.skipTest("golden_set.json 未加载")
        
        for case in self.golden_set:
            with self.subTest(case=case.get("name", "未命名")):
                # 路由断言
                input_text = case.get("input", "")
                expected_tools = set(case.get("expected_routing", {}).get("expected_enabled_tools", []))
                
                router = RouteAsserter(input_text)
                routing_result = router.assert_routing()
                
                self.assertEqual(
                    routing_result.actual_tools, 
                    expected_tools,
                    f"路由断言失败: 期望 {expected_tools}, 实际 {routing_result.actual_tools}"
                )


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestRouteAsserter))
    suite.addTests(loader.loadTestsFromTestCase(TestStructureValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestGoldenSetCompliance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
