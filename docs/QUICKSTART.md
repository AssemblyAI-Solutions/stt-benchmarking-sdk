# Quick Start Guide

## Installation

1. Clone or navigate to the project directory
2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install the package in development mode:

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Basic Usage

### 1. Simple Evaluation

```python
from stt_benchmarking import STTBenchmark

# Initialize
benchmark = STTBenchmark()

# Your data
reference = [
    {"speaker": "Alice", "text": "Hello world"},
    {"speaker": "Bob", "text": "How are you"}
]

hypothesis = [
    {"speaker": "spk_0", "text": "hello world"},
    {"speaker": "spk_1", "text": "how are you"}
]

# Evaluate
results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

print(f"WER: {results['wer']:.2%}")
print(f"CP-WER: {results['cp_wer']:.2%}")
```

### 2. With Timestamps (for DER)

```python
reference = [
    {"speaker": "Alice", "text": "Hello", "start_time": 0.0, "end_time": 1.0},
    {"speaker": "Bob", "text": "Hi", "start_time": 1.0, "end_time": 2.0}
]

hypothesis = [
    {"speaker": "spk_0", "text": "hello", "start_time": 0.0, "end_time": 1.0},
    {"speaker": "spk_1", "text": "hi", "start_time": 1.0, "end_time": 2.0}
]

results = benchmark.evaluate(reference, hypothesis)
print(f"DER: {results['der']:.2%}")
```

### 3. Check Speaker Mapping

```python
mapping = benchmark.get_speaker_mapping(reference, hypothesis)
print(mapping)  # e.g., {'spk_0': 'Alice', 'spk_1': 'Bob'}
```

## Key Features

### Automatic Text Normalization

By default, the SDK normalizes text using `whisper_normalizer`:

```python
# Enabled by default
benchmark = STTBenchmark(normalize=True)

# Disable if needed
benchmark = STTBenchmark(normalize=False)
```

### Automatic Speaker Matching

Speaker labels are automatically matched using fuzzy string matching:

```python
# Default threshold: 80%
benchmark = STTBenchmark(speaker_matching_threshold=80.0)

# More strict matching
benchmark = STTBenchmark(speaker_matching_threshold=90.0)

# Disable speaker matching
benchmark = STTBenchmark(match_speakers=False)
```

### Selective Metric Calculation

```python
# Only WER
results = benchmark.evaluate_wer_only(reference, hypothesis)

# Only diarization metrics (CP-WER and DER)
results = benchmark.evaluate_diarization_only(reference, hypothesis)

# Custom selection
results = benchmark.evaluate(
    reference,
    hypothesis,
    calculate_wer=True,
    calculate_cp_wer=True,
    calculate_der=False  # Skip DER if no timestamps
)
```

## Output Metrics

### WER Results
- `wer`: Word Error Rate
- `mer`: Match Error Rate
- `wil`: Word Information Lost
- `wip`: Word Information Preserved
- `substitutions`: Number of word substitutions
- `deletions`: Number of word deletions
- `insertions`: Number of word insertions
- `hits`: Number of correct words

### CP-WER Results
- `cp_wer`: Concatenated minimum-Permutation WER
- `total_errors`: Total errors across all speakers
- `total_reference_words`: Total words in reference

### DER Results (with timestamps)
- `der`: Diarization Error Rate
- `false_alarm`: False alarm rate
- `missed_detection`: Missed detection rate
- `confusion`: Speaker confusion rate
- `total`: Total DER

### DER Results (without timestamps)
- `speaker_error_rate`: Simplified speaker attribution error rate
- `speaker_errors`: Number of speaker attribution errors
- `total_words`: Total words evaluated

## Examples

Run the example scripts:

```bash
python examples/basic_usage.py
python examples/advanced_usage.py
```

## Data Format Requirements

### Minimum Required Fields
```python
{"speaker": "SpeakerName", "text": "Transcribed text"}
```

### With Timestamps (for DER)
```python
{
    "speaker": "SpeakerName",
    "text": "Transcribed text",
    "start_time": 0.0,  # seconds
    "end_time": 1.5     # seconds
}
```

## Exporting Results to CSV

### Single File Export

```python
from stt_benchmarking import ResultsExporter

results = benchmark.evaluate(reference, hypothesis)

ResultsExporter.to_csv(
    results,
    output_path="metrics.csv",
    file_identifiers="conversation_001.json"
)
```

### Multiple Files Export

```python
from stt_benchmarking import BatchEvaluator

# Create batch evaluator
batch = BatchEvaluator(benchmark)

# Add multiple evaluations
batch.add_evaluation("file1.json", reference1, hypothesis1, calculate_der=False)
batch.add_evaluation("file2.json", reference2, hypothesis2, calculate_der=False)
batch.add_evaluation("file3.json", reference3, hypothesis3, calculate_der=False)

# Export all to CSV
batch.export_to_csv("all_results.csv", precision=4)

# Get summary statistics
stats = batch.get_summary_stats()
print(f"Average WER: {stats['wer']['mean']:.2%}")
print(f"Min WER: {stats['wer']['min']:.2%}")
print(f"Max WER: {stats['wer']['max']:.2%}")
```

### Append to Existing CSV

```python
# First file - create new CSV
ResultsExporter.to_csv(results1, "metrics.csv", file_identifiers="file1.json", append=False)

# Additional files - append to existing CSV
ResultsExporter.to_csv(results2, "metrics.csv", file_identifiers="file2.json", append=True)
ResultsExporter.to_csv(results3, "metrics.csv", file_identifiers="file3.json", append=True)
```

## Common Use Cases

### Benchmarking Multiple Vendors

```python
from stt_benchmarking import BatchEvaluator

vendors = {
    "Vendor A": vendor_a_transcript,
    "Vendor B": vendor_b_transcript,
    "Vendor C": vendor_c_transcript,
}

benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

# Evaluate all vendors
for vendor_name, hypothesis in vendors.items():
    batch.add_evaluation(
        vendor_name,
        reference_transcript,
        hypothesis,
        calculate_der=False
    )

# Export comparison to CSV
batch.export_to_csv("vendor_comparison.csv")

# Display results
for vendor_name in vendors.keys():
    results = batch.results[list(vendors.keys()).index(vendor_name)]
    print(f"{vendor_name}: WER={results['wer']:.2%}, CP-WER={results['cp_wer']:.2%}")
```

### Different Speaker Label Conventions

The SDK handles different speaker naming conventions automatically:

```python
# Reference uses names
reference = [
    {"speaker": "Dr. Smith", "text": "..."},
    {"speaker": "Patient", "text": "..."}
]

# Hypothesis uses generic labels
hypothesis = [
    {"speaker": "speaker_0", "text": "..."},
    {"speaker": "speaker_1", "text": "..."}
]

# Automatically matched!
results = benchmark.evaluate(reference, hypothesis)
```

## Troubleshooting

### ImportError for meeteval or pyannote

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Speaker Matching Not Working

Try adjusting the threshold:
```python
# Lower threshold for more lenient matching
benchmark = STTBenchmark(speaker_matching_threshold=70.0)
```

### DER Calculation Fails

Ensure your transcripts have timestamps:
```python
# Check if timestamps exist
for utt in transcript:
    if utt.get('start_time') is None:
        print("Missing timestamps!")
```

Or disable DER calculation:
```python
results = benchmark.evaluate(reference, hypothesis, calculate_der=False)
```

## Next Steps

- See `README.md` for complete API documentation
- Check `examples/` for more detailed usage patterns
- Run tests: `pytest tests/`
