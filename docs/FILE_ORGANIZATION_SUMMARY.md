# File Organization Summary

Quick visual reference for organizing your STT benchmarking project.

## Your Scenario

- **5 audio files** to evaluate
- **Ground truth** (human transcriptions) for each
- **3 STT vendors** to compare (vendor_a, vendor_b, vendor_c)
- Each vendor has transcribed all 5 audio files

## Recommended Structure

```
your-project/
│
├── truth/                              # Ground truth transcripts
│   ├── audio_001.json                  # Human transcription of audio 1
│   ├── audio_002.json                  # Human transcription of audio 2
│   ├── audio_003.json                  # Human transcription of audio 3
│   ├── audio_004.json                  # Human transcription of audio 4
│   └── audio_005.json                  # Human transcription of audio 5
│
├── vendors/                            # Vendor transcriptions
│   │
│   ├── vendor_a/                       # Transcriptions from Vendor A
│   │   ├── audio_001.json              # Vendor A's transcription of audio 1
│   │   ├── audio_002.json              # Vendor A's transcription of audio 2
│   │   ├── audio_003.json              # Vendor A's transcription of audio 3
│   │   ├── audio_004.json              # Vendor A's transcription of audio 4
│   │   └── audio_005.json              # Vendor A's transcription of audio 5
│   │
│   ├── vendor_b/                       # Transcriptions from Vendor B
│   │   ├── audio_001.json
│   │   ├── audio_002.json
│   │   ├── audio_003.json
│   │   ├── audio_004.json
│   │   └── audio_005.json
│   │
│   └── vendor_c/                       # Transcriptions from Vendor C
│       ├── audio_001.json
│       ├── audio_002.json
│       ├── audio_003.json
│       ├── audio_004.json
│       └── audio_005.json
│
├── results/                            # Generated results (CSVs)
│   ├── vendor_a_results.csv            # All audio files for vendor A
│   ├── vendor_b_results.csv            # All audio files for vendor B
│   ├── vendor_c_results.csv            # All audio files for vendor C
│   └── comparison_summary.csv          # Summary comparing all vendors
│
└── run_benchmark.py                    # Your benchmark script

```

## Key Points

### ✅ File Naming Rules

1. **Same filename across all directories**
   - Truth file: `truth/audio_001.json`
   - Vendor A: `vendors/vendor_a/audio_001.json`
   - Vendor B: `vendors/vendor_b/audio_001.json`
   - Vendor C: `vendors/vendor_c/audio_001.json`

2. **Use consistent naming pattern**
   - ✓ Good: `audio_001.json`, `audio_002.json`, ...
   - ✓ Good: `conversation_001.json`, `conversation_002.json`, ...
   - ✗ Bad: `audio1.json`, `audio_2.json`, `audio_03.json` (inconsistent)

### ✅ File Format

Each JSON file contains a list of utterances:

```json
[
    {
        "speaker": "Doctor",
        "text": "Hello, how are you?"
    },
    {
        "speaker": "Patient",
        "text": "I'm doing well, thank you."
    }
]
```

### ✅ What Gets Compared

For each audio file (e.g., `audio_001.json`):

```
truth/audio_001.json          (ground truth)
    ↓
    ↓ compared with →  vendors/vendor_a/audio_001.json  →  Result: WER for audio_001
    ↓ compared with →  vendors/vendor_b/audio_001.json  →  Result: WER for audio_001
    ↓ compared with →  vendors/vendor_c/audio_001.json  →  Result: WER for audio_001
```

## Workflow

```
Step 1: Prepare Files
┌────────────────────────────────────────┐
│ Create directory structure             │
│ Place truth files in truth/            │
│ Place vendor files in vendors/vendor_*/ │
└────────────────────────────────────────┘
                  ↓
Step 2: Configure Script
┌────────────────────────────────────────┐
│ Copy run_benchmark_template.py         │
│ Update TRUTH_DIR, VENDORS_DIR, etc.    │
└────────────────────────────────────────┘
                  ↓
Step 3: Run Benchmark
┌────────────────────────────────────────┐
│ python run_benchmark.py                │
└────────────────────────────────────────┘
                  ↓
Step 4: Analyze Results
┌────────────────────────────────────────┐
│ Check results/*.csv files              │
│ Compare vendor performance             │
│ Identify problematic audio files       │
└────────────────────────────────────────┘
```

