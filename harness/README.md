# Literature Review Skill v4.3.0 - Harness 测试框架

## 概述

本 Harness 测试框架用于验证 literature-review-skill 的**原则零**（自适应路径 + 执行确定性）是否正确实现。

## 组件说明

### 1. golden_set.json
Golden Set 测试用例集，包含 3 个经典《论语》章节的测试数据：
- **八佾章** (bayi_chapter): 政治史全启用场景
- **学而章** (xueer_chapter): 仅基础字词+异常检测
- **乞醯章** (qixi_chapter): 六维解剖+变量替换+异常检测

### 2. route_assertions.py
路由断言模块，验证文本特征→方法论启用的映射：

```bash
# 运行所有 golden set 用例
python route_assertions.py

# 运行指定用例
python route_assertions.py --case bayi

# 自定义文本路由分析
python route_assertions.py --text "孔子谓季氏..."
```

**路由规则**（与 SKILL.md 原则零对应）：
| 方法论工具 | 触发条件 | 输出章节 |
|-----------|---------|---------|
| political_history | 三桓/季氏/公室/君臣/礼制/僭越 | 第2章 政治史还原 |
| anomaly_detection | 异文/脱文/衍文/历代多角度解读 | 第4章 异常检测报告 |
| variable_replacement | 概念可替换性检测 | 第5章 变量替换实验 |
| six_dimension | 用户提供注疏原文 | 第3章 注疏六维解剖 |

### 3. structure_validator.py
9章输出结构验证器，检查：
- 必须章节（1,7,8章）是否存在
- 已启用工具对应的章节是否输出
- 未启用章节是否标注"本篇不适用"
- 老丁因子（第8章）子结构完整性
- 证据锚定标记（[实证]/[推论]/[缺失]）

```python
from structure_validator import StructureValidator, validate_structure

# 验证输出结构
content = "...文献综述输出..."
enabled_tools = ["political", "anomaly"]  # 启用的工具

validator = StructureValidator(content, enabled_tools)
result, issues = validator.validate()
# result: ValidationResult.PASS/WARNING/FAIL

# 便捷函数
passed, issues = validate_structure(content, enabled_tools)
```

### 4. run_regression.py
回归测试入口，整合路由断言和结构验证：

```bash
# 运行完整回归测试
python run_regression.py

# 指定 golden set 路径
python run_regression.py /path/to/golden_set.json
```

## 9章输出结构

```
第1章：原子化扫描结果（必须）
第2章：政治史还原（可选，political_history启用时）
第3章：注疏六维解剖（可选，six_dimension启用时）
第4章：异常检测报告（可选，anomaly_detection启用时）
第5章：变量替换实验（可选，variable_replacement启用时）
第6章：圆桌会议纪要（视需要）
第7章：证据分级综述（必须）
第8章：老丁因子（必须）
第9章：冷知识命题（可选）
```

## 老丁因子结构（第8章）

```
### 核心判断
一句话概括，须违背常见理解

### 证据链
[实证] 级证据逐条列出

### 论证路径
从文本证据到核心判断的推理过程

### 潜在反例
质疑：...
回应：...

### 与主流解释的分歧点
与朱熹/刘宝楠/钱穆等人的差异

### 定位说明
[已论证] / [待挖掘]
```

## 运行测试

```bash
cd ~/.workbuddy/skills/literature-review-skill/harness

# 单独运行路由断言
python route_assertions.py

# 单独运行结构验证（通过回归测试）
python run_regression.py

# 全部通过输出示例
# RESULTS: 3 passed, 0 failed
# Pass Rate: 100.0%
```

## 添加新测试用例

在 `golden_set.json` 的 `cases` 数组中添加：

```json
{
  "id": "unique_id",
  "name": "用例名称",
  "input": {
    "topic": "主题描述",
    "text": "原文文本",
    "context": "上下文",
    "provided_commentaries": ["注疏1", "注疏2"]
  },
  "expected_routes": {
    "political_history": true/false,
    "anomaly_detection": true/false,
    "variable_replacement": true/false,
    "six_dimension": true/false
  },
  "expected_chapters": {
    "present": ["存在的章节"],
    "not_applicable": ["标注不适用的章节"],
    "optional": ["可选章节"]
  }
}
```

## 版本历史

- **v4.3.0** (2026-04-14): 初始版本，实现原则零自适应路径+执行确定性验证
