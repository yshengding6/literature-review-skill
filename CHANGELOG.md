# Literature Review Skill - 变更日志

## [2.2.1] - 2026-03-13

### 新增功能
- 添加简单读取模式 (`--simple-read`) 用于快速文件查看
- 添加日志基础设施，便于调试和问题追踪
- 添加完整的 Feishu 集成使用示例

### 改进
- **SKILL.md 描述改进**：添加触发关键词（"用于"、"帮助"、"for"、"use"）使 skill 更容易被正确触发
- **SKILL.md 使用示例**：添加 5 个完整的使用场景示例，包括基本综述、交叉验证、简单读取、英文输出、禁用网络搜索
- **异常处理改进**：修复 markdown-converter.py 中的裸 except 子句，使用特定异常类型 (OSError, IOError, RuntimeError, ValueError, AttributeError)
- **网络搜索文档**：在 README.md 和 SKILL.md 中明确标注网络搜索为模拟实现，提醒用户需要配置真实 API
- **类型提示**：为私有方法添加类型提示 (`-> str`, `-> float`)

### 文档
- 新增 LICENSE 文件（MIT License）
- 新增 CHANGELOG.md 本文件
- 改进 SKILL.md 描述和添加使用示例

### 代码质量
- 添加 logging 模块用于统一的日志记录
- 在关键函数中添加日志调用（文件分析、BibTeX 生成等）
- 修复异常处理中的裸 except 子句

### 安全
- 网络搜索模拟实现明确标注为模拟状态
- Feishu 集成需要用户配置凭证（环境变量或 config.yaml）

## [2.1.0] - 2024-01-XX

### 新增功能
- 交叉验证：识别共识与分歧
- 研究空白：自动检测研究空白
- 引用溯源：严格的引用格式 [Author, Year]
- PDF 解析：支持学术论文 PDF
- BibTeX 导出：生成 Zotero/LaTeX 兼容的参考文献
- Windows 兼容：完全支持 Windows 路径和编码
- 飞书数据集成：从飞书多维表格/电子表格获取数据

### 高级功能
- PDF 解析：集成 pypdf 用于更好的中文支持
- BibTeX 支持：自动生成学术引用格式
- 多语言支持：中文（zh）和英文（en）输出

### 文档
- 完善 README.md，包含安装、使用示例、故障排除
- 新增 SKILL.md 用于 skill 描述和功能说明

## [1.0.0] - 2024-01-XX

### 初始版本
- 基本文档分析
- 网络搜索支持（模拟实现）
- Markdown 综述报告生成
- 文件编码自动检测（UTF-8、GBK、Latin-1）
