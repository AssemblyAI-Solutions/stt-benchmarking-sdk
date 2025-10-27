# LLM Vibe Eval - Quick Reference

## What Is It?

**Vibe eval** uses state-of-the-art language models to provide qualitative assessments of transcription quality that complement quantitative metrics like WER.

- **Quantitative (WER)**: Tells you *how many* errors
- **Qualitative (Vibe)**: Tells you *how bad* those errors are

## Why Use It?

✅ **Context-aware**: Understands semantic meaning
✅ **Holistic**: Evaluates overall quality and usability
✅ **Specific feedback**: Provides actionable insights
✅ **Multi-model consensus**: Uses multiple LLMs for robust evaluation

## Quick Start

### 1. Set API Key

Create a `.env` file (recommended):

```bash
cp .env.example .env
# Edit .env and add: ASSEMBLYAI_API_KEY=your_actual_key_here
```

Or set environment variable directly:

```bash
export ASSEMBLYAI_API_KEY='your-key-here'
```

### 2. Basic Usage

```python
from stt_benchmarking import LLMEvaluator, Transcript

evaluator = LLMEvaluator()

result = evaluator.evaluate_and_score(
    reference=truth_transcript,
    hypothesis=vendor_transcript,
    vendor_name="Vendor A",
    file_identifier="audio_001"
)

print(f"Vibe Score: {result['vibe_score']}/10")
print(result['consolidation'])  # Detailed feedback
```

### 3. Compare Vendors

```python
from stt_benchmarking import evaluate_vendor_comparison

comparison = evaluate_vendor_comparison(
    evaluator=evaluator,
    reference=truth,
    vendor_transcripts={
        "Vendor A": vendor_a,
        "Vendor B": vendor_b,
        "Vendor C": vendor_c
    },
    file_identifier="audio_001"
)

print(comparison['comparison'])  # Ranking and analysis
```

## What You Get

### Vibe Score (1-10)

| Score | Quality | Description |
|-------|---------|-------------|
| 9-10 | Excellent | Minimal issues, production-ready |
| 7-8 | Good | Minor issues, acceptable for most uses |
| 5-6 | Acceptable | Notable issues, may need review |
| 3-4 | Poor | Significant issues, needs correction |
| 1-2 | Very Poor | Unusable, major problems |

### Qualitative Feedback

Example output:

```
CONSENSUS SCORE: 7.5/10

Areas of Agreement:
All evaluators agree that word accuracy is excellent (~95%) but
speaker diarization has occasional boundary errors.

Key Strengths:
- Excellent word-level transcription
- Good handling of technical terms
- Proper temporal alignment

Key Weaknesses:
- Speaker boundaries occasionally incorrect
- "Class" → "clash" error at 00:00
- Some utterances merged incorrectly

Specific Example:
At [00:05], two utterances were merged:
  Truth: Speaker A: "What is this?" | Speaker B: "Interesting"
  Vendor: Speaker A: "What is this interesting"

Recommendation:
Quality acceptable for general use but review needed for
applications requiring precise speaker attribution.
```

## Integration with Benchmarking

### Add to Existing Workflow

```python
# Standard benchmarking
benchmark = STTBenchmark()
results = benchmark.evaluate(truth, hypothesis)

# Add vibe score
evaluator = LLMEvaluator()
vibe_result = evaluator.evaluate_and_score(truth, hypothesis, "Vendor A", "audio_001")

# Combine
results['vibe_score'] = vibe_result['vibe_score']
```

### CSV Output

```csv
file,wer,cp_wer,vibe_score
audio_001.json,0.0234,0.0245,8.5
audio_002.json,0.0512,0.0534,6.0
audio_003.json,0.0187,0.0201,9.0
```

## Default Models

By default, vibe eval uses **3 LLMs**:

1. **Claude 4.5 Sonnet** - Best overall reasoning
2. **GPT-5** - Strong at pattern recognition
3. **Gemini 2.5 Pro** - Good multi-modal understanding

Plus **Claude 4.5** for final consolidation = **4 API calls total**

### Faster Option (1 model)

```python
evaluator = LLMEvaluator(
    evaluator_models=["claude-sonnet-4-5-20250929"]
)
# Only 1 API call per evaluation
```

## When to Use Vibe Eval

### ✅ Good Use Cases

- **Vendor selection**: Compare quality across providers
- **Quality assurance**: Identify problematic transcriptions
- **Edge case analysis**: Understand why some files have high WER
- **A/B testing**: Compare model versions
- **Representative sampling**: Evaluate subset of large dataset

### ❌ Not Recommended For

- **Every file in large datasets**: Too expensive
- **Real-time evaluation**: Too slow
- **Replacing quantitative metrics**: Use together, not instead
- **Deterministic scoring**: Results may vary slightly

## Cost Optimization

### Strategy 1: Selective Evaluation

Only evaluate files with issues:

```python
for filename, results in batch_results.items():
    if results['wer'] > 0.05:  # High WER
        vibe = evaluator.evaluate_and_score(...)
        results['vibe_score'] = vibe['vibe_score']
```

