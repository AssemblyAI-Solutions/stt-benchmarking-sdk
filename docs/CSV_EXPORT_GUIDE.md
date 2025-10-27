# CSV Export Guide

Complete guide for exporting STT benchmarking results to CSV files.

## Overview

The SDK provides two main classes for CSV export:
1. **ResultsExporter**: Low-level export functions
2. **BatchEvaluator**: High-level batch processing and export

## Quick Start

### Single File Export

```python
from stt_benchmarking import STTBenchmark, ResultsExporter

benchmark = STTBenchmark()
results = benchmark.evaluate(reference, hypothesis)

ResultsExporter.to_csv(
    results,
    output_path="metrics.csv",
    file_identifiers="conversation_001.json"
)
```

Output CSV:
```csv
file,wer,mer,wil,wip,cp_wer,hits,substitutions,deletions,insertions
conversation_001.json,0.0234,0.0156,0.0289,0.9711,0.0245,428,8,2,0
```

## ResultsExporter Class

### Method: `to_csv()`

Export single or multiple results to CSV.

**Parameters:**
- `results`: Single dict or list of dicts containing metrics
- `output_path`: Path to output CSV file (str or Path)
- `file_identifiers`: Optional identifier(s) for each result (str or list)
- `append`: If True, append to existing file (default: False)

**Examples:**

```python
# Single result
ResultsExporter.to_csv(
    results,
    "metrics.csv",
    file_identifiers="file1.json"
)

# Multiple results
ResultsExporter.to_csv(
    [results1, results2, results3],
    "metrics.csv",
    file_identifiers=["file1.json", "file2.json", "file3.json"]
)

# Auto-generate identifiers
ResultsExporter.to_csv(
    [results1, results2],
    "metrics.csv"
    # Uses "result_1", "result_2" as identifiers
)
```

### Method: `format_for_export()`

Format results with custom precision.

**Parameters:**
- `results`: Results dictionary
- `precision`: Number of decimal places (default: 4)

**Example:**

```python
formatted = ResultsExporter.format_for_export(results, precision=6)
ResultsExporter.to_csv(formatted, "metrics.csv")
```

## BatchEvaluator Class

Convenient class for evaluating multiple files and exporting results.

### Basic Usage

```python
from stt_benchmarking import STTBenchmark, BatchEvaluator

benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

# Add evaluations
batch.add_evaluation("file1.json", ref1, hyp1)
batch.add_evaluation("file2.json", ref2, hyp2)
batch.add_evaluation("file3.json", ref3, hyp3)

# Export all to CSV
batch.export_to_csv("results.csv", precision=4)
```

### Methods

#### `add_evaluation(file_identifier, reference, hypothesis, **eval_kwargs)`

Add an evaluation to the batch.

**Parameters:**
- `file_identifier`: Name/ID for this file (e.g., "conversation_001.json")
- `reference`: Reference transcript
- `hypothesis`: Hypothesis transcript
- `**eval_kwargs`: Additional args for `benchmark.evaluate()` (e.g., `calculate_der=False`)

**Returns:** Results dictionary

**Example:**

```python
results = batch.add_evaluation(
    "medical_call_001.json",
    reference,
    hypothesis,
    calculate_der=False,
    calculate_cp_wer=True
)
print(f"WER: {results['wer']:.2%}")
```

#### `export_to_csv(output_path, precision=4)`

Export all collected results to CSV.

**Parameters:**
- `output_path`: Path to output CSV file
- `precision`: Number of decimal places for floats

**Example:**

```python
batch.export_to_csv("all_results.csv", precision=6)
```

#### `get_summary_stats()`

Get summary statistics across all evaluated files.

**Returns:** Dictionary with mean, min, max, count for each metric

**Example:**

```python
stats = batch.get_summary_stats()

print(f"Average WER: {stats['wer']['mean']:.2%}")
print(f"Min WER: {stats['wer']['min']:.2%}")
print(f"Max WER: {stats['wer']['max']:.2%}")
print(f"Number of files: {stats['wer']['count']}")
```

#### `clear()`

Clear all stored results (useful for processing multiple batches).

```python
batch.clear()
```

## Common Patterns

### Pattern 1: Vendor Comparison

Compare multiple STT vendors on the same dataset.

```python
benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

vendors = ["Vendor_A", "Vendor_B", "Vendor_C"]

for vendor in vendors:
    hypothesis = load_vendor_transcript(vendor)
    batch.add_evaluation(
        vendor,
        reference_transcript,
        hypothesis,
        calculate_der=False
    )

batch.export_to_csv("vendor_comparison.csv")

# Get best vendor
stats = batch.get_summary_stats()
best_wer = stats['wer']['min']
print(f"Best WER: {best_wer:.2%}")
```

### Pattern 2: Batch Processing Directory

Process all files in a directory.

```python
import os
import json

benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

reference_dir = "ground_truth/"
hypothesis_dir = "vendor_transcripts/"

for filename in os.listdir(reference_dir):
    if filename.endswith(".json"):
        # Load transcripts
        with open(f"{reference_dir}/{filename}") as f:
            reference = json.load(f)
        with open(f"{hypothesis_dir}/{filename}") as f:
            hypothesis = json.load(f)

        # Evaluate
        batch.add_evaluation(filename, reference, hypothesis)

# Export all results
batch.export_to_csv("batch_results.csv")

# Print summary
stats = batch.get_summary_stats()
print(f"Processed {stats['wer']['count']} files")
print(f"Average WER: {stats['wer']['mean']:.2%}")
```

### Pattern 3: Incremental Export

Process files incrementally and append to CSV.

