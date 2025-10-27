# Speaker Metrics Guide

Complete guide for speaker-related metrics in the STT Benchmarking SDK.

## Overview

The SDK now tracks speaker identification metrics in addition to transcription accuracy:

1. **Speaker Count**: Reference and hypothesis speaker counts
2. **Speaker Identification Accuracy**: % of files with correct speaker count
3. **DER (Diarization Error Rate)**: Standard diarization metric (with timestamps)

## New Metrics in CSV Output

### Per-File CSV (e.g., vendor_a_results.csv)

| Metric | Description | Values |
|--------|-------------|--------|
| `ref_num_speakers` | Number of speakers in ground truth | Integer (e.g., 2, 3, 4) |
| `hyp_num_speakers` | Number of speakers identified by vendor | Integer (e.g., 2, 3, 4) |
| `speaker_count_correct` | Whether speaker count matches | 1 (correct) or 0 (incorrect) |
| `der` | Diarization Error Rate (with timestamps) | 0.0 to 1.0 (lower is better) |
| `speaker_error_rate` | Speaker attribution errors (without timestamps) | 0.0 to 1.0 (lower is better) |

### Summary CSV (vendor_summary.csv)

| Metric | Description | Formula |
|--------|-------------|---------|
| `vendor` | Vendor identifier | - |
| `avg_wer` | Average Word Error Rate | Mean WER across all files |
| `avg_cp_wer` | Average CP-WER | Mean CP-WER across all files |
| `speaker_id_accuracy` | Speaker identification accuracy | % of files with correct speaker count |
| `avg_ref_speakers` | Average # of speakers in ground truth | Mean of ref_num_speakers |
| `avg_hyp_speakers` | Average # of speakers identified | Mean of hyp_num_speakers |
| `num_files` | Number of files processed | Count |

## Example Outputs

### Detailed CSV: vendor_a_results.csv

```csv
file,wer,cp_wer,ref_num_speakers,hyp_num_speakers,speaker_count_correct
audio_001.json,0.0234,0.0245,2,2,1
audio_002.json,0.0189,0.0201,3,3,1
audio_003.json,0.0145,0.0156,2,2,1
audio_004.json,0.0267,0.0289,4,4,1
audio_005.json,0.0198,0.0212,2,2,1
```

**In this example:**
- All files have correct speaker counts (speaker_count_correct=1 for all)
- Speaker ID Accuracy = 5/5 = 100%

### Detailed CSV: vendor_b_results.csv

```csv
file,wer,cp_wer,ref_num_speakers,hyp_num_speakers,speaker_count_correct
audio_001.json,0.0298,0.0312,2,3,0
audio_002.json,0.0245,0.0267,3,2,0
audio_003.json,0.0178,0.0189,2,2,1
audio_004.json,0.0334,0.0356,4,3,0
audio_005.json,0.0223,0.0245,2,2,1
```

**In this example:**
- 3 files have incorrect speaker counts (audio_001, audio_002, audio_004)
- 2 files have correct speaker counts (audio_003, audio_005)
- Speaker ID Accuracy = 2/5 = 40%

### Summary CSV: vendor_summary.csv

```csv
vendor,avg_wer,avg_cp_wer,speaker_id_accuracy,avg_ref_speakers,avg_hyp_speakers,num_files
vendor_a,0.0207,0.0221,1.0,2.6,2.6,5
vendor_b,0.0256,0.0274,0.4,2.6,2.4,5
```

**Interpretation:**
- Vendor A: 100% speaker identification accuracy (got speaker count right every time)
- Vendor B: 40% speaker identification accuracy (got speaker count right 2 out of 5 times)
- Both vendors: Average of 2.6 speakers per file in ground truth
- Vendor A: Correctly identified 2.6 speakers on average
- Vendor B: Identified 2.4 speakers on average (under-counting)

## Speaker Identification Accuracy

### Definition

