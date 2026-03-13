# Literature Review Skill v2.2.0 - 发布说明

## 发布日期
2026-03-13

## 版本说明

这是 literature-review skill 的 v2.2.0 版本，包含多项改进和增强功能。

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

## 新增功能

### 1. 简单读取模式 (`--simple-read`)

新增快速文件查看功能，用于只需要读取文件内容而不进行完整分析的场景。

```bash
# 简单读取模式
python main.py --topic "快速查看" --files examples/sample.txt --simple-read
```

### 2. 日志基础设施

添加统一的日志记录系统，便于调试和问题追踪。

日志文件位置：`literature_review.log`

### 3. 完整使用示例

SKILL.md 中新增 5 个完整的使用场景示例：

1. 基础文献综述（三篇文档）
2. 交叉验证共识与分歧
3. 简单文件读取（快速模式）
4. 英文输出与 BibTeX 导出
5. 禁用网络搜索（仅本地文档）

### 4. Feishu 集成配置说明

新增 Feishu API 配置示例和说明。

---

## 改进内容

### 文档改进

- **SKILL.md 描述优化**：添加触发关键词（"用于"、"帮助"、"for"）
- **使用示例完善**：5 个不同场景的完整示例
- **网络搜索说明**：明确标注为模拟实现

### 代码质量提升

- **异常处理改进**：修复裸 except 子句
- **类型提示完善**：为私有方法添加类型提示
- **日志系统集成**：统一的日志记录

### 法律合规

- **LICENSE 文件**：新增 MIT License，满足开源项目要求

---

## 使用说明

### MCP 工具

skill 提供以下 MCP 工具：

- `generate_literature_review` - 生成文献综述
- `analyze_document` - 分析单个文档
- `cross_verify_documents` - 交叉验证多篇文档
- `fetch_feishu_data` - 获取飞书数据

### 命令行使用

```bash
# 基础用法
python main.py --topic "研究主题" --files doc1.txt doc2.pdf

# 带选项
python main.py --topic "研究主题" --files doc1.txt --lang en --depth deep

# 简单读取模式
python main.py --topic "快速查看" --files doc1.txt --simple-read
```

### 配置文件

复制 `config.yaml.example` 为 `config.yaml` 并根据需要配置：

```yaml
feishu:
  enabled: true
  app_id: "your_app_id"
  app_secret: "your_app_secret"
```

---

## 已知问题

1. **网络搜索**：当前为模拟实现，需要配置真实 API 才能使用
2. **Feishu 集成**：需要配置 API 凭证才能使用
3. **PDF 解析**：某些复杂 PDF 布局可能需要 marker-pdf 库

---

## 迁移指南

从 v2.1.0 升级到 v2.2.0：

1. 更新 SKILL.md（描述和使用示例）
2. 替换 main.py（新增日志和简单读取模式）
3. 修复 markdown-converter.py（异常处理）
4. 添加 CHANGELOG.md（记录变更）
5. 添加 LICENSE 文件

---

## 贡献者

欢迎提交问题报告和功能建议！

- 报告问题：GitHub Issues
- 功能建议：GitHub Discussions 或 Pull Request
- 文档改进：直接提交 PR

---

## 许可证

MIT License - 详见 LICENSE 文件
