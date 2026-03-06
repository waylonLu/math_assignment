# Math Exam Generator

AI 驅動的小學數學試卷生成器（小一至小三），支援自動生成 PDF 試卷與圖表。

## 專案簡介

本專案採用 **LLM 外置架構**，透過生成精準的提示詞交由外部 LLM 生成題目內容，再由本系統負責 PDF 渲染與圖表生成，實現高效、低成本的試卷自動化生成。

支援四種題型：計算題、選擇題、應用題、圖表題，以及三種自動圖表：棒形圖、時鐘、數線。

## 技術架構

```
使用者輸入參數
    ↓
collect_parameters()   # 參數收集與驗證
    ↓
generate_prompt()      # 生成 LLM 提示詞
    ↓
外部 LLM               # 生成題目資料（JSON）
    ↓
generate_exam()        # PDF 渲染 + matplotlib 圖表生成
    ↓
輸出 PDF（試卷 + 答案卷）
```

**核心依賴：**
- `weasyprint` — HTML/CSS 轉 PDF
- `matplotlib` — 自動生成圖表
- 外部 LLM — 題目內容生成（不內建）

## 快速開始

```bash
pip install -r requirements.txt
```

```python
from skill import collect_parameters, generate_prompt, generate_exam

params = collect_parameters(grade=2, difficulty="中等")
prompt = generate_prompt(**params["parameters"])

# 呼叫外部 LLM 取得 problems...

result = generate_exam(grade=2, exam_time=60, difficulty="中等", problems=problems)
# 輸出: result["exam_file"], result["answer_file"]
```

## 檔案結構

```
├── skill.py            # 核心邏輯（參數收集、提示詞生成、PDF 渲染）
├── knowledge_base.py   # 18 個知識點定義（3 個年級）
├── config.py           # PDF 樣式與預設設定
├── skill_manifest.json # API 元資料
├── requirements.txt    # 依賴清單
└── output/             # 生成的 PDF 檔案
```

## License

MIT
