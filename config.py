"""
配置檔案 - Configuration for Math Exam Generator Skill
"""

import os
from pathlib import Path

# Skill 基本信息
SKILL_NAME = "math_exam_generator"
SKILL_VERSION = "1.0.0"
SKILL_DESCRIPTION = "AI-powered elementary math exam generator for grades 1-3"

# 项目路径
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# 默认參數
DEFAULT_EXAM_TIME = {
    1: 45,  # 小一默认45分鐘
    2: 60,  # 小二默认60分鐘
    3: 60,  # 小三默认60分鐘
}

DEFAULT_DIFFICULTY = "中等"

# PDF 样式配置
PDF_FONT_SIZE = "14pt"
PDF_LINE_HEIGHT = 1.8
PDF_PAGE_SIZE = "A4"
PDF_MARGIN = "2cm"

# 调试模式
DEBUG_MODE = bool(os.getenv("DEBUG_MODE", "false").lower() == "true")

def ensure_output_dir():
    """确保輸出目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR
