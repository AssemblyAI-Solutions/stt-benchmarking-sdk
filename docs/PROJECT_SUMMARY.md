# STT Benchmarking SDK - Project Summary

## Overview

A complete Python SDK for benchmarking Speech-to-Text (STT) systems with comprehensive metrics for transcription accuracy and speaker diarization quality.

## Architecture

### Core Components

1. **Data Models** (`models.py`)
   - `Utterance`: Single speaker utterance with text and optional timestamps
   - `Transcript`: Collection of utterances with helper methods

2. **Text Normalization** (`normalizer.py`)
   - Uses `whisper_normalizer.english.EnglishTextNormalizer`
   - Ensures fair comparison by normalizing both reference and hypothesis

3. **Speaker Matching** (`speaker_matcher.py`)
   - Fuzzy string matching using `thefuzz` library
   - Concatenates all text per speaker for robust matching
   - Configurable similarity threshold (default: 80%)

4. **Metrics** (`metrics.py`)
   - **WERMetrics**: Word Error Rate using `jiwer`
   - **CPWERMetrics**: Concatenated minimum-Permutation WER for multi-speaker
   - **DERMetrics**: Diarization Error Rate using `pyannote.metrics`

5. **Main Interface** (`benchmark.py`)
   - `STTBenchmark`: High-level API for evaluation
   - Configurable preprocessing options
   - Selective metric calculation

## Key Features

### 1. Automatic Speaker Label Alignment

Different STT vendors use different speaker naming conventions:
- Reference: "Dr. Smith", "Patient Jones"
- Vendor A: "speaker_0", "speaker_1"
- Vendor B: "spk_A", "spk_B"
- Vendor C: "SPEAKER_00", "SPEAKER_01"

The SDK automatically matches these using fuzzy text matching on the concatenated speech content of each speaker.

### 2. Comprehensive Metrics

**Word Error Rate (WER)**
- Standard ASR metric
- Includes substitutions, deletions, insertions
- Additional metrics: MER, WIL, WIP

**Concatenated minimum-Permutation WER (CP-WER)**
- Specialized for multi-speaker transcription
- Finds optimal speaker permutation
- Evaluates both transcription and speaker separation

**Diarization Error Rate (DER)**
- Gold standard for speaker diarization
- Components: false alarm, missed detection, confusion
- Requires timestamps
- Fallback metric available without timestamps

### 3. Flexible Configuration

```python
STTBenchmark(
    normalize=True,                    # Text normalization
    match_speakers=True,               # Auto speaker matching
    speaker_matching_threshold=80.0    # Fuzzy match threshold
)
```

## Data Format

### Standard Format
```python
[
    {
        "speaker": "SpeakerID",
        "text": "Transcribed text"
    },
    ...
]
```

### With Timestamps (for DER)
```python
[
    {
        "speaker": "SpeakerID",
        "text": "Transcribed text",
        "start_time": 0.0,
        "end_time": 1.5
    },
    ...
]
```

## Dependencies

### Core Libraries
- `jiwer`: WER calculation
- `whisper-normalizer`: Text normalization
- `thefuzz` + `python-Levenshtein`: Fuzzy speaker matching
- `meeteval`: CP-WER calculation
- `pyannote.metrics` + `pyannote.core`: DER calculation
- `scipy`: Optimization for speaker mapping
- `numpy`: Numerical operations

## Usage Patterns

### Basic Evaluation
```python
benchmark = STTBenchmark()
results = benchmark.evaluate(reference, hypothesis)
```

### Vendor Comparison
```python
for vendor_name, transcript in vendor_transcripts.items():
    results[vendor_name] = benchmark.evaluate(truth, transcript)
```