## Example: 5 Audio Files × 3 Vendors

### Files You Need to Provide (20 total)

**Ground Truth (5 files):**
```
truth/audio_001.json
truth/audio_002.json
truth/audio_003.json
truth/audio_004.json
truth/audio_005.json
```

**Vendor A (5 files):**
```
vendors/vendor_a/audio_001.json
vendors/vendor_a/audio_002.json
vendors/vendor_a/audio_003.json
vendors/vendor_a/audio_004.json
vendors/vendor_a/audio_005.json
```

**Vendor B (5 files):**
```
vendors/vendor_b/audio_001.json
vendors/vendor_b/audio_002.json
vendors/vendor_b/audio_003.json
vendors/vendor_b/audio_004.json
vendors/vendor_b/audio_005.json
```

**Vendor C (5 files):**
```
vendors/vendor_c/audio_001.json
vendors/vendor_c/audio_002.json
vendors/vendor_c/audio_003.json
vendors/vendor_c/audio_004.json
vendors/vendor_c/audio_005.json
```

### Files Generated by SDK (4 CSV files)

```
results/vendor_a_results.csv       # 5 rows (one per audio file)
results/vendor_b_results.csv       # 5 rows (one per audio file)
results/vendor_c_results.csv       # 5 rows (one per audio file)
results/comparison_summary.csv     # 3 rows (one per vendor)
```

## Output: CSV Results

### results/vendor_a_results.csv

| file | wer | cp_wer | substitutions | deletions | insertions |
|------|-----|--------|---------------|-----------|------------|
| audio_001.json | 0.0234 | 0.0245 | 8 | 2 | 0 |
| audio_002.json | 0.0512 | 0.0534 | 15 | 5 | 1 |
| audio_003.json | 0.0187 | 0.0201 | 5 | 3 | 0 |
| audio_004.json | 0.0298 | 0.0312 | 10 | 2 | 1 |
| audio_005.json | 0.0445 | 0.0467 | 13 | 4 | 2 |

### results/comparison_summary.csv

| vendor | avg_wer | min_wer | max_wer | avg_cp_wer |
|--------|---------|---------|---------|------------|
| vendor_a | 0.0335 | 0.0187 | 0.0512 | 0.0352 |
| vendor_b | 0.0423 | 0.0234 | 0.0678 | 0.0445 |
| vendor_c | 0.0567 | 0.0312 | 0.0891 | 0.0589 |

## Quick Reference: What Goes Where

| Item | Location | Purpose |
|------|----------|---------|
| Human transcriptions | `truth/*.json` | Ground truth for comparison |
| Vendor transcriptions | `vendors/vendor_*/​*.json` | Transcriptions to evaluate |
| Benchmark script | `run_benchmark.py` | Script that runs evaluation |
| Per-vendor results | `results/vendor_*_results.csv` | Detailed results per file |
| Overall comparison | `results/comparison_summary.csv` | Summary across vendors |

## Don't Worry About

❌ **Pre-normalizing text** - SDK does this automatically
❌ **Matching speaker labels** - SDK handles different naming conventions
❌ **Case sensitivity** - SDK normalizes case
❌ **Punctuation** - SDK removes punctuation for fair comparison

## Just Provide

✅ **Raw transcript data** in the format:
```json
[{"speaker": "...", "text": "..."}, ...]
```

✅ **Same filenames** across truth and all vendors

✅ **Organized directories** as shown above

## Next Steps

1. **Create the directory structure** shown above
2. **Place your JSON files** in the appropriate directories
3. **Copy and configure** `run_benchmark_template.py`
4. **Run:** `python run_benchmark.py`
5. **Analyze:** Open CSV files in `results/` directory

See `GETTING_STARTED.md` for detailed instructions!
