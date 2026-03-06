#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试：1. 图片放右边 2. 选择题圆圈只在答案区
"""

from skill import MathExamGeneratorSkill

print("=" * 70)
print("测试布局优化：图片右侧 + 圆圈仅在答案区")
print("=" * 70)

skill = MathExamGeneratorSkill()

test_problems = [
    # 计算题
    {"question": "34 + 56 = __", "answer": "90", "type": "calculation"},
    
    # 选择题 - 测试圆圈只在答案区
    {
        "question": "下列哪个数字是10的倍数？",
        "answer": "B",
        "type": "choice",
        "options": ["15", "20", "23", "37"]
    },
    {
        "question": "5 + 8 = ?",
        "answer": "C",
        "type": "choice",
        "options": ["11", "12", "13", "14"]
    },
    {
        "question": "一个正方形有几个角？",
        "answer": "D",
        "type": "choice",
        "options": ["1个", "2个", "3个", "4个"]
    },
    
    # 图表题 - 测试图片在右边
    {
        "question": "根据棒形图回答：哪种水果的数量最多？哪种最少？",
        "answer": "苹果最多，梨最少",
        "type": "chart",
        "chart_data": {
            "type": "bar",
            "data": {
                "title": "水果统计",
                "x_label": "种类",
                "y_label": "数量",
                "categories": ["苹果", "香蕉", "梨"],
                "values": [30, 20, 15]
            }
        }
    },
    {
        "question": "时钟显示的是什么时间？如果再过2小时是几点？",
        "answer": "4点整，再过2小时是6点",
        "type": "chart",
        "chart_data": {
            "type": "clock",
            "data": {
                "hour": 4,
                "minute": 0
            }
        }
    },
    {
        "question": "数线上有两个标记点，它们分别是哪两个数字？",
        "answer": "2和8",
        "type": "chart",
        "chart_data": {
            "type": "number_line",
            "data": {
                "start": 0,
                "end": 10,
                "highlight": [2, 8]
            }
        }
    },
    
    # 应用题
    {
        "question": "小明买了3本书，每本15元，一共花了多少钱？",
        "answer": "45元",
        "type": "word"
    }
]

print(f"\n📋 测试题目：")
print(f"  - 计算题: 1道")
print(f"  - 选择题: 3道")
print(f"  - 图表题: 3道 ⭐ 图片放右边，尺寸更小")
print(f"  - 应用题: 1道")

print(f"\n🎯 验证要点：")
print(f"  1. 选择题选项前面没有圆圈")
print(f"  2. 选择题答案区有A B C D四个圆圈")
print(f"  3. 学生可以在答案区圆圈中填涂")
print(f"  4. 图片显示在题目右侧")
print(f"  5. 图片尺寸更小（280px）")

print(f"\n📄 生成PDF...")
result = skill.generate_exam_from_problems(
    grade=2,
    exam_time=60,
    difficulty='中等',
    problems=test_problems
)

if result['success']:
    print(f"\n✅ 成功生成试卷")
    print(f"  试卷: {result['exam_file']}")
    print(f"  答案: {result['answer_file']}")
    
    print(f"\n🔍 请打开PDF检查：")
    print(f"  □ 选择题选项：A. ... B. ... C. ... D. ...（选项前无圆圈）")
    print(f"  □ 选择题答案区：答案：(A) (B) (C) (D)（四个圆圈）")
    print(f"  □ 答案卷：正确答案的圆圈被填充红色")
    print(f"  □ 图表题：图片在右边，题目在左边")
    print(f"  □ 图片尺寸：更小更紧凑（280px）")
else:
    print(f"\n✗ 生成失败: {result['message']}")

print("\n" + "=" * 70)
