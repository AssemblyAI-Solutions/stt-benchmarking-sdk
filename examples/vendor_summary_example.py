"""Example showing vendor summary CSV with speaker identification accuracy."""

import json
from pathlib import Path
from stt_benchmarking import STTBenchmark, BatchEvaluator, ResultsExporter


def setup_example_data():
    """Create example data with varying speaker counts."""
    Path("vendor_summary_data/truth").mkdir(parents=True, exist_ok=True)
    Path("vendor_summary_data/vendors/vendor_a").mkdir(parents=True, exist_ok=True)
    Path("vendor_summary_data/vendors/vendor_b").mkdir(parents=True, exist_ok=True)
    Path("vendor_summary_data/results").mkdir(parents=True, exist_ok=True)

    # Create 5 audio files with different speaker counts
    files_data = [
        # audio_001: 2 speakers
        {
            "truth": [
                {"speaker": "Doctor", "text": "Hello how are you feeling"},
                {"speaker": "Patient", "text": "I am feeling much better thank you"},
            ],
            "vendor_a": [
                {"speaker": "spk_0", "text": "hello how are you feeling"},
                {"speaker": "spk_1", "text": "i am feeling much better thank you"},
            ],
            "vendor_b": [  # Incorrect: 3 speakers instead of 2
                {"speaker": "Speaker_1", "text": "hello how"},
                {"speaker": "Speaker_2", "text": "are you feeling"},
                {"speaker": "Speaker_3", "text": "i am feeling much better thank you"},
            ],
        },
        # audio_002: 3 speakers
        {
            "truth": [
                {"speaker": "Doctor", "text": "Please describe your symptoms"},
                {"speaker": "Patient", "text": "I have a headache"},
                {"speaker": "Nurse", "text": "Let me check your temperature"},
            ],
            "vendor_a": [
                {"speaker": "spk_0", "text": "please describe your symptoms"},
                {"speaker": "spk_1", "text": "i have a headache"},
                {"speaker": "spk_2", "text": "let me check your temperature"},
            ],
            "vendor_b": [  # Incorrect: 2 speakers instead of 3
                {"speaker": "Speaker_1", "text": "please describe your symptoms"},
                {"speaker": "Speaker_2", "text": "i have a headache let me check your temperature"},
            ],
        },
        # audio_003: 2 speakers
        {
            "truth": [
                {"speaker": "Alice", "text": "What do you think about this"},
                {"speaker": "Bob", "text": "I think it looks great"},
            ],
            "vendor_a": [
                {"speaker": "spk_0", "text": "what do you think about this"},
                {"speaker": "spk_1", "text": "i think it looks great"},
            ],
            "vendor_b": [
                {"speaker": "Speaker_1", "text": "what do you think about this"},
                {"speaker": "Speaker_2", "text": "i think it looks great"},
            ],
        },
        # audio_004: 4 speakers
        {
            "truth": [
                {"speaker": "A", "text": "Welcome everyone"},
                {"speaker": "B", "text": "Thank you for having us"},
                {"speaker": "C", "text": "Happy to be here"},
                {"speaker": "D", "text": "Lets get started"},
            ],
            "vendor_a": [
                {"speaker": "spk_0", "text": "welcome everyone"},
                {"speaker": "spk_1", "text": "thank you for having us"},
                {"speaker": "spk_2", "text": "happy to be here"},
                {"speaker": "spk_3", "text": "lets get started"},
            ],
            "vendor_b": [  # Incorrect: 3 speakers instead of 4
                {"speaker": "Speaker_1", "text": "welcome everyone"},
                {"speaker": "Speaker_2", "text": "thank you for having us happy to be here"},
                {"speaker": "Speaker_3", "text": "lets get started"},
            ],
        },
        # audio_005: 2 speakers
        {
            "truth": [
                {"speaker": "X", "text": "Good morning"},
                {"speaker": "Y", "text": "Good morning to you too"},
            ],
            "vendor_a": [
                {"speaker": "spk_0", "text": "good morning"},
                {"speaker": "spk_1", "text": "good morning to you too"},
            ],
            "vendor_b": [
                {"speaker": "Speaker_1", "text": "good morning"},
                {"speaker": "Speaker_2", "text": "good morning to you too"},
            ],
        },
    ]

    for i, data in enumerate(files_data, 1):
        filename = f"audio_{i:03d}.json"

        with open(f"vendor_summary_data/truth/{filename}", "w") as f:
            json.dump(data["truth"], f, indent=2)

        with open(f"vendor_summary_data/vendors/vendor_a/{filename}", "w") as f:
            json.dump(data["vendor_a"], f, indent=2)

        with open(f"vendor_summary_data/vendors/vendor_b/{filename}", "w") as f:
            json.dump(data["vendor_b"], f, indent=2)

    print("✓ Example data created\n")


