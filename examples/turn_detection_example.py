"""Turn detection benchmarking example.

Demonstrates how to benchmark turn-end detection accuracy using
AssemblyAI's streaming APIs (Universal-3 and Universal-3 Pro).

Requirements:
    - ASSEMBLYAI_API_KEY environment variable set
    - Audio files in 16kHz mono 16-bit PCM WAV format
    - webrtcvad installed (pip install webrtcvad)
"""

import os
from dotenv import load_dotenv

load_dotenv()

from stt_benchmarking.turn_detection import (
    TurnSample,
    TurnDetectionBenchmark,
    TurnDetectionMetrics,
    TurnDetectionExporter,
)

API_KEY = os.getenv("ASSEMBLYAI_API_KEY")


def example_single_sample():
    """Evaluate a single audio file."""
    from stt_benchmarking.turn_detection import AssemblyAIStreamingDetector

    detector = AssemblyAIStreamingDetector(
        api_key=API_KEY,
        model="universal-streaming-multilingual",  # or "u3-rt-pro"
        preset="balanced",
    )

    result = detector.process_audio_file(
        "path/to/audio.wav",
        vad_window_ms=1000,
        verbose=True,
    )

    print(f"Turn-end detected: {result.end_of_turn_detected}")
    print(f"Confidence: {result.end_of_turn_confidence:.4f}")
    print(f"Speech end time: {result.speech_end_time:.3f}s")
    print(f"Transcript: {result.transcript[:80]}...")


def example_batch_benchmark():
    """Run a batch benchmark with multiple samples and presets."""

    # Option 1: Load from JSON file (pipecat dataset format)
    # benchmark.evaluate_dataset("data/pipecat_samples.json")

    # Option 2: Construct samples manually
    samples = [
        TurnSample(
            id="sample-001",
            audio_path="data/audio/sample_001.wav",
            ground_truth=True,  # turn-shift expected
            turn_label="TURN_SHIFT",
        ),
        TurnSample(
            id="sample-002",
            audio_path="data/audio/sample_002.wav",
            ground_truth=False,  # turn-hold expected
            turn_label="TURN_HOLD",
        ),
    ]

    # Benchmark universal-streaming-multilingual
    benchmark_multilingual = TurnDetectionBenchmark(
        api_key=API_KEY,
        model="universal-streaming-multilingual",
        presets=["aggressive", "balanced", "conservative"],
        vad_window_ms=1000,
        max_workers=3,
    )

    results_multilingual = benchmark_multilingual.evaluate_samples(samples)

    # Export results
    TurnDetectionExporter.to_csv(results_multilingual, "results/multilingual_per_sample.csv")
    TurnDetectionExporter.metrics_to_csv(results_multilingual, "results/metrics.csv")
    TurnDetectionExporter.to_json(results_multilingual, "results/multilingual_full_results.json")

    # Benchmark u3-rt-pro
    benchmark_pro = TurnDetectionBenchmark(
        api_key=API_KEY,
        model="u3-rt-pro",
        presets=["aggressive", "balanced", "conservative"],
        vad_window_ms=1000,
        max_workers=3,
    )

    results_pro = benchmark_pro.evaluate_samples(samples)

    # Append pro metrics to same CSV for comparison
    TurnDetectionExporter.metrics_to_csv(results_pro, "results/metrics.csv", append=True)
    TurnDetectionExporter.to_json(results_pro, "results/u3_pro_full_results.json")


def example_dataset_benchmark():
    """Load and benchmark a dataset JSON file (pipecat format)."""

    benchmark = TurnDetectionBenchmark(
        api_key=API_KEY,
        model="u3-rt-pro",
        vad_window_ms=700,
        max_workers=5,
    )

    results = benchmark.evaluate_dataset(
        "data/pipecat_samples.json",
        limit=10,  # test first 10 samples
    )

    # Print metrics per preset
    for preset_name, preset_data in results["presets"].items():
        m = preset_data["metrics"]
        print(f"\n{preset_name}:")
        print(f"  Accuracy:  {m['accuracy']:.1%}")
        print(f"  Precision: {m['precision']:.1%}")
        print(f"  Recall:    {m['recall']:.1%}")
        print(f"  F1:        {m['f1_score']:.1%}")
        print(f"  TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']}")


def example_metrics_only():
    """Use TurnDetectionMetrics directly with pre-existing results."""
    from stt_benchmarking.turn_detection import TurnDetectionResult

    # Simulate results (e.g. loaded from a previous run)
    results = [
        TurnDetectionResult(end_of_turn_detected=True, end_of_turn_confidence=0.85,
                            transcript="hello", audio_duration_ms=3000, speech_end_time=2.5),
        TurnDetectionResult(end_of_turn_detected=False, end_of_turn_confidence=0.2,
                            transcript="I was thinking", audio_duration_ms=4000, speech_end_time=3.1),
        TurnDetectionResult(end_of_turn_detected=True, end_of_turn_confidence=0.9,
                            transcript="yes", audio_duration_ms=1500, speech_end_time=1.0),
        TurnDetectionResult(end_of_turn_detected=False, end_of_turn_confidence=0.1,
                            transcript="well um", audio_duration_ms=2000, speech_end_time=1.5),
    ]
    ground_truths = [True, False, True, True]  # last one is a false negative

    metrics = TurnDetectionMetrics.calculate(results, ground_truths)
    print("Metrics:", metrics)

    # Per-sample evaluation
    for i, (result, gt) in enumerate(zip(results, ground_truths)):
        sample = TurnDetectionMetrics.calculate_per_sample(result, gt)
        print(f"  Sample {i}: {sample['classification']} (correct={sample['correct']})")


if __name__ == "__main__":
    # Run the metrics-only example (no API key needed)
    example_metrics_only()

    # Uncomment to run live benchmarks (requires API key + audio files):
    # example_single_sample()
    # example_batch_benchmark()
    # example_dataset_benchmark()