### Strategy 2: Sample-Based

Evaluate representative sample:

```python
import random

# Evaluate 10% of dataset
sample = random.sample(files, len(files) // 10)

for file in sample:
    vibe = evaluator.evaluate_and_score(...)
```

### Strategy 3: Single Model

Use one model instead of three:

```python
evaluator = LLMEvaluator(
    evaluator_models=["claude-sonnet-4-5-20250929"]
)
# 75% cost reduction
```

## Real-World Example

### Before Vibe Eval

```
Vendor A: WER=2.5%, CP-WER=2.8%
Vendor B: WER=2.3%, CP-WER=2.6%

Decision: Choose Vendor B (lower WER)
```

### After Vibe Eval

```
Vendor A:
  WER=2.5%, Vibe=8.5/10
  "Excellent speaker diarization, minor word errors"

Vendor B:
  WER=2.3%, Vibe=6.0/10
  "Good word accuracy but significant speaker merging issues.
   Multiple utterances combined incorrectly."

Decision: Choose Vendor A
  → Lower quantitative score but better real-world usability
```

## Configuration Options

### Full Configuration

```python
evaluator = LLMEvaluator(
    api_key="your-key",              # Or use env var
    evaluator_models=[               # Models for evaluation
        "claude-sonnet-4-5-20250929",
        "gpt-5",
        "gemini-2.5-pro"
    ],
    consolidator_model="claude-sonnet-4-5-20250929",  # Final summary
    max_tokens=4000                  # Response length
)
```

### Minimal Configuration

```python
# Uses defaults, reads API key from environment
evaluator = LLMEvaluator()
```

## Output Files

### Individual Evaluation

```python
result = evaluator.evaluate_and_score(...)

with open("vibe_eval_vendor_a.txt", "w") as f:
    f.write(f"Vibe Score: {result['vibe_score']}/10\n\n")
    f.write(result['consolidation'])
    f.write("\n\n")
    for model, eval_text in result['individual_evaluations'].items():
        f.write(f"=== {model} ===\n{eval_text}\n\n")
```

### Comparison

```python
comparison = evaluate_vendor_comparison(...)

with open("vendor_comparison.txt", "w") as f:
    f.write(comparison['comparison'])
```

## API Reference

### LLMEvaluator Class

```python
evaluator = LLMEvaluator(
    api_key=None,
    evaluator_models=None,
    consolidator_model="claude-sonnet-4-5-20250929",
    max_tokens=4000
)
```

**Methods:**
- `evaluate_and_score()` - Full evaluation with score extraction
- `evaluate_single()` - Get evaluations from multiple models
- `consolidate_evaluations()` - Combine evaluations into summary
- `extract_score()` - Extract numerical score from text

### Standalone Function

```python
evaluate_vendor_comparison(
    evaluator,
    reference,
    vendor_transcripts,
    file_identifier
)
```

## Examples

See `examples/llm_vibe_eval_example.py` for:
1. Single vendor evaluation
2. Multi-vendor comparison
3. Batch processing with vibe scores
4. Integration with standard benchmarking

## Troubleshooting

### No API Key

```
Error: AssemblyAI API key required
```

**Fix**: `export ASSEMBLYAI_API_KEY='your-key'`

### Rate Limiting

**Fix**: Add delays or use fewer models

```python
import time
for file in files:
    result = evaluator.evaluate_and_score(...)
    time.sleep(1)
```

### High Cost

**Fix**: Use selective evaluation or single model

## Complete Workflow Example

```python
from stt_benchmarking import STTBenchmark, BatchEvaluator, LLMEvaluator

# 1. Standard metrics
benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

for file in audio_files:
    batch.add_evaluation(file, truth, hypothesis)

# 2. Export quantitative results
batch.export_to_csv("results_quantitative.csv")

# 3. Add vibe eval for high-WER files
evaluator = LLMEvaluator()

for i, results in enumerate(batch.results):
    if results['wer'] > 0.05:  # Only problematic files
        vibe = evaluator.evaluate_and_score(
            truth,
            hypothesis,
            "Vendor A",
            batch.file_identifiers[i]
        )
        batch.results[i]['vibe_score'] = vibe['vibe_score']

# 4. Export combined results
batch.export_to_csv("results_with_vibe.csv")
```

## Summary

| Feature | Quantitative (WER) | Qualitative (Vibe) |
|---------|-------------------|-------------------|
| **Speed** | Fast (milliseconds) | Slow (seconds) |
| **Cost** | Free | API costs |
| **Deterministic** | Yes | Mostly |
| **Interpretability** | Requires expertise | Human-readable |
| **Use case** | All files | Sample/edge cases |
| **Complementary** | ← Use both together → |

**Best practice**: Use WER for all files, vibe eval for understanding quality issues.

## See Also

- **`LLM_VIBE_EVAL_GUIDE.md`**: Complete documentation
- **`examples/llm_vibe_eval_example.py`**: Working examples
- **`README.md`**: Main SDK docs
