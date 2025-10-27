# Getting Started: Benchmarking Multiple Audio Files

Complete guide for running benchmarks on multiple audio files across multiple STT vendors.

## Quick Start (5 Steps)

### Step 1: Install the SDK

```bash
cd stt-benchmarking-sdk

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the SDK
pip install -e .
```

**Note:** The virtual environment keeps dependencies isolated. You'll need to activate it (`source venv/bin/activate`) each time you work on the project.

### Step 2: Organize Your Files

Create this directory structure:

```
your-project/
├── truth/                  # Ground truth transcripts
│   ├── audio_001.json
│   ├── audio_002.json
│   ├── audio_003.json
│   ├── audio_004.json
│   └── audio_005.json
│
├── vendors/                # Vendor transcripts
│   ├── vendor_a/
│   │   ├── audio_001.json
│   │   ├── audio_002.json
│   │   ├── audio_003.json
│   │   ├── audio_004.json
│   │   └── audio_005.json
│   │
│   ├── vendor_b/
│   │   ├── audio_001.json
│   │   └── ...
│   │
│   └── vendor_c/
│       ├── audio_001.json
│       └── ...
│
└── results/                # Will be created automatically
```

### Step 3: Prepare Your Transcript Files

Each JSON file should contain a list of utterances:

**Format:**
```json
[
    {
        "speaker": "Doctor",
        "text": "Hello, how are you feeling today?"
    },
    {
        "speaker": "Patient",
        "text": "I'm feeling much better, thank you."
    }
]
```

**With timestamps (optional, for DER):**
```json
[
    {
        "speaker": "Doctor",
        "text": "Hello, how are you feeling today?",
        "start_time": 0.0,
        "end_time": 3.2
    },
    {
        "speaker": "Patient",
        "text": "I'm feeling much better, thank you.",
        "start_time": 3.2,
        "end_time": 5.8
    }
]
```

### Step 4: Copy and Configure the Template Script

```bash
# Copy the template
cp run_benchmark_template.py run_benchmark.py

# Edit the configuration section
nano run_benchmark.py  # or use your preferred editor
```

Update these variables:
```python
TRUTH_DIR = "truth/"
VENDORS_DIR = "vendors/"
VENDORS = ["vendor_a", "vendor_b", "vendor_c"]
RESULTS_DIR = "results/"
CALCULATE_DER = False  # Set True if you have timestamps
```

### Step 5: Run the Benchmark

```bash
python run_benchmark.py
```

Done! Results will be in the `results/` directory as CSV files.

## Detailed Example

Let's walk through a complete example with 5 audio files and 3 vendors.

### Example File: truth/audio_001.json

```json
[
    {
        "speaker": "Doctor",
        "text": "What symptoms are you experiencing?"
    },
    {
        "speaker": "Patient",
        "text": "I have a headache and fever."
    },
    {
        "speaker": "Doctor",
        "text": "How long have you had these symptoms?"
    },
    {
        "speaker": "Patient",
        "text": "About three days now."
    }
]
```

### Example File: vendors/vendor_a/audio_001.json

```json
[
    {
        "speaker": "spk_0",
        "text": "what symptoms are you experiencing"
    },
    {
        "speaker": "spk_1",
        "text": "i have a headache and fever"
    },
    {
        "speaker": "spk_0",
        "text": "how long have you had these symptoms"
    },
    {
        "speaker": "spk_1",
        "text": "about three days now"
    }
]
```

Note the differences:
- **Different speaker labels**: "Doctor"/"Patient" vs "spk_0"/"spk_1" ✓ Handled automatically
- **Different capitalization**: "What" vs "what" ✓ Handled by normalization
- **Different punctuation**: "experiencing?" vs "experiencing" ✓ Handled by normalization

### Running the Benchmark

```bash
$ python run_benchmark.py

Initializing STT Benchmark...

Configuration:
  Truth directory: truth/
  Vendors directory: vendors/
  Vendors: vendor_a, vendor_b, vendor_c
  Results directory: results/

======================================================================
Processing: vendor_a
======================================================================
  ✓ audio_001.json: WER=0.00%, CP-WER=0.00%
  ✓ audio_002.json: WER=2.34%, CP-WER=2.45%
  ✓ audio_003.json: WER=1.87%, CP-WER=2.01%
  ✓ audio_004.json: WER=2.98%, CP-WER=3.12%
  ✓ audio_005.json: WER=4.45%, CP-WER=4.67%

✓ Results exported to: results/vendor_a_results.csv

Summary for vendor_a:
  Files processed: 5/5
  Failed: 0
  Average WER: 2.33%
  Min WER: 0.00%
  Max WER: 4.45%
  Average CP-WER: 2.45%

======================================================================
Processing: vendor_b
======================================================================
...
```

### Output CSV: results/vendor_a_results.csv

```csv
file,wer,mer,wil,wip,cp_wer,hits,substitutions,deletions,insertions
audio_001.json,0.0000,0.0000,0.0000,1.0000,0.0000,156,0,0,0
audio_002.json,0.0234,0.0156,0.0289,0.9711,0.0245,428,8,2,0
audio_003.json,0.0187,0.0124,0.0215,0.9785,0.0201,445,5,3,0
audio_004.json,0.0298,0.0201,0.0345,0.9655,0.0312,410,10,2,1
audio_005.json,0.0445,0.0356,0.0512,0.9488,0.0467,385,13,4,2
```