**Speaker Identification Accuracy** = (# of files with correct speaker count) / (total # of files)

- This is a binary metric per file: either the vendor got the speaker count exactly right (1) or wrong (0)
- The average across all files gives the overall accuracy

### Examples

**Example 1: Perfect Identification**
- 5 files, all with correct speaker count
- Speaker ID Accuracy = 5/5 = 100%

**Example 2: Partial Identification**
- 10 files total
- 7 files with correct speaker count
- 3 files with incorrect speaker count
- Speaker ID Accuracy = 7/10 = 70%

**Example 3: Poor Identification**
- 8 files total
- 2 files with correct speaker count
- 6 files with incorrect speaker count
- Speaker ID Accuracy = 2/8 = 25%

## DER (Diarization Error Rate)

### With Timestamps

When your transcripts include `start_time` and `end_time`:

```json
[
    {
        "speaker": "Doctor",
        "text": "Hello",
        "start_time": 0.0,
        "end_time": 1.5
    },
    {
        "speaker": "Patient",
        "text": "Hi",
        "start_time": 1.5,
        "end_time": 3.0
    }
]
```

The SDK calculates standard DER with components:
- `der`: Overall Diarization Error Rate
- `false_alarm`: Speech attributed to wrong speaker
- `missed_detection`: Speech not detected
- `confusion`: Speech segments assigned to wrong speaker

### Without Timestamps

When timestamps are not available, the SDK calculates a simplified metric:
- `speaker_error_rate`: Word-level speaker attribution errors

## Usage Examples

### Basic Usage

```python
from stt_benchmarking import STTBenchmark

benchmark = STTBenchmark()

reference = [
    {"speaker": "A", "text": "Hello"},
    {"speaker": "B", "text": "Hi"},
]

hypothesis = [
    {"speaker": "spk_0", "text": "hello"},
    {"speaker": "spk_1", "text": "hi"},
]

results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

print(f"Reference speakers: {results['ref_num_speakers']}")
print(f"Hypothesis speakers: {results['hyp_num_speakers']}")
print(f"Correct count: {results['speaker_count_correct']}")
```

### Batch Processing with Summary

```python
from stt_benchmarking import STTBenchmark, BatchEvaluator

benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

# Process multiple files
for ref, hyp in dataset:
    batch.add_evaluation(filename, ref, hyp, calculate_der=False)

# Export detailed results
batch.export_to_csv("detailed_results.csv")

# Get vendor summary
summary = batch.get_vendor_summary("vendor_a")
print(f"Speaker ID Accuracy: {summary['speaker_id_accuracy']:.1%}")
print(f"Avg Reference Speakers: {summary['avg_ref_speakers']:.1f}")
print(f"Avg Hypothesis Speakers: {summary['avg_hyp_speakers']:.1f}")

# Export summary CSV
batch.export_summary_to_csv("vendor_summary.csv", "vendor_a")
```

### Multiple Vendor Comparison

```python
from stt_benchmarking import STTBenchmark, BatchEvaluator, ResultsExporter

benchmark = STTBenchmark()
vendors = ["vendor_a", "vendor_b", "vendor_c"]

all_summaries = []

for vendor in vendors:
    batch = BatchEvaluator(benchmark)

    # Process all files for this vendor
    for filename in files:
        truth = load_truth(filename)
        hypothesis = load_vendor(vendor, filename)
        batch.add_evaluation(filename, truth, hypothesis)

    # Export detailed results
    batch.export_to_csv(f"results/{vendor}_detailed.csv")

    # Get summary
    summary = batch.get_vendor_summary(vendor)
    all_summaries.append(summary)

# Export combined summary
ResultsExporter.to_csv(
    all_summaries,
    "results/vendor_summary.csv",
    file_identifiers=[s["vendor"] for s in all_summaries]
)

# Display comparison
for s in sorted(all_summaries, key=lambda x: x['avg_wer']):
    print(f"{s['vendor']}: WER={s['avg_wer']:.2%}, "
          f"Speaker ID Acc={s['speaker_id_accuracy']:.1%}")
```

## Interpreting Results

### Good Speaker Identification

**Characteristics:**
- `speaker_id_accuracy` ≥ 90%
- `avg_hyp_speakers` ≈ `avg_ref_speakers`
- Low `speaker_error_rate` (if calculated)

**Example:**
```
speaker_id_accuracy: 95%
avg_ref_speakers: 2.8
avg_hyp_speakers: 2.8
```

### Over-Segmentation (Too Many Speakers)

**Characteristics:**
- `avg_hyp_speakers` > `avg_ref_speakers`
- Low `speaker_id_accuracy`

**Example:**
```
speaker_id_accuracy: 45%
avg_ref_speakers: 2.5
avg_hyp_speakers: 3.2
```

**Interpretation:** Vendor is splitting single speakers into multiple speakers

### Under-Segmentation (Too Few Speakers)

**Characteristics:**
- `avg_hyp_speakers` < `avg_ref_speakers`
- Low `speaker_id_accuracy`

**Example:**
```
speaker_id_accuracy: 40%
avg_ref_speakers: 3.2
avg_hyp_speakers: 2.3
```

**Interpretation:** Vendor is merging multiple speakers into single speakers

## Best Practices

### 1. Always Include Speaker Counts

Even if not calculating DER, speaker counts provide valuable insights:

```python
# DER disabled, but still get speaker counts
results = benchmark.evaluate(ref, hyp, calculate_der=False)
```

### 2. Review Both Detailed and Summary CSVs

- **Detailed CSV**: Identify specific problematic files
- **Summary CSV**: Compare overall vendor performance

### 3. Consider Speaker Count in Vendor Selection

A vendor with slightly higher WER but better speaker identification may be preferable for multi-speaker scenarios.

### 4. Track Trends Over Time

Monitor speaker identification accuracy across datasets:

```python
# Track by dataset type
medical_summary = batch_medical.get_vendor_summary("vendor_a")
legal_summary = batch_legal.get_vendor_summary("vendor_a")

print(f"Medical: {medical_summary['speaker_id_accuracy']:.1%}")
print(f"Legal: {legal_summary['speaker_id_accuracy']:.1%}")
```

## Troubleshooting

### Issue: All speaker_count_correct = 0

**Possible causes:**
- Speaker matching threshold too high
- Vendor consistently over/under-segments

**Solution:**
Check individual file results to understand the pattern:
```python
# Load detailed results
import pandas as pd
df = pd.read_csv('vendor_a_detailed.csv')

# Check speaker count distribution
print(df[['ref_num_speakers', 'hyp_num_speakers']].describe())
```

### Issue: speaker_id_accuracy is low but WER is good

**Interpretation:** Transcription is accurate, but speaker boundaries are incorrect.

**Action:** Consider if speaker diarization quality is critical for your use case.

### Issue: DER not calculated

**Cause:** Timestamps missing from transcripts

**Solution:** Either add timestamps or rely on `speaker_error_rate` metric:
```python
results = benchmark.evaluate(ref, hyp, calculate_der=False)
# Uses speaker_error_rate instead
```

## See Also

- `examples/vendor_summary_example.py`: Complete working example
- `run_benchmark_template.py`: Template with summary CSV generation
- `README.md`: Full API documentation
- `CSV_EXPORT_GUIDE.md`: CSV export details
