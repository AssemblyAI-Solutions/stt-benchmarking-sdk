"""Tests for STT Benchmark functionality."""

import pytest
from stt_benchmarking import STTBenchmark
from stt_benchmarking.models import Transcript


def test_basic_evaluation():
    """Test basic evaluation with simple transcripts."""
    reference = [
        {"speaker": "A", "text": "Hello world"},
        {"speaker": "B", "text": "Hi there"},
    ]

    hypothesis = [
        {"speaker": "A", "text": "hello world"},
        {"speaker": "B", "text": "hi there"},
    ]

    benchmark = STTBenchmark()
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    assert "wer" in results
    assert "cp_wer" in results
    assert results["wer"] >= 0.0
    assert results["cp_wer"] >= 0.0


def test_with_speaker_matching():
    """Test evaluation with different speaker labels."""
    reference = [
        {"speaker": "Alice", "text": "Hello how are you"},
        {"speaker": "Bob", "text": "I am fine thanks"},
    ]

    hypothesis = [
        {"speaker": "spk_0", "text": "hello how are you"},
        {"speaker": "spk_1", "text": "i am fine thanks"},
    ]

    benchmark = STTBenchmark(match_speakers=True)
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    # Should have low error rates due to speaker matching
    assert results["wer"] < 0.5
    assert results["cp_wer"] < 0.5


def test_get_speaker_mapping():
    """Test getting speaker mapping."""
    reference = [
        {"speaker": "Alice", "text": "Hello world how are you"},
        {"speaker": "Bob", "text": "I am doing great"},
    ]

    hypothesis = [
        {"speaker": "spk_0", "text": "hello world how are you"},
        {"speaker": "spk_1", "text": "i am doing great"},
    ]

    benchmark = STTBenchmark()
    mapping = benchmark.get_speaker_mapping(reference, hypothesis)

    assert isinstance(mapping, dict)
    assert len(mapping) == 2
    # Mapping should contain reference speaker names
    assert "Alice" in mapping.values() or "Bob" in mapping.values()


def test_wer_only():
    """Test WER-only evaluation."""
    reference = [
        {"speaker": "A", "text": "The quick brown fox"},
    ]

    hypothesis = [
        {"speaker": "A", "text": "the quick brown fox"},
    ]

    benchmark = STTBenchmark()
    results = benchmark.evaluate_wer_only(reference, hypothesis)

    assert "wer" in results
    assert "mer" in results
    assert "wil" in results
    assert "cp_wer" not in results


def test_without_normalization():
    """Test evaluation without text normalization."""
    reference = [
        {"speaker": "A", "text": "Hello World"},
    ]

    hypothesis = [
        {"speaker": "A", "text": "hello world"},
    ]

    # With normalization (default)
    benchmark_norm = STTBenchmark(normalize=True)
    results_norm = benchmark_norm.evaluate(reference, hypothesis, calculate_der=False)

    # Without normalization
    benchmark_no_norm = STTBenchmark(normalize=False)
    results_no_norm = benchmark_no_norm.evaluate(reference, hypothesis, calculate_der=False)

    # WER should be different due to case sensitivity without normalization
    # (though in this case whisper normalizer handles case, so results may be similar)
    assert "wer" in results_norm
    assert "wer" in results_no_norm


def test_with_timestamps():
    """Test evaluation with timestamps."""
    reference = [
        {"speaker": "A", "text": "Hello", "start_time": 0.0, "end_time": 1.0},
        {"speaker": "B", "text": "Hi", "start_time": 1.0, "end_time": 2.0},
    ]

    hypothesis = [
        {"speaker": "A", "text": "hello", "start_time": 0.0, "end_time": 1.0},
        {"speaker": "B", "text": "hi", "start_time": 1.0, "end_time": 2.0},
    ]

    benchmark = STTBenchmark()
    results = benchmark.evaluate(reference, hypothesis)

    # Should include DER metrics
    assert "der" in results or "speaker_error_rate" in results


def test_transcript_objects():
    """Test using Transcript objects instead of lists."""
    reference_data = [
        {"speaker": "A", "text": "Hello world"},
    ]

    hypothesis_data = [
        {"speaker": "A", "text": "hello world"},
    ]

    # Create Transcript objects
    reference = Transcript.from_list(reference_data)
    hypothesis = Transcript.from_list(hypothesis_data)

    benchmark = STTBenchmark()
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    assert "wer" in results


def test_empty_transcripts():
    """Test handling of empty transcripts."""
    reference = []
    hypothesis = []

    benchmark = STTBenchmark()

    # Should handle empty transcripts gracefully
    # (may raise error or return 0/nan depending on implementation)
    try:
        results = benchmark.evaluate(reference, hypothesis, calculate_der=False)
        # If it doesn't raise an error, check results are valid
        assert isinstance(results, dict)
    except (ValueError, ZeroDivisionError):
        # Expected for empty transcripts
        pass


def test_mismatched_speaker_count():
    """Test with different number of speakers in reference and hypothesis."""
    reference = [
        {"speaker": "A", "text": "Hello"},
        {"speaker": "B", "text": "Hi"},
        {"speaker": "C", "text": "Hey"},
    ]

    hypothesis = [
        {"speaker": "spk_0", "text": "hello"},
        {"speaker": "spk_1", "text": "hi hey"},  # Combined speakers
    ]

    benchmark = STTBenchmark()
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    # Should still return results
    assert "wer" in results
    assert "cp_wer" in results


def test_custom_threshold():
    """Test custom speaker matching threshold."""
    reference = [
        {"speaker": "Alice", "text": "Hello world"},
    ]

    hypothesis = [
        {"speaker": "spk_0", "text": "hello world"},
    ]

    # Very high threshold
    benchmark_high = STTBenchmark(speaker_matching_threshold=95.0)
    results_high = benchmark_high.evaluate(reference, hypothesis, calculate_der=False)

    # Low threshold
    benchmark_low = STTBenchmark(speaker_matching_threshold=50.0)
    results_low = benchmark_low.evaluate(reference, hypothesis, calculate_der=False)

    # Both should return valid results
    assert "wer" in results_high
    assert "wer" in results_low


def test_diarization_only():
    """Test diarization-only evaluation."""
    reference = [
        {"speaker": "A", "text": "Hello"},
        {"speaker": "B", "text": "Hi"},
    ]

    hypothesis = [
        {"speaker": "A", "text": "hello"},
        {"speaker": "B", "text": "hi"},
    ]

    benchmark = STTBenchmark()
    results = benchmark.evaluate_diarization_only(reference, hypothesis)

    # Should include diarization metrics
    assert "cp_wer" in results
    # May or may not have DER depending on timestamps
    assert "wer" not in results or results.get("wer") is None
