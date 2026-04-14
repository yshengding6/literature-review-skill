#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structure Validator - 9章输出结构完整性校验器
验证 literature-review-skill 的输出是否符合 v4.3.0 的 9 章结构规范
"""

import json
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


@dataclass
class ChapterCheck:
    """单章检查结果"""
    chapter_num: int
    chapter_name: str
    required: bool  # 是否为必须章节
    exists: bool
    has_content: bool
    issues: List[str]


class StructureValidator:
    """9章输出结构验证器"""
    
    # 9章结构定义
    CHAPTERS = [
        {"num": 1, "name": "原子化扫描结果", "required": True, 
         "keywords": ["原子化", "扫描", "字词校释"]},
        {"num": 2, "name": "政治史还原", "required": False,
         "keywords": ["政治史", "三桓", "季氏", "公室", "君臣", "礼制"]},
        {"num": 3, "name": "注疏六维解剖", "required": False,
         "keywords": ["六维", "注疏", "训诂", "义理", "语境", "源流"]},
        {"num": 4, "name": "异常检测报告", "required": False,
         "keywords": ["异常", "异文", "脱文", "衍文", "错简"]},
        {"num": 5, "name": "变量替换实验", "required": False,
         "keywords": ["变量", "替换", "换词", "语义"]},
        {"num": 6, "name": "圆桌会议纪要", "required": False,
         "keywords": ["圆桌", "苏格拉底", "质疑", "讨论"]},
        {"num": 7, "name": "证据分级综述", "required": True,
         "keywords": ["证据", "综述", "[实证]", "[推论]", "[缺失]"]},
        {"num": 8, "name": "老丁因子", "required": True,
         "keywords": ["老丁因子", "核心判断", "证据链", "论证路径", "潜在反例"]},
        {"num": 9, "name": "冷知识命题", "required": False,
         "keywords": ["冷知识", "违背", "常见理解"]},
    ]
    
    def __init__(self, content: str, enabled_tools: List[str]):
        """
        初始化验证器
        
        Args:
            content: 文献综述输出内容
            enabled_tools: 启用的工具列表 ["political", "anatomy", "anomaly", "variable"]
        """
        self.content = content
        self.enabled_tools = enabled_tools
        self.issues: List[str] = []
        self.checks: List[ChapterCheck] = []
    
    def validate(self) -> Tuple[ValidationResult, List[str]]:
        """
        执行完整验证
        
        Returns:
            (验证结果, 问题列表)
        """
        self.issues = []
        self.checks = []
        
        # 1. 检查必须章节
        self._check_required_chapters()
        
        # 2. 检查已启用工具的章节
        self._check_enabled_tool_chapters()
        
        # 3. 检查未启用章节是否标注"不适用"
        self._check_disabled_chapters()
        
        # 4. 检查老丁因子结构完整性
        self._check_laoding_factor_structure()
        
        # 5. 检查证据锚定
        self._check_evidence_anchoring()
        
        # 6. 汇总结果
        return self._summarize_result()
    
    def _check_required_chapters(self):
        """检查必须章节是否存在"""
        for chapter in self.CHAPTERS:
            if chapter["required"]:
                exists = self._chapter_exists(chapter)
                self.checks.append(ChapterCheck(
                    chapter_num=chapter["num"],
                    chapter_name=chapter["name"],
                    required=True,
                    exists=exists,
                    has_content=exists and self._has_substantial_content(chapter),
                    issues=[] if exists else [f"缺少必须章节：{chapter['name']}"]
                ))
                if not exists:
                    self.issues.append(f"[FAIL] 必须章节 {chapter['num']}. {chapter['name']} 缺失")
    
    def _check_enabled_tool_chapters(self):
        """检查已启用工具的对应章节"""
        tool_to_chapter = {
            "political": 2,
            "anatomy": 3,
            "anomaly": 4,
            "variable": 5,
        }
        
        for tool, chapter_num in tool_to_chapter.items():
            if tool in self.enabled_tools:
                chapter = self._get_chapter_by_num(chapter_num)
                exists = self._chapter_exists(chapter)
                
                if not exists:
                    self.issues.append(
                        f"[FAIL] 已启用工具 '{tool}' 对应章节 {chapter_num}. {chapter['name']} 缺失"
                    )
    
    def _check_disabled_chapters(self):
        """检查未启用章节是否标注'不适用'"""
        tool_to_chapter = {
            "political": 2,
            "anatomy": 3,
            "anomaly": 4,
            "variable": 5,
        }
        
        for tool, chapter_num in tool_to_chapter.items():
            if tool not in self.enabled_tools:
                chapter = self._get_chapter_by_num(chapter_num)
                
                # 检查是否标注"不适用"或"本篇不适用"
                if not self._has_not_applicable_marker(chapter):
                    self.issues.append(
                        f"[WARN] 未启用工具 '{tool}' 对应章节 {chapter_num}. {chapter['name']} "
                        f"应标注'本篇不适用'或类似说明"
                    )
    
    def _check_laoding_factor_structure(self):
        """检查老丁因子（第8章）结构完整性"""
        chapter_8 = self._get_chapter_by_num(8)
        
        if not self._chapter_exists(chapter_8):
            return
        
        # 提取第8章内容（通过章节标题定位）
        chapter_content = self._extract_chapter_content(chapter_8)
        
        required_sections = [
            ("核心判断", r"核心判断|核心观点"),
            ("证据链", r"证据链|证据"),
            ("论证路径", r"论证路径|论证过程"),
            ("潜在反例", r"潜在反例|反例|质疑"),
            ("与主流解释的分歧点", r"分歧点|主流解释|与.*分歧"),
            ("定位说明", r"定位说明|\[已论证\]|\[待挖掘\]"),
        ]
        
        missing_sections = []
        for section_name, pattern in required_sections:
            if not re.search(pattern, chapter_content, re.IGNORECASE):
                missing_sections.append(section_name)
        
        if missing_sections:
            self.issues.append(
                f"[WARN] 老丁因子（第8章）缺少以下子结构：{', '.join(missing_sections)}"
            )
    
    def _check_evidence_anchoring(self):
        """检查证据锚定（[实证]/[推论]/[缺失]）"""
        # 至少应该出现这些标记
        evidence_markers = ["[实证]", "[推论]", "[缺失]"]
        found_markers = [m for m in evidence_markers if m in self.content]
        
        if len(found_markers) < 2:
            self.issues.append(
                f"[WARN] 证据锚定不充分：只发现 {len(found_markers)}/3 种证据标记 "
                f"({', '.join(found_markers) if found_markers else '无'})"
            )
    
    def _chapter_exists(self, chapter: Dict) -> bool:
        """检查章节是否存在"""
        # 检查章节标题（多种格式）
        patterns = [
            rf"##?\s*{chapter['num']}[.\s]+{chapter['name']}",
            rf"第{chapter['num']}章[.\s]*{chapter['name']}",
            rf"【{chapter['num']}】{chapter['name']}",
        ]
        
        for pattern in patterns:
            if re.search(pattern, self.content, re.IGNORECASE):
                return True
        
        # 检查关键词
        keyword_count = sum(
            1 for kw in chapter["keywords"]
            if kw in self.content
        )
        return keyword_count >= 2  # 至少2个关键词出现
    
    def _has_substantial_content(self, chapter: Dict) -> bool:
        """检查章节是否有实质性内容（不只是标题）"""
        chapter_content = self._extract_chapter_content(chapter)
        # 除去标题后至少有100个字符
        return len(chapter_content.strip()) > 100
    
    def _has_not_applicable_marker(self, chapter: Dict) -> bool:
        """检查是否标注'不适用'"""
        chapter_content = self._extract_chapter_content(chapter)
        patterns = [
            r"本篇不适用",
            r"本章不适用",
            r"未启用.*本章",
            r"N/A",
        ]
        return any(re.search(p, chapter_content, re.IGNORECASE) for p in patterns)
    
    def _extract_chapter_content(self, chapter: Dict) -> str:
        """提取指定章节的内容"""
        patterns = [
            rf"##?\s*{chapter['num']}[.\s]+{chapter['name']}.*?(?=##?\s*{chapter['num']+1}|$)",
            rf"第{chapter['num']}章[.\s]*{chapter['name']}.*?(?=第{chapter['num']+1}章|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        
        return ""
    
    def _get_chapter_by_num(self, num: int) -> Dict:
        """根据章节号获取章节定义"""
        for chapter in self.CHAPTERS:
            if chapter["num"] == num:
                return chapter
        return {"num": num, "name": "未知", "keywords": [], "required": False}
    
    def _summarize_result(self) -> Tuple[ValidationResult, List[str]]:
        """汇总验证结果"""
        if not self.issues:
            return ValidationResult.PASS, ["[PASS] 所有检查通过"]
        
        # 如果有必须章节缺失，直接失败
        has_critical_fail = any("[FAIL]" in issue for issue in self.issues)
        
        if has_critical_fail:
            return ValidationResult.FAIL, self.issues
        else:
            return ValidationResult.WARNING, self.issues
    
    def generate_report(self) -> str:
        """生成详细验证报告"""
        result, issues = self.validate()
        
        report_lines = [
            "=" * 60,
            "Literature Review Skill 结构验证报告 (v4.3.0)",
            "=" * 60,
            f"启用工具: {', '.join(self.enabled_tools) if self.enabled_tools else '无'}",
            f"验证结果: {result.value}",
            "-" * 60,
            "章节检查明细:",
        ]
        
        for check in self.checks:
            status = "[OK]" if check.exists else "[MISSING]"
            req_marker = "[必须]" if check.required else "[可选]"
            report_lines.append(
                f"  {status} {check.chapter_num}. {check.chapter_name} {req_marker}"
            )
        
        report_lines.extend([
            "-" * 60,
            "问题列表:",
        ])
        
        if issues:
            for issue in issues:
                report_lines.append(f"  {issue}")
        else:
            report_lines.append("  无")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)


def validate_structure(content: str, enabled_tools: List[str]) -> Tuple[bool, List[str]]:
    """
    便捷函数：验证输出结构
    
    Args:
        content: 文献综述输出内容
        enabled_tools: 启用的工具列表
    
    Returns:
        (是否通过, 问题列表)
    """
    validator = StructureValidator(content, enabled_tools)
    result, issues = validator.validate()
    return result == ValidationResult.PASS, issues


if __name__ == "__main__":
    # 测试用例
    test_content = """
# 文献综述：论语·学而篇

## 1. 原子化扫描结果
本文"学而时习之"的"学"字...

## 7. 证据分级综述
[实证] 朱熹《四书章句集注》...
[推论] 基于宋学立场推测...

## 8. 老丁因子
### 核心判断
"学"并非单纯学习...
### 证据链
[实证] 孔子时代的"学"...
### 论证路径
从文本证据...
### 潜在反例
质疑：...
回应：...
### 与主流解释的分歧点
朱熹认为...
### 定位说明
[已论证]

## 2. 政治史还原
本篇不适用（无可关联政治史背景）

## 3. 注疏六维解剖
本篇不适用

## 4. 异常检测报告
本篇不适用

## 5. 变量替换实验
本篇不适用

## 6. 圆桌会议纪要
本篇不适用
"""
    
    validator = StructureValidator(test_content, [])
    print(validator.generate_report())
