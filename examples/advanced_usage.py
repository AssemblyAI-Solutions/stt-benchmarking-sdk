"""Advanced usage examples for STT Benchmarking SDK."""

from stt_benchmarking import STTBenchmark, Transcript
from stt_benchmarking.speaker_matcher import SpeakerMatcher
from stt_benchmarking.normalizer import TextNormalizer
from stt_benchmarking.metrics import WERMetrics, CPWERMetrics, DERMetrics


def example_custom_speaker_matching():
    """Example with custom speaker matching threshold."""
    print("=" * 60)
    print("Custom Speaker Matching Threshold")
    print("=" * 60)

    reference = [
        {"speaker": "Doctor_Smith", "text": "Please describe your symptoms in detail"},
        {"speaker": "Patient_Jones", "text": "I have been experiencing severe headaches"},
        {"speaker": "Doctor_Smith", "text": "How long have these headaches persisted"},
    ]

    hypothesis = [
        {"speaker": "spk_A", "text": "please describe your symptoms in detail"},
        {"speaker": "spk_B", "text": "i have been experiencing severe headaches"},
        {"speaker": "spk_A", "text": "how long have these headaches persisted"},
    ]

    # Use a higher threshold for more strict matching
    benchmark = STTBenchmark(speaker_matching_threshold=90.0)

    mapping = benchmark.get_speaker_mapping(reference, hypothesis)
    print("\nSpeaker Mapping (90% threshold):")
    for hyp, ref in mapping.items():
        print(f"  {hyp} -> {ref}")

    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)
    print(f"\nCP-WER: {results['cp_wer']:.2%}")


def example_manual_speaker_matching():
    """Example showing manual control over speaker matching."""
    print("\n" + "=" * 60)
    print("Manual Speaker Matching")
    print("=" * 60)

    reference_data = [
        {"speaker": "Alice", "text": "Hello world"},
        {"speaker": "Bob", "text": "Hi there Alice"},
        {"speaker": "Alice", "text": "How are you Bob"},
    ]

    hypothesis_data = [
        {"speaker": "Speaker_1", "text": "hello world"},
        {"speaker": "Speaker_2", "text": "hi there alice"},
        {"speaker": "Speaker_1", "text": "how are you bob"},
    ]

    # Convert to Transcript objects
    reference = Transcript.from_list(reference_data)
    hypothesis = Transcript.from_list(hypothesis_data)

    # Manually match speakers
    matcher = SpeakerMatcher(threshold=70.0)
    mapping = matcher.match_speakers(reference, hypothesis)

    print("\nAutomatic Speaker Mapping:")
    for hyp, ref in mapping.items():
        print(f"  {hyp} -> {ref}")

    # Apply the mapping
    aligned_hypothesis = matcher.apply_speaker_mapping(hypothesis, mapping)

    # Now evaluate with speaker matching disabled
    benchmark = STTBenchmark(match_speakers=False)
    results = benchmark.evaluate(reference, aligned_hypothesis, calculate_der=False)

    print(f"\nWER: {results['wer']:.2%}")
    print(f"CP-WER: {results['cp_wer']:.2%}")


def example_selective_metrics():
    """Example calculating specific metrics only."""
    print("\n" + "=" * 60)
    print("Selective Metrics Calculation")
    print("=" * 60)

    reference = [
        {"speaker": "A", "text": "The quick brown fox jumps over the lazy dog"},
        {"speaker": "B", "text": "This is a test of the emergency broadcast system"},
    ]

    hypothesis = [
        {"speaker": "A", "text": "the quick brown fox jumps over the lazy dog"},
        {"speaker": "B", "text": "this is a test of the emergency broadcast system"},
    ]

    benchmark = STTBenchmark()

    # Calculate only WER
    print("\n1. WER Only:")
    wer_results = benchmark.evaluate_wer_only(reference, hypothesis)
    print(f"   WER: {wer_results['wer']:.2%}")
    print(f"   MER: {wer_results['mer']:.2%}")

    # Calculate only diarization metrics
    print("\n2. Diarization Metrics Only:")
    diar_results = benchmark.evaluate_diarization_only(reference, hypothesis)
    print(f"   CP-WER: {diar_results['cp_wer']:.2%}")


def example_batch_evaluation():
    """Example evaluating multiple transcripts."""
    print("\n" + "=" * 60)
    print("Batch Evaluation")
    print("=" * 60)

    # Multiple test cases
    test_cases = [
        {
            "name": "Conversation 1",
            "reference": [
                {"speaker": "A", "text": "Hello how are you"},
                {"speaker": "B", "text": "I am fine thanks"},
            ],
            "hypothesis": [
                {"speaker": "spk_0", "text": "hello how are you"},
                {"speaker": "spk_1", "text": "i am fine thanks"},
            ]
        },
        {
            "name": "Conversation 2",
            "reference": [
                {"speaker": "A", "text": "What is your name"},
                {"speaker": "B", "text": "My name is John"},
            ],
            "hypothesis": [
                {"speaker": "spk_0", "text": "what is your name"},
                {"speaker": "spk_1", "text": "my name is john"},
            ]
        },
    ]

    benchmark = STTBenchmark()

    print("\nEvaluating multiple transcripts:")
    all_results = []

    for test in test_cases:
        results = benchmark.evaluate(
            test["reference"],
            test["hypothesis"],
            calculate_der=False
        )
        all_results.append(results)

        print(f"\n  {test['name']}:")
        print(f"    WER: {results['wer']:.2%}")
        print(f"    CP-WER: {results['cp_wer']:.2%}")

    # Calculate average metrics
    avg_wer = sum(r['wer'] for r in all_results) / len(all_results)
    avg_cp_wer = sum(r['cp_wer'] for r in all_results) / len(all_results)

    print(f"\n  Average WER: {avg_wer:.2%}")
    print(f"  Average CP-WER: {avg_cp_wer:.2%}")


def example_direct_metrics_usage():
    """Example using metric classes directly."""
    print("\n" + "=" * 60)
    print("Direct Metrics Usage")
    print("=" * 60)

    reference_data = [
        {"speaker": "A", "text": "Hello world"},
        {"speaker": "B", "text": "Hi there"},
    ]

    hypothesis_data = [
        {"speaker": "A", "text": "hello world"},
        {"speaker": "B", "text": "hi there"},
    ]

    # Create Transcript objects
    reference = Transcript.from_list(reference_data)
    hypothesis = Transcript.from_list(hypothesis_data)

    # Normalize first
    normalizer = TextNormalizer()
    reference = normalizer.normalize_transcript(reference)
    hypothesis = normalizer.normalize_transcript(hypothesis)

    # Calculate WER directly
    wer_results = WERMetrics.calculate(reference, hypothesis)
    print(f"\nWER Results:")
    print(f"  WER: {wer_results['wer']:.2%}")
    print(f"  Substitutions: {wer_results['substitutions']}")
    print(f"  Deletions: {wer_results['deletions']}")
    print(f"  Insertions: {wer_results['insertions']}")

    # Calculate CP-WER directly
    cp_wer_results = CPWERMetrics.calculate(reference, hypothesis)
    print(f"\nCP-WER Results:")
    print(f"  CP-WER: {cp_wer_results['cp_wer']:.2%}")
    print(f"  Total Errors: {cp_wer_results['total_errors']}")
    print(f"  Total Reference Words: {cp_wer_results['total_reference_words']}")


if __name__ == "__main__":
    example_custom_speaker_matching()
    example_manual_speaker_matching()
    example_selective_metrics()
    example_batch_evaluation()
    example_direct_metrics_usage()
