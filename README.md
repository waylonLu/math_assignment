# Math Exam Generator Skill

AI 數學試卷生成器（小一至小三）- LLM 集成版本 + 智能圖表生成

## 🎯 設計理念

本 Skill 采用 **LLM 外置架构**，避免双重 LLM 调用：
- ✅ 外層 LLM 負責生成題目內容（含圖表數據）
- ✅ Skill 負責參數驗證、提示詞生成和 PDF 輸出
- ✅ **使用 matplotlib 自動生成圖表**（棒形圖、時鐘、數線）
- ✅ 高效、低成本、易集成

## ✨ 核心功能

- � **四種題型支持**：計算題、選擇題、應用題、圖表題
- ⭕ **選擇題優化**：橫向排列選項，圓圈設計便於塗答，答案卷自動填充
- 📊 **智能圖表生成**：根據知識點類型自動判斷是否需要圖表
- 🎨 **三種圖表類型**：棒形圖 (bar)、時鐘 (clock)、數線 (number_line)
- 🖼️ **圖片尺寸優化**：圖表大小適中（350px），版面更美觀
- 🤖 **動態Prompt**：自動在prompt中包含圖表格式說明
- 📄 **PDF混合輸出**：多種題型無縫整合
- ⏰ **時鐘精確顯示**：12點位置在正上方，數字位置準確

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt  # 包含 weasyprint 和 matplotlib
```

### 2. 使用流程

```python
from skill import collect_parameters, generate_prompt, generate_exam

# 步驟 1: 收集參數
params_result = collect_parameters(grade=2, difficulty="中等")

if not params_result["complete"]:
    # 參數不完整，詢問用户
    for question in params_result["questions"]:
        print(question["question"])
else:
    params = params_result["parameters"]
    
    # 步驟 2: 生成提示詞
    prompt_data = generate_prompt(**params)
    
    # 步驟 3: 调用外層 LLM 生成題目
    # problems = your_llm_call(prompt_data["system_prompt"], prompt_data["user_prompt"])
    
    # 步驟 4: 生成 PDF
    result = generate_exam(
        grade=params["grade"],
        exam_time=params["exam_time"],
        difficulty=params["difficulty"],
        problems=problems  # LLM 生成的題目數据
    )
```

## 📖 API 文档

### 1. collect_parameters()

收集和驗證用户输入參數，缺少參數时返回問題列表。

**參數：**
- `grade` (int, 可选): 年級 (1, 2, 3)
- `exam_time` (int, 可选): 考試時間（分鐘）
- `difficulty` (str, 可选): 難度（簡單/中等/困難）
- `topics` (list, 可选): 知識點列表（不提供則隨機選擇2-4個）

**返回：**
```python
{
    "complete": True/False,
    "parameters": {...},  # 如果完整
    "questions": [...]     # 如果不完整
}
```

### 2. generate_prompt()

根据參數生成 LLM 提示詞。

**參數：**
- `grade` (int): 年級
- `exam_time` (int): 考試時間
- `difficulty` (str): 難度
- `topics` (list): 知識點列表

**返回：**
```python
{
    "system_prompt": "...",      # System prompt（根據知識點智能調整）
    "user_prompt": "...",         # User prompt（包含圖表說明，如果需要）
    "expected_format": {...},     # 期望的 JSON 格式
    "num_problems": 20,           # 建議題目數
    "metadata": {...}             # 元數据
}
```

**圖表支持：**

當選擇的知識點需要圖表時（如棒形圖、時間等），prompt 會自動包含圖表數據格式說明：
- **棒形圖** (bar_chart): 需要提供類別和數值
- **時間** (time_advanced): 需要提供小時和分鐘
- **數的概念** (number_concepts): 需要提供數線數據

### 3. generate_exam()

从題目數据生成 PDF 檔案（自動處理圖表生成）。

**參數：**
- `grade` (int): 年級
- `exam_time` (int): 考試時間
- `difficulty` (str): 難度
- `problems` (list): 題目列表，支持四種類型：
  ```python
  [
      # 計算題
      {"question": "5 + 3 = ", "answer": "8", "type": "calculation"},
      
      # 選擇題（橫向排列，圓圈選項）
      {
          "question": "下列哪個數字最大？",
          "answer": "C",  # 答案為選項字母
          "type": "choice",
          "options": ["15", "23", "47", "31"]  # 4個選項
      },
      
      # 應用題
      {"question": "小明有...", "answer": "5個", "type": "word"},
      
      # 圖表題（含圖表數據，系統自動使用matplotlib生成圖片）
      {
          "question": "根據下圖回答：哪個數值最大？",
          "answer": "蘋果",
          "type": "chart",
          "chart_data": {
              "type": "bar",  # bar(棒形圖), clock(時鐘), number_line(數線)
              "data": {
                  "title": "水果銷售量",
                  "x_label": "水果",
                  "y_label": "數量",
                  "categories": ["蘋果", "香蕉", "橙子"],
                  "values": [25, 15, 20]
              }
          }
      }
  ]
  ```
- `output_dir` (str, 可选): 輸出目录

**返回：**
```python
{
    "success": True,
    "exam_file": "path/to/exam.pdf",
    "answer_file": "path/to/answer.pdf",
    "metadata": {...},
    "message": "✓ 成功生成試卷，共 20 道題目"
}
```

## 📚 知識點列表

**注意：** 知識點參數是可選的：
- ✅ 可以明確指定知識點列表
- ✅ 不指定則隨機選擇2-4個知識點
- ✅ 讓系統更靈活，適合快速生成試卷

### 小一年級
- `number_concepts` - 顺數和倒數，奇數和偶數 **[支持數線圖表]**
- `addition_single` - 加法（個位）
- `addition_double` - 加法（兩位數）
- `subtraction_single` - 减法（個位）
- `subtraction_double` - 减法（兩位數）
- `mixed_single` - 加减混合（個位）

### 小二年級
- `addition_triple` - 加法（三位數）
- `addition_multi` - 加法（多位數）
- `subtraction_triple` - 减法（三位數）
- `subtraction_multi` - 减法（多位數）
- `mixed_multi` - 加减混合（多位數）
- `multiplication_single` - 乘法（個位）

### 小三年級
- `multiplication_triple` - 乘法（三位數）
- `division_triple` - 除法（三位數）
- `four_operations` - 四则运算（三位數）
- `time_advanced` - 時間（進階）**[支持時鐘圖表]**
- `money_advanced` - 货币（進階）
- `bar_chart` - 棒形圖 **[支持棒形圖表]**

## 💡 使用示例

### 示例 1: 不指定知識點（隨機選擇）

```python
# 1. 收集參數（不指定topics，系統隨機選擇2-4個知識點）
params = collect_parameters(grade=2, difficulty="中等")

