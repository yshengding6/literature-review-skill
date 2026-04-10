# -*- coding: utf-8 -*-
"""
古文典籍文献综述提示词格式转换脚本
将 Markdown 文件转换为 PDF 格式（使用 ReportLab）
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def register_fonts():
    """注册中文字体"""
    # 尝试注册常见的中文字体
    font_paths = [
        # Windows 常见中文字体
        'C:/Windows/Fonts/simsun.ttc',      # 宋体
        'C:/Windows/Fonts/simhei.ttf',       # 黑体
        'C:/Windows/Fonts/msyh.ttc',         # 微软雅黑
        'C:/Windows/Fonts/simkai.ttf',       # 楷体
        'C:/Windows/Fonts/simfang.ttf',      # 仿宋
        # 备选路径
        'C:/Windows/Fonts/simsun.ttf',
    ]

    font_registered = False

    # 尝试注册宋体
    for font_path in font_paths:
        if Path(font_path).exists():
            try:
                if font_path.endswith('.ttc'):
                    # TTC 文件需要指定子字体
                    pdfmetrics.registerFont(TTFont('SimSun', font_path, subfontIndex=0))
                    pdfmetrics.registerFont(TTFont('SimSun-Bold', font_path, subfontIndex=1))
                else:
                    pdfmetrics.registerFont(TTFont('SimSun', font_path))
                font_registered = True
                print(f"已注册字体: {font_path}")
                break
            except Exception as e:
                continue

    # 如果宋体注册失败，尝试其他字体
    if not font_registered:
        for font_path in font_paths:
            if Path(font_path).exists():
                try:
                    if font_path.endswith('.ttc'):
                        pdfmetrics.registerFont(TTFont('SimSun', font_path, subfontIndex=0))
                    else:
                        pdfmetrics.registerFont(TTFont('SimSun', font_path))
                    font_registered = True
                    print(f"已注册字体: {font_path}")
                    break
                except Exception as e:
                    continue

    if not font_registered:
        print("警告: 未能注册中文字体，可能无法正确显示中文")
        print("请确保系统已安装中文字体")

    return font_registered


def create_custom_styles():
    """创建自定义样式"""
    from reportlab.lib.styles import StyleSheet1

    styles = StyleSheet1()

    # 标题样式
    styles.add(ParagraphStyle(
        name='TitleStyle',
        fontName='SimSun',
        fontSize=18,
        leading=24,
        spaceAfter=12,
        textColor=(0, 0, 0),
    ))

    styles.add(ParagraphStyle(
        name='Heading1',
        fontName='SimSun',
        fontSize=16,
        leading=20,
        spaceAfter=10,
        spaceBefore=12,
        textColor=(0, 0, 0),
    ))

    styles.add(ParagraphStyle(
        name='Heading2',
        fontName='SimSun',
        fontSize=14,
        leading=18,
        spaceAfter=8,
        spaceBefore=10,
        textColor=(0, 0, 0),
    ))

    styles.add(ParagraphStyle(
        name='Heading3',
        fontName='SimSun',
        fontSize=12,
        leading=16,
        spaceAfter=6,
        spaceBefore=8,
        textColor=(0, 0, 0),
    ))

    styles.add(ParagraphStyle(
        name='BodyText',
        fontName='SimSun',
        fontSize=10,
        leading=14,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    ))

    styles.add(ParagraphStyle(
        name='Quote',
        fontName='SimSun',
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6,
        textColor=(80, 80, 80),
    ))

    styles.add(ParagraphStyle(
        name='List',
        fontName='SimSun',
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=3,
    ))

    return styles


def escape_html(text):
    """转义HTML特殊字符"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def process_markdown_to_pdf(md_content, pdf_path):
    """处理 Markdown 内容并生成 PDF"""
    print(f"正在生成 PDF 文件: {pdf_path}")

    # 注册中文字体
    font_registered = register_fonts()

    # 创建文档
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=0.8 * inch,
        rightMargin=0.8 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
    )

    # 获取样式
    styles = create_custom_styles()

    # 存储所有元素
    elements = []

    # 解析 Markdown 内容
    lines = md_content.split('\n')
    in_list = False
    list_level = 0

    for line in lines:
        line = line.rstrip()

        # 空行
        if not line:
            elements.append(Spacer(1, 0.1 * inch))
            in_list = False
            continue

        # 标题处理
        if line.startswith('#'):
            in_list = False
            level = line.count('#')
            title = line.lstrip('#').strip()
            if level == 1:
                elements.append(Paragraph(escape_html(title), styles['TitleStyle']))
            elif level == 2:
                elements.append(Spacer(1, 0.1 * inch))
                elements.append(Paragraph(escape_html(title), styles['Heading1']))
            elif level == 3:
                elements.append(Spacer(1, 0.05 * inch))
                elements.append(Paragraph(escape_html(title), styles['Heading2']))
            else:
                elements.append(Paragraph(escape_html(title), styles['Heading3']))

        # 引用块
        elif line.startswith('>'):
            in_list = False
            text = line.lstrip('>').strip()
            elements.append(Paragraph(f"<i>{escape_html(text)}</i>", styles['Quote']))

        # 分割线
        elif line.startswith('---'):
            in_list = False
            elements.append(Paragraph('<font size="8"><hr/></font>', styles['BodyText']))

        # 列表项
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            text = line.strip()[2:].strip()
            # 处理嵌套列表
            level = (len(line) - len(line.lstrip())) // 2
            indent = 10 + level * 15
            list_style = ParagraphStyle(
                'ListIndent',
                parent=styles['List'],
                leftIndent=indent,
                bulletIndent=indent - 10,
                bulletFontSize=9
            )
            elements.append(Paragraph(f"• {escape_html(text)}", list_style))
            in_list = True

        # 数字列表
        elif line.strip() and line.strip()[0].isdigit() and '. ' in line.strip():
            in_list = False
            num, text = line.strip().split('. ', 1)
            elements.append(Paragraph(f"{num}. {escape_html(text)}", styles['List']))

        # 表格行（简化处理）
        elif '|' in line and line.count('|') >= 2:
            in_list = False
            # 分割线
            if '---' in line:
                continue
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_line = ' | '.join(escape_html(cell) for cell in cells)
            elements.append(Paragraph(f"<b>{table_line}</b>" if cells[0].startswith('核心命题') else table_line, styles['BodyText']))

        # 加粗文本
        elif '**' in line:
            in_list = False
            parts = line.split('**')
            html_parts = []
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    html_parts.append(escape_html(part))
                else:
                    html_parts.append(f"<b>{escape_html(part)}</b>")
            elements.append(Paragraph(''.join(html_parts), styles['BodyText']))

        # 普通段落
        else:
            if not in_list:
                elements.append(Paragraph(escape_html(line), styles['BodyText']))

    # 生成 PDF
    doc.build(elements)
    print(f"PDF 文件已生成: {pdf_path}")


def main():
    """主函数"""
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent
    md_file = script_dir / "古文典籍文献综述_标准提示词_v2.0.md"

    if not md_file.exists():
        print(f"错误: 找不到文件 {md_file}")
        return

    # 输出文件路径
    pdf_output = script_dir / "古文典籍文献综述_标准提示词_v2.0.pdf"

    try:
        # 读取 Markdown 文件
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 转换为 PDF
        process_markdown_to_pdf(md_content, pdf_output)

    except Exception as e:
        print(f"PDF 生成失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
