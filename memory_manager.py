#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Literature Review Skill Memory Manager
实现 Read-Write Reflective Learning 的记忆管理功能

Version: 4.1.2 (Cultural Comparison + P3 Enhanced Routing)
Aligned with: Memento-Skills paper (arXiv:2603.18743)

v4.1.2 新增功能:
- 文化比较模块：诸子百家 vs 西方哲学跨文化分析
- Get笔记集成：自动保存到【论语研究】知识库
- 工作流编排器：生成三种文档（注疏解读、圆桌纪要、文献综述）

P3 增强路由核心变化:
- route_chapter 命令：直接传入章节ID，从 chapter_graph.json 读取 compression 数据
- _compute_chapter_features()：将 compression 数据转换为 blade 对齐的特征向量
- routing_rules 支持文本特征→blade 加权映射（替代简单的 context_match）
- analysis_priority 直接参与 effective_score 计算
"""

import json
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# 配置
SKILL_DIR = Path.home() / ".workbuddy" / "skills" / "literature-review-skill"
MEMORY_FILE = SKILL_DIR / "literature_review_memory.json"
CHAPTER_GRAPH_FILE = SKILL_DIR / "chapter_graph.json"
INITIAL_UTILITY = 0.75
WRITE_TRIGGER_FAILURES = 3
WRITE_TRIGGER_THRESHOLD = 0.5

# ========================================
# 编码处理（Windows 兼容）
# ========================================

def _setup_encoding():
    """设置 Windows 环境的 UTF-8 编码"""
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr, encoding='utf-8', errors='replace')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        return True
    return False

_windows_mode = _setup_encoding()

# ========================================
# 状态标签
# ========================================

STATUS_OK = "[OK]"
STATUS_WARN = "[WARN]"
STATUS_FAIL = "[FAIL]"

# ========================================
# 类定义
# ========================================

class MemoryManager:
    """记忆管理器，实现 Read-Write 闭环

    核心功能：
    - read_file: 读取技能历史和性能数据
    - write_to_file: 记录执行结果，更新 utility_score
    - Route: 基于文本特征和性能数据计算动态路由（P3 增强版）
    - Optimize: 触发写阶段的技能自优化
    """

    def __init__(self, memory_path: Optional[Path] = None,
                 chapter_graph_path: Optional[Path] = None):
        """初始化记忆管理器"""
        self.file = memory_path or MEMORY_FILE
        self.chapter_graph_file = chapter_graph_path or CHAPTER_GRAPH_FILE
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_initialized()

    # ========================================
    # 初始化与迁移
    # ========================================

    def _ensure_initialized(self):
        """确保记忆文件存在且格式正确"""
        if not self.file.exists():
            self._create_initial()
        else:
            try:
                data = self.read()
                if not self._validate_schema(data):
                    self._migrate_schema(data)
            except Exception as e:
                _print_warning(f"读取记忆文件异常，将重建: {e}")
                self._create_initial()

    def _create_initial(self) -> Dict[str, Any]:
        """创建初始记忆文件"""
        initial_data = {
            "version": "4.1.2",
            "created_at": datetime.now().isoformat(),
            "last_session": datetime.now().isoformat(),
            "user_preferences": {
                "output_format": "md",
                "skip_socratic": False,
                "preferred_commentators": ["朱熹", "刘宝楠"],
                "cold_knowledge_enabled": True,
                "auto_optimization": True
            },
            "blades": {
                "political_history_probe": self._init_blade(),
                "six_dimension_deconstruct": self._init_blade(),
                "anomaly_detection": self._init_blade(),
                "variable_substitution": self._init_blade()
            },
            "socratic_session": self._init_blade(),
            "execution_log": [],
            "cold_knowledge_cache": [],
            "router_config": {
                "mode": "heuristic",
                "model_path": None,
                "last_training": None,
                "chapter_graph_path": str(CHAPTER_GRAPH_FILE),
                "hyperparameters": {
                    "context_match_bonus": 1.2,
                    "failure_penalty": 0.5,
                    "initial_score": INITIAL_UTILITY,
                    "learning_rate": 0.1,
                    # P3 新增超参数
                    "priority_boost": 0.15,      # analysis_priority 各维度 boost 上限
                    "interpretive_penalty": 0.1,  # 某朝代注疏异常高时的额外惩罚
                },
                # P3 新增：章节特征→blade 加权规则
                "routing_rules": {
                    "political_history_probe": {
                        "boost_tags": ["政治", "三桓", "季氏", "君臣", "礼制", "僭越",
                                       "公室", "家臣", "权臣", "陈蔡", "流亡", "去国"],
                        "priority_dim": "人物重要性",
                        "weight": 1.0
                    },
                    "six_dimension_deconstruct": {
                        "boost_tags": ["注疏丰富", "多朝代注家", "核心争议丰富",
                                       "诠释史", "范式演变", "训诂", "义理"],
                        "priority_dim": "注家丰富度",
                        "weight": 1.0
                    },
                    "anomaly_detection": {
                        "boost_tags": ["异文", "文字差异", "版本", "脱文", "衍文",
                                       "错简", "异解", "训诂争议"],
                        "priority_dim": "争议密度",
                        "weight": 1.0
                    },
                    "variable_substitution": {
                        "boost_tags": ["假设", "如果", " counterfactual", "因果",
                                       "历史假设", "制度比较", "角色互换"],
                        "priority_dim": "主题深度",
                        "weight": 1.0
                    }
                }
            },
            "skill_version_history": []
        }
        self.write(initial_data)
        return initial_data

    def _init_blade(self) -> Dict[str, Any]:
        """初始化单个 blade 的数据结构"""
        return {
            "utility_score": INITIAL_UTILITY,
            "success_count": 0,
            "failure_count": 0,
            "total_duration_min": 0,
            "last_success": None,
            "last_failure": None,
            "context_patterns": [],
            "failure_reasons": [],
            "optimization_history": []
        }

    def _validate_schema(self, data: Dict[str, Any]) -> bool:
        """验证数据结构是否符合 v4.x 规范"""
        required_keys = [
            "version", "user_preferences", "blades",
            "socratic_session", "execution_log", "cold_knowledge_cache",
            "router_config", "skill_version_history"
        ]
        return all(key in data for key in required_keys)

    def _migrate_schema(self, old_data: Dict[str, Any]):
        """从旧版本迁移数据到 v4.1"""
        new_data = self._create_initial()

        # 迁移执行日志（如果有）
        if "execution_log" in old_data:
            new_data["execution_log"] = old_data["execution_log"]
            self._replay_history_utility(new_data)

        # 迁移冷知识缓存（如果有）
        if "cold_knowledge_cache" in old_data:
            new_data["cold_knowledge_cache"] = old_data["cold_knowledge_cache"]

        # 迁移 router_config（保留旧超参数，补充新字段）
        if "router_config" in old_data:
            old_rc = old_data["router_config"]
            new_rc = new_data["router_config"]
            if "hyperparameters" in old_rc:
                new_rc["hyperparameters"].update(old_rc["hyperparameters"])
            new_rc["last_training"] = old_rc.get("last_training")
            new_rc["mode"] = old_rc.get("mode", "heuristic")

        self.write(new_data)
        _print_migration("数据已从旧版本迁移到 v4.1.0")

    def _replay_history_utility(self, data: Dict[str, Any]):
        """根据历史执行日志重新计算 utility_score"""
        blade_totals = {
            "political_history_probe": {"success": 0, "failure": 0, "duration": 0},
            "six_dimension_deconstruct": {"success": 0, "failure": 0, "duration": 0},
            "anomaly_detection": {"success": 0, "failure": 0, "duration": 0},
            "variable_substitution": {"success": 0, "failure": 0, "duration": 0}
        }

        for log in data.get("execution_log", []):
            for blade in log.get("blades_used", []):
                if blade in blade_totals:
                    blade_totals[blade]["success"] += 1
                    blade_totals[blade]["duration"] += log.get("duration_min", 0)

        for blade_name, totals in blade_totals.items():
            if blade_name in data["blades"]:
                data["blades"][blade_name]["success_count"] = totals["success"]
                data["blades"][blade_name]["failure_count"] = totals["failure"]
                data["blades"][blade_name]["total_duration_min"] = totals["duration"]
                data["blades"][blade_name]["utility_score"] = self._recalculate_utility(
                    data["blades"][blade_name])
                if totals["success"] > 0:
                    data["blades"][blade_name]["last_success"] = data["last_session"]

    # ========================================
    # 基础读写操作
    # ========================================

    def read(self) -> Dict[str, Any]:
        """读取记忆文件"""
        try:
            return json.loads(self.file.read_text(encoding='utf-8'))
        except FileNotFoundError:
            return self._create_initial()
        except Exception as e:
            _print_error(f"读取记忆文件失败: {e}")
            return self._create_initial()

    def write(self, data: Dict[str, Any]):
        """写入记忆文件"""
        data["last_session"] = datetime.now().isoformat()
        try:
            self.file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            _print_error(f"写入记忆文件失败: {e}")

    # ========================================
    # P3 增强路由：章节级特征计算
    # ========================================

    def _load_chapter_compression(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """从 chapter_graph.json 加载指定章节的 compression 数据

        Args:
            chapter_id: 章节标识，如 "4.5", "5.21", "1.1" 等

        Returns:
            chapter compression 数据，或 None（章节不存在）
        """
        if not self.chapter_graph_file.exists():
            _print_warning(f"chapter_graph.json 未找到: {self.chapter_graph_file}")
            return None

        try:
            with open(self.chapter_graph_file, encoding='utf-8') as f:
                graph = json.load(f)

            chapters = graph.get("chapter_compressions", {}).get("chapters", {})
            if chapter_id in chapters:
                return chapters[chapter_id]

            # 尝试带前缀的格式
            for key in chapters:
                if key.replace(".", "") == chapter_id.replace(".", ""):
                    return chapters[key]

            _print_warning(f"章节 {chapter_id} 在 chapter_graph.json 中未找到")
            return None

        except Exception as e:
            _print_error(f"读取 chapter_graph.json 失败: {e}")
            return None

    def _compute_chapter_features(self, compression: Dict[str, Any]) -> Dict[str, Any]:
        """将 chapter compression 数据转换为 blade 对齐的特征向量

        这是 P3 增强路由的核心：通过章节元数据直接推算 blade 有效性

        Args:
            compression: 来自 chapter_graph.json 的章节压缩数据

        Returns:
            text_features 格式的特征向量，供 get_routing_scores() 使用
        """
        routing_tags = compression.get("routing_tags", [])
        analysis_priority = compression.get("analysis_priority", {})
        interpretive_dist = compression.get("interpretive_distribution", {})

        # 合并所有字符串特征（用于关键词匹配）
        all_text_parts = routing_tags + list(interpretive_dist.keys())
        all_text = " ".join(all_text_parts)

        # 计算注疏朝代跨度（跨度越大，六维解剖价值越高）
        non_zero_eras = sum(1 for v in interpretive_dist.values() if v > 0)
        era_span = non_zero_eras

        # 构建文本特征向量
        features = {
            # 标准字段（保持兼容）
            "length": "medium",  # compression 数据不直接包含文本长度
            "keywords": all_text,
            "has_anomaly": any(tag in all_text for tag in ["异文", "异解", "争议"]),
            "commentator_count": sum(interpretive_dist.values()),
            "semantic_dependency": "high" if era_span >= 4 else "medium" if era_span >= 2 else "low",

            # P3 新增字段（来自 chapter_compressions）
            "_routing_tags": routing_tags,
            "_analysis_priority": analysis_priority,
            "_era_span": era_span,
            "_interpretive_dist": interpretive_dist,
            "_chapter_id": compression.get("chapter_id", "unknown"),
        }

        return features

    def route_chapter(self, chapter_id: str, debug: bool = False) -> List[tuple]:
        """P3 核心接口：直接对章节进行路由排序

        自动从 chapter_graph.json 读取 compression 数据，
        计算增强特征，执行加权路由，返回排序后的 blade 列表

        Args:
            chapter_id: 章节标识，如 "4.5", "5.21"
            debug: 是否打印详细调试信息

        Returns:
            [(blade_name, effective_score)] 排序列表
        """
        # 1. 加载章节 compression
        compression = self._load_chapter_compression(chapter_id)
        if not compression:
            _print_warning(f"无法加载章节 {chapter_id}，降级为基于记忆的路由")
            return self.get_sorted_blades({})

        # 2. 计算章节级特征
        features = self._compute_chapter_features(compression)

        # 3. 打印章节概览（debug 模式）
        if debug:
            self._print_chapter_overview(chapter_id, compression, features)

        # 4. 执行增强路由
        scores = self._get_enhanced_routing_scores(features)
        sorted_blades = sorted(scores.items(), key=lambda x: -x[1])

        return sorted_blades

    def _get_enhanced_routing_scores(self, features: Dict[str, Any]) -> Dict[str, float]:
        """P3 增强路由分数计算

        在原有 utility_score + context_match 基础上，
        叠加来自 chapter_graph 的 routing_rules 加权

        公式：
        effective_score = clip_to_1(
            base_utility
            × context_match_bonus（若有匹配）
            × failure_penalty（若有失败模式）
            × priority_boost（来自 analysis_priority 的维度加权）
        )

        Args:
            features: _compute_chapter_features() 输出的特征向量

        Returns:
            {blade_name: effective_score}
        """
        data = self.read()
        router_config = data.get("router_config", {})
        hp = router_config.get("hyperparameters", {})
        routing_rules = router_config.get("routing_rules", {})

        context_match_bonus = hp.get("context_match_bonus", 1.2)
        failure_penalty = hp.get("failure_penalty", 0.5)
        priority_boost = hp.get("priority_boost", 0.15)

        scores = {}
        routing_tags = features.get("_routing_tags", [])
        analysis_priority = features.get("_analysis_priority", {})

        for blade_name, blade_data in data.get("blades", {}).items():
            base_score = blade_data.get("utility_score", INITIAL_UTILITY)
            effective_score = base_score

            # --- 第1层：上下文匹配加成 ---
            context_matched = self._check_context_match(
                features, blade_data.get("context_patterns", [])
            )
            if context_matched:
                effective_score = min(1.0, effective_score * context_match_bonus)

            # --- 第2层：已知失败模式惩罚 ---
            failure_reasons = blade_data.get("failure_reasons", [])
            if failure_reasons:
                failure_kw = self._extract_failure_keywords(failure_reasons)
                if self._check_failure_mode_match(features, failure_kw):
                    effective_score *= failure_penalty

            # --- 第3层：P3 增强 - routing_rules 加权 ---
            rule = routing_rules.get(blade_name, {})
            boost_tags = rule.get("boost_tags", [])
            priority_dim = rule.get("priority_dim", None)
            rule_weight = rule.get("weight", 1.0)

            # 3a. routing_tags 匹配加成
            matched_tags = [t for t in boost_tags if t in routing_tags]
            if matched_tags:
                # 每个匹配标签 +0.05，最多 +0.15
                tag_boost = min(0.15, 0.05 * len(matched_tags))
                effective_score = min(1.0, effective_score + tag_boost)

            # 3b. analysis_priority 维度加权
            if priority_dim and priority_dim in analysis_priority:
                # priority 是 1-10 整数，映射到 [0, priority_boost]
                prio_val = analysis_priority[priority_dim]
                prio_factor = (prio_val / 10.0) * priority_boost
                effective_score = min(1.0, effective_score + prio_factor)

            # 3c. 规则整体权重
            effective_score *= rule_weight

            scores[blade_name] = effective_score

        return scores

    def _print_chapter_overview(self, chapter_id: str,
                                compression: Dict[str, Any],
                                features: Dict[str, Any]):
        """打印章节概览（debug 用）"""
        analysis_priority = features.get("_analysis_priority", {})
        routing_tags = features.get("_routing_tags", [])

        print("\n" + "=" * 60)
        print(f"## P3 章节路由: {chapter_id}")
        print("=" * 60)
        print(f"routing_tags: {', '.join(routing_tags[:8])}")
        if routing_tags:
            print(f"  (共 {len(routing_tags)} 个标签)")
        print(f"\nanalysis_priority:")
        for dim, val in analysis_priority.items():
            bar = "█" * val + "░" * (10 - val)
            print(f"  {dim:12s}: {bar} ({val}/10)")
        print(f"\ninterpretive_dist: {features.get('_interpretive_dist', {})}")
        print(f"era_span: {features.get('_era_span', 0)} 个朝代有注疏")
        print("-" * 60)

    def print_routing_result(self, text_features: Dict[str, Any],
                           debug: bool = False) -> List[str]:
        """打印路由结果（兼容旧接口）"""
        # 优先尝试章节级路由（如果 features 包含 _chapter_id）
        chapter_id = text_features.get("_chapter_id")
        if chapter_id:
            sorted_blades = self.route_chapter(chapter_id, debug=debug)
        else:
            scores = self._get_enhanced_routing_scores(text_features)
            sorted_blades = sorted(scores.items(), key=lambda x: -x[1])

        print("\n" + "=" * 60)
        print("## 动态路由结果（Enhanced Routing v4.1 P3）")
        print("=" * 60)
        print(f"\n输入文本特征:")
        print(f"  - 长度: {text_features.get('length', 'unknown')}")
        print(f"  - 关键词: {text_features.get('keywords', '')[:80]}")
        print(f"  - 异文: {text_features.get('has_anomaly', False)}")
        print(f"  - 注疏数量: {text_features.get('commentator_count', 0)}")
        if text_features.get('_chapter_id'):
            print(f"  - 章节ID: {text_features['_chapter_id']}")
            print(f"  - 优先维度: {text_features.get('_analysis_priority', {})}")
        print(f"\n路由计算（utility_score + 上下文匹配 + P3 routing_rules 加权）：")
        print("-" * 60)

        data = self.read()
        routing_rules = data.get("router_config", {}).get("routing_rules", {})

        for i, (blade, score) in enumerate(sorted_blades, 1):
            blade_data = data["blades"][blade]
            base = blade_data["utility_score"]
            rule = routing_rules.get(blade, {})
            matched_tags = [t for t in rule.get("boost_tags", [])
                           if t in text_features.get("_routing_tags", [])]

            print(f"  {i}. {blade:40s} : {score:.3f} "
                  f"(base={base:.2f}, tags={matched_tags[:3]})")

        print("\n" + "=" * 60)
        print("执行顺序:", " -> ".join(b[0] for b in sorted_blades))
        print("=" * 60 + "\n")

        return [b[0] for b in sorted_blades]

    # ========================================
    # Read-Write: 执行记录
    # ========================================

    def record_execution(self, chapter: str, blades_used: List[str],
                     quality_score: float, duration_min: int,
                     user_corrections: int = 0,
                     skipped_blades: List[str] = None):
        """记录一次完整执行"""
        data = self.read()

        for blade in blades_used:
            if blade in data["blades"]:
                blade_data = data["blades"][blade]
                blade_data["success_count"] += 1
                blade_data["total_duration_min"] += duration_min
                blade_data["last_success"] = datetime.now().isoformat()
                blade_data["utility_score"] = self._recalculate_utility(blade_data)

        if skipped_blades:
            for blade in skipped_blades:
                if blade in data["blades"]:
                    data["blades"][blade]["utility_score"] = max(
                        0.0,
                        data["blades"][blade]["utility_score"] - 0.05
                    )

        execution_entry = {
            "id": datetime.now().strftime("%Y%m%d-%H%M%S"),
            "chapter": chapter,
            "timestamp": datetime.now().isoformat(),
            "blades_used": blades_used,
            "skipped": skipped_blades or [],
            "output_quality": quality_score,
            "user_corrections": user_corrections,
            "duration_min": duration_min
        }
        data["execution_log"].append(execution_entry)

        if len(data["execution_log"]) > 100:
            data["execution_log"] = data["execution_log"][-100:]

        self.write(data)
        _print_info(f"记录执行: 章节={chapter}, blades={blades_used}, quality={quality_score:.2f}")

    def record_failure(self, blade_name: str, reason: str, context: str = ""):
        """记录一次失败"""
        data = self.read()

        blade_data = None
        if blade_name in data["blades"]:
            blade_data = data["blades"][blade_name]
            blade_data["failure_count"] += 1
            if reason not in blade_data["failure_reasons"]:
                blade_data["failure_reasons"].append(reason)
            blade_data["utility_score"] = self._recalculate_utility(blade_data)
            blade_data["last_failure"] = datetime.now().isoformat()

        self.write(data)

        if blade_data and self._should_trigger_write(blade_data):
            return self._generate_optimization_proposal(blade_name, blade_data)
        return None

    def _recalculate_utility(self, blade_data: Dict[str, Any]) -> float:
        """根据历史数据重新计算 utility_score

        公式：utility = initial + lr × (successes - failures) / (successes + failures + 1)
        """
        initial = INITIAL_UTILITY
        lr = 0.1
        successes = blade_data.get("success_count", 0)
        failures = blade_data.get("failure_count", 0)
        total = successes + failures + 1
        score = initial + lr * (successes - failures) / total
        return max(0.0, min(1.0, score))

    def _should_trigger_write(self, blade_data: Dict[str, Any]) -> bool:
        """判断是否触发写阶段优化"""
        condition1 = blade_data.get("failure_count", 0) >= WRITE_TRIGGER_FAILURES
        condition2 = blade_data.get("utility_score", 0.75) < WRITE_TRIGGER_THRESHOLD
        return condition1 or condition2

    def _generate_optimization_proposal(self, blade_name: str,
                                     blade_data: Dict[str, Any]) -> str:
        """生成技能优化提案"""
        failure_reasons = blade_data.get("failure_reasons", [])[-3:]
        return f"""
## [WRITE PHASE] 技能自优化建议

**技能名称**: `{blade_name}`
**当前状态**: utility_score = {blade_data.get('utility_score', 0.75):.3f}
**触发原因**: 连续失败 {blade_data.get('failure_count', 0)} 次 / utility_score 低于阈值 {WRITE_TRIGGER_THRESHOLD}

### 最近失败记录
{chr(10).join(f'- {r}' for r in failure_reasons)}

### 优化方向
基于 Memento-Skills 的 Policy Evaluation 机制：

1. **根因分析**: 分析失败模式是否由 prompt 设计或执行逻辑导致
2. **指令重写**: 重写该 blade 的执行指令段（保留核心方法）
3. **A/B 验证**: 创建新版本并行测试，选择 utility 更高的版本

### 操作选项
回复以下任一选项：

- `同意优化` → 自动应用优化方案，下次使用新版本
- `查看详情` → 查看完整的失败分析和重写建议
- `暂不优化` → 跳过本次优化，继续使用当前版本

---
*本优化由 Read-Write Reflective Learning Write Phase 自动触发*
"""

    # ========================================
    # Read-Write: 旧版动态路由（保留兼容）
    # ========================================

    def get_routing_scores(self, text_features: Dict[str, Any]) -> Dict[str, float]:
        """计算动态路由分数（兼容旧接口，内部调用增强版）"""
        return self._get_enhanced_routing_scores(text_features)

    def get_sorted_blades(self, text_features: Dict[str, Any]) -> List[tuple]:
        """获取排序后的 blade 列表（兼容旧接口）"""
        chapter_id = text_features.get("_chapter_id")
        if chapter_id:
            return self.route_chapter(chapter_id, debug=False)
        scores = self.get_routing_scores(text_features)
        return sorted(scores.items(), key=lambda x: -x[1])

    def _check_context_match(self, text_features: Dict[str, Any],
                              context_patterns: List[str]) -> bool:
        """检查文本特征是否匹配上下文模式"""
        if not context_patterns:
            return False
        keywords = text_features.get("keywords", "")
        text_desc = json.dumps(text_features, ensure_ascii=False).lower()
        for pattern in context_patterns:
            if pattern.lower() in keywords.lower():
                return True
            if pattern.lower() in text_desc:
                return True
        return False

    def _check_failure_mode_match(self, text_features: Dict[str, Any],
                                 failure_keywords: List[str]) -> bool:
        """检查文本特征是否匹配已知失败模式"""
        if not failure_keywords:
            return False
        text_desc = json.dumps(text_features, ensure_ascii=False).lower()
        return any(kw.lower() in text_desc for kw in failure_keywords)

    def _extract_failure_keywords(self, failure_reasons: List[str]) -> List[str]:
        """从失败原因列表提取关键词"""
        keywords_map = {
            "文本过长": ["长", "篇幅", "字数", "冗长"],
            "文本过短": ["短", "简短", "字少"],
            "异文": ["异文", "版本差异", "文字不同"],
            "虚词": ["虚词", "助词", "之乎者也", "而", "矣"],
            "注疏": ["注疏", "注释", "解释"],
            "政治": ["政治", "权力", "三桓", "季氏"],
            "语境": ["语境", "上下文", "语义"]
        }
        extracted_keywords = []
        for reason in failure_reasons:
            for key, patterns in keywords_map.items():
                if any(p in reason for p in patterns):
                    if patterns[0] not in extracted_keywords:
                        extracted_keywords.extend(patterns)
        return extracted_keywords

    # ========================================
    # Read-Write: 冷知识管理
    # ========================================

    def add_cold_knowledge(self, proposition: str, chapter: str,
                         confidence: str = "推论"):
        """添加冷知识命题"""
        data = self.read()
        cold_entry = {
            "proposition": proposition,
            "chapter": chapter,
            "date": datetime.now().isoformat(),
            "confidence": confidence
        }
        data["cold_knowledge_cache"].append(cold_entry)
        if len(data["cold_knowledge_cache"]) > 50:
            data["cold_knowledge_cache"] = data["cold_knowledge_cache"][-50:]
        self.write(data)
        _print_info(f"冷知识已添加: {proposition[:50]}...")

    def get_cold_knowledge(self, chapter: str = None) -> List[Dict[str, Any]]:
        """获取冷知识缓存"""
        data = self.read()
        cache = data.get("cold_knowledge_cache", [])
        if chapter:
            return [k for k in cache if chapter in k.get("chapter", "")]
        return cache

    # ========================================
    # Read-Write: 写阶段优化
    # ========================================

    def apply_optimization(self, blade_name: str, new_instruction: str,
                        reason: str = ""):
        """应用技能优化"""
        data = self.read()
        if blade_name in data["blades"]:
            blade_data = data["blades"][blade_name]
            blade_data["failure_count"] = 0
            blade_data["utility_score"] = INITIAL_UTILITY
            blade_data["optimization_history"].append({
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "new_instruction": new_instruction[:200] + "...",
                "reset_count": blade_data["success_count"]
            })
            version_entry = {
                "version": f"4.1.1-{blade_name}",
                "date": datetime.now().isoformat(),
                "blade": blade_name,
                "changes": f"写阶段优化: {reason}",
                "previous_utility": blade_data.get("utility_score", 0)
            }
            data["skill_version_history"].append(version_entry)
            self.write(data)
            _print_info(f"优化已应用: {blade_name} -> v4.1.1")
            return True
        return False

    def get_optimization_history(self, blade_name: str = None) -> List[Dict[str, Any]]:
        """获取优化历史"""
        data = self.read()
        if blade_name:
            if blade_name in data["blades"]:
                return data["blades"][blade_name].get("optimization_history", [])
            return []
        all_history = []
        for bn, blade_data in data.get("blades", {}).items():
            for opt in blade_data.get("optimization_history", []):
                opt["blade"] = bn
                all_history.append(opt)
        all_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return all_history

    # ========================================
    # 工具方法
    # ========================================

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        data = self.read()
        total_executions = len(data.get("execution_log", []))
        total_duration = sum(
            log.get("duration_min", 0) for log in data.get("execution_log", [])
        )
        blade_stats = {}
        for blade_name, blade_data in data.get("blades", {}).items():
            blade_stats[blade_name] = {
                "utility_score": blade_data.get("utility_score", 0),
                "success_count": blade_data.get("success_count", 0),
                "failure_count": blade_data.get("failure_count", 0),
                "total_duration": blade_data.get("total_duration_min", 0)
            }
        return {
            "total_executions": total_executions,
            "total_duration": total_duration,
            "last_session": data.get("last_session", ""),
            "blade_stats": blade_stats,
            "cold_knowledge_count": len(data.get("cold_knowledge_cache", [])),
            "version_history_count": len(data.get("skill_version_history", []))
        }

    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        data = self.read()

        print("\n" + "=" * 60)
        print("## Literature Review Skill 统计 (v4.1.0 P3)")
        print("=" * 60)
        print(f"\n版本: {data.get('version', 'unknown')}")
        print(f"总执行次数: {stats['total_executions']}")
        print(f"总时长: {stats['total_duration']} 分钟")
        print(f"冷知识数: {stats['cold_knowledge_count']}")
        print(f"chapter_graph: {data.get('router_config', {}).get('chapter_graph_path', 'N/A')}")
        print(f"路由模式: {data.get('router_config', {}).get('mode', 'unknown')}")
        print(f"上次会话: {stats['last_session']}")

        print("\n### Blades 性能")
        print("-" * 60)
        for blade, stat in stats["blade_stats"].items():
            status = (STATUS_OK if stat["utility_score"] > 0.7
                      else STATUS_WARN if stat["utility_score"] > 0.5
                      else STATUS_FAIL)
            print(f"{status} {blade:40s}")
            print(f"    utility: {stat['utility_score']:.3f} | "
                  f"成功: {stat['success_count']} | 失败: {stat['failure_count']} | "
                  f"时长: {stat['total_duration']}min")

        # P3: 打印 routing_rules 概览
        routing_rules = data.get("router_config", {}).get("routing_rules", {})
        if routing_rules:
            print("\n### P3 路由规则（routing_rules）")
            print("-" * 60)
            for blade, rule in routing_rules.items():
                tags = rule.get("boost_tags", [])[:5]
                print(f"  {blade}:")
                print(f"    boost_tags: {', '.join(tags)}{'...' if len(rule.get('boost_tags', [])) > 5 else ''}")
                print(f"    priority_dim: {rule.get('priority_dim', 'N/A')}")

        print("\n" + "=" * 60 + "\n")


# ========================================
# 辅助打印函数
# ========================================

def _print_info(msg: str):
    print(f"[Info] {msg}")

def _print_warning(msg: str):
    print(f"[Warning] {msg}")

def _print_error(msg: str):
    print(f"[Error] {msg}")

def _print_migration(msg: str):
    print(f"[Migration] {msg}")


# ========================================
# 命令行接口
# ========================================

def main():
    parser = argparse.ArgumentParser(
        description="Literature Review Memory Manager - v4.1.0 P3 Enhanced Routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  初始化记忆文件:
    python memory_manager.py init

  查看统计:
    python memory_manager.py stats

  P3 章节级路由（直接对章节排序）:
    python memory_manager.py route_chapter --chapter=4.5 --debug

  旧版动态路由（AI 自动调用）:
    python memory_manager.py route --features='{"length":"short","keywords":"季氏"}'

  记录执行:
    python memory_manager.py execute --chapter="公冶长_5.21" --blades="political,six_dim,var_sub,anomaly" --duration=15 --quality=0.88

  记录失败:
    python memory_manager.py fail --blade=anomaly_detection --reason="文本过长导致赘词误报"

  添加冷知识:
    python memory_manager.py cold --prop="孔子归与之叹是政治失败找台阶" --chapter="公冶长_5.21"

  应用优化:
    python memory_manager.py optimize --blade=anomaly_detection --reason="调整长文本判断标准"
        """
    )

    parser.add_argument("command", nargs="?",
                       choices=["init", "read", "stats", "route", "route_chapter",
                               "execute", "fail", "optimize", "cold", "history"],
                       default="stats",
                       help="要执行的命令")

    # 路由相关参数
    parser.add_argument("--features", type=str, help="文本特征（JSON 字符串）")
    parser.add_argument("--chapter", type=str, help="章节ID（用于 route_chapter 命令）")
    parser.add_argument("--debug", action="store_true", help="打印详细调试信息")

    # 执行记录参数
    parser.add_argument("--blades", type=str, help="使用的 blades（逗号分隔）")
    parser.add_argument("--duration", type=int, help="执行时长（分钟）")
    parser.add_argument("--quality", type=float, help="输出质量分数 [0, 1]")
    parser.add_argument("--corrections", type=int, default=0, help="用户纠正次数")
    parser.add_argument("--skipped", type=str, help="跳过的 blades（逗号分隔）")

    # 失败记录参数
    parser.add_argument("--blade", type=str, help="Blade 名称")
    parser.add_argument("--reason", type=str, help="失败原因")

    # 冷知识参数
    parser.add_argument("--prop", type=str, help="冷知识命题")
    parser.add_argument("--confidence", type=str, default="推论",
                       choices=["实证", "推论"], help="置信度")

    # 优化参数
    parser.add_argument("--instruction", type=str, help="新指令内容")

    args = parser.parse_args()
    manager = MemoryManager()

    if args.command == "init":
        _print_info(f"记忆文件已创建: {manager.file}")
        _print_info("运行 'python memory_manager.py stats' 查看初始状态")

    elif args.command == "read":
        data = manager.read()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.command == "stats":
        manager.print_stats()

    elif args.command == "route":
        if args.features:
            try:
                features = json.loads(args.features)
                manager.print_routing_result(features, args.debug)
            except json.JSONDecodeError as e:
                _print_error(f"JSON 格式错误: {e}")
        else:
            _print_error("请提供 --features 参数（JSON 格式）")

    elif args.command == "route_chapter":
        # P3 核心命令
        if args.chapter:
            result = manager.route_chapter(args.chapter, debug=args.debug)
            manager.print_routing_result({"_chapter_id": args.chapter}, debug=False)
        else:
            _print_error("route_chapter 需要 --chapter 参数（如 --chapter=4.5）")

    elif args.command == "execute":
        if args.chapter and args.blades and args.duration is not None:
            blade_map = {
                "political": "political_history_probe",
                "six_dim": "six_dimension_deconstruct",
                "anomaly": "anomaly_detection",
                "var_sub": "variable_substitution"
            }
            blades_expanded = []
            for b in args.blades.split(","):
                blades_expanded.append(blade_map.get(b.strip(), b.strip()))
            skipped = [blade_map.get(s.strip()) for s in args.skipped.split(",")] if args.skipped else []
            manager.record_execution(
                chapter=args.chapter,
                blades_used=blades_expanded,
                quality_score=args.quality or 0.75,
                duration_min=args.duration,
                user_corrections=args.corrections,
                skipped_blades=skipped
            )
        else:
            _print_error("execute 命令需要 --chapter, --blades, --duration 参数")

    elif args.command == "fail":
        if args.blade and args.reason:
            proposal = manager.record_failure(args.blade, args.reason)
            if proposal:
                print(proposal)
        else:
            _print_error("fail 命令需要 --blade 和 --reason 参数")

    elif args.command == "cold":
        if args.prop and args.chapter:
            manager.add_cold_knowledge(args.prop, args.chapter, args.confidence)
        else:
            _print_error("cold 命令需要 --prop 和 --chapter 参数")

    elif args.command == "optimize":
        if args.blade and args.instruction:
            manager.apply_optimization(args.blade, args.instruction, args.reason or "")
        else:
            _print_error("optimize 命令需要 --blade 和 --instruction 参数")

    elif args.command == "history":
        history = manager.get_optimization_history()
        if history:
            print("\n## 优化历史")
            for h in history[:10]:
                print(f"\n{h['timestamp']}")
                print(f"Blade: {h.get('blade', 'unknown')}")
                print(f"Reason: {h.get('reason', 'N/A')}")
                print("-" * 40)
        else:
            _print_info("暂无优化历史")


if __name__ == "__main__":
    main()
