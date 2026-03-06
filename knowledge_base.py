"""
知識點庫 - Knowledge Base for Math Topics
定義每個年級的知識點和題目類型
"""

# 年級知識點庫
KNOWLEDGE_BASE = {
    1: {  # 小一
        "年級名": "小一",
        "知識點": [
            {"id": 1, "name": "順數和倒數，奇數和偶數", "type": "number_concepts"},
            {"id": 2, "name": "加法（個位）", "type": "addition_single"},
            {"id": 3, "name": "加法（兩位數）", "type": "addition_double"},
            {"id": 4, "name": "減法（個位）", "type": "subtraction_single"},
            {"id": 5, "name": "減法（兩位數）", "type": "subtraction_double"},
            {"id": 6, "name": "加減混合（個位）", "type": "mixed_single"},
        ]
    },
    2: {  # 小二
        "年級名": "小二",
        "知識點": [
            {"id": 1, "name": "加法（三位數）", "type": "addition_triple"},
            {"id": 2, "name": "加法（多位數）", "type": "addition_multi"},
            {"id": 3, "name": "減法（三位數）", "type": "subtraction_triple"},
            {"id": 4, "name": "減法（多位數）", "type": "subtraction_multi"},
            {"id": 5, "name": "加減混合（多位數）", "type": "mixed_multi"},
            {"id": 6, "name": "乘法（個位）", "type": "multiplication_single"},
        ]
    },
    3: {  # 小三
        "年級名": "小三",
        "知識點": [
            {"id": 1, "name": "乘法（三位數）", "type": "multiplication_triple"},
            {"id": 2, "name": "除法（三位數）", "type": "division_triple"},
            {"id": 3, "name": "四則運算（三位數）", "type": "four_operations"},
            {"id": 4, "name": "時間（進階）", "type": "time_advanced"},
            {"id": 5, "name": "貨幣（進階）", "type": "money_advanced"},
            {"id": 6, "name": "棒形圖", "type": "bar_chart"},
        ]
    }
}

# 難度係數 (影響數值範圍和複雜度)
DIFFICULTY_SETTINGS = {
    "簡單": {
        "multiplier": 0.6,
        "word_problem_complexity": "low",
        "description": "基礎題目，數值較小"
    },
    "中等": {
        "multiplier": 1.0,
        "word_problem_complexity": "medium",
        "description": "標準難度"
    },
    "困難": {
        "multiplier": 1.5,
        "word_problem_complexity": "high",
        "description": "進階題目，數值較大，步驟較多"
    }
}

# 考試時間建議 (分鐘)
EXAM_TIME_SUGGESTIONS = {
    1: {"min": 30, "recommended": 45, "max": 60},
    2: {"min": 40, "recommended": 60, "max": 90},
    3: {"min": 45, "recommended": 60, "max": 90}
}

def get_grade_topics(grade):
    """獲取指定年級的知識點列表"""
    return KNOWLEDGE_BASE.get(grade, {}).get("知識點", [])

def get_grade_name(grade):
    """獲取年級名稱"""
    return KNOWLEDGE_BASE.get(grade, {}).get("年級名", f"小{grade}")

def get_difficulty_info(difficulty):
    """獲取難度設置"""
    return DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["中等"])

def get_time_suggestion(grade):
    """獲取考試時間建議"""
    return EXAM_TIME_SUGGESTIONS.get(grade, {"min": 30, "recommended": 60, "max": 90})

# 需要圖片的知識點類型
IMAGE_REQUIRED_TOPICS = {
    "bar_chart": {"name": "棒形圖", "chart_type": "bar"},
    "time_advanced": {"name": "時間", "chart_type": "clock"},
    "number_concepts": {"name": "數的概念", "chart_type": "number_line"},
}

def get_random_topics(grade, count=None):
    """隨機選擇指定年級的知識點
    
    Args:
        grade: 年級 (1, 2, 3)
        count: 要選擇的知識點數量，None則隨機選2-4個
    
    Returns:
        知識點類型列表
    """
    import random
    
    all_topics = get_grade_topics(grade)
    if not all_topics:
        return []
    
    # 如果沒有指定數量，隨機選2-4個
    if count is None:
        count = random.randint(2, min(4, len(all_topics)))
    
    # 確保count不超過可用知識點數量
    count = min(count, len(all_topics))
    
    # 隨機選擇
    selected = random.sample(all_topics, count)
    return [t["type"] for t in selected]

def requires_image(topic_type):
    """判斷知識點是否需要圖片
    
    Args:
        topic_type: 知識點類型
    
    Returns:
        bool: True 如果需要圖片
    """
    return topic_type in IMAGE_REQUIRED_TOPICS

def get_chart_type(topic_type):
    """獲取知識點對應的圖表類型
    
    Args:
        topic_type: 知識點類型
    
    Returns:
        str: 圖表類型或None
    """
    return IMAGE_REQUIRED_TOPICS.get(topic_type, {}).get("chart_type")
