# Speaker Metrics - Quick Reference

## What's Included

✅ **YES - DER is included** in the benchmark when timestamps are available

✅ **NEW - Speaker count tracking**: `ref_num_speakers`, `hyp_num_speakers`, `speaker_count_correct`

✅ **NEW - Speaker identification accuracy**: % of files where vendor got speaker count correct

✅ **NEW - Vendor summary CSV**: Separate CSV with vendor averages and speaker metrics

## Two CSV Files Generated

### 1. Detailed CSV (per-file metrics)

**Filename**: `vendor_a_results.csv`, `vendor_b_results.csv`, etc.

**One row per audio file** with columns:

| Column | Description |
|--------|-------------|
| `file` | Filename |
| `wer` | Word Error Rate |
| `cp_wer` | CP-WER |
| `der` | Diarization Error Rate (if timestamps available) |
| `ref_num_speakers` | **NEW**: True # of speakers |
| `hyp_num_speakers` | **NEW**: Vendor's # of speakers identified |
| `speaker_count_correct` | **NEW**: 1 if correct, 0 if wrong |
| ... | Other metrics |

**Example:**
```csv
file,wer,cp_wer,ref_num_speakers,hyp_num_speakers,speaker_count_correct
audio_001.json,0.0234,0.0245,2,2,1
audio_002.json,0.0189,0.0201,3,3,1
audio_003.json,0.0145,0.0156,2,3,0
audio_004.json,0.0267,0.0289,4,4,1
audio_005.json,0.0198,0.0212,2,2,1
```

### 2. Summary CSV (vendor averages)

**Filename**: `vendor_summary.csv`

**One row per vendor** with columns:

| Column | Description |
|--------|-------------|
| `vendor` | Vendor name |
| `avg_wer` | Average WER across all files |
| `avg_cp_wer` | Average CP-WER across all files |
| `speaker_id_accuracy` | **NEW**: % files with correct speaker count |
| `avg_ref_speakers` | **NEW**: Average true # of speakers |
| `avg_hyp_speakers` | **NEW**: Average identified # of speakers |
| `num_files` | Total files processed |

**Example:**
```csv
vendor,avg_wer,avg_cp_wer,speaker_id_accuracy,avg_ref_speakers,avg_hyp_speakers,num_files
vendor_a,0.0207,0.0221,1.0,2.6,2.6,5
vendor_b,0.0256,0.0274,0.4,2.6,2.4,5
vendor_c,0.0312,0.0334,0.6,2.6,3.1,5
```

**Interpretation:**
- **Vendor A**: Best performance - 100% speaker ID accuracy, best WER
- **Vendor B**: Under-segments (2.4 vs 2.6 speakers), 40% accuracy
- **Vendor C**: Over-segments (3.1 vs 2.6 speakers), 60% accuracy

## Speaker Identification Accuracy Formula

```
Speaker ID Accuracy = (# files with correct speaker count) / (total files)
```

**Example:**
- 5 audio files total
- Vendor got speaker count correct in 4 files
- Speaker ID Accuracy = 4/5 = 80%

## Code Example

```python
from stt_benchmarking import STTBenchmark, BatchEvaluator, ResultsExporter

benchmark = STTBenchmark()
vendors = ["vendor_a", "vendor_b", "vendor_c"]

all_summaries = []

for vendor in vendors:
    batch = BatchEvaluator(benchmark)

    # Process all files
    for filename in audio_files:
        truth = load_truth(filename)
        hypothesis = load_vendor(vendor, filename)
        batch.add_evaluation(filename, truth, hypothesis, calculate_der=False)

    # Export detailed results (per-file)
    batch.export_to_csv(f"results/{vendor}_detailed.csv")

    # Get vendor summary
    summary = batch.get_vendor_summary(vendor)
    all_summaries.append(summary)

    print(f"{vendor}:")
    print(f"  WER: {summary['avg_wer']:.2%}")
    print(f"  Speaker ID Accuracy: {summary['speaker_id_accuracy']:.1%}")

# Export vendor summary CSV
ResultsExporter.to_csv(
    all_summaries,
    "results/vendor_summary.csv",
    file_identifiers=[s["vendor"] for s in all_summaries]
)
```

## Output Structure

```
results/
├── vendor_a_detailed.csv      # 5 rows (one per audio file)
├── vendor_b_detailed.csv      # 5 rows (one per audio file)
├── vendor_c_detailed.csv      # 5 rows (one per audio file)
└── vendor_summary.csv         # 3 rows (one per vendor)
```

## Quick Check: Is DER Included?

**YES!** DER is automatically included when:

1. Your transcripts have timestamps:
```json
{
    "speaker": "Doctor",
    "text": "Hello",
    "start_time": 0.0,
    "end_time": 1.5
}
```

2. You enable DER calculation (enabled by default):
```python
results = benchmark.evaluate(ref, hyp, calculate_der=True)  # Default
```

**Without timestamps**, you get:
- `speaker_error_rate` (simplified metric)
- `ref_num_speakers` / `hyp_num_speakers`
- `speaker_count_correct`

## Template Script

The `run_benchmark_template.py` has been updated to automatically:
- ✅ Track speaker counts in detailed CSVs
- ✅ Calculate speaker identification accuracy
- ✅ Generate vendor summary CSV
- ✅ Display speaker metrics in console output

Just run:
```bash
python run_benchmark_template.py
```

## Example Console Output

```
Processing: vendor_a
======================================================================
  ✓ audio_001.json: WER=2.34%, Speakers: 2 → 2 ✓
  ✓ audio_002.json: WER=1.89%, Speakers: 3 → 3 ✓
  ✓ audio_003.json: WER=1.45%, Speakers: 2 → 3 ✗
  ✓ audio_004.json: WER=2.67%, Speakers: 4 → 4 ✓
  ✓ audio_005.json: WER=1.98%, Speakers: 2 → 2 ✓

Summary for vendor_a:
  Files processed: 5/5
  Average WER: 2.07%
  Speaker ID Accuracy: 80.0%
    (Correct speaker count in 4 of 5 files)
```

## See Full Documentation

- **`SPEAKER_METRICS_GUIDE.md`**: Complete guide with examples
- **`examples/vendor_summary_example.py`**: Runnable example
- **`run_benchmark_template.py`**: Updated template script
