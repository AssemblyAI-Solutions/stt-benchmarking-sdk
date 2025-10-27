"""
Example of using LLM-based "vibe eval" for qualitative transcription assessment.

This shows how to use AssemblyAI's LLM Gateway to get qualitative feedback
on transcription quality from multiple state-of-the-art language models.
"""

import os
import json
from pathlib import Path
from stt_benchmarking import (
    STTBenchmark,
    BatchEvaluator,
    LLMEvaluator,
    ResultsExporter,
    evaluate_vendor_comparison
)


def setup_example_data():
    """Create example transcripts for vibe eval demonstration."""
    Path("vibe_eval_data/truth").mkdir(parents=True, exist_ok=True)
    Path("vibe_eval_data/vendors/vendor_a").mkdir(parents=True, exist_ok=True)
    Path("vibe_eval_data/vendors/vendor_b").mkdir(parents=True, exist_ok=True)
    Path("vibe_eval_data/results").mkdir(parents=True, exist_ok=True)

    # Create sample transcript with timestamps
    truth = [
        {"speaker": "Teacher", "text": "Good morning class, today we're going to learn about photosynthesis", "start_time": 0.0, "end_time": 4.5},
        {"speaker": "Student", "text": "What is photosynthesis exactly?", "start_time": 5.0, "end_time": 7.0},
        {"speaker": "Teacher", "text": "Photosynthesis is the process by which plants convert sunlight into energy", "start_time": 7.5, "end_time": 12.0},
        {"speaker": "Student", "text": "That's really interesting, how does it work?", "start_time": 12.5, "end_time": 15.0},
    ]

    # Vendor A: Good quality
    vendor_a = [
        {"speaker": "spk_0", "text": "good morning class today were going to learn about photosynthesis", "start_time": 0.0, "end_time": 4.5},
        {"speaker": "spk_1", "text": "what is photosynthesis exactly", "start_time": 5.0, "end_time": 7.0},
        {"speaker": "spk_0", "text": "photosynthesis is the process by which plants convert sunlight into energy", "start_time": 7.5, "end_time": 12.0},
        {"speaker": "spk_1", "text": "thats really interesting how does it work", "start_time": 12.5, "end_time": 15.0},
    ]

    # Vendor B: Lower quality with errors
    vendor_b = [
        {"speaker": "Speaker_1", "text": "good morning clash today were going to learn about photo sin thesis", "start_time": 0.0, "end_time": 4.8},
        {"speaker": "Speaker_1", "text": "what is photosynthesis exactly that really interesting", "start_time": 5.0, "end_time": 15.2},  # Wrong speaker + merged utterances
        {"speaker": "Speaker_2", "text": "photosynthesis is the process which plants convert sun into energy how does it work", "start_time": 7.3, "end_time": 15.0},  # Mixed up
    ]

    with open("vibe_eval_data/truth/lesson_001.json", "w") as f:
        json.dump(truth, f, indent=2)

    with open("vibe_eval_data/vendors/vendor_a/lesson_001.json", "w") as f:
        json.dump(vendor_a, f, indent=2)

    with open("vibe_eval_data/vendors/vendor_b/lesson_001.json", "w") as f:
        json.dump(vendor_b, f, indent=2)

    print("✓ Example data created\n")


