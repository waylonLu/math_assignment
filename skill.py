"""
數學試卷生成器 Skill - Main Skill Class
這是一个符合 skill 標準的模塊化設計
"""

from typing import Dict, List, Optional, Union
import os
from datetime import datetime
from pathlib import Path
import base64
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非互動式後端
import matplotlib.pyplot as plt
from matplotlib import font_manager

from config import (
    SKILL_NAME, SKILL_VERSION, SKILL_DESCRIPTION,
    ensure_output_dir
)
from knowledge_base import (
    KNOWLEDGE_BASE,
    get_grade_topics,
    get_grade_name,
    get_difficulty_info,
    get_time_suggestion,
    get_random_topics,
    requires_image,
    get_chart_type
)
from weasyprint import HTML


class MathExamGeneratorSkill:
    """
    數學試卷生成器 Skill
    
    提供統一接口生成數學試卷。由外層 LLM 生成題目內容，
    Skill 負責參數驗證、提示詞生成和 PDF 輸出。
    """
    
    def __init__(self):
        """初始化 Skill"""
        self.skill_name = SKILL_NAME
        self.version = SKILL_VERSION
        self.description = SKILL_DESCRIPTION
        ensure_output_dir()
    
    def get_info(self) -> Dict:
        """獲取 Skill 信息"""
        return {
            "name": self.skill_name,
            "version": self.version,
            "description": self.description,
            "supported_grades": [1, 2, 3],
            "supported_difficulties": ["簡單", "中等", "困難"],
            "workflow": "parameter_collection -> prompt_generation -> llm_generation -> pdf_output"
        }
    
    def validate_params(
        self,
        grade: int,
        exam_time: int,
        difficulty: str,
        topics: List[str]
    ) -> Dict[str, Union[bool, str]]:
        """
        驗證參數
        
        Returns:
            {"valid": bool, "message": str}
        """
        # 驗證年級
        if grade not in [1, 2, 3]:
            return {"valid": False, "message": f"年級必须是 1, 2 或 3，當前值: {grade}"}
        
        # 驗證時間
        if not (1 <= exam_time <= 120):
            return {"valid": False, "message": f"考試時間必须在 1-120 分鐘之间，當前值: {exam_time}"}
        
        # 驗證難度
        if difficulty not in ["簡單", "中等", "困難"]:
            return {"valid": False, "message": f"難度必须是 '簡單', '中等' 或 '困難'，當前值: {difficulty}"}
        
        # 驗證知識點
        valid_topics = [t["type"] for t in get_grade_topics(grade)]
        invalid_topics = [t for t in topics if t not in valid_topics]
        if invalid_topics:
            return {"valid": False, "message": f" 無效的知識點: {invalid_topics}"}
        
        return {"valid": True, "message": "參數驗證通過"}
    
    def collect_parameters(
        self,
        grade: int = None,
        exam_time: int = None,
        difficulty: str = None,
        topics: List[str] = None
    ) -> Dict:
        """
        收集參數，如果缺少则返回需要詢問的問題
        
        Returns:
            {
                "complete": bool,
                "parameters": dict,  # 如果完整
                "questions": list    # 如果不完整
            }
        """
        questions = []
        
        if grade is None:
            questions.append({
                "field": "grade",
                "question": "請選擇年級",
                "options": [
                    {"value": 1, "label": "小一年級"},
                    {"value": 2, "label": "小二年級"},
                    {"value": 3, "label": "小三年級"}
                ]
            })
        
        if difficulty is None:
            questions.append({
                "field": "difficulty",
                "question": "請選擇難度",
                "options": [
                    {"value": "簡單", "label": "簡單"},
                    {"value": "中等", "label": "中等（推薦）"},
                    {"value": "困難", "label": "困難"}
                ]
            })
        
        if grade is not None and exam_time is None:
            suggestion = get_time_suggestion(grade)
            questions.append({
                "field": "exam_time",
                "question": f"請設置考試時間（建議 {suggestion['recommended']} 分鐘）",
                "type": "number",
                "default": suggestion["recommended"],
                "range": [suggestion["min"], suggestion["max"]]
            })
        
        if questions:
            return {
                "complete": False,
                "questions": questions
            }
        
        # 參數完整，使用預設值
        if exam_time is None:
            exam_time = get_time_suggestion(grade)["recommended"]
        
        # 如果未指定知識點，隨機選擇2-4個
        if topics is None or topics == []:
            topics = get_random_topics(grade)
        
        return {
            "complete": True,
            "parameters": {
                "grade": grade,
                "exam_time": exam_time,
                "difficulty": difficulty,
                "topics": topics
            }
        }
    
    def generate_prompt(
        self,
        grade: int,
        exam_time: int,
        difficulty: str,
        topics: List[str]
    ) -> Dict:
        """
        生成给外層 LLM 的 system prompt
        
        Returns:
            {
                "system_prompt": str,
                "user_prompt": str,
                "expected_format": dict,
                "num_problems": int
            }
        """
        grade_name = get_grade_name(grade)
        num_problems = max(10, min(30, exam_time // 3))
        problems_per_topic = max(1, num_problems // len(topics))
        
        # 檢查是否有需要圖片的知識點
        has_image_topics = any(requires_image(t) for t in topics)
        image_topics = [t for t in topics if requires_image(t)]
        
        # 獲取知識點詳情
        topic_details = []
        for topic_type in topics:
            topic_info = next(
                (t for t in get_grade_topics(grade) if t["type"] == topic_type),
                None
            )
            if topic_info:
                topic_detail = {
                    "name": topic_info["name"],
                    "count": problems_per_topic
                }
                if requires_image(topic_type):
                    topic_detail["requires_image"] = True
                    topic_detail["chart_type"] = get_chart_type(topic_type)
                topic_details.append(topic_detail)
        
        # 難度描述
        difficulty_desc = {
            "簡單": "基礎題目，數值較小（10以內），步驟簡單",
            "中等": "標準難度，數值適中（100以內），符合教學大綱",
            "困難": "進階題目，數值較大（1000以內），步驟較多，有綜合應用"
        }
        
        system_prompt = f"""你是一位专业的{grade_name}年級數學老師，擅長出题和教學。

你的任務是為{grade_name}年級學生生成數學試卷題目。

要求：
1. 嚴格符合{grade_name}年級的認知水平
2. 題目清晰準確，答案正確無誤
3. 題型多樣化：計算題、填空題、應用題、選擇題
4. 應用題要貼近學生生活，有趣味性
5. 選擇題要有4個選項，只有一個正確答案
6. 難度：{difficulty_desc.get(difficulty, '中等')}
"""
        
        topic_list = "\n".join([
            f"  - {t['name']}: {t['count']}道題" + 
            (f" (需要圖表: {t['chart_type']})" if t.get('requires_image') else "")
            for t in topic_details
        ])
        
        # 基本格式說明
        base_format = """
{{
    "problems": [
        {{
            "question": "題目內容（例如：5 + 3 = ）",
            "answer": "答案（例如：8）",
            "type": "calculation"  // 或 "word"（應用題）、"choice"（選擇題）
        }},
        {{
            "question": "選擇題內容",
            "answer": "A",  // 正確選項的字母
            "type": "choice",
            "options": [
                "選項A內容",
                "選項B內容",
                "選項C內容",
                "選項D內容"
            ]
        }}
    ]
}}
"""
        
        # 如果有需要圖片的知識點，添加圖表格式說明
        chart_format = """
        
對於需要圖表的題目（棒形圖、時間、數線等），請使用以下格式：
{{
    "question": "根據下圖回答問題...",
    "answer": "答案",
    "type": "chart",
    "chart_data": {{
        "type": "bar",  // bar(棒形圖), clock(時鐘), number_line(數線)
        "data": {{...}}  // 圖表數據，根據不同類型提供
    }}
}}

圖表數據格式說明：

1. 棒形圖 (bar):
{{
    "type": "bar",
    "data": {{
        "title": "圖表標題",
        "x_label": "X軸標籤",
        "y_label": "Y軸標籤",
        "categories": ["類別1", "類別2", "類別3"],
        "values": [10, 20, 15]
    }}
}}

2. 時鐘 (clock):
{{
    "type": "clock",
    "data": {{
        "hour": 3,
        "minute": 30
    }}
}}

3. 數線 (number_line):
{{
    "type": "number_line",
    "data": {{
        "start": 0,
        "end": 10,
        "highlight": [3, 7]  // 需要標記的數字
    }}
}}
""" if has_image_topics else ""
        
        user_prompt = f"""請生成以下題目：

年級：{grade_name}
難度：{difficulty}
考試時間：{exam_time}分鐘
总题數：{num_problems}道

知識點分佈：
{topic_list}

請以 JSON 格式返回，基本格式如下：{base_format}{chart_format}
注意事項：
- 計算題用 "__" 或 "=" 表示填空处
- 應用題要有完整情境和問題
- 答案要簡潔明確，带單位（如果需要）
- 題目要符合{grade_name}年級水平
- 對於需要圖表的知識點，必須提供 chart_data 欄位
"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "expected_format": {
                "problems": [
                    {
                        "question": "string",
                        "answer": "string",
                        "type": "calculation | word | chart | choice",
                        "options": ["A", "B", "C", "D"],  # 僅當 type="choice" 時需要
                        "chart_data": {  # 僅當 type="chart" 時需要
                            "type": "bar | clock | number_line",
                            "data": {}
                        }
                    }
                ]
            },
            "num_problems": num_problems,
            "metadata": {
                "grade": grade,
                "grade_name": grade_name,
                "difficulty": difficulty,
                "exam_time": exam_time,
                "topics": topics
            }
        }
    
    def _generate_chart_image(self, chart_data: Dict) -> str:
        """
        使用 matplotlib 生成圖表並返回 base64 編碼的圖片
        
        Args:
            chart_data: 圖表數據，包含 type 和 data
        
        Returns:
            base64 編碼的圖片字符串
        """
        chart_type = chart_data.get("type")
        data = chart_data.get("data", {})
        
        # 配置中文字體
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        try:
            if chart_type == "bar":
                # 棒形圖
                categories = data.get("categories", [])
                values = data.get("values", [])
                title = data.get("title", "")
                x_label = data.get("x_label", "")
                y_label = data.get("y_label", "")
                
                ax.bar(categories, values, color='steelblue')
                ax.set_title(title, fontsize=28, fontweight='bold')
                ax.set_xlabel(x_label, fontsize=20)
                ax.set_ylabel(y_label, fontsize=20)
                ax.tick_params(axis='both', labelsize=18)
                ax.grid(axis='y', alpha=0.3)
                
            elif chart_type == "clock":
                # 時鐘
                hour = data.get("hour", 0)
                minute = data.get("minute", 0)
                
                # 繪製時鐘背景
                circle = plt.Circle((0.5, 0.5), 0.4, color='white', ec='black', linewidth=2)
                ax.add_patch(circle)
                
                # 繪製刻度（12點在上方，順時針）
                for i in range(12):
                    angle = 90 - i * 30  # 從12點開始（90度），順時針遞減
                    x = 0.5 + 0.35 * np.cos(np.radians(angle))
                    y = 0.5 + 0.35 * np.sin(np.radians(angle))
                    number = 12 if i == 0 else i
                    ax.text(x, y, str(number), ha='center', va='center', fontsize=26, fontweight='bold')
                
                # 繪製時針（從12點開始，順時針）
                hour_angle = 90 - ((hour % 12) + minute / 60) * 30
                hour_x = 0.5 + 0.2 * np.cos(np.radians(hour_angle))
                hour_y = 0.5 + 0.2 * np.sin(np.radians(hour_angle))
                ax.plot([0.5, hour_x], [0.5, hour_y], 'k-', linewidth=6)
                
                # 繪製分針（從12點開始，順時針）
                minute_angle = 90 - minute * 6
                minute_x = 0.5 + 0.3 * np.cos(np.radians(minute_angle))
                minute_y = 0.5 + 0.3 * np.sin(np.radians(minute_angle))
                ax.plot([0.5, minute_x], [0.5, minute_y], 'k-', linewidth=3)
                
                # 中心點
                ax.plot(0.5, 0.5, 'ko', markersize=8)
                
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_aspect('equal')
                ax.axis('off')
                
            elif chart_type == "number_line":
                # 數線
                start = data.get("start", 0)
                end = data.get("end", 10)
                highlight = data.get("highlight", [])
                
                # 繪製數線
                ax.plot([start, end], [0, 0], 'k-', linewidth=2)
                
                # 繪製刻度
                for i in range(start, end + 1):
                    ax.plot([i, i], [-0.1, 0.1], 'k-', linewidth=2)
                    ax.text(i, -0.3, str(i), ha='center', va='top', fontsize=24)
                
                # 突出顯示指定的數字
                for num in highlight:
                    if start <= num <= end:
                        ax.plot(num, 0, 'ro', markersize=15)
                
                ax.set_xlim(start - 1, end + 1)
                ax.set_ylim(-1, 1)
                ax.axis('off')
            
            # 將圖表轉換為 base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close(fig)
            
            return image_base64
            
        except Exception as e:
            plt.close(fig)
            # 生成錯誤提示圖片
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, f'圖表生成失敗:\n{str(e)}', ha='center', va='center', fontsize=14)
            ax.axis('off')
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close(fig)
            return image_base64
    
    def generate_exam_from_problems(
        self,
        grade: int,
        exam_time: int,
        difficulty: str,
        problems: List[Dict],
        output_dir: str = None
    ) -> Dict:
        """
        从外層 LLM 生成的題目數据生成 PDF 試卷
        
        Args:
            grade: 年級 (1, 2, 3)
            exam_time: 考試時間（分鐘）
            difficulty: 難度级别
            problems: 題目列表 [{"question": str, "answer": str, "type": str}]
            output_dir: 輸出目录，None 则使用默认目录
        
        Returns:
            {
                "success": bool,
                "exam_file": str,
                "answer_file": str,
                "metadata": dict,
                "message": str
            }
        """
        try:
            if not problems:
                return {
                    "success": False,
                    "message": "題目列表為空"
                }
            
            # 處理圖表題目，生成圖片
            for problem in problems:
                if problem.get("type") == "chart" and "chart_data" in problem:
                    # 生成圖表圖片
                    image_base64 = self._generate_chart_image(problem["chart_data"])
                    problem["image"] = image_base64
            
            # 生成 PDF
            output_path = Path(output_dir) if output_dir else ensure_output_dir()
            exam_file, answer_file = self._generate_pdf(
                grade, exam_time, difficulty, problems, output_path
            )
            
            # 元數据
            metadata = {
                "grade": grade,
                "grade_name": get_grade_name(grade),
                "exam_time": exam_time,
                "difficulty": difficulty,
                "num_problems": len(problems),
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "exam_file": str(exam_file),
                "answer_file": str(answer_file),
                "metadata": metadata,
                "message": f"✓ 成功生成試卷，共 {len(problems)} 道題目"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"生成失敗: {str(e)}"
            }
    
    def _generate_pdf(
        self,
        grade: int,
        exam_time: int,
        difficulty: str,
        problems: List[Dict],
        output_dir: Path
    ) -> tuple:
        """生成 PDF 檔案"""
        grade_name = get_grade_name(grade)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{grade_name}_{difficulty}_{exam_time}分鐘"
        
        # 生成試卷（無答案）
        html_content = generate_html_exam(grade, exam_time, difficulty, problems, False)
        exam_file = output_dir / f"{base_filename}_試卷_{timestamp}.pdf"
        HTML(string=html_content).write_pdf(str(exam_file))
        
        # 生成答案
        html_content_ans = generate_html_exam(grade, exam_time, difficulty, problems, True)
        answer_file = output_dir / f"{base_filename}_答案_{timestamp}.pdf"
        HTML(string=html_content_ans).write_pdf(str(answer_file))
        
        return exam_file, answer_file


def generate_html_exam(grade, exam_time, difficulty, problems, include_answers=False):
    """生成HTML試卷"""
    grade_name = get_grade_name(grade)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <title>{grade_name}年級數學試卷</title>
        <style>
            @page {{
                size: A4;
                margin: 2.5cm 2cm;
                @bottom-center {{
                    content: "第 " counter(page) " 頁，共 " counter(pages) " 頁";
                    font-size: 11pt;
                    font-family: 'SimSun', serif;
                }}
            }}
            body {{
                font-family: 'BiauKai', 'KaiTi', 'DFKai-SB', 'SimSun', 'STSong', serif;
                font-size: 15pt;
                line-height: 2;
                color: #000;
            }}
            .header {{
                text-align: center;
                margin-bottom: 15px;
            }}
            .title {{
                font-size: 26pt;
                font-family: 'SimHei', 'Microsoft YaHei', sans-serif;
                letter-spacing: 2px;
                font-weight: bold;
                margin-bottom: 15px;
            }}
            .subtitle {{
                font-size: 13pt;
                color: #333;
                margin-bottom: 20px;
            }}
            .student-info {{
                display: flex;
                justify-content: space-around;
                margin-bottom: 25px;
                font-size: 14pt;
            }}
            .score-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 35px;
                text-align: center;
                font-size: 13pt;
                font-family: 'SimHei', 'Microsoft YaHei', sans-serif;
            }}
            .score-table th, .score-table td {{
                border: 1px solid #000;
                padding: 10px;
            }}
            .score-table th {{
                font-weight: normal;
                height: 35px;
            }}
            .score-table td {{
                height: 50px;
            }}
            .section {{
                margin-bottom: 35px;
            }}
            .section-title {{
                font-size: 16pt;
                font-weight: bold;
                margin-bottom: 20px;
                font-family: 'SimHei', 'Microsoft YaHei', sans-serif;
            }}
            .problem {{
                margin-bottom: 25px;
                page-break-inside: avoid;
            }}
            .problem-number {{
                font-weight: bold;
                display: inline-block;
                width: 40px;
            }}
            .answer-line {{
                display: inline-block;
                min-width: 100px;
                border-bottom: 1px solid #000;
                margin: 0 10px;
            }}
            .chart-image {{
                max-width: 200px;
                max-height: 200px;
                margin: 0;
                display: block;
            }}
            .chart-problem-container {{
                display: flex;
                gap: 20px;
                align-items: flex-start;
            }}
            .chart-question-area {{
                flex: 1;
            }}
            .chart-image-area {{
                flex-shrink: 0;
            }}
            .answer {{
                color: #d32f2f;
                font-weight: bold;
            }}
            .choice-options-row {{
                margin-left: 40px;
                margin-top: 10px;
                margin-bottom: 10px;
                line-height: 2;
            }}
            .choice-option {{
                display: inline-block;
                margin-right: 35px;
                display: flex;
                align-items: center;
            }}
            .choice-label {{
                font-family: 'SimHei', 'Microsoft YaHei', sans-serif;
                margin-right: 5px;
                margin-left: 5px;
            }}
            .choice-text {{
                font-size: 14pt;
            }}
            .answer-circle {{
                display: inline-block;
                width: 24px;
                height: 24px;
                border: 2px solid #000;
                border-radius: 50%;
                margin-right: 2px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">{grade_name}年級數學學力檢測卷</div>
            <div class="subtitle">
                ( 考試時間：{exam_time} 分鐘 &nbsp;&nbsp;&nbsp;&nbsp;滿分：100 分 &nbsp;&nbsp;&nbsp;&nbsp;難度：{difficulty} )
            </div>
        </div>
        
        <div class="student-info">
            <span>學校：________________</span>
            <span>班級：______________</span>
            <span>姓名：______________</span>
            <span>學號：______________</span>
        </div>

        <table class="score-table">
            <tr>
                <th style="width: 15%;">題號</th>
                <th style="width: 17%;">一</th>
                <th style="width: 17%;">二</th>
                <th style="width: 17%;">三</th>
                <th style="width: 17%;">四</th>
                <th style="width: 17%;">總分</th>
            </tr>
            <tr>
                <td>得分</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
            </tr>
        </table>
    """
    
    # 按類型分組
    calc_problems = [p for p in problems if p['type'] == 'calculation']
    word_problems = [p for p in problems if p['type'] == 'word']
    choice_problems = [p for p in problems if p['type'] == 'choice']
    chart_problems = [p for p in problems if p.get('type') == 'chart']
    
    # 計算題
    if calc_problems:
        html += '<div class="section"><div class="section-title">一、計算題（每題5分）</div>'
        for i, p in enumerate(calc_problems, 1):
            html += f'<div class="problem"><span class="problem-number">{i}.</span>'
            html += f'<span>{p["question"]}'
            if not include_answers:
                html += '<span class="answer-line"></span>'
            else:
                html += f'<span class="answer">{p["answer"]}</span>'
            html += '</span></div>'
        html += '</div>'
    
    # 選擇題
    if choice_problems:
        html += '<div class="section"><div class="section-title">二、選擇題（每題5分）</div>'
        for i, p in enumerate(choice_problems, 1):
            html += f'<div class="problem"><span class="problem-number">{i}.</span>'
            html += f'<span>{p["question"]}</span><br>'
            
            # 顯示選項（帶空心圓圈，選項和字母）
            options = p.get('options', [])
            option_labels = ['A', 'B', 'C', 'D']
            
            # 使用 Flexbox 让选项横排
            html += '<div class="choice-options-row" style="display: flex; flex-wrap: wrap;">'
            for j, option in enumerate(options):
                label = option_labels[j] if j < len(option_labels) else str(j+1)
                
                # 如果是答案卷且是正确选项，改变圆圈样式
                circle_style = ""
                if include_answers and p["answer"] == label:
                    circle_style = 'background-color: #d32f2f; border-color: #d32f2f;'
                
                html += f'<span class="choice-option">'
                html += f'<span class="answer-circle" style="{circle_style}"></span>'
                html += f'<span class="choice-label">{label}.</span>'
                html += f'<span class="choice-text">{option}</span>'
                html += '</span>'
            html += '</div>'
            html += '</div>'
        html += '</div>'
    
    # 應用題
    if word_problems:
        section_number = '三' if choice_problems else '二'
        html += f'<div class="section"><div class="section-title">{section_number}、應用題（每題10分）</div>'
        for i, p in enumerate(word_problems, 1):
            html += f'<div class="problem"><span class="problem-number">{i}.</span>'
            html += f'<span>{p["question"]}</span><br>'
            if not include_answers:
                html += '<div style="margin-left: 40px; margin-top: 10px;">答：_______________________________</div>'
            else:
                html += f'<div style="margin-left: 40px; margin-top: 10px;"><span class="answer">答：{p["answer"]}</span></div>'
            html += '</div>'
        html += '</div>'
    
    # 圖表题
    if chart_problems:
        # 動態計算題號
        section_nums = ['一', '二', '三', '四', '五']
        section_count = sum([bool(calc_problems), bool(choice_problems), bool(word_problems)])
        section_number = section_nums[section_count] if section_count < len(section_nums) else str(section_count + 1)
        
        html += f'<div class="section"><div class="section-title">{section_number}、看圖答題（每題15分）</div>'
        for i, p in enumerate(chart_problems, 1):
            html += f'<div class="problem">'
            # 使用 flex 布局：左邊題目，右邊圖片
            html += '<div class="chart-problem-container">'
            html += '<div class="chart-question-area">'
            html += f'<div style="margin-bottom: 10px;"><span class="problem-number">{i}.</span><span>{p["question"]}</span></div>'
            if not include_answers:
                html += '<div style="margin-top: 10px; margin-left: 40px;">答：_______________________________</div>'
            else:
                html += f'<div style="margin-top: 10px; margin-left: 40px;"><span class="answer">答：{p["answer"]}</span></div>'
            html += '</div>'
            html += '<div class="chart-image-area">'
            html += f'<img src="data:image/png;base64,{p["image"]}" class="chart-image">'
            html += '</div>'
            html += '</div>'
            html += '</div>'
        html += '</div>'
    
    html += """
    </body>
    </html>
    """
    
    return html


# Skill 實例
_skill_instance = None

def get_skill() -> MathExamGeneratorSkill:
    """獲取 Skill 單例"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = MathExamGeneratorSkill()
    return _skill_instance


# Skill API（供外部调用）

def collect_parameters(**kwargs) -> Dict:
    """收集和驗證參數"""
    skill = get_skill()
    return skill.collect_parameters(**kwargs)


def generate_prompt(**kwargs) -> Dict:
    """生成 LLM 提示詞"""
    skill = get_skill()
    return skill.generate_prompt(
        kwargs["grade"],
        kwargs["exam_time"],
        kwargs["difficulty"],
        kwargs["topics"]
    )


def generate_exam(**kwargs) -> Dict:
    """从題目數据生成試卷 PDF"""
    skill = get_skill()
    return skill.generate_exam_from_problems(**kwargs)


def get_skill_info() -> Dict:
    """獲取 Skill 信息"""
    skill = get_skill()
    return skill.get_info()


def validate_params(**kwargs) -> Dict:
    """驗證參數"""
    skill = get_skill()
    return skill.validate_params(
        kwargs.get("grade"),
        kwargs.get("exam_time"),
        kwargs.get("difficulty"),
        kwargs.get("topics", [])
    )


def get_skill_info() -> Dict:
    """獲取 Skill 信息"""
    skill = get_skill()
    return skill.get_info()


def validate_params(**kwargs) -> Dict:
    """驗證參數"""
    skill = get_skill()
    return skill.validate_params(
        kwargs.get("grade"),
        kwargs.get("exam_time"),
        kwargs.get("difficulty"),
        kwargs.get("topics", [])
    )
