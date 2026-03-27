# Literature Review Skill v3.0.0 - 发布说明

## 发布日期
2026-03-27

## 版本代号
Socratic Roundtable（苏格拉底圆桌版）

## 版本说明

这是 literature-review skill 的 v3.0.0 版本，是一次**全面方法论重构**。从"文献综述工具"进化为"学术史侦探系统"。

---

## 核心更新

### 🔪 四把手术刀（深度研究方法论）

v3.0 强制要求 AI 放弃平庸的道德感悟，通过四种硬核逻辑路径进行推演：

1. **政治史视角探针 (Political History Probe)**：将文本还原为春秋时代的权力博弈
2. **注疏六维解剖 (6-Dimension Deconstruction)**：拆解注疏的文本解释、方法论、概念重构、立场假设、隐含前提、时代动机
3. **文本异常检测 (Anomaly Detection)**：扫描"赘词""矛盾词""沉默区"，作为冷知识突破口
4. **变量替换实验 (Counterfactual Testing)**：通过换动词/对象/时间，以"语义塌陷"反证原意图唯一性

### 🏛️ 苏格拉底圆桌会议

- **冲突点将**：自动识别 6 位代表学者，强制包含至少两组对立学术立场
- **苏格拉底固定席位**：使用助产术进行逻辑清洗，提出 3 个致命反问
- **重点追问**：这个解释是为了掩盖什么政治尴尬？

### ⏸️ 交互式检查点机制

- **检查点 A**：原子化扫描完成后暂停，用户确认基础事实
- **检查点 B**：圆桌会议角色阵容确认，用户可调整学者组合

### 📊 证据分级协议

- **[实证]**：来自古籍原文或可信史料的直接证据
- **[推论]**：基于学派立场的逻辑推导，须标注学派归属
- **[缺失]**：明确指出缺乏直接证据的问题

### 🔥 老丁因子 (The Non-Consensus Factor)

- 强制在输出阶段寻找一个"非共识"观察点
- **异见捕捉器**：总结主流注疏中被共同忽略的细节
- **冷知识命题**：生成"X 并不是 Y，而是 Z"格式的判断性结论

---

## 输出增强

- PDF/Docx 导出支持**标准学术脚注格式**
- 输出字数扩展至 4000–6000 字
- 新增圆桌会议实录作为独立章节
- 新增多格式输出参数 `--format md|pdf|docx`

## 幻觉控制强化

- 严禁混淆注者原话与 AI 解读
- 所有注疏引用必须标注具体出处（作者、篇名、版本）
- AI 推论必须使用 `[推论]` 标签显式声明

---

## 安装方法

### 方式一：从 ZIP 包安装

```bash
# 解压 skill 包
unzip literature-review-skill.zip

# 复制到 Claude Code skills 目录
cp -r literature-review-skill ~/.claude/skills/
```

### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/yshengding6/literature-review-skill.git

# 安装依赖
cd literature-review-skill
pip install -r requirements.txt
```

---

## 使用示例

### 示例 1：论语章句深度分析

```bash
python main.py --topic "论语·八佾·八佾舞于庭" --format md
```

### 示例 2：跳过圆桌会议

```bash
python main.py --topic "论语·学而·孝弟为仁之本" --no-socratic --format pdf
```

### 示例 3：带用户笔记的综述

```bash
python main.py --topic "论语·为政·吾十有五而志于学" --files notes/xue-er-notes.txt
```

---

## 向后兼容

- 保留原有 MCP 工具接口（generate_literature_review, analyze_document, cross_verify_documents）
- 保留飞书集成功能
- 保留 PDF 解析、BibTeX 导出等功能
- 新增 `--no-socratic` 参数可跳过圆桌会议阶段

---

## 迁移指南

从 v2.2.1 升级到 v3.0.0：

1. 替换 SKILL.md（完全重写）
2. 替换 PROMPT_TEMPLATE.md（苏格拉底圆桌版）
3. 更新 main.py（版本号和文档字符串）
4. 更新 README.md 和 README_CN.md
5. 更新 CHANGELOG.md
6. （可选）如需跳过圆桌会议，使用 `--no-socratic` 参数

---

## 已知限制

1. **圆桌会议角色**：AI 模拟的学者观点基于学派立场推演，需用户在检查点 B 确认
2. **政治史还原**：需要用户具备一定的春秋史知识基础，AI 推测部分需审慎对待
3. **冷知识命题**：非共识观察点需用户自行验证

---

## 贡献者

欢迎提交问题报告和功能建议！

- 报告问题：GitHub Issues
- 功能建议：GitHub Discussions 或 Pull Request
- 文档改进：直接提交 PR

---

## 许可证

MIT License - 详见 LICENSE 文件
