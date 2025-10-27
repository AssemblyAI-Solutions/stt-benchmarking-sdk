## LLM Vibe Eval Guide

Qualitative evaluation of transcription quality using state-of-the-art language models via AssemblyAI's LLM Gateway.

## Overview

**"Vibe eval"** uses LLMs to provide qualitative assessments of transcription quality that complement quantitative metrics like WER. While WER tells you *how many* errors there are, vibe eval tells you *how bad* those errors are and their impact on usability.

### Why Use Vibe Eval?

- **Context-aware**: LLMs understand semantic meaning, not just word matching
- **Holistic assessment**: Evaluates overall quality, readability, and usability
- **Specific feedback**: Provides actionable insights and examples
- **Multi-model consensus**: Uses multiple LLMs for robust evaluation

### What You Get

- **Vibe Score**: 1-10 rating of overall transcription quality
- **Qualitative feedback**: Strengths, weaknesses, specific examples
- **Comparative rankings**: When comparing multiple vendors
- **Actionable insights**: Recommendations for improvement

## Setup

### 1. Get AssemblyAI API Key

Sign up at https://www.assemblyai.com to get your API key.

### 2. Configure Environment Variables

The SDK uses a `.env` file to securely store your API key (never commit this file to git):

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# .env should contain:
# ASSEMBLYAI_API_KEY=your_actual_api_key_here
```

Alternatively, you can set the environment variable directly:

```bash
export ASSEMBLYAI_API_KEY='your-api-key-here'
```

### 3. Install SDK

```bash
pip install -e .  # Includes python-dotenv for .env support
```

The SDK automatically loads your API key from the `.env` file when you use `LLMEvaluator()`.

## Basic Usage

### Single Vendor Evaluation

```python
from stt_benchmarking import LLMEvaluator, Transcript

# Initialize evaluator
evaluator = LLMEvaluator()

# Load transcripts
truth = Transcript.from_list(truth_data)
hypothesis = Transcript.from_list(vendor_data)

# Run evaluation
result = evaluator.evaluate_and_score(
    reference=truth,
    hypothesis=hypothesis,
    vendor_name="Vendor A",
    file_identifier="audio_001"
)

print(f"Vibe Score: {result['vibe_score']}/10")
print(result['consolidation'])
```

### Multiple Vendor Comparison

```python
from stt_benchmarking import LLMEvaluator, evaluate_vendor_comparison

evaluator = LLMEvaluator()

comparison = evaluate_vendor_comparison(
    evaluator=evaluator,
    reference=truth,
    vendor_transcripts={
        "Vendor A": vendor_a_transcript,
        "Vendor B": vendor_b_transcript,
        "Vendor C": vendor_c_transcript
    },
    file_identifier="audio_001"
)

print(comparison['comparison'])
print(f"Vendor scores: {comparison['vendor_scores']}")
```

## Configuration

### Evaluator Models

By default, three models evaluate each transcript:
- **Claude 4.5 Sonnet** (claude-sonnet-4-5-20250929)
- **GPT-5** (gpt-5)
- **Gemini 2.5 Pro** (gemini-2.5-pro)

Customize:

```python
evaluator = LLMEvaluator(
    evaluator_models=[
        "claude-sonnet-4-5-20250929",
        "gpt-5"
    ],  # Use only these two
    consolidator_model="claude-sonnet-4-5-20250929",  # For final summary
    max_tokens=4000  # Maximum response length
)
```

### Single Model (Faster)

For quick evaluation, use just one model:

```python
evaluator = LLMEvaluator(
    evaluator_models=["claude-sonnet-4-5-20250929"]
)
```

## Integration with Benchmarking

### Add Vibe Scores to CSV

```python
from stt_benchmarking import STTBenchmark, BatchEvaluator, LLMEvaluator

# Standard benchmarking
benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

# Process files
for filename, truth, hypothesis in dataset:
    results = batch.add_evaluation(filename, truth, hypothesis)

# Add vibe scores
evaluator = LLMEvaluator()

