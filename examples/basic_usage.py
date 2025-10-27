"""Basic usage example for STT Benchmarking SDK."""

from stt_benchmarking import STTBenchmark

# Example 1: Basic evaluation without timestamps
def example_basic_evaluation():
    """Basic evaluation of WER and CP-WER."""
    print("=" * 60)
    print("Example 1: Basic Evaluation (no timestamps)")
    print("=" * 60)

    # Reference transcript (ground truth)
    reference = [
        {"speaker": "Alice", "text": "Hello world how are you today"},
        {"speaker": "Bob", "text": "I am doing great thank you"},
        {"speaker": "Alice", "text": "That's wonderful to hear"},
    ]

    # Hypothesis transcript (from STT vendor)
    # Note: Different speaker labels that will be auto-matched
    hypothesis = [
        {"speaker": "spk_0", "text": "hello world how are you today"},
        {"speaker": "spk_1", "text": "i am doing great thank you"},
        {"speaker": "spk_0", "text": "thats wonderful to hear"},
    ]

    # Initialize benchmark
    benchmark = STTBenchmark()

    # Run evaluation
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    # Display results
    print(f"\nWER: {results['wer']:.2%}")
    print(f"CP-WER: {results['cp_wer']:.2%}")
    print(f"MER: {results['mer']:.2%}")
    print(f"WIL: {results['wil']:.2%}")
    print(f"\nError breakdown:")
    print(f"  Substitutions: {results['substitutions']}")
    print(f"  Deletions: {results['deletions']}")
    print(f"  Insertions: {results['insertions']}")
    print(f"  Hits: {results['hits']}")


# Example 2: Evaluation with timestamps for DER
def example_with_timestamps():
    """Evaluation including DER with timestamps."""
    print("\n" + "=" * 60)
    print("Example 2: Evaluation with Timestamps (including DER)")
    print("=" * 60)

    # Reference with timestamps
    reference = [
        {"speaker": "Alice", "text": "Hello world", "start_time": 0.0, "end_time": 1.5},
        {"speaker": "Bob", "text": "Hi there", "start_time": 1.5, "end_time": 2.5},
        {"speaker": "Alice", "text": "How are you", "start_time": 2.5, "end_time": 4.0},
    ]

    # Hypothesis with timestamps
    hypothesis = [
        {"speaker": "spk_0", "text": "hello world", "start_time": 0.0, "end_time": 1.5},
        {"speaker": "spk_1", "text": "hi there", "start_time": 1.6, "end_time": 2.6},
        {"speaker": "spk_0", "text": "how are you", "start_time": 2.5, "end_time": 4.0},
    ]

    benchmark = STTBenchmark()
    results = benchmark.evaluate(reference, hypothesis)

    print(f"\nWER: {results['wer']:.2%}")
    print(f"CP-WER: {results['cp_wer']:.2%}")
    print(f"DER: {results['der']:.2%}")
    print(f"\nDER Components:")
    print(f"  False Alarm: {results['false_alarm']:.2%}")
    print(f"  Missed Detection: {results['missed_detection']:.2%}")
    print(f"  Confusion: {results['confusion']:.2%}")


# Example 3: Check speaker mapping
def example_speaker_mapping():
    """Show how speaker labels are matched."""
    print("\n" + "=" * 60)
    print("Example 3: Speaker Label Matching")
    print("=" * 60)

    reference = [
        {"speaker": "Doctor", "text": "What symptoms are you experiencing"},
        {"speaker": "Patient", "text": "I have a headache and fever"},
        {"speaker": "Doctor", "text": "How long have you had these symptoms"},
    ]

    hypothesis = [
        {"speaker": "Speaker_1", "text": "what symptoms are you experiencing"},
        {"speaker": "Speaker_2", "text": "i have a headache and fever"},
        {"speaker": "Speaker_1", "text": "how long have you had these symptoms"},
    ]

    benchmark = STTBenchmark()
    mapping = benchmark.get_speaker_mapping(reference, hypothesis)

    print("\nSpeaker Mapping:")
    for hyp_speaker, ref_speaker in mapping.items():
        print(f"  {hyp_speaker} -> {ref_speaker}")

    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)
    print(f"\nWER: {results['wer']:.2%}")
    print(f"CP-WER: {results['cp_wer']:.2%}")


# Example 4: Disable normalization and speaker matching
def example_without_preprocessing():
    """Evaluation without text normalization or speaker matching."""
    print("\n" + "=" * 60)
    print("Example 4: Without Preprocessing")
    print("=" * 60)

    reference = [
        {"speaker": "Alice", "text": "Hello world"},
        {"speaker": "Bob", "text": "Hi there"},
    ]

    hypothesis = [
        {"speaker": "Alice", "text": "hello world"},  # Same speaker labels
        {"speaker": "Bob", "text": "hi there"},
    ]

    # Disable normalization and speaker matching
    benchmark = STTBenchmark(normalize=False, match_speakers=False)
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    print(f"\nWER (without normalization): {results['wer']:.2%}")


if __name__ == "__main__":
    example_basic_evaluation()
    example_with_timestamps()
    example_speaker_mapping()
    example_without_preprocessing()
