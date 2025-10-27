# Directory Structure Guide

This guide shows how to organize your files when benchmarking multiple audio files across multiple STT vendors.

## Recommended Directory Structure

```
your-project/
├── truth/                          # Ground truth (human transcriptions)
│   ├── audio_001.json
│   ├── audio_002.json
│   ├── audio_003.json
│   ├── audio_004.json
│   └── audio_005.json
│
├── vendors/                        # Vendor transcriptions
│   ├── vendor_a/
│   │   ├── audio_001.json
│   │   ├── audio_002.json
│   │   ├── audio_003.json
│   │   ├── audio_004.json
│   │   └── audio_005.json
│   │
│   ├── vendor_b/
│   │   ├── audio_001.json
│   │   ├── audio_002.json
│   │   ├── audio_003.json
│   │   ├── audio_004.json
│   │   └── audio_005.json
│   │
│   └── vendor_c/
│       ├── audio_001.json
│       ├── audio_002.json
│       ├── audio_003.json
│       ├── audio_004.json
│       └── audio_005.json
│
├── results/                        # Benchmark results (generated)
│   ├── vendor_a_results.csv
│   ├── vendor_b_results.csv
│   ├── vendor_c_results.csv
│   └── comparison_summary.csv
│
├── run_benchmark.py               # Your benchmark script
└── requirements.txt
```

## File Format

Each JSON file should contain a list of utterances:

```json
[
    {
        "speaker": "Speaker_A",
        "text": "Hello, how are you today?",
        "start_time": 0.0,
        "end_time": 2.5
    },
    {
        "speaker": "Speaker_B",
        "text": "I'm doing well, thank you for asking.",
        "start_time": 2.5,
        "end_time": 5.0
    }
]
```

**Note:** `start_time` and `end_time` are optional (only needed for DER calculation).

## Alternative Structure: By Audio File

If you prefer to organize by audio file instead of by vendor:

```
your-project/
├── audio_001/
│   ├── truth.json
│   ├── vendor_a.json
│   ├── vendor_b.json
│   └── vendor_c.json
│
├── audio_002/
│   ├── truth.json
│   ├── vendor_a.json
│   ├── vendor_b.json
│   └── vendor_c.json
│
├── audio_003/
│   ├── truth.json
│   ├── vendor_a.json
│   ├── vendor_b.json
│   └── vendor_c.json
│
├── audio_004/
│   ├── truth.json
│   ├── vendor_a.json
│   ├── vendor_b.json
│   └── vendor_c.json
│
├── audio_005/
│   ├── truth.json
│   ├── vendor_a.json
│   ├── vendor_b.json
│   └── vendor_c.json
│
├── results/
│   └── all_results.csv
│
└── run_benchmark.py
```

## Example Scripts

### Option 1: Organized by Vendor (Recommended)

```python
import os
import json
from stt_benchmarking import STTBenchmark, BatchEvaluator

# Setup
benchmark = STTBenchmark()
vendors = ["vendor_a", "vendor_b", "vendor_c"]

# Process each vendor
for vendor in vendors:
    print(f"\nProcessing {vendor}...")
    batch = BatchEvaluator(benchmark)

    # Get all truth files
    truth_dir = "truth/"
    vendor_dir = f"vendors/{vendor}/"

    for filename in sorted(os.listdir(truth_dir)):
        if filename.endswith(".json"):
            # Load truth
            with open(f"{truth_dir}/{filename}") as f:
                truth = json.load(f)

            # Load vendor transcript
            with open(f"{vendor_dir}/{filename}") as f:
                hypothesis = json.load(f)

            # Evaluate
            batch.add_evaluation(
                filename,
                truth,
                hypothesis,
                calculate_der=False
            )

    # Export results
    batch.export_to_csv(f"results/{vendor}_results.csv")

    # Print summary
    stats = batch.get_summary_stats()
    print(f"  Files processed: {stats['wer']['count']}")
    print(f"  Average WER: {stats['wer']['mean']:.2%}")
    print(f"  Average CP-WER: {stats['cp_wer']['mean']:.2%}")
```

### Option 2: Organized by Audio File

```python
import os
import json
from stt_benchmarking import STTBenchmark, BatchEvaluator

# Setup
benchmark = STTBenchmark()
vendors = ["vendor_a", "vendor_b", "vendor_c"]
audio_dirs = ["audio_001", "audio_002", "audio_003", "audio_004", "audio_005"]

# Process each vendor
for vendor in vendors:
    print(f"\nProcessing {vendor}...")
    batch = BatchEvaluator(benchmark)

    for audio_dir in audio_dirs:
        # Load truth
        with open(f"{audio_dir}/truth.json") as f:
            truth = json.load(f)

        # Load vendor transcript
        with open(f"{audio_dir}/{vendor}.json") as f:
            hypothesis = json.load(f)

        # Evaluate
        batch.add_evaluation(
            audio_dir,
            truth,
            hypothesis,
            calculate_der=False
        )

    # Export results
    batch.export_to_csv(f"results/{vendor}_results.csv")

    # Print summary
    stats = batch.get_summary_stats()
    print(f"  Files processed: {stats['wer']['count']}")
    print(f"  Average WER: {stats['wer']['mean']:.2%}")
```

## CSV Output

After running, you'll have CSV files like:

**results/vendor_a_results.csv:**
```csv
file,wer,mer,wil,wip,cp_wer,hits,substitutions,deletions,insertions
audio_001.json,0.0234,0.0156,0.0289,0.9711,0.0245,428,8,2,0
audio_002.json,0.0512,0.0423,0.0598,0.9402,0.0534,392,15,5,1
audio_003.json,0.0187,0.0124,0.0215,0.9785,0.0201,445,5,3,0
audio_004.json,0.0298,0.0201,0.0345,0.9655,0.0312,410,10,2,1
audio_005.json,0.0445,0.0356,0.0512,0.9488,0.0467,385,13,4,2
```

## Additional Considerations

### With Timestamps (for DER)

If you have timestamp information, include it in your JSON:

```json
[
    {
        "speaker": "Doctor",
        "text": "What symptoms are you experiencing?",
        "start_time": 0.0,
        "end_time": 2.5
    },
    {
        "speaker": "Patient",
        "text": "I have a headache and fever.",
        "start_time": 2.5,
        "end_time": 5.0
    }
]
```

Then enable DER calculation:
```python
batch.add_evaluation(
    filename,
    truth,
    hypothesis,
    calculate_der=True  # Enable DER calculation
)
```

### Different File Formats

If your transcripts are in different formats (CSV, TXT, etc.), you'll need to convert them. See the next section for utilities.

### Error Handling

Add error handling for missing files:

```python
import os

for filename in sorted(os.listdir(truth_dir)):
    if not filename.endswith(".json"):
        continue

    truth_path = f"{truth_dir}/{filename}"
    vendor_path = f"{vendor_dir}/{filename}"

    # Check if vendor file exists
    if not os.path.exists(vendor_path):
        print(f"Warning: {vendor_path} not found, skipping...")
        continue

    try:
        with open(truth_path) as f:
            truth = json.load(f)
        with open(vendor_path) as f:
            hypothesis = json.load(f)

        batch.add_evaluation(filename, truth, hypothesis)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        continue
```

## Next Steps

1. Organize your files using one of the structures above
2. Use the example script that matches your structure
3. Run the benchmark: `python run_benchmark.py`
4. Analyze results in the `results/` directory

See `examples/batch_processing.py` for a complete working example.
