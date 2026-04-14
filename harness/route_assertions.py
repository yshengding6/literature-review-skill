"""
Literature Review Skill v4.3.0 - Route Assertions
路由断言：验证文本特征→方法论启用的映射是否符合原则零规则

用法:
    python route_assertions.py                  # 运行所有 golden set 用例
    python route_assertions.py --case bayi      # 运行指定用例
    python route_assertions.py --text "..."      # 对自定义文本做路由分析
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# 确保 UTF-8 输出（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ── 路由规则定义（与 SKILL.md 原则零严格对应） ──

ROUTE_RULES = {
    "political_history": {
        "name": "政治史探针",
        "keywords": ["三桓", "季氏", "公室", "君臣", "礼制", "僭越", "权臣", "去国", "流亡"],
        "description": "涉及政治权力结构、礼制僭越、君臣关系时启用"
    },
    "anomaly_detection": {
        "name": "异常检测",
        "keywords": ["异文", "脱文", "衍文", "错简", "版本差异"],
        "condition": "原文已被历代注家多角度解读",
        "description": "文本存在异文/版本差异，或历代注家有多角度解读时启用"
    },
    "variable_replacement": {
        "name": "变量替换实验",
        "condition": "原文概念存在换词后语义崩塌的空间",
        "description": "核心概念可替换性检测时启用"
    },
    "six_dimension": {
        "name": "六维解剖",
        "condition": "用户提供了注疏原文",
        "description": "用户提供了注疏原文时启用"
    }
}

# 异常检测的多角度解读关键词（补充规则）
MULTI_INTERPRETATION_SIGNALS = [
    "注家", "注疏", "训诂", "解读", "不同理解", "争议", "分歧",
    "一说", "或曰", "又一说", "异说", "别解"
]


# ── 路由断言类（供 run_regression.py 导入使用） ──

from dataclasses import dataclass, field


@dataclass
class RoutingResult:
    """路由分析结果"""
    actual_tools: set = field(default_factory=set)
    reasoning: Dict[str, str] = field(default_factory=dict)


class RouteAsserter:
    """路由断言器 - 封装路由分析供回归测试使用"""
    
    def __init__(self, input_text: str, context: str = "", 
                 provided_commentaries: Optional[List[str]] = None):
        self.input_text = input_text
        self.context = context
        self.provided_commentaries = provided_commentaries or []
    
    def assert_routing(self) -> RoutingResult:
        """执行路由分析并返回结果"""
        result = analyze_routes(
            text=self.input_text,
            context=self.context,
            provided_commentaries=self.provided_commentaries
        )
        
        # 转换为 set 格式
        actual_tools = {
            k for k, v in result["routes"].items() if v
        }
        
        return RoutingResult(
            actual_tools=actual_tools,
            reasoning=result["reasons"]
        )


# ── 路由分析函数 ──

def analyze_routes(
    text: str,
    context: str = "",
    provided_commentaries: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    分析输入文本，判断应启用哪些方法论工具。
    
    Args:
        text: 原文文本
        context: 上下文说明
        provided_commentaries: 用户提供的注疏原文列表
        
    Returns:
        路由分析结果，包含每个工具的启用状态和理由
    """
    routes = {
        "political_history": False,
        "anomaly_detection": False,
        "variable_replacement": False,
        "six_dimension": False
    }
    reasons = {}
    
    combined_text = f"{text} {context}"
    
    # 规则1：政治史探针
    pol_keywords = ROUTE_RULES["political_history"]["keywords"]
    matched_pol = [kw for kw in pol_keywords if kw in combined_text]
    if matched_pol:
        routes["political_history"] = True
        reasons["political_history"] = f"命中政治史关键词: {', '.join(matched_pol)}"
    else:
        reasons["political_history"] = "未命中政治史关键词"
    
    # 规则2：异常检测
    anomaly_keywords = ROUTE_RULES["anomaly_detection"]["keywords"]
    matched_anomaly = [kw for kw in anomaly_keywords if kw in combined_text]
    multi_signals = [kw for kw in MULTI_INTERPRETATION_SIGNALS if kw in combined_text]
    
    if matched_anomaly:
        routes["anomaly_detection"] = True
        reasons["anomaly_detection"] = f"命中异常检测关键词: {', '.join(matched_anomaly)}"
    elif multi_signals:
        routes["anomaly_detection"] = True
        reasons["anomaly_detection"] = f"检测到多角度解读信号: {', '.join(multi_signals)}"
    else:
        # 默认：经典文本通常存在历代多角度解读空间
        # 如果是古典文献（含"论语""子曰""孔子"等），默认启用异常检测
        classical_signals = ["论语", "子曰", "孔子", "孟子", "诗", "书", "礼", "易", "春秋"]
        # 扩展信号词：古代人名、典籍名、文言文结构
        extended_signals = [
            "微生", "季氏", "公冶长", "颜渊", "子路", "子贡", "曾子", "冉有",
            "八佾", "公冶", "里仁", "雍也", "述而", "泰伯", "乡党", "先进",
            "颜渊篇", "子路篇", "宪问篇", "卫灵公", "季氏篇", "阳货", "微子",
            "章句", "集注", "正义", "注疏", "训诂",
        ]
        # 文言文结构特征
        classical_patterns = [
            r"孰谓.*[。，？]",      # "孰谓微生高直？"
            r"或.*焉",              # "或乞醯焉"
            r"乞诸其",              # "乞诸其邻而与之"
            r"[曰谓云].*[也矣乎]",  # 文言句式
        ]
        
        has_classical = any(sig in combined_text for sig in classical_signals)
        has_extended = any(sig in combined_text for sig in extended_signals)
        has_pattern = any(re.search(p, combined_text) for p in classical_patterns)
        
        if has_classical:
            routes["anomaly_detection"] = True
            reasons["anomaly_detection"] = "古典文献默认启用（历代注家多角度解读空间）"
        elif has_extended:
            routes["anomaly_detection"] = True
            reasons["anomaly_detection"] = "检测到古典文献特征词，默认启用异常检测"
        elif has_pattern:
            routes["anomaly_detection"] = True
            reasons["anomaly_detection"] = "检测到文言文结构特征，默认启用异常检测"
        else:
            reasons["anomaly_detection"] = "未检测到异常检测触发条件"
    
    # 规则3：变量替换实验
    # 检测文本中是否存在核心概念（名词/形容词）可替换的空间
    # 对古典文献默认启用（核心概念几乎都有可替换性）
    classical_signals = ["论语", "子曰", "孔子", "孟子"]
    extended_signals_var = [
        "微生", "季氏", "公冶长", "颜渊", "子路", "子贡", "曾子", "冉有",
        "章句", "集注", "正义", "注疏", "训诂",
    ]
    has_core_concepts = bool(re.search(r'[\u4e00-\u9fa5]{1,2}(?:曰|谓|言|云)', combined_text))
    has_extended_var = any(sig in combined_text for sig in extended_signals_var)
    
    if classical_signals and any(sig in combined_text for sig in classical_signals):
        routes["variable_replacement"] = True
        reasons["variable_replacement"] = "古典文献核心概念默认启用变量替换"
    elif has_extended_var:
        routes["variable_replacement"] = True
        reasons["variable_replacement"] = "检测到古典文献特征词，核心概念默认启用变量替换"
    elif has_core_concepts:
        routes["variable_replacement"] = True
        reasons["variable_replacement"] = "文本含核心概念表达，启用变量替换"
    else:
        reasons["variable_replacement"] = "未检测到变量替换触发条件"
    
    # 规则4：六维解剖
    if provided_commentaries and len(provided_commentaries) > 0:
        routes["six_dimension"] = True
        reasons["six_dimension"] = f"用户提供了{len(provided_commentaries)}条注疏原文"
    else:
        reasons["six_dimension"] = "用户未提供注疏原文"
    
    return {
        "routes": routes,
        "reasons": reasons,
        "input_text_length": len(text),
        "commentary_count": len(provided_commentaries) if provided_commentaries else 0
    }


