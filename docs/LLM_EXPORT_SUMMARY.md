# LLM Evaluation Export - Complete Guide

## Yes! Full LLM Descriptions/Rankings Are Included

The vibe score in the CSV is just a summary number. The **full LLM evaluations** (descriptions, rankings, feedback) are included in the results and can be exported in multiple formats.

## What You Get

### 1. In-Memory Results

```python
result = evaluator.evaluate_and_score(truth, hypothesis, "Vendor A", "audio_001")

# Result contains EVERYTHING:
{
    'vibe_score': 8.5,  # Number for CSV
    'consolidation': "CONSENSUS SCORE: 8.5/10\n\nAreas of Agreement...",  # Full summary
    'individual_evaluations': {
        'claude-sonnet-4-5-20250929': "Full detailed evaluation...",
        'gpt-5': "Full detailed evaluation...",
        'gemini-2.5-pro': "Full detailed evaluation..."
    }
}
```

### 2. CSV Export (Vibe Scores Only)

```csv
file,wer,cp_wer,vibe_score
meeting_001.json,0.0234,0.0245,8.5
meeting_002.json,0.0189,0.0201,7.8
```

**Why not full text in CSV?** LLM evaluations are multi-paragraph text (hundreds of words), not suitable for CSV columns.

### 3. Text/JSON Export (Full Descriptions)

The SDK provides **comprehensive export functions** for the full LLM feedback:

## Export Options

### Option 1: Automatic Export (Recommended)

Exports everything with one function call:

```python
from stt_benchmarking import export_llm_results_with_csv

# Run evaluations
llm_results = []
for file in audio_files:
    result = evaluator.evaluate_and_score(truth, hypothesis, vendor, file)
    llm_results.append({
        'vendor': vendor,
        'file': file,
        'vibe_score': result['vibe_score'],
        'consolidation': result['consolidation'],
        'individual_evaluations': result['individual_evaluations']
    })

# Export everything
export_llm_results_with_csv(
    csv_path="results.csv",
    llm_results=llm_results,
    output_dir="llm_evaluations"
)
```

**Creates:**
```
llm_evaluations/
├── audio_001_vendor_a_vibe_eval.txt       # Human-readable
├── audio_001_vendor_a_vibe_eval.json      # Machine-readable
├── audio_002_vendor_a_vibe_eval.txt
├── audio_002_vendor_a_vibe_eval.json
└── combined_vibe_eval_report.txt          # All evaluations in one file
```

### Option 2: Individual File Exports

For more control:

```python
from stt_benchmarking import LLMResultsExporter

exporter = LLMResultsExporter()

# Export as text file
exporter.to_text_file(
    result,
    "vendor_a_audio_001_vibe_eval.txt",
    vendor_name="Vendor A",
    file_identifier="audio_001"
)

# Export as JSON
exporter.to_json_file(
    result,
    "vendor_a_audio_001_vibe_eval.json",
    vendor_name="Vendor A",
    file_identifier="audio_001"
)

# Export as Markdown
exporter.to_markdown_file(
    result,
    "vendor_a_audio_001_vibe_eval.md",
    vendor_name="Vendor A",
    file_identifier="audio_001"
)
```

### Option 3: Batch Report

Create single report with all evaluations:

```python
# Combine multiple evaluations into one report
exporter.batch_to_text_report(
    results=llm_results,
    output_path="all_evaluations_report.txt",
    title="Vendor A - Complete Evaluation Report"
)
```

### Option 4: Comparison Export

Export vendor comparison:

```python
comparison = evaluate_vendor_comparison(evaluator, truth, {
    "Vendor A": vendor_a,
    "Vendor B": vendor_b
}, "audio_001")

exporter.comparison_to_text_file(
    comparison,
    "vendor_comparison_audio_001.txt"
)
```

## Example Output Files

### Text File (audio_001_vendor_a_vibe_eval.txt)

```
================================================================================
LLM VIBE EVAL: Vendor A - audio_001.json
================================================================================

📊 VIBE SCORE: 8.5/10

================================================================================
CONSOLIDATED EVALUATION (Multi-Model Consensus)
================================================================================

CONSENSUS SCORE: 8.5/10

Areas of Agreement:
All three evaluators agree that this transcription demonstrates excellent
word accuracy and perfect speaker diarization. The quality is suitable for
professional use.

Key Strengths:
- Perfect speaker identification (2 speakers correctly identified)
- Excellent word accuracy (~98%)
- Proper temporal alignment
- Numbers handled well ("fifteen percent" → "15 percent")

Key Weaknesses:
- Minor capitalization differences from ground truth
- Could improve punctuation for better readability

Specific Examples:
At [00:00], the transcription correctly identifies:
  Truth: CEO: "Let's discuss the quarterly results"
  Vendor: spk_0: "lets discuss the quarterly results"

The only difference is capitalization and apostrophe, which are handled
by normalization. The semantic meaning is perfectly preserved.

Recommendation:
This transcription quality is excellent and suitable for all professional
use cases including meeting minutes, analysis, and archival purposes.
The speaker diarization is flawless and word accuracy is outstanding.

================================================================================
INDIVIDUAL EVALUATION: CLAUDE-SONNET-4-5-20250929
================================================================================

Overall Quality Score: 8.5/10

This transcription demonstrates strong performance across all evaluation
criteria...

[Full detailed evaluation continues...]

================================================================================
INDIVIDUAL EVALUATION: GPT-5
================================================================================

[Full evaluation from GPT-5...]

================================================================================
INDIVIDUAL EVALUATION: GEMINI-2.5-PRO
================================================================================

[Full evaluation from Gemini...]
```