for i, (filename, truth, hypothesis) in enumerate(dataset):
    vibe_result = evaluator.evaluate_and_score(
        reference=truth,
        hypothesis=hypothesis,
        vendor_name="Vendor A",
        file_identifier=filename
    )

    # Add vibe score to results
    batch.results[i]['vibe_score'] = vibe_result['vibe_score']

# Export with vibe scores
batch.export_to_csv("results_with_vibe_scores.csv")
```

### Batch Processing

```python
# Get vibe scores for all files
vibe_scores = []

for filename in audio_files:
    truth = load_truth(filename)
    hypothesis = load_vendor(filename)

    result = evaluator.evaluate_and_score(
        reference=Transcript.from_list(truth),
        hypothesis=Transcript.from_list(hypothesis),
        vendor_name="Vendor A",
        file_identifier=filename
    )

    vibe_scores.append({
        'file': filename,
        'vibe_score': result['vibe_score']
    })

# Calculate average
avg_vibe = sum(s['vibe_score'] for s in vibe_scores) / len(vibe_scores)
print(f"Average vibe score: {avg_vibe:.1f}/10")
```

## Output Examples

### Vibe Score

A single number from 1-10:
- **9-10**: Excellent quality, minimal issues
- **7-8**: Good quality, minor issues
- **5-6**: Acceptable quality, notable issues
- **3-4**: Poor quality, significant issues
- **1-2**: Very poor quality, unusable

### Consolidation Text

Example output:

```
CONSENSUS SCORE: 7.5/10

Areas of Agreement:
All three evaluators agree that the transcription achieves high word accuracy
(~95% correct) but struggles with speaker diarization. The vendor correctly
identified 2 speakers but merged some utterances incorrectly.

Key Strengths:
- Excellent word-level transcription accuracy
- Proper handling of technical terminology
- Good temporal alignment

Key Weaknesses:
- Speaker boundaries occasionally incorrect
- "Class" transcribed as "clash" in one instance
- Some utterances attributed to wrong speaker

Specific Example:
At timestamp [00:05], the vendor merged two distinct utterances:
  Truth: Speaker A: "What is photosynthesis?" | Speaker B: "That's interesting"
  Vendor: Speaker A: "What is photosynthesis that's interesting"

Recommendation:
This transcription quality is acceptable for general-purpose applications but
may require review for use cases where precise speaker attribution is critical.
The word accuracy is strong enough for search and analysis purposes.
```

### Comparison Output

When comparing vendors:

```
VENDOR COMPARISON - audio_001

Overall Rankings:
1st Place: Vendor A (Score: 8.5/10)
2nd Place: Vendor B (Score: 6.5/10)
3rd Place: Vendor C (Score: 5.0/10)

Vendor A Strengths:
- Best speaker diarization accuracy
- Excellent handling of overlapping speech
- Strong word accuracy across all speakers

Vendor B Strengths:
- Good word accuracy
- Better than Vendor C at speaker identification

Vendor C Weaknesses:
- Significant speaker merging issues
- Several transcription errors ("photosynthesis" → "photo sin thesis")
- Poor handling of multiple speakers

Recommendation:
For this educational content with clear speaker turns, Vendor A provides
the best overall quality. Vendor B is acceptable if cost is a concern.
Vendor C requires too much manual correction to be practical.
```

## Cost Considerations

### API Usage

- Each evaluation calls multiple LLMs (default: 3 models)
- Consolidation makes 1 additional call
- **Total per file**: 4 LLM API calls

### Recommendations

**For large datasets:**
- Use single model mode (1 call per file)
- Sample files for vibe eval (e.g., 10% of dataset)
- Focus vibe eval on edge cases identified by high WER

**Example: Selective vibe eval**

```python
# Only run vibe eval on files with WER > 5%
for filename, results in batch_results.items():
    if results['wer'] > 0.05:
        # High WER - worth deeper investigation
        vibe_result = evaluator.evaluate_and_score(truth, hypothesis, ...)
        results['vibe_score'] = vibe_result['vibe_score']
```

## Use Cases

### 1. Vendor Selection

Compare vendors qualitatively:

```python
comparison = evaluate_vendor_comparison(
    evaluator, truth,
    {"Vendor A": a, "Vendor B": b, "Vendor C": c},
    "sample_audio"
)