def example_single_vendor_vibe_eval():
    """Example: Evaluate a single vendor with LLM."""
    print("=" * 70)
    print("Example 1: Single Vendor Vibe Eval")
    print("=" * 70)

    # Check for API key
    if not os.environ.get('ASSEMBLYAI_API_KEY'):
        print("\n⚠️  ASSEMBLYAI_API_KEY not set. Skipping LLM evaluation.")
        print("   Set your API key: export ASSEMBLYAI_API_KEY='your-key-here'")
        return

    # Load transcripts
    with open("vibe_eval_data/truth/lesson_001.json") as f:
        truth_data = json.load(f)

    with open("vibe_eval_data/vendors/vendor_a/lesson_001.json") as f:
        vendor_a_data = json.load(f)

    from stt_benchmarking import Transcript
    truth = Transcript.from_list(truth_data)
    vendor_a = Transcript.from_list(vendor_a_data)

    # Initialize LLM evaluator
    print("\nInitializing LLM evaluator...")
    evaluator = LLMEvaluator(
        evaluator_models=[
            "claude-sonnet-4-5-20250929",
            "gpt-5",
            "gemini-2.5-pro"
        ]
    )

    # Run evaluation
    result = evaluator.evaluate_and_score(
        reference=truth,
        hypothesis=vendor_a,
        vendor_name="Vendor A",
        file_identifier="lesson_001"
    )

    # Display results
    print(f"\n{'='*70}")
    print(f"Vibe Eval Results for Vendor A")
    print(f"{'='*70}\n")

    print(f"📊 Vibe Score: {result['vibe_score']}/10\n")

    print("🤖 Consolidated Evaluation:")
    print("-" * 70)
    print(result['consolidation'])
    print()

    # Save detailed evaluation
    output_path = Path("vibe_eval_data/results/vendor_a_vibe_eval.txt")
    with open(output_path, "w") as f:
        f.write(f"VIBE EVAL: Vendor A - lesson_001\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Vibe Score: {result['vibe_score']}/10\n\n")
        f.write(f"{'='*70}\n")
        f.write("CONSOLIDATED EVALUATION\n")
        f.write(f"{'='*70}\n\n")
        f.write(result['consolidation'])
        f.write("\n\n")

        for model, evaluation in result['individual_evaluations'].items():
            f.write(f"{'='*70}\n")
            f.write(f"EVALUATION FROM: {model.upper()}\n")
            f.write(f"{'='*70}\n\n")
            f.write(evaluation)
            f.write("\n\n")

    print(f"✓ Detailed evaluation saved to: {output_path}")


def example_vendor_comparison_vibe_eval():
    """Example: Compare multiple vendors with LLM."""
    print("\n\n" + "=" * 70)
    print("Example 2: Multi-Vendor Comparison Vibe Eval")
    print("=" * 70)

    if not os.environ.get('ASSEMBLYAI_API_KEY'):
        print("\n⚠️  ASSEMBLYAI_API_KEY not set. Skipping LLM evaluation.")
        return

    # Load transcripts
    with open("vibe_eval_data/truth/lesson_001.json") as f:
        truth_data = json.load(f)

    with open("vibe_eval_data/vendors/vendor_a/lesson_001.json") as f:
        vendor_a_data = json.load(f)

    with open("vibe_eval_data/vendors/vendor_b/lesson_001.json") as f:
        vendor_b_data = json.load(f)

    from stt_benchmarking import Transcript
    truth = Transcript.from_list(truth_data)
    vendor_a = Transcript.from_list(vendor_a_data)
    vendor_b = Transcript.from_list(vendor_b_data)

    # Initialize evaluator
    evaluator = LLMEvaluator()

    # Compare vendors
    comparison = evaluate_vendor_comparison(
        evaluator=evaluator,
        reference=truth,
        vendor_transcripts={
            "Vendor A": vendor_a,
            "Vendor B": vendor_b
        },
        file_identifier="lesson_001"
    )

    # Display results
    print(f"\n{'='*70}")
    print("Comparative Evaluation")
    print(f"{'='*70}\n")

    print(comparison['comparison'])

    if comparison['vendor_scores']:
        print(f"\n{'='*70}")
        print("Extracted Vibe Scores:")
        print(f"{'='*70}\n")
        for vendor, score in comparison['vendor_scores'].items():
            print(f"  {vendor}: {score}/10")

    # Save comparison
    output_path = Path("vibe_eval_data/results/vendor_comparison_vibe_eval.txt")
    with open(output_path, "w") as f:
        f.write(f"VIBE EVAL COMPARISON: lesson_001\n")
        f.write(f"{'='*70}\n\n")
        f.write(comparison['comparison'])
        f.write("\n")

    print(f"\n✓ Comparison saved to: {output_path}")