```python
benchmark = STTBenchmark()

# Process files one at a time
for i, (ref, hyp) in enumerate(dataset):
    results = benchmark.evaluate(ref, hyp, calculate_der=False)

    ResultsExporter.to_csv(
        results,
        "incremental_results.csv",
        file_identifiers=f"file_{i:04d}.json",
        append=(i > 0)  # Append after first file
    )

    print(f"Processed file {i+1}: WER={results['wer']:.2%}")
```

### Pattern 4: Multiple Datasets

Evaluate same system on different datasets.

```python
benchmark = STTBenchmark()

datasets = {
    "medical": (medical_refs, medical_hyps),
    "legal": (legal_refs, legal_hyps),
    "casual": (casual_refs, casual_hyps),
}

for dataset_name, (refs, hyps) in datasets.items():
    batch = BatchEvaluator(benchmark)

    for i, (ref, hyp) in enumerate(zip(refs, hyps)):
        batch.add_evaluation(f"{dataset_name}_{i:03d}", ref, hyp)

    batch.export_to_csv(f"{dataset_name}_results.csv")

    stats = batch.get_summary_stats()
    print(f"{dataset_name}: Avg WER = {stats['wer']['mean']:.2%}")
```

## CSV Output Format

### Standard Columns

The CSV will include all metrics returned by the evaluation:

| Column | Description |
|--------|-------------|
| `file` | File identifier |
| `wer` | Word Error Rate |
| `mer` | Match Error Rate |
| `wil` | Word Information Lost |
| `wip` | Word Information Preserved |
| `cp_wer` | Concatenated minimum-Permutation WER |
| `hits` | Number of correct words |
| `substitutions` | Number of substituted words |
| `deletions` | Number of deleted words |
| `insertions` | Number of inserted words |

If DER is calculated (with timestamps):
| Column | Description |
|--------|-------------|
| `der` | Diarization Error Rate |
| `false_alarm` | False alarm rate |
| `missed_detection` | Missed detection rate |
| `confusion` | Speaker confusion rate |
| `total` | Total DER |

If DER is calculated (without timestamps):
| Column | Description |
|--------|-------------|
| `speaker_error_rate` | Simplified speaker error rate |
| `speaker_errors` | Number of speaker errors |
| `total_words` | Total words evaluated |

### Example Output

```csv
file,wer,mer,wil,wip,cp_wer,hits,substitutions,deletions,insertions,total_errors,total_reference_words
conversation_001.json,0.0234,0.0156,0.0289,0.9711,0.0245,428,8,2,0,10,438
conversation_002.json,0.0512,0.0423,0.0598,0.9402,0.0534,392,15,5,1,21,413
conversation_003.json,0.0187,0.0124,0.0215,0.9785,0.0201,445,5,3,0,8,453
```

## Advanced Features

### Custom Precision

Control decimal precision for cleaner output:

```python
# High precision (6 decimals)
batch.export_to_csv("results.csv", precision=6)
# Output: 0.023456

# Low precision (2 decimals)
batch.export_to_csv("results.csv", precision=2)
# Output: 0.02
```

### Append Mode

Build CSV file incrementally:

```python
# Create new file
ResultsExporter.to_csv(results1, "metrics.csv", "file1.json", append=False)

# Append additional results
ResultsExporter.to_csv(results2, "metrics.csv", "file2.json", append=True)
ResultsExporter.to_csv(results3, "metrics.csv", "file3.json", append=True)
```

### Reading Results Back

```python
import csv

with open("results.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['file']}: WER={float(row['wer']):.2%}")
```

## Best Practices

1. **Use BatchEvaluator for Multiple Files**
   - Simpler API than manual ResultsExporter calls
   - Automatic summary statistics
   - Single export call for all results

2. **Use Meaningful File Identifiers**
   - Include dataset name: `"medical_001.json"`
   - Include vendor name: `"vendor_a_conversation_001.json"`
   - Use consistent naming for sorting

3. **Set Appropriate Precision**
   - Use 4-6 decimals for analysis
   - Use 2-3 decimals for reports
   - Higher precision preserves information

4. **Export After Each Batch**
   - Clear results with `batch.clear()` after export
   - Prevents memory issues with large datasets

5. **Use Append Mode for Long-Running Jobs**
   - Export incrementally to avoid data loss
   - Can resume if process crashes

## Troubleshooting

### Issue: Missing Columns in CSV

**Cause:** Different evaluations calculated different metrics

**Solution:** All evaluations should use same parameters
```python
# Good: Consistent parameters
for ref, hyp in dataset:
    batch.add_evaluation(file_id, ref, hyp, calculate_der=False)

# Bad: Inconsistent parameters
batch.add_evaluation("file1", ref1, hyp1, calculate_der=True)
batch.add_evaluation("file2", ref2, hyp2, calculate_der=False)
```

### Issue: File Identifiers Don't Match Results

**Cause:** Mismatch in list lengths

**Solution:** Ensure equal number of identifiers and results
```python
# This will raise ValueError
ResultsExporter.to_csv(
    [result1, result2],
    "out.csv",
    file_identifiers=["file1"]  # Only 1 identifier for 2 results!
)
```

### Issue: Encoding Errors

**Cause:** Non-ASCII characters in file identifiers

**Solution:** Use UTF-8 encoding (handled automatically) or sanitize identifiers
```python
# SDK handles UTF-8 automatically
file_id = "conversation_médical_001.json"  # Works fine
```

## See Also

- `examples/csv_export_example.py`: Comprehensive examples
- `README.md`: Full API documentation
- `QUICKSTART.md`: Quick start guide
