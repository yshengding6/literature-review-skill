# -*- coding: utf-8 -*-
"""
Get笔记集成模块 (GetNote Integration Module)
literature-review-skill v4.1.2

功能：
- 保存笔记到 Get笔记知识库
- 自动标注标签
- 支持 docx 文件内容保存
- 自动上传到【论语研究】知识库
"""

import json
import re
import sys
import os
import time
import urllib.request
import urllib.error
import io
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 设置编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ========================================
# 配置
# ========================================

BASE_URL = "https://openapi.biji.com"
LUNYU_KB_ID = "QYA1qm4Y"  # 【论语研究】知识库 ID

# 默认标签（文化比较相关）
DEFAULT_TAGS = ["论语研究", "文化比较", "文献综述"]

# 文化比较文档类型标签
DOC_TYPE_TAGS = {
    "annotation": ["注疏解读", "文化比较"],
    "roundtable": ["圆桌会议纪要", "文化比较"],
    "review": ["文献综述", "文化比较"],
    "default": ["论语研究"]
}

# 学派标签
SCHOOL_TAGS = {
    "confucian": ["儒家", "诸子百家"],
    "daoist": ["道家", "诸子百家"],
    "mohist": ["墨家", "诸子百家"],
    "legalist": ["法家", "诸子百家"],
    "western": ["西方哲学"],
}


# ========================================
# 凭证管理
# ========================================

def load_credentials() -> Dict[str, str]:
    """从 ~/.openclaw/openclaw.json 加载 Get笔记 API 凭证"""
    openclaw_path = Path.home() / ".openclaw" / "openclaw.json"

    if not openclaw_path.exists():
        return {"api_key": "", "client_id": ""}

    try:
        with open(openclaw_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        skills = data.get("skills", {})
        getnote = skills.get("entries", {}).get("getnote", {})
        env = getnote.get("env", {})
        return {
            "api_key": getnote.get("apiKey", ""),
            "client_id": env.get("GETNOTE_CLIENT_ID", "") or getnote.get("clientId", "")
        }
    except Exception:
        return {"api_key": "", "client_id": ""}


def check_credentials() -> bool:
    """检查凭证是否有效"""
    creds = load_credentials()
    return bool(creds.get("api_key"))


# ========================================
# API 请求
# ========================================

def api_request(method: str, endpoint: str, data: Dict = None,
                retry: int = 3) -> Dict[str, Any]:
    """发送 API 请求到 Get笔记

    Args:
        method: HTTP 方法 (GET/POST)
        endpoint: API 端点
        data: 请求体数据
        retry: 重试次数

    Returns:
        API 响应字典
    """
    creds = load_credentials()
    api_key = creds.get("api_key", "")
    client_id = creds.get("client_id", "")

    if not api_key:
        return {"success": False, "error": {"message": "API Key 未配置", "reason": "not_configured"}}

    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key,
        "X-Client-ID": client_id
    }

    payload = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None

    for attempt in range(retry):
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers=headers,
                method=method
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                # 处理大整数 ID：64位转字符串
                safe = re.sub(r'"(id|note_id|next_cursor|parent_id|follow_id|live_id)"\s*:\s*(\d+)',
                              r'"\1":"\2"', raw)
                return json.loads(safe)
        except urllib.error.HTTPError as e:
            if attempt < retry - 1:
                time.sleep(1 * (attempt + 1))
                continue
            return {"success": False, "error": {"message": f"HTTP错误: {e.code}"}}
        except urllib.error.URLError as e:
            if attempt < retry - 1:
                time.sleep(1 * (attempt + 1))
                continue
            return {"success": False, "error": {"message": f"网络错误: {e.reason}"}}
        except Exception as e:
            return {"success": False, "error": {"message": str(e)}}

    return {"success": False, "error": {"message": "重试次数耗尽"}}


# ========================================
# 笔记操作
# ========================================

def save_note(title: str, content: str, tags: List[str] = None,
              note_type: str = "plain_text") -> Dict[str, Any]:
    """保存笔记到 Get笔记

    Args:
        title: 笔记标题
        content: 笔记内容（Markdown）
        tags: 标签列表
        note_type: 笔记类型 (plain_text/link/img_text)

    Returns:
        包含 note_id 的响应字典
    """
    payload = {
        "title": title,
        "content": content,
        "note_type": note_type,
        "tags": tags or [],
        "parent_id": 0
    }

    result = api_request("POST", "/open/api/v1/resource/note/save", payload)

    if result.get("success"):
        note_id = result.get("data", {}).get("note_id", "")
        if isinstance(note_id, int):
            note_id = str(note_id)
        return {
            "success": True,
            "note_id": note_id,
            "title": title
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "保存失败")
        }


def add_tags_to_note(note_id: str, tags: List[str]) -> Dict[str, Any]:
    """为笔记添加标签

    Args:
        note_id: 笔记 ID
        tags: 标签列表

    Returns:
        操作结果
    """
    if isinstance(note_id, int):
        note_id = str(note_id)

    payload = {
        "note_id": note_id,
        "tags": tags
    }

    result = api_request("POST", "/open/api/v1/resource/note/tags/add", payload)

    if result.get("success"):
        return {
            "success": True,
            "note_id": note_id,
            "tags_added": tags
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "添加标签失败")
        }