def example_batch_with_vibe_eval():
    """Example: Batch processing with optional vibe eval."""
    print("\n\n" + "=" * 70)
    print("Example 3: Batch Processing + Vibe Eval")
    print("=" * 70)

    # Run standard benchmarking first
    benchmark = STTBenchmark()
    vendors = ["vendor_a", "vendor_b"]

    print("\n📊 Running standard metrics...")

    all_results = {}

    for vendor in vendors:
        batch = BatchEvaluator(benchmark)

        # Load and process
        with open("vibe_eval_data/truth/lesson_001.json") as f:
            truth = json.load(f)

        with open(f"vibe_eval_data/vendors/{vendor}/lesson_001.json") as f:
            hypothesis = json.load(f)

        results = batch.add_evaluation(
            "lesson_001.json",
            truth,
            hypothesis,
            calculate_der=True
        )

        all_results[vendor] = results

        print(f"\n{vendor}:")
        print(f"  WER: {results['wer']:.2%}")
        print(f"  CP-WER: {results['cp_wer']:.2%}")
        print(f"  DER: {results.get('der', 'N/A')}")
        print(f"  Speakers: {results['ref_num_speakers']} → {results['hyp_num_speakers']}")

    # Now add vibe scores if API key available
    if os.environ.get('ASSEMBLYAI_API_KEY'):
        print("\n\n🤖 Running LLM vibe eval...")

        evaluator = LLMEvaluator(
            evaluator_models=["claude-sonnet-4-5-20250929"]  # Just one for speed
        )

        from stt_benchmarking import Transcript

        with open("vibe_eval_data/truth/lesson_001.json") as f:
            truth = Transcript.from_list(json.load(f))

        for vendor in vendors:
            with open(f"vibe_eval_data/vendors/{vendor}/lesson_001.json") as f:
                hypothesis = Transcript.from_list(json.load(f))

            vibe_result = evaluator.evaluate_and_score(
                reference=truth,
                hypothesis=hypothesis,
                vendor_name=vendor,
                file_identifier="lesson_001"
            )

            # Add vibe score to results
            all_results[vendor]['vibe_score'] = vibe_result['vibe_score']

            print(f"\n{vendor}:")
            print(f"  Vibe Score: {vibe_result['vibe_score']}/10")

        # Export with vibe scores
        results_list = []
        for vendor, results in all_results.items():
            results['vendor'] = vendor
            results_list.append(results)

        ResultsExporter.to_csv(
            results_list,
            "vibe_eval_data/results/combined_metrics_with_vibe.csv",
            file_identifiers=[r['vendor'] for r in results_list]
        )

        print(f"\n✓ Combined metrics (with vibe scores) saved to CSV")


def main():
    """Run all vibe eval examples."""
    print("\n" + "=" * 70)
    print("LLM Vibe Eval Examples")
    print("=" * 70)
    print("\nThis demonstrates qualitative evaluation using multiple LLMs")
    print("via AssemblyAI's LLM Gateway.\n")

    # Setup
    setup_example_data()

    # Run examples
    example_single_vendor_vibe_eval()
    example_vendor_comparison_vibe_eval()
    example_batch_with_vibe_eval()

    # Cleanup
    print("\n" + "=" * 70)
    print("✓ All examples complete!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - vibe_eval_data/results/vendor_a_vibe_eval.txt")
    print("  - vibe_eval_data/results/vendor_comparison_vibe_eval.txt")
    print("  - vibe_eval_data/results/combined_metrics_with_vibe.csv")

    import shutil
    response = input("\n\nRemove example data? (y/n): ")
    if response.lower() == 'y':
        shutil.rmtree("vibe_eval_data")
        print("✓ Example data removed")


if __name__ == "__main__":
    main()
