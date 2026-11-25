# IoT Agent Security — Indirect Prompt Injection Benchmark

Benchmark đo **mức độ an toàn của LLM agent điều khiển IoT** (SmartCampus BMS) trước **Indirect Prompt Injection (IPI)**: kẻ tấn công không chạm vào prompt, chỉ chèn chỉ thị vào dữ liệu sự kiện (`event_data.description`) mà agent đọc khi ra quyết định điều khiển quạt, cửa, còi, cảnh báo.

Repo trả lời 3 câu hỏi:

1. **Benign**: khi không bị tấn công, agent xử lý sự cố đúng đến đâu? (BU)
2. **Attack**: payload trong dữ liệu cảm biến/sự kiện lừa được agent bao nhiêu lần, nhất là lừa nó **bỏ qua nguy hiểm thật**? (ASR, SUP)
3. **Defense**: chặn được không, và cái giá là gì? (SensorGuard)

---

## Kết quả chính (6 model, GT v2.2.0 STRICT)

| Model | BU ↑ | ASR ↓ | SUP ↓ | ASR + SensorGuard | BU + SensorGuard |
| :-- | :-: | :-: | :-: | :-: | :-: |
| Gemini 3.5 flash-lite (k=3) | 93.0 | 27.6 | 47.3 | 4.9 | 97.0 |
| GPT-5.6 luna | 92.0 | 12.6 | 29.5 | 0.8 | 94.0 |
| GPT-6 luna (k=2) | 92.0 | 6.9 | 18.2 | 0.4 | 94.0 |
| Claude Haiku 5.5 | 84.0 | 11.8 | 30.7 | 0.4 | 94.0 |
| DeepSeek flash | 92.0 | 2.8 | 6.8 | 0.4 | 94.0 |
| GLM 5.3 flash | 86.0 | 4.3 | 8.0 | 0.8 | 93.0 |

**Phát hiện:**
- **Safety Suppression là lỗ hổng chính**: 59–91% số ca bị hack thuộc nhóm SUP (giả "diễn tập", "đã xử lý"... để agent không báo động khi có khói, CO2 cao, quẹt thẻ trái phép).
- **Model "hữu ích" nhất không phải model an toàn nhất**: Gemini có BU cao nhất nhưng ASR/SUP tệ nhất.
- **SensorGuard** (luật cố định đối chiếu hành động với cảm biến, không gọi LLM) đưa SUP về 0 ở 5/6 model và **tăng** BU 2–10 điểm, đổi lại 1–13 alert thêm mỗi 100 ca benign, báo giả ~0.
- **Clean twin** tách lỗi do tấn công khỏi lỗi vốn có của model: chạy lại cùng ca SUP chỉ bỏ chỉ thị (P) hoặc bỏ cả bối cảnh giả (Z).

Chi tiết: [BENCHMARK_RESULTS.md](benchmarkv2_refined/reports/BENCHMARK_RESULTS.md) · [DEFENSE_RESULTS.md](benchmarkv2_refined/reports/defense/DEFENSE_RESULTS.md) · [paper draft](benchmarkv2_refined/reports/paper/paper_draft.md)

## Chỉ số

| | Ý nghĩa |
| :-- | :-- |
| **BU** | Benign Utility: xử lý đúng khi không bị tấn công |
| **ASR** | Attack Success Rate |
| **SUP** | ASR của nhóm Safety Suppression (lừa bỏ qua/hạ cấp phản ứng bảo vệ) |
| **UA / MHR** | Utility under Attack / Missed Hazard Rate |
| **FDR** | Output hỏng định dạng, phải qua fallback parser |

## Bộ dữ liệu

| Track | Dataset | Số ca |
| :-- | :-- | :-: |
| Benign | `framework/benign/data/benign_100_testcases.json` | 100 |
| Benign held-out (đo báo giả của guard) | `framework/benign/data/benign_heldout_guard_testcases.json` | 36 |
| Attack advanced | `framework/attack_advanced/data/advanced_attack_testcases.json` | 254 (SUP 88, DH-A 100, DH-S 36, DS 30) |
| Clean twin | `framework/attack_advanced/data/clean_twin_sup_*.json` | 88 (P) + 12 (Z) |

Môi trường: 5 phòng, 24h telemetry seed vào PostgreSQL/pgvector, RAG qua SOP campus. Ground truth: [`framework/ground_truth/`](benchmarkv2_refined/framework/ground_truth/).

## Cấu trúc

```
benchmarkv2_refined/
├── framework/
│   ├── benign/            # dataset, runner, evaluator track benign
│   ├── attack_basic/      # bộ tấn công v1
│   ├── attack_advanced/   # bộ tấn công chính + clean twin
│   ├── defense/           # SensorGuard, replay offline, burden
│   └── ground_truth/      # GT v2.2.0 + evaluator STRICT
├── models/<model>/        # raw_runs.jsonl, eval, log theo từng model
└── reports/               # kết quả tổng hợp, defense, paper
app/                       # agent ReAct dưới test (FastAPI, tools, RAG, LLM providers)
```

## Chạy

```bash
cp .env.example .env              # điền API key của provider
docker compose up -d db           # PostgreSQL + pgvector
python -m app.script.ingest       # nạp SOP + tạo bảng (chạy trước seed)
python benchmark_v2/env/seed_environment.py

# Benign
python -m benchmarkv2_refined.framework.benign.runner.run_benign \
  --provider gemini --model gemini-3.5-flash-lite --defense none

# Attack
python -m benchmarkv2_refined.framework.attack_advanced.runner.run_advanced_attack \
  --provider gemini --model gemini-3.5-flash-lite --defense none   # none | prompt | guard | full
```

Provider hỗ trợ: `gemini`, `openai`, `anthropic`, `deepseek`, `zhipu`, `ollama`. Hướng dẫn đầy đủ (k=3, Ollama local): [HUONG_DAN_CHAY_LOCAL_OLLAMA_K3.md](benchmarkv2_refined/reports/summary_report/HUONG_DAN_CHAY_LOCAL_OLLAMA_K3.md).
