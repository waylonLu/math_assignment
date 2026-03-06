# Math Exam Generator

AI 驱动的小学数学试卷生成器（小一至小三），支持自动生成 PDF 试卷与图表。

## 项目简介

本项目采用 **LLM 外置架构**，通过生成精准的提示词交由外部 LLM 生成题目内容，再由本系统负责 PDF 渲染与图表生成，实现高效、低成本的试卷自动化生成。

支持四种题型：计算题、选择题、应用题、图表题，以及三种自动图表：棒形图、时钟、数线。

## 技术架构

```
用户输入参数
    ↓
collect_parameters()   # 参数收集与验证
    ↓
generate_prompt()      # 生成 LLM 提示词
    ↓
外部 LLM               # 生成题目数据（JSON）
    ↓
generate_exam()        # PDF 渲染 + matplotlib 图表生成
    ↓
输出 PDF（试卷 + 答案卷）
```

**核心依赖：**
- `weasyprint` — HTML/CSS 转 PDF
- `matplotlib` — 自动生成图表
- 外部 LLM — 题目内容生成（不内置）

## 快速开始

```bash
pip install -r requirements.txt
```

```python
from skill import collect_parameters, generate_prompt, generate_exam

params = collect_parameters(grade=2, difficulty="中等")
prompt = generate_prompt(**params["parameters"])

# 调用外部 LLM 获取 problems...

result = generate_exam(grade=2, exam_time=60, difficulty="中等", problems=problems)
# 输出: result["exam_file"], result["answer_file"]
```

## 文件结构

```
├── skill.py            # 核心逻辑（参数收集、提示词生成、PDF 渲染）
├── knowledge_base.py   # 18 个知识点定义（3 个年级）
├── config.py           # PDF 样式与默认配置
├── skill_manifest.json # API 元数据
├── requirements.txt    # 依赖列表
└── output/             # 生成的 PDF 文件
```

## License

MIT
