# STT Benchmarking SDK

A comprehensive Python SDK for benchmarking Speech-to-Text systems with quantitative and qualitative metrics.

## Features

- **WER Metrics**: Word Error Rate, Match Error Rate, Word Information Lost/Preserved
- **CP-WER**: Concatenated minimum-Permutation WER for multi-speaker evaluation
- **DER**: Diarization Error Rate with timestamp-based speaker accuracy
- **Speaker Metrics**: Track speaker count accuracy and identification performance
- **Automatic Normalization**: Text normalization using Whisper's normalizer
- **Speaker Matching**: Fuzzy matching to align different speaker label conventions
- **LLM Vibe Eval**: Qualitative evaluation using state-of-the-art LLMs (Claude, GPT, Gemini)
- **Batch Processing**: Evaluate multiple files and vendors efficiently
- **CSV Export**: Export detailed and summary results for analysis

## Installation

### Using Virtual Environment (Recommended)

```bash
# Clone or download the repository
cd stt-benchmarking-sdk

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install the SDK
pip install -e .
```

### Without Virtual Environment

```bash
cd stt-benchmarking-sdk
pip install -e .
```

**Note:** Virtual environments are recommended to avoid dependency conflicts. See **[VIRTUAL_ENV_GUIDE.md](VIRTUAL_ENV_GUIDE.md)** for detailed setup or **[VENV_AND_ENV_SUMMARY.md](VENV_AND_ENV_SUMMARY.md)** for a quick overview of how venv + .env work together.

## Quick Start Options

### Option 1: Benchmark Multiple Vendors (Recommended for Production Use)

**Best for:** Comparing multiple STT vendors across many audio files

See **[GETTING_STARTED.md](GETTING_STARTED.md)** for the complete 5-step guide.

**Quick version:**

```bash
# 1. Install
pip install -e .

# 2. Organize your files
mkdir -p truth vendors/{vendor_a,vendor_b,vendor_c} results

# Place ground truth transcripts in truth/
# Place vendor transcripts in vendors/vendor_name/

# 3. Configure the template
cp run_benchmark_template.py run_benchmark.py
# Edit run_benchmark.py to set your paths and vendor names

# 4. Run
python run_benchmark.py
```

**Output:**
- `results/vendor_a_results.csv` - Per-file metrics for Vendor A
- `results/vendor_b_results.csv` - Per-file metrics for Vendor B
- `results/vendor_summary.csv` - Vendor comparison with speaker ID accuracy

### Option 2: Use as a Python Library

**Best for:** Custom integrations, notebooks, or one-off evaluations

```python
from stt_benchmarking import STTBenchmark

# Initialize benchmark
benchmark = STTBenchmark()

# Your transcripts
reference = [
    {"speaker": "Doctor", "text": "What brings you in today?"},
    {"speaker": "Patient", "text": "I have a persistent headache."}
]

hypothesis = [
    {"speaker": "spk_0", "text": "what brings you in today"},
    {"speaker": "spk_1", "text": "i have a persistent headache"}
]

# Evaluate
results = benchmark.evaluate(reference, hypothesis)

print(f"WER: {results['wer']:.2%}")
print(f"CP-WER: {results['cp_wer']:.2%}")
print(f"Speaker Count Correct: {results['speaker_count_correct']}")
```

## Key Features Explained

### Automatic Speaker Matching

Different STT vendors use different speaker labels. The SDK automatically matches them:

```python
# Reference uses: "Doctor", "Patient"
# Vendor A uses: "Speaker_1", "Speaker_2"
# Vendor B uses: "spk_0", "spk_1"
# SDK automatically aligns these using fuzzy text matching
```

### Speaker Identification Accuracy

Track how often vendors get the speaker count correct:

```csv
vendor,avg_wer,avg_cp_wer,speaker_id_accuracy,num_files
vendor_a,0.0234,0.0245,1.0,50
vendor_b,0.0198,0.0212,0.85,50
vendor_c,0.0267,0.0289,0.62,50
```