### Custom Preprocessing
```python
# Manual speaker matching
matcher = SpeakerMatcher(threshold=85.0)
mapping = matcher.match_speakers(reference, hypothesis)
aligned = matcher.apply_speaker_mapping(hypothesis, mapping)

# Manual normalization
normalizer = TextNormalizer()
ref_norm = normalizer.normalize_transcript(reference)
hyp_norm = normalizer.normalize_transcript(hypothesis)

# Direct metric calculation
wer_results = WERMetrics.calculate(ref_norm, hyp_norm)
```

## Project Structure

```
stt-benchmarking-sdk/
├── src/
│   └── stt_benchmarking/
│       ├── __init__.py
│       ├── models.py           # Data models
│       ├── normalizer.py       # Text normalization
│       ├── speaker_matcher.py  # Speaker matching
│       ├── metrics.py          # Metric calculations
│       └── benchmark.py        # Main interface
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_benchmark.py
├── examples/
│   ├── basic_usage.py
│   ├── advanced_usage.py
│   └── csv_export_example.py
├── setup.py
├── requirements.txt
├── README.md
├── QUICKSTART.md
└── PROJECT_SUMMARY.md
```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

Test coverage includes:
- Data model creation and conversion
- Speaker matching with various thresholds
- Metric calculation
- Edge cases (empty transcripts, mismatched speakers)

## Examples

Three comprehensive example files:
1. `basic_usage.py`: Simple evaluation scenarios
2. `advanced_usage.py`: Custom configurations, batch processing, manual control
3. `csv_export_example.py`: CSV export, batch evaluation, and vendor comparison

## CSV Export Feature

The SDK includes comprehensive CSV export functionality:

**ResultsExporter**: Static methods for exporting metrics
- `to_csv()`: Export single or multiple results to CSV
- `format_for_export()`: Format results with custom precision
- Support for appending to existing CSV files

**BatchEvaluator**: Convenient batch processing
- Add multiple evaluations with `add_evaluation()`
- Export all results at once with `export_to_csv()`
- Get summary statistics with `get_summary_stats()` (mean, min, max)
- Clear stored results with `clear()`

Example CSV output:
```csv
file,wer,mer,wil,cp_wer,hits,substitutions,deletions,insertions
file1.json,0.0234,0.0156,0.0289,0.0245,428,8,2,0
file2.json,0.0512,0.0423,0.0598,0.0534,392,15,5,1
file3.json,0.0187,0.0124,0.0215,0.0201,445,5,3,0
```

## Design Decisions

### Why Fuzzy Speaker Matching?
- Different vendors use arbitrary speaker labels
- Text-based matching is more reliable than trying to match based on voice characteristics
- Concatenating all text per speaker provides robust matching signal

### Why Whisper Normalizer?
- Industry standard for STT evaluation
- Handles common variations (punctuation, capitalization, numbers)
- Ensures fair comparison across vendors

### Why Both CP-WER and DER?
- CP-WER: Focuses on transcription accuracy with speaker separation
- DER: Focuses on temporal diarization accuracy
- Together provide complete picture of multi-speaker STT quality

### Fallback Metrics
- DER requires timestamps, which not all vendors provide
- Simplified speaker error metric available without timestamps
- Graceful degradation ensures SDK works with various data formats

## Future Enhancements

Potential additions:
- Support for multiple languages (currently English only)
- Real-time evaluation for streaming STT
- Confidence score analysis
- Sentence/utterance level metrics
- JSON export for results
- Batch evaluation with parallel processing
- Integration with popular STT APIs
- Visualization tools for results
- Per-speaker metrics breakdown

## Installation

```bash
# From source
pip install -e .

# Dependencies only
pip install -r requirements.txt
```

## Quick Start

```python
from stt_benchmarking import STTBenchmark

benchmark = STTBenchmark()

results = benchmark.evaluate(
    reference=[{"speaker": "A", "text": "Hello world"}],
    hypothesis=[{"speaker": "spk_0", "text": "hello world"}]
)

print(f"WER: {results['wer']:.2%}")
```

## License

MIT License

## Support

- Documentation: See README.md and QUICKSTART.md
- Examples: See examples/ directory
- Issues: Create issue in project repository