# 2. 生成提示詞
prompt = generate_prompt(**params["parameters"])

# 3. 调用 LLM（由外層系统完成）
# problems = llm.generate(prompt["system_prompt"], prompt["user_prompt"])

# 4. 生成 PDF
result = generate_exam(grade=2, exam_time=60, difficulty="中等", problems=problems)
```

### 示例 2: 指定知識點

```python
# 明確指定知識點列表
params = collect_parameters(
    grade=2, 
    difficulty="中等",
    topics=["addition_triple", "subtraction_triple"]  # 只考三位數加減法
)

prompt = generate_prompt(**params["parameters"])
# ...後續流程相同
```

### 示例 3: 生成包含圖表的試卷

```python
# 指定包含圖表的知識點
params = collect_parameters(
    grade=3, 
    difficulty="中等",
    topics=["bar_chart", "time_advanced"]  # 棒形圖和時間題
)

# 生成prompt（會自動包含圖表格式說明）
prompt = generate_prompt(**params["parameters"])

# LLM 返回包含圖表數據的題目
problems = [
    {
        "question": "根據下圖回答：哪種水果最多？",
        "answer": "蘋果",
        "type": "chart",
        "chart_data": {
            "type": "bar",
            "data": {
                "title": "水果數量",
                "x_label": "水果",
                "y_label": "數量",
                "categories": ["蘋果", "香蕉", "橙子"],
                "values": [25, 15, 20]
            }
        }
    }
]

# 生成PDF（圖表會自動生成並嵌入）
result = generate_exam(grade=3, exam_time=60, difficulty="中等", problems=problems)
```

### 示例 4: 參數不完整的处理

```python
result = collect_parameters(grade=3)  # 缺少其他參數

if not result["complete"]:
    for question in result["questions"]:
        print(f"{question['question']}")
        # 显示选项给用户選擇
```

## 📁 檔案结构

```
Math Assignment/
├── skill.py              # 主 Skill 类
├── config.py             # 配置檔案
├── knowledge_base.py     # 知識點库
├── skill_manifest.json   # Skill 清单
├── requirements.txt      # 依赖列表
└── README.md             # 文档说明
```

## ⚙️ 特性

- ✅ LLM 外置架构，避免双重调用
- ✅ 智能參數收集，缺少时自动提问
- ✅ 知識點可選，不指定則隨機選擇2-4個
- ✅ 动态提示詞生成，根據知識點類型智能調整
- ✅ **四種題型**：計算題、選擇題（橫向排列+圓圈設計）、應用題、圖表題
- ✅ **圖表自動生成**：使用 matplotlib 自動生成棒形圖、時鐘、數線等圖表
- ✅ **圖片尺寸優化**：圖表大小適中（350px），不會過大影響排版
- ✅ **時鐘精確顯示**：數字位置準確（12在上、3在右、6在下、9在左）
- ✅ **選擇題優化**：選項橫向排列，圓圈設計方便學生作答
- ✅ 专业 PDF 輸出，支持多種題型混合，排版美觀
- ✅ 支持 18 个知識點（3個需要圖表支持）

## 📄 License

MIT License