- `speaker_id_accuracy = 1.0` means vendor got speaker count right in 100% of files
- `speaker_id_accuracy = 0.85` means vendor got speaker count right in 85% of files

See **[SPEAKER_METRICS_GUIDE.md](SPEAKER_METRICS_GUIDE.md)** for details.

### LLM Vibe Eval (Qualitative Assessment)

Get AI-powered qualitative feedback on transcription quality:

```python
from stt_benchmarking import LLMEvaluator

# Setup (requires AssemblyAI API key)
evaluator = LLMEvaluator()

# Evaluate
result = evaluator.evaluate_and_score(
    reference=truth,
    hypothesis=vendor_transcript,
    vendor_name="Vendor A",
    file_identifier="meeting_001"
)

print(f"Vibe Score: {result['vibe_score']}/10")
print(result['consolidation'])  # Detailed AI feedback
```

**Setup for LLM Vibe Eval:**

1. Get an AssemblyAI API key from https://www.assemblyai.com
2. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```
3. The SDK will automatically load your API key from `.env`

See **[LLM_VIBE_EVAL_GUIDE.md](LLM_VIBE_EVAL_GUIDE.md)** for complete documentation.

## Data Format

Transcripts are simple JSON arrays:

```json
[
    {
        "speaker": "Speaker_A",
        "text": "Hello, how are you today?"
    },
    {
        "speaker": "Speaker_B",
        "text": "I'm doing well, thank you."
    }
]
```

**With timestamps (optional, for DER calculation):**

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
        "text": "I'm doing well, thank you.",
        "start_time": 2.5,
        "end_time": 4.0
    }
]
```

## Metrics Explained

### Word Error Rate (WER)

Standard metric for transcription accuracy:

```
WER = (Substitutions + Deletions + Insertions) / Total Words
```

- **Good:** < 5%
- **Acceptable:** 5-10%
- **Needs improvement:** > 10%

### CP-WER (Concatenated minimum-Permutation WER)

Specialized metric for multi-speaker transcription. Accounts for both transcription accuracy and speaker separation.

### Diarization Error Rate (DER)

Measures speaker diarization quality when timestamps are available:
- **False Alarm**: Speech attributed incorrectly
- **Missed Detection**: Speech not detected
- **Confusion**: Speech assigned to wrong speaker

### Speaker Identification Accuracy

Binary metric: Did the vendor identify the correct number of speakers?

```
Speaker ID Accuracy = (Files with correct speaker count) / (Total files)
```

## Batch Processing & Export

```python
from stt_benchmarking import STTBenchmark, BatchEvaluator

benchmark = STTBenchmark()
batch = BatchEvaluator(benchmark)

# Evaluate multiple files
for filename in audio_files:
    truth = load_truth(filename)
    hypothesis = load_vendor(filename)
    batch.add_evaluation(filename, truth, hypothesis)

# Export to CSV
batch.export_to_csv("results.csv")

# Get summary statistics
stats = batch.get_summary_stats()
print(f"Average WER: {stats['wer']['mean']:.2%}")
print(f"Speaker ID Accuracy: {stats['speaker_count_correct']['mean']:.1%}")
```

## Examples

The `examples/` directory contains 8 comprehensive examples:

- **`basic_usage.py`** - Simple evaluation scenarios
- **`advanced_usage.py`** - Custom configurations and batch processing
- **`batch_processing.py`** - Process multiple files efficiently
- **`csv_export_example.py`** - CSV export and analysis
- **`vendor_summary_example.py`** - Multi-vendor comparison with speaker metrics
- **`llm_vibe_eval_example.py`** - Qualitative LLM evaluation
- **`complete_workflow_with_llm.py`** - Full workflow with quantitative + qualitative metrics
- **`normalization_demo.py`** - Text normalization examples

Run any example:
```bash
python examples/basic_usage.py
```

## Documentation

Comprehensive guides available:

### Getting Started
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete guide for benchmarking multiple vendors
- **[QUICKSTART.md](QUICKSTART.md)** - Library usage quick reference
- **[VIRTUAL_ENV_GUIDE.md](VIRTUAL_ENV_GUIDE.md)** - Virtual environment setup and best practices

### Features
- **[SPEAKER_METRICS_GUIDE.md](SPEAKER_METRICS_GUIDE.md)** - Speaker count tracking and accuracy
- **[LLM_VIBE_EVAL_GUIDE.md](LLM_VIBE_EVAL_GUIDE.md)** - Qualitative evaluation with LLMs
- **[CSV_EXPORT_GUIDE.md](CSV_EXPORT_GUIDE.md)** - CSV export patterns and best practices

### Configuration
- **[ENV_SETUP.md](ENV_SETUP.md)** - Environment variables and API key setup
- **[DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md)** - File organization options

## API Reference

### STTBenchmark

Main class for evaluation:

```python
benchmark = STTBenchmark(
    normalize=True,                    # Text normalization (default: True)
    match_speakers=True,               # Speaker label matching (default: True)
    speaker_matching_threshold=80.0    # Fuzzy match threshold 0-100 (default: 80)
)
```

**Methods:**
- `evaluate(reference, hypothesis, calculate_wer=True, calculate_cp_wer=True, calculate_der=True)` - Full evaluation
- `evaluate_wer_only(reference, hypothesis)` - Only WER metrics
- `evaluate_diarization_only(reference, hypothesis)` - Only CP-WER and DER
- `get_speaker_mapping(reference, hypothesis)` - Get speaker label mapping

### BatchEvaluator

Batch processing helper:

```python
batch = BatchEvaluator(benchmark)
batch.add_evaluation(file_id, reference, hypothesis)
batch.export_to_csv(output_path)
batch.get_summary_stats()
batch.get_vendor_summary(vendor_name)
```

### LLMEvaluator

LLM-based qualitative evaluation:

```python
evaluator = LLMEvaluator(
    api_key=None,                      # Defaults to ASSEMBLYAI_API_KEY env var
    evaluator_models=[...],            # Models for evaluation (default: Claude, GPT, Gemini)
    consolidator_model="...",          # Model for consolidation
    max_tokens=4000                    # Max response length
)
```

**Methods:**
- `evaluate_and_score(reference, hypothesis, vendor_name, file_identifier)` - Get vibe score + feedback
- `evaluate_single(reference, hypothesis, vendor_name, file_identifier)` - Get individual model evaluations

### Utility Functions

```python
from stt_benchmarking import TranscriptLoader, TranscriptWriter, validate_transcript

# Load from various formats
transcript = TranscriptLoader.from_json("file.json")
transcript = TranscriptLoader.from_csv("file.csv")
transcript = TranscriptLoader.from_text("file.txt")
transcript = TranscriptLoader.auto_detect_format("file.json")

# Write to various formats
TranscriptWriter.to_json(utterances, "output.json")
TranscriptWriter.to_csv(utterances, "output.csv")

# Validate format
validate_transcript(transcript_data)
```

## Requirements

- Python 3.8+
- jiwer (WER calculation)
- whisper-normalizer (text normalization)
- thefuzz + python-Levenshtein (speaker matching)
- meeteval (CP-WER calculation)
- pyannote.metrics + pyannote.core (DER calculation)
- scipy + numpy (numerical operations)
- requests (LLM API calls)
- python-dotenv (environment configuration)

All dependencies are installed automatically with `pip install -e .`

## Testing

Run the test suite:

```bash
pip install pytest
pytest tests/
```

## Contributing

This is a public benchmarking tool. Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Issues**: Report bugs or request features via GitHub issues
- **Documentation**: See the `docs/` directory for comprehensive guides
- **Examples**: Check `examples/` for working code samples

## License

MIT License - see LICENSE file for details

## Citation

If you use this SDK in academic work, please cite:

```
@software{stt_benchmarking_sdk,
  title = {STT Benchmarking SDK},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/stt-benchmarking-sdk}
}
```