## Understanding the Results

### Metrics in the CSV

| Metric | Description | Good Value |
|--------|-------------|------------|
| `wer` | Word Error Rate - overall transcription accuracy | Lower is better (< 5% is excellent) |
| `mer` | Match Error Rate | Lower is better |
| `wil` | Word Information Lost | Lower is better |
| `wip` | Word Information Preserved | Higher is better |
| `cp_wer` | CP-WER for multi-speaker | Lower is better |
| `hits` | Number of correct words | Higher is better |
| `substitutions` | Wrong words | Lower is better |
| `deletions` | Missing words | Lower is better |
| `insertions` | Extra words | Lower is better |

### Analyzing Results

Open the CSV in Excel, Google Sheets, or Python:

```python
import pandas as pd

# Load results
df = pd.read_csv('results/vendor_a_results.csv')

# Basic statistics
print(df['wer'].describe())

# Find worst performing files
worst = df.nlargest(5, 'wer')
print("\nWorst 5 files:")
print(worst[['file', 'wer', 'cp_wer']])

# Compare vendors
vendor_a = pd.read_csv('results/vendor_a_results.csv')
vendor_b = pd.read_csv('results/vendor_b_results.csv')

print(f"Vendor A average WER: {vendor_a['wer'].mean():.2%}")
print(f"Vendor B average WER: {vendor_b['wer'].mean():.2%}")
```

## Common File Formats

The SDK supports multiple file formats:

### JSON (Recommended)
```python
# Load automatically
from stt_benchmarking import TranscriptLoader
transcript = TranscriptLoader.from_json("file.json")
```

### CSV
```python
transcript = TranscriptLoader.from_csv(
    "file.csv",
    speaker_column="speaker",
    text_column="text"
)
```

### Plain Text
```python
# Format: "Speaker A: Hello world"
transcript = TranscriptLoader.from_text("file.txt")
```

### SRT Subtitles
```python
transcript = TranscriptLoader.from_srt("file.srt")
```

### Auto-detect
```python
# Automatically detects format from extension
transcript = TranscriptLoader.auto_detect_format("file.json")
```

## Troubleshooting

### Issue: "File not found"

**Solution:** Check that:
1. Truth and vendor files have the **same filename**
2. Paths in configuration are correct
3. File extensions match `FILE_EXTENSION` setting

### Issue: "Invalid JSON"

**Solution:** Validate your JSON:
```bash
python -m json.tool your_file.json
```

Or use the validator:
```python
from stt_benchmarking import validate_transcript
import json

with open("file.json") as f:
    data = json.load(f)

validate_transcript(data)  # Raises error if invalid
```

### Issue: High WER even though transcripts look similar

**Solution:**
1. Check if normalization is enabled: `NORMALIZE_TEXT = True`
2. Check speaker matching: `MATCH_SPEAKERS = True`
3. Verify file content is correct

### Issue: Speaker matching not working

**Solution:** Lower the threshold:
```python
SPEAKER_THRESHOLD = 70.0  # More lenient (default is 80.0)
```

### Issue: Want to skip DER calculation

**Solution:**
```python
CALCULATE_DER = False  # DER requires timestamps
```

## Advanced Usage

### Custom Processing Script

For more control, write a custom script:

```python
import os
import json
from stt_benchmarking import STTBenchmark, BatchEvaluator

benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

# Your custom logic here
for truth_file, vendor_file in get_file_pairs():
    with open(truth_file) as f:
        truth = json.load(f)
    with open(vendor_file) as f:
        hypothesis = json.load(f)

    batch.add_evaluation(
        os.path.basename(truth_file),
        truth,
        hypothesis,
        calculate_der=False
    )

batch.export_to_csv("custom_results.csv")
```

### Process Single Vendor

```python
from stt_benchmarking import STTBenchmark, BatchEvaluator

benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

# Just test vendor_a
for filename in os.listdir("truth/"):
    truth = json.load(open(f"truth/{filename}"))
    hyp = json.load(open(f"vendors/vendor_a/{filename}"))
    batch.add_evaluation(filename, truth, hyp)

batch.export_to_csv("vendor_a_only.csv")
stats = batch.get_summary_stats()
print(f"Average WER: {stats['wer']['mean']:.2%}")
```

### Filter Results

```python
import pandas as pd

# Load results
df = pd.read_csv('results/vendor_a_results.csv')

# Filter high-error files
high_error = df[df['wer'] > 0.05]
high_error.to_csv('high_error_files.csv', index=False)

# Get statistics
print(f"Files with >5% WER: {len(high_error)}")
print(f"Average WER of high-error files: {high_error['wer'].mean():.2%}")
```

## Next Steps

- See `examples/batch_processing.py` for a runnable example
- Read `DIRECTORY_STRUCTURE.md` for more organization options
- Check `CSV_EXPORT_GUIDE.md` for export details
- Review `README.md` for full API documentation

## Getting Help

If you encounter issues:
1. Check the examples in `examples/`
2. Review the documentation files
3. Validate your transcript format
4. Enable debug output in your script