def run_benchmark_with_summaries():
    """Run benchmark and generate both detailed and summary CSVs."""
    print("=" * 70)
    print("Vendor Summary Example")
    print("=" * 70)

    benchmark = STTBenchmark()
    vendors = ["vendor_a", "vendor_b"]

    all_summaries = []

    for vendor in vendors:
        print(f"\n📊 Processing {vendor}...")
        batch = BatchEvaluator(benchmark)

        truth_dir = "vendor_summary_data/truth/"
        vendor_dir = f"vendor_summary_data/vendors/{vendor}/"

        # Process all files
        import os
        for filename in sorted(os.listdir(truth_dir)):
            if not filename.endswith(".json"):
                continue

            with open(f"{truth_dir}/{filename}") as f:
                truth = json.load(f)
            with open(f"{vendor_dir}/{filename}") as f:
                hypothesis = json.load(f)

            results = batch.add_evaluation(
                filename,
                truth,
                hypothesis,
                calculate_der=False
            )

            print(f"   ✓ {filename}: WER={results['wer']:.2%}, "
                  f"Speakers: {results['ref_num_speakers']} → {results['hyp_num_speakers']} "
                  f"{'✓' if results['speaker_count_correct'] else '✗'}")

        # Export detailed results (per file)
        detailed_csv = f"vendor_summary_data/results/{vendor}_detailed.csv"
        batch.export_to_csv(detailed_csv, precision=4)
        print(f"\n   📄 Detailed results: {detailed_csv}")

        # Get and display summary
        summary = batch.get_vendor_summary(vendor)
        all_summaries.append(summary)

        print(f"\n   📈 Summary for {vendor}:")
        print(f"      Files processed: {summary['num_files']}")
        print(f"      Average WER: {summary['avg_wer']:.2%}")
        print(f"      Average CP-WER: {summary['avg_cp_wer']:.2%}")
        print(f"      Speaker ID Accuracy: {summary['speaker_id_accuracy']:.1%}")
        print(f"         (Correct speaker count in {summary['speaker_id_accuracy']*100:.0f}% of files)")
        print(f"      Avg Reference Speakers: {summary['avg_ref_speakers']:.1f}")
        print(f"      Avg Hypothesis Speakers: {summary['avg_hyp_speakers']:.1f}")

    # Export combined vendor summary
    print("\n" + "=" * 70)
    print("Vendor Comparison Summary")
    print("=" * 70)

    summary_csv = "vendor_summary_data/results/vendor_summary.csv"
    ResultsExporter.to_csv(
        all_summaries,
        summary_csv,
        file_identifiers=[s["vendor"] for s in all_summaries]
    )

    print(f"\n📊 Combined summary exported to: {summary_csv}")
    print()
    print(f"{'Vendor':<15} {'Avg WER':<12} {'Avg CP-WER':<12} {'Speaker ID Acc':<18}")
    print("-" * 70)
    for s in all_summaries:
        print(f"{s['vendor']:<15} {s['avg_wer']:<12.2%} {s['avg_cp_wer']:<12.2%} {s['speaker_id_accuracy']:<18.1%}")

    print("\n✓ Both detailed and summary CSVs generated!")
    print("\nGenerated files:")
    print("  1. vendor_summary_data/results/vendor_a_detailed.csv  (5 rows, one per file)")
    print("  2. vendor_summary_data/results/vendor_b_detailed.csv  (5 rows, one per file)")
    print("  3. vendor_summary_data/results/vendor_summary.csv     (2 rows, one per vendor)")


def show_csv_examples():
    """Show example CSV outputs."""
    print("\n" + "=" * 70)
    print("CSV Output Examples")
    print("=" * 70)

    print("\n1. Detailed CSV (vendor_a_detailed.csv):")
    print("-" * 70)
    print("file,wer,cp_wer,ref_num_speakers,hyp_num_speakers,speaker_count_correct,...")
    print("audio_001.json,0.0234,0.0245,2,2,1,...")
    print("audio_002.json,0.0189,0.0201,3,3,1,...")
    print("audio_003.json,0.0145,0.0156,2,2,1,...")
    print("audio_004.json,0.0267,0.0289,4,4,1,...")
    print("audio_005.json,0.0198,0.0212,2,2,1,...")

    print("\n2. Summary CSV (vendor_summary.csv):")
    print("-" * 70)
    print("vendor,avg_wer,avg_cp_wer,speaker_id_accuracy,avg_ref_speakers,avg_hyp_speakers,num_files")
    print("vendor_a,0.0207,0.0221,1.0,2.6,2.6,5")
    print("vendor_b,0.0298,0.0312,0.6,2.6,2.4,5")

    print("\nKey Metrics Explained:")
    print("  - speaker_id_accuracy: % of files where speaker count was correct")
    print("  - avg_ref_speakers: Average # of speakers in ground truth")
    print("  - avg_hyp_speakers: Average # of speakers identified by vendor")
    print("  - speaker_count_correct: 1 if correct, 0 if incorrect (in detailed CSV)")


def cleanup():
    """Remove example data."""
    import shutil

    response = input("\n\nRemove example data directory? (y/n): ")
    if response.lower() == 'y':
        shutil.rmtree("vendor_summary_data")
        print("✓ Example data removed")
    else:
        print("✓ Example data kept in 'vendor_summary_data/' directory")


if __name__ == "__main__":
    setup_example_data()
    run_benchmark_with_summaries()
    show_csv_examples()
    cleanup()