# Use LLM's recommendation to guide vendor choice
print(comparison['comparison'])
```

### 2. Quality Assurance

Identify problematic transcriptions:

```python
threshold = 6.0  # Minimum acceptable vibe score

for file, score in vibe_scores.items():
    if score < threshold:
        print(f"⚠️  {file}: Low quality ({score}/10) - needs review")
```

### 3. Error Analysis

Get specific feedback on errors:

```python
result = evaluator.evaluate_and_score(truth, hypothesis, ...)

# LLM provides specific examples of errors
print(result['consolidation'])  # Shows concrete problems
```

### 4. A/B Testing

Compare model versions:

```python
old_model_score = evaluator.evaluate_and_score(truth, old_model, ...)
new_model_score = evaluator.evaluate_and_score(truth, new_model, ...)

if new_model_score['vibe_score'] > old_model_score['vibe_score']:
    print("New model is better!")
```

## Best Practices

### 1. Combine with Quantitative Metrics

Don't use vibe eval alone - combine with WER:

```csv
file,wer,cp_wer,vibe_score
audio_001.json,0.0234,0.0245,8.5
audio_002.json,0.0512,0.0534,6.0
```

### 2. Use Representative Samples

For large datasets, evaluate a representative sample:
- Different speakers
- Various audio conditions
- Different content types

### 3. Save Full Evaluations

Save the complete LLM output, not just scores:

```python
with open(f"evaluations/{filename}_vibe_eval.txt", "w") as f:
    f.write(result['consolidation'])
    f.write("\n\n")
    for model, eval_text in result['individual_evaluations'].items():
        f.write(f"=== {model} ===\n{eval_text}\n\n")
```

### 4. Interpret Scores in Context

- **Educational content**: Higher standards (aim for 8+)
- **Casual conversation**: More forgiving (6+ may be fine)
- **Medical/legal**: Critical accuracy needed (9+ required)

## Limitations

1. **Subjective**: Different LLMs may disagree slightly
2. **Context-dependent**: Score interpretation varies by use case
3. **Not deterministic**: Same input may yield slightly different scores
4. **API cost**: Can be expensive for large-scale evaluation
5. **Speed**: Slower than quantitative metrics

## Troubleshooting

### API Key Error

```
Error: AssemblyAI API key required
```

**Solution**: Set environment variable
```bash
export ASSEMBLYAI_API_KEY='your-key-here'
```

### Rate Limiting

```
Error: 429 Too Many Requests
```

**Solution**: Add delays or use fewer models
```python
import time

for file in files:
    result = evaluator.evaluate_and_score(...)
    time.sleep(1)  # Rate limit protection
```

### Timeout Errors

**Solution**: Reduce max_tokens or transcript length
```python
evaluator = LLMEvaluator(max_tokens=2000)  # Shorter responses
```

## Examples

See `examples/llm_vibe_eval_example.py` for:
- Single vendor evaluation
- Multi-vendor comparison
- Batch processing with vibe scores
- Integration with standard metrics

## API Reference

### LLMEvaluator

```python
evaluator = LLMEvaluator(
    api_key=None,                    # Defaults to env var
    evaluator_models=[...],          # Models for evaluation
    consolidator_model="...",        # Model for consolidation
    max_tokens=4000                  # Max response length
)
```

### Methods

**evaluate_and_score(reference, hypothesis, vendor_name, file_identifier)**
- Returns: Dict with `vibe_score`, `consolidation`, `individual_evaluations`

**evaluate_single(reference, hypothesis, vendor_name, file_identifier)**
- Returns: Dict with evaluations from each model

**call_llm(model, prompt)**
- Returns: LLM response text

### Standalone Function

**evaluate_vendor_comparison(evaluator, reference, vendor_transcripts, file_identifier)**
- Returns: Dict with `comparison`, `vendor_scores`, `file`

## See Also

- `examples/llm_vibe_eval_example.py`: Complete working example
- `README.md`: Main SDK documentation
- AssemblyAI LLM Gateway docs: https://www.assemblyai.com/docs