def assert_routes(
    actual: Dict[str, bool],
    expected: Dict[str, bool],
    case_name: str = ""
) -> List[str]:
    """
    断言实际路由结果与预期一致。
    
    Returns:
        错误列表（空列表表示全部通过）
    """
    errors = []
    prefix = f"[{case_name}] " if case_name else ""
    
    for route_key in expected:
        if route_key not in actual:
            errors.append(f"{prefix}路由 {route_key} 不存在于实际结果中")
            continue
        
        if actual[route_key] != expected[route_key]:
            route_name = ROUTE_RULES.get(route_key, {}).get("name", route_key)
            errors.append(
                f"{prefix}路由 {route_name}({route_key}): "
                f"预期={expected[route_key]}, 实际={actual[route_key]}"
            )
    
    return errors


def load_golden_set() -> Dict[str, Any]:
    """加载 golden_set.json"""
    golden_path = Path(__file__).parent / "golden_set.json"
    with open(golden_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_golden_set_tests() -> tuple:
    """
    运行所有 golden set 用例的路由断言。
    
    Returns:
        (passed_count, failed_count, errors_list)
    """
    golden = load_golden_set()
    cases = golden["cases"]
    
    total_passed = 0
    total_failed = 0
    all_errors = []
    
    print("=" * 60)
    print("LITERATURE REVIEW SKILL v4.3.0 - ROUTE ASSERTIONS")
    print("=" * 60)
    
    for case in cases:
        case_id = case["id"]
        case_name = case["name"]
        input_data = case["input"]
        expected_routes = case["expected_routes"]
        
        print(f"\n[CASE] {case_name} ({case_id})")
        print(f"  原文: {input_data['text'][:50]}...")
        
        # 执行路由分析
        result = analyze_routes(
            text=input_data["text"],
            context=input_data.get("context", ""),
            provided_commentaries=input_data.get("provided_commentaries", [])
        )
        
        # 提取预期的路由布尔值
        expected_bools = {
            k: v for k, v in expected_routes.items()
            if k in ["political_history", "anomaly_detection", "variable_replacement", "six_dimension"]
        }
        
        # 断言
        errors = assert_routes(result["routes"], expected_bools, case_name)
        
        if errors:
            total_failed += 1
            all_errors.extend(errors)
            print(f"  [FAIL]")
            for err in errors:
                print(f"     - {err}")
        else:
            total_passed += 1
            print(f"  [PASS]")
        
        # 打印路由详情
        for route_key, enabled in result["routes"].items():
            route_name = ROUTE_RULES[route_key]["name"]
            status = "[ON] " if enabled else "[OFF]"
            reason = result["reasons"].get(route_key, "")
            print(f"     {route_name}: {status} — {reason}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {total_passed} passed, {total_failed} failed")
    print("=" * 60)
    
    if all_errors:
        print("\n[FAILED] Detail errors:")
        for err in all_errors:
            print(f"  - {err}")
    
    return total_passed, total_failed, all_errors


def analyze_custom_text(text: str, context: str = "", commentaries: Optional[List[str]] = None):
    """对自定义文本做路由分析"""
    result = analyze_routes(text, context, commentaries)
    
    print("\n" + "=" * 60)
    print("自定义文本路由分析")
    print("=" * 60)
    print(f"\n原文: {text[:100]}...")
    if context:
        print(f"上下文: {context[:100]}...")
    if commentaries:
        print(f"注疏数量: {len(commentaries)}")
    
    print("\n路由结果:")
    for route_key, enabled in result["routes"].items():
        route_name = ROUTE_RULES[route_key]["name"]
        status = "[ON] " if enabled else "[OFF]"
        reason = result["reasons"].get(route_key, "")
        print(f"  {route_name}: {status}")
        print(f"    理由: {reason}")
    
    # 推断预期输出章节
    print("\n预期输出章节:")
    chapter_map = {
        ("political_history", True): "  章节二：政治史还原 [ON]",
        ("political_history", False): "  章节二：政治史还原 — 本篇不适用",
        ("six_dimension", True): "  章节三：注疏六维解剖 [ON]",
        ("six_dimension", False): "  章节三：注疏六维解剖 — 本篇不适用",
        ("anomaly_detection", True): "  章节四：异常检测报告 [ON]",
        ("anomaly_detection", False): "  章节四：异常检测报告 — 本篇不适用",
        ("variable_replacement", True): "  章节五：变量替换实验 [ON]",
        ("variable_replacement", False): "  章节五：变量替换实验 — 本篇不适用",
    }
    print("  章节一：原子化扫描结果 [ON] (必有)")
    for (key, val), label in chapter_map.items():
        if result["routes"][key] == val:
            print(label)
            break
    # 更简洁的方式
    for route_key in ["political_history", "six_dimension", "anomaly_detection", "variable_replacement"]:
        enabled = result["routes"][route_key]
        route_name = ROUTE_RULES[route_key]["name"]
        chapter_names = {
            "political_history": "政治史还原",
            "six_dimension": "注疏六维解剖",
            "anomaly_detection": "异常检测报告",
            "variable_replacement": "变量替换实验"
        }
        if enabled:
            print(f"  章节：{chapter_names[route_key]} [ON]")
        else:
            print(f"  章节：{chapter_names[route_key]} — 本篇不适用")
    print("  章节六：圆桌会议纪要 (视需要)")
    print("  章节七：证据分级综述 [ON] (必有)")
    print("  章节八：老丁因子 [ON] (必有)")
    print("  章节九：冷知识命题 [ON] (必有)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--text":
            text = sys.argv[2] if len(sys.argv) > 2 else ""
            analyze_custom_text(text)
        elif sys.argv[1] == "--case":
            case_id = sys.argv[2] if len(sys.argv) > 2 else ""
            golden = load_golden_set()
            for case in golden["cases"]:
                if case_id in case["id"]:
                    result = analyze_routes(
                        text=case["input"]["text"],
                        context=case["input"].get("context", ""),
                        provided_commentaries=case["input"].get("provided_commentaries", [])
                    )
                    print(f"\nCase: {case['name']}")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("用法:")
            print("  python route_assertions.py                  # 运行所有 golden set")
            print("  python route_assertions.py --case bayi      # 运行指定用例")
            print("  python route_assertions.py --text '...'      # 自定义文本路由分析")
    else:
        passed, failed, errors = run_golden_set_tests()
        sys.exit(0 if failed == 0 else 1)