def add_note_to_knowledge_base(note_id: str, topic_id: str = LUNYU_KB_ID) -> Dict[str, Any]:
    """将笔记添加到知识库

    Args:
        note_id: 笔记 ID
        topic_id: 知识库 ID

    Returns:
        操作结果
    """
    if isinstance(note_id, int):
        note_id = str(note_id)

    payload = {
        "topic_id": topic_id,
        "note_ids": [note_id]
    }

    result = api_request("POST", "/open/api/v1/resource/knowledge/note/batch-add", payload)

    if result.get("success"):
        return {
            "success": True,
            "note_id": note_id,
            "topic_id": topic_id
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "添加到知识库失败")
        }


# ========================================
# 高级操作
# ========================================

def save_docx_to_getnote(title: str, docx_content: str, doc_type: str = "default",
                         school_tags: List[str] = None,
                         chapter_id: str = "") -> Dict[str, Any]:
    """保存 docx 内容到 Get笔记并添加到知识库（完整流程）

    Args:
        title: 文档标题
        docx_content: docx 文件的文本内容（从 markdown-converter 生成）
        doc_type: 文档类型 (annotation/roundtable/review/default)
        school_tags: 学派标签列表
        chapter_id: 章节 ID

    Returns:
        完整操作结果汇总
    """
    # 1. 构建标签（Get笔记限制：最多5个标签）
    tags = []
    tags.append("论语研究")  # 主题标签
    tags.append("文化比较")  # 类型标签
    
    if school_tags and school_tags[0] in ["儒家", "道家", "墨家", "法家"]:
        tags.append(school_tags[0])  # 学派标签
    elif doc_type in DOC_TYPE_TAGS and DOC_TYPE_TAGS[doc_type][0] not in tags:
        tags.append(DOC_TYPE_TAGS[doc_type][0])  # 注疏/圆桌/综述
    
    if len(tags) < 5 and chapter_id:
        tags.append(chapter_id)

    # 2. 保存笔记
    save_result = save_note(title, docx_content, tags)
    if not save_result.get("success"):
        return {
            "success": False,
            "step": "save_note",
            "error": save_result.get("error")
        }

    note_id = save_result.get("note_id")

    # 3. 添加到知识库
    kb_result = add_note_to_knowledge_base(note_id, LUNYU_KB_ID)
    if not kb_result.get("success"):
        return {
            "success": True,  # 保存成功，知识库可能失败
            "note_id": note_id,
            "kb_warning": kb_result.get("error")
        }

    return {
        "success": True,
        "note_id": note_id,
        "topic_id": LUNYU_KB_ID,
        "tags": tags
    }


def get_lunyu_notes(page: int = 1, max_notes: int = 20) -> Dict[str, Any]:
    """获取【论语研究】知识库的笔记列表

    Args:
        page: 页码
        max_notes: 最大笔记数

    Returns:
        笔记列表
    """
    result = api_request("GET", f"/open/api/v1/resource/knowledge/notes?topic_id={LUNYU_KB_ID}&page={page}")

    if result.get("success"):
        notes = result.get("data", {}).get("notes", [])
        return {
            "success": True,
            "notes": notes[:max_notes],
            "total": result.get("data", {}).get("total", 0)
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "获取笔记失败")
        }


# ========================================
# 入口函数
# ========================================

def save_document(title: str, content: str, doc_type: str = "default",
                  school: str = None, chapter: str = "") -> Dict[str, Any]:
    """保存文档的简明入口

    Args:
        title: 文档标题
        content: 文档内容
        doc_type: 文档类型 (annotation/roundtable/review)
        school: 学派 (confucian/daoist/mohist/legalist/western)
        chapter: 章节 ID

    Returns:
        操作结果
    """
    # 构建学派标签
    school_tags = []
    if school and school in SCHOOL_TAGS:
        school_tags = SCHOOL_TAGS[school]

    return save_docx_to_getnote(title, content, doc_type, school_tags, chapter)


# ========================================
# 测试
# ========================================

if __name__ == "__main__":
    print("=== Get笔记集成模块测试 ===")
    print()

    # 检查凭证
    creds = load_credentials()
    if creds.get("api_key"):
        print(f"✓ 凭证已配置 (client_id: {creds.get('client_id', '')[:20]}...)")
    else:
        print("✗ 凭证未配置，请先运行 /note config")

    # 检查凭证状态
    if check_credentials():
        print("✓ 凭证有效")

        # 测试获取论语研究笔记
        print()
        print("尝试获取【论语研究】笔记...")
        result = get_lunyu_notes()
        if result.get("success"):
            print(f"✓ 知识库笔记数: {result.get('total', 0)}")
        else:
            print(f"✗ 获取失败: {result.get('error')}")
    else:
        print("✗ 凭证无效")