### JSON File (audio_001_vendor_a_vibe_eval.json)

```json
{
  "vendor": "Vendor A",
  "file": "audio_001.json",
  "vibe_score": 8.5,
  "consolidation": "CONSENSUS SCORE: 8.5/10\n\nAreas of Agreement...",
  "individual_evaluations": {
    "claude-sonnet-4-5-20250929": "Full evaluation text...",
    "gpt-5": "Full evaluation text...",
    "gemini-2.5-pro": "Full evaluation text..."
  }
}
```

### Combined Report (combined_vibe_eval_report.txt)

```
================================================================================
Batch LLM Evaluation Report
================================================================================

Total Files Evaluated: 5

SUMMARY OF VIBE SCORES
--------------------------------------------------------------------------------
audio_001.json                 Vendor A             8.5/10
audio_002.json                 Vendor A             7.8/10
audio_003.json                 Vendor A             9.0/10
audio_004.json                 Vendor A             6.5/10
audio_005.json                 Vendor A             8.2/10


################################################################################
EVALUATION 1/5
################################################################################

Vendor: Vendor A
File: audio_001.json
Vibe Score: 8.5/10

--------------------------------------------------------------------------------
CONSOLIDATED EVALUATION
--------------------------------------------------------------------------------

[Full evaluation for audio_001...]


################################################################################
EVALUATION 2/5
################################################################################

[Continue for all files...]
```

## Complete Workflow

```python
from stt_benchmarking import (
    STTBenchmark,
    BatchEvaluator,
    LLMEvaluator,
    export_llm_results_with_csv
)

# 1. Run quantitative benchmarking
benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

for file in audio_files:
    batch.add_evaluation(file, truth, hypothesis)

# 2. Run LLM evaluations
evaluator = LLMEvaluator()
llm_results = []

for file in audio_files:
    result = evaluator.evaluate_and_score(truth, hypothesis, "Vendor A", file)

    # Add vibe score to quantitative results
    batch.results[i]['vibe_score'] = result['vibe_score']

    # Store full result for export
    llm_results.append({
        'vendor': "Vendor A",
        'file': file,
        **result  # Includes vibe_score, consolidation, individual_evaluations
    })

# 3. Export CSV (quantitative + vibe scores)
batch.export_to_csv("vendor_a_results.csv")

# 4. Export full LLM evaluations (descriptions, rankings, feedback)
export_llm_results_with_csv(
    "vendor_a_results.csv",
    llm_results,
    "vendor_a_llm_evaluations"
)
```

## Output Structure

```
results/
├── vendor_a_results.csv                     # Numbers only
│
└── vendor_a_llm_evaluations/                # Full LLM feedback
    ├── audio_001_vendor_a_vibe_eval.txt     # Human-readable
    ├── audio_001_vendor_a_vibe_eval.json    # Machine-readable
    ├── audio_002_vendor_a_vibe_eval.txt
    ├── audio_002_vendor_a_vibe_eval.json
    ├── audio_003_vendor_a_vibe_eval.txt
    ├── audio_003_vendor_a_vibe_eval.json
    └── combined_vibe_eval_report.txt        # All in one
```

## File Format Comparison

| Format | Use Case | Contains |
|--------|----------|----------|
| **CSV** | Quick analysis, spreadsheets | Vibe score (number only) |
| **TXT** | Reading, documentation | Full evaluations, rankings, examples |
| **JSON** | Programmatic access | Structured data with all evaluations |
| **MD** | Documentation, GitHub | Formatted with headers and emphasis |
| **Combined Report** | Comprehensive review | All evaluations in single file |

## Accessing Results Programmatically

### From JSON Files

```python
import json

with open("audio_001_vendor_a_vibe_eval.json") as f:
    result = json.load(f)

print(f"Vibe Score: {result['vibe_score']}")
print(f"Consolidation:\n{result['consolidation']}")

for model, evaluation in result['individual_evaluations'].items():
    print(f"\n{model}:\n{evaluation}")
```

### From In-Memory Results

```python
# During evaluation
result = evaluator.evaluate_and_score(truth, hypothesis, "Vendor A", "audio_001")

# Immediate access to everything
print(result['vibe_score'])              # 8.5
print(result['consolidation'])           # "CONSENSUS SCORE: 8.5/10..."
print(result['individual_evaluations']) # Dict of full evaluations
```

## Summary

✅ **Vibe scores** → CSV (for spreadsheet analysis)
✅ **Full LLM descriptions/rankings** → TXT/JSON/MD files (for detailed review)
✅ **Automatic export** → One function call exports everything
✅ **Multiple formats** → Choose based on your needs
✅ **Programmatic access** → JSON format for code integration

The full LLM evaluations are **always included** in the results and can be exported in multiple formats alongside the CSV.

## See Also

- `examples/complete_workflow_with_llm.py` - Complete working example
- `LLM_VIBE_EVAL_GUIDE.md` - Full LLM evaluation documentation
- `README.md` - Main SDK documentation
