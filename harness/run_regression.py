#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression Test Runner - 回归测试入口
整合路由断言和结构验证，执行完整的回归测试
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# 导入 harness 模块
from route_assertions import RouteAsserter, RoutingResult
from structure_validator import StructureValidator, ValidationResult


class RegressionRunner:
    """回归测试运行器"""
    
    def __init__(self, golden_set_path: str = None):
        """
        初始化测试运行器
        
        Args:
            golden_set_path: golden_set.json 文件路径，默认为 harness 目录下
        """
        if golden_set_path is None:
            harness_dir = Path(__file__).parent
            golden_set_path = harness_dir / "golden_set.json"
        
        self.golden_set_path = Path(golden_set_path)
        self.golden_set: List[Dict] = []
        self.results: List[Dict] = []
        
    def load_golden_set(self) -> bool:
        """加载 golden set"""
        try:
            with open(self.golden_set_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.golden_set = data.get("cases", [])
            print(f"[OK] Loaded {len(self.golden_set)} test cases")
            return True
        except Exception as e:
            print(f"[FAIL] Load golden set failed: {e}")
            return False
    
    def run_all_tests(self) -> Tuple[bool, Dict]:
        """
        运行所有回归测试
        
        Returns:
            (全部通过, 详细结果)
        """
        if not self.golden_set:
            if not self.load_golden_set():
                return False, {"error": "无法加载测试用例"}
        
        self.results = []
        all_passed = True
        
        print("\n" + "=" * 70)
        print("Literature Review Skill Regression Test (v4.3.0)")
        print("=" * 70)
        
        for i, test_case in enumerate(self.golden_set, 1):
            print(f"\n[TEST {i}/{len(self.golden_set)}] {test_case.get('name', 'Unnamed')}")
            print("-" * 70)
            
            result = self._run_single_test(test_case)
            self.results.append(result)
            
            if not result["passed"]:
                all_passed = False
        
        return all_passed, self._generate_summary()
    
    def _run_single_test(self, test_case: Dict) -> Dict:
        """运行单个测试用例"""
        result = {
            "name": test_case.get("name", "未命名"),
            "passed": True,
            "routing_test": None,
            "structure_test": None,
            "errors": []
        }
        
        # 1. 路由断言测试
        input_data = test_case.get("input", {})
        input_text = input_data.get("text", "")
        expected_routes = test_case.get("expected_routes", {})
        expected_tools = set()
        if expected_routes.get("political_history"):
            expected_tools.add("political_history")
        if expected_routes.get("anomaly_detection"):
            expected_tools.add("anomaly_detection")
        if expected_routes.get("variable_replacement"):
            expected_tools.add("variable_replacement")
        if expected_routes.get("six_dimension"):
            expected_tools.add("six_dimension")
        
        print(f"  [RUN] Routing assertion test...")
        print(f"     Input: {input_text[:50]}...")
        print(f"     Expected tools: {expected_tools if expected_tools else 'None'}")
        
        context = input_data.get("context", "")
        commentaries = input_data.get("provided_commentaries", [])
        router = RouteAsserter(input_text, context, commentaries)
        routing_result = router.assert_routing()
        
        routing_passed = routing_result.actual_tools == expected_tools
        result["routing_test"] = {
            "passed": routing_passed,
            "expected": list(expected_tools),
            "actual": list(routing_result.actual_tools),
            "reasoning": routing_result.reasoning
        }
        
        if not routing_passed:
            result["passed"] = False
            error_msg = f"Routing assertion failed: expected {expected_tools}, got {routing_result.actual_tools}"
            result["errors"].append(error_msg)
            print(f"     [FAIL] {error_msg}")
        else:
            print(f"     [PASS] Routing assertion passed")
        
        # 2. 结构验证测试
        expected_chapters = test_case.get("expected_chapters", {})
        if expected_chapters:
            print(f"  [RUN] Structure validation test...")
            
            mock_output = test_case.get("mock_output", "")
            if not mock_output:
                mock_output = self._generate_minimal_output(
                    routing_result.actual_tools,
                    expected_chapters
                )
            
            # 转换工具名
            enabled_tools = []
            if routing_result.actual_tools:
                tool_mapping = {
                    "political_history": "political",
                    "six_dimension": "anatomy",
                    "anomaly_detection": "anomaly",
                    "variable_replacement": "variable"
                }
                for t in routing_result.actual_tools:
                    if t in tool_mapping:
                        enabled_tools.append(tool_mapping[t])
            
            validator = StructureValidator(mock_output, enabled_tools)
            struct_result, struct_issues = validator.validate()
            
            struct_passed = struct_result == ValidationResult.PASS
            result["structure_test"] = {
                "passed": struct_passed,
                "result": struct_result.value,
                "issues": struct_issues
            }
            
            if not struct_passed:
                result["passed"] = False
                for issue in struct_issues:
                    result["errors"].append(f"Structure validation: {issue}")
                print(f"     [FAIL] Structure validation: {len(struct_issues)} issues")
                for issue in struct_issues:
                    print(f"        - {issue}")
            else:
                print(f"     [PASS] Structure validation passed")
        
        return result
    
    def _generate_minimal_output(self, enabled_tools: set, 
                                  expected_structure: Dict) -> str:
        """生成最小化验证内容"""
        chapters = []
        
        # 第1章：必须
        chapters.append("## 1. 原子化扫描结果\n字词校释内容...")
        
        # 第2-5章：根据启用工具
        tool_chapters = {
            "political_history": ("2", "政治史还原", "政治史分析内容..."),
            "six_dimension": ("3", "注疏六维解剖", "六维解剖内容..."),
            "anomaly_detection": ("4", "异常检测报告", "异常检测内容..."),
            "variable_replacement": ("5", "变量替换实验", "变量替换内容..."),
        }
        
        for tool, (num, name, content) in tool_chapters.items():
            if tool in enabled_tools:
                chapters.append(f"## {num}. {name}\n{content}")
            else:
                chapters.append(f"## {num}. {name}\n本篇不适用")
        
        # 第6章：圆桌（可选）
        if expected_structure.get("optional", []):
            chapters.append("## 6. 圆桌会议纪要\n圆桌讨论内容...")
        else:
            chapters.append("## 6. 圆桌会议纪要\n本篇不适用")
        
        # 第7章：必须
        chapters.append("## 7. 证据分级综述\n[实证] 证据...\n[推论] 推论...")
        
        # 第8章：老丁因子（必须）
        chapters.append("""## 8. 老丁因子
### 核心判断
核心判断内容...
### 证据链
[实证] 证据...
### 论证路径
论证路径...
### 潜在反例
质疑：...
回应：...
### 与主流解释的分歧点
分歧点...
### 定位说明
[已论证]""")
        
        # 第9章：冷知识（可选）
        chapters.append("## 9. 冷知识命题\n[本篇无冷知识触发点]")
        
        return "\n\n".join(chapters)
    
    def _generate_summary(self) -> Dict:
        """生成测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        
        return {
            "timestamp": datetime.now().isoformat(),
            "version": "v4.3.0",
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A",
            "details": self.results
        }
    
    def print_summary(self, summary: Dict):
        """打印测试摘要"""
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        print(f"Total: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass Rate: {summary['pass_rate']}")
        print("=" * 70)
        
        if summary['failed'] > 0:
            print("\n[FAILED] Case details:")
            for result in self.results:
                if not result["passed"]:
                    print(f"\n  - {result['name']}")
                    for error in result['errors']:
                        print(f"    - {error}")
        
        print("\n" + "=" * 70)


def run_regression_tests(golden_set_path: str = None) -> Tuple[bool, Dict]:
    """
    便捷函数：运行回归测试
    
    Args:
        golden_set_path: golden_set.json 路径
    
    Returns:
        (是否全部通过, 详细结果)
    """
    runner = RegressionRunner(golden_set_path)
    passed, summary = runner.run_all_tests()
    runner.print_summary(summary)
    return passed, summary


if __name__ == "__main__":
    # 命令行入口
    if len(sys.argv) > 1:
        golden_set_path = sys.argv[1]
    else:
        golden_set_path = None
    
    passed, summary = run_regression_tests(golden_set_path)
    sys.exit(0 if passed else 1)
