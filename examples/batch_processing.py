"""Complete example of batch processing multiple audio files across multiple vendors."""

import os
import json
from pathlib import Path
from stt_benchmarking import STTBenchmark, BatchEvaluator, ResultsExporter


def setup_example_data():
    """Create example directory structure and sample data for demonstration."""
    print("Setting up example data structure...\n")

    # Create directories
    Path("example_data/truth").mkdir(parents=True, exist_ok=True)
    Path("example_data/vendors/vendor_a").mkdir(parents=True, exist_ok=True)
    Path("example_data/vendors/vendor_b").mkdir(parents=True, exist_ok=True)
    Path("example_data/vendors/vendor_c").mkdir(parents=True, exist_ok=True)
    Path("example_data/results").mkdir(parents=True, exist_ok=True)

    # Create sample transcripts for 5 audio files
    audio_files = ["audio_001", "audio_002", "audio_003", "audio_004", "audio_005"]

    for audio_file in audio_files:
        # Ground truth
        truth = [
            {"speaker": "Doctor", "text": f"Hello, welcome to session {audio_file}"},
            {"speaker": "Patient", "text": "Thank you doctor"},
            {"speaker": "Doctor", "text": "How are you feeling today"},
            {"speaker": "Patient", "text": "I have been feeling much better"},
        ]
        with open(f"example_data/truth/{audio_file}.json", "w") as f:
            json.dump(truth, f, indent=2)

        # Vendor A (good accuracy)
        vendor_a = [
            {"speaker": "spk_0", "text": f"hello welcome to session {audio_file}"},
            {"speaker": "spk_1", "text": "thank you doctor"},
            {"speaker": "spk_0", "text": "how are you feeling today"},
            {"speaker": "spk_1", "text": "i have been feeling much better"},
        ]
        with open(f"example_data/vendors/vendor_a/{audio_file}.json", "w") as f:
            json.dump(vendor_a, f, indent=2)

        # Vendor B (medium accuracy)
        vendor_b = [
            {"speaker": "Speaker_1", "text": f"hello welcome to session {audio_file}"},
            {"speaker": "Speaker_2", "text": "thank you dr"},
            {"speaker": "Speaker_1", "text": "how are you feeling today"},
            {"speaker": "Speaker_2", "text": "ive been feeling much better"},
        ]
        with open(f"example_data/vendors/vendor_b/{audio_file}.json", "w") as f:
            json.dump(vendor_b, f, indent=2)

        # Vendor C (lower accuracy)
        vendor_c = [
            {"speaker": "SPEAKER_00", "text": f"hello welcome to the session {audio_file}"},
            {"speaker": "SPEAKER_01", "text": "thank you"},
            {"speaker": "SPEAKER_00", "text": "how you feeling today"},
            {"speaker": "SPEAKER_01", "text": "i been feeling much better"},
        ]
        with open(f"example_data/vendors/vendor_c/{audio_file}.json", "w") as f:
            json.dump(vendor_c, f, indent=2)

    print("✓ Example data created in 'example_data/' directory\n")


def process_by_vendor():
    """Process all files for each vendor (Recommended approach)."""
    print("=" * 70)
    print("Method 1: Process by Vendor (Recommended)")
    print("=" * 70)

    benchmark = STTBenchmark()
    vendors = ["vendor_a", "vendor_b", "vendor_c"]

    all_vendor_stats = {}

    # Process each vendor
    for vendor in vendors:
        print(f"\n📊 Processing {vendor}...")
        batch = BatchEvaluator(benchmark)

        truth_dir = "example_data/truth/"
        vendor_dir = f"example_data/vendors/{vendor}/"

        # Process all files for this vendor
        for filename in sorted(os.listdir(truth_dir)):
            if not filename.endswith(".json"):
                continue

            truth_path = f"{truth_dir}/{filename}"
            vendor_path = f"{vendor_dir}/{filename}"

            # Check if vendor file exists
            if not os.path.exists(vendor_path):
                print(f"   ⚠️  Warning: {vendor_path} not found, skipping...")
                continue

            try:
                # Load transcripts
                with open(truth_path) as f:
                    truth = json.load(f)
                with open(vendor_path) as f:
                    hypothesis = json.load(f)

                # Evaluate
                results = batch.add_evaluation(
                    filename,
                    truth,
                    hypothesis,
                    calculate_der=False
                )

                print(f"   ✓ {filename}: WER={results['wer']:.2%}, CP-WER={results['cp_wer']:.2%}")

            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
                continue

        # Export results for this vendor
        output_file = f"example_data/results/{vendor}_results.csv"
        batch.export_to_csv(output_file, precision=4)
        print(f"\n   📄 Results exported to: {output_file}")

        # Get and display summary statistics
        stats = batch.get_summary_stats()
        all_vendor_stats[vendor] = stats

        print(f"\n   📈 Summary for {vendor}:")
        print(f"      Files processed: {stats['wer']['count']}")
        print(f"      Average WER: {stats['wer']['mean']:.2%}")
        print(f"      Min WER: {stats['wer']['min']:.2%}")
        print(f"      Max WER: {stats['wer']['max']:.2%}")
        print(f"      Average CP-WER: {stats['cp_wer']['mean']:.2%}")

    # Create comparison summary
    print("\n" + "=" * 70)
    print("📊 Vendor Comparison Summary")
    print("=" * 70)

    comparison_data = []
    for vendor, stats in all_vendor_stats.items():
        comparison_data.append({
            "vendor": vendor,
            "avg_wer": stats['wer']['mean'],
            "min_wer": stats['wer']['min'],
            "max_wer": stats['wer']['max'],
            "avg_cp_wer": stats['cp_wer']['mean'],
            "files_processed": stats['wer']['count']
        })

    # Export comparison
    ResultsExporter.to_csv(
        comparison_data,
        "example_data/results/comparison_summary.csv",
        file_identifiers=[d["vendor"] for d in comparison_data]
    )

    # Display comparison
    print(f"\n{'Vendor':<15} {'Avg WER':<12} {'Min WER':<12} {'Max WER':<12} {'Avg CP-WER':<12}")
    print("-" * 70)
    for data in sorted(comparison_data, key=lambda x: x['avg_wer']):
        print(f"{data['vendor']:<15} {data['avg_wer']:<12.2%} {data['min_wer']:<12.2%} "
              f"{data['max_wer']:<12.2%} {data['avg_cp_wer']:<12.2%}")

    print(f"\n✓ Comparison exported to: example_data/results/comparison_summary.csv")


def process_single_vendor_example():
    """Example: Process just one vendor (e.g., when testing a single system)."""
    print("\n\n" + "=" * 70)
    print("Method 2: Process Single Vendor")
    print("=" * 70)

    benchmark = STTBenchmark()
    batch = BatchEvaluator(benchmark)

    vendor = "vendor_a"
    truth_dir = "example_data/truth/"
    vendor_dir = f"example_data/vendors/{vendor}/"

    print(f"\n📊 Processing only {vendor}...\n")

    for filename in sorted(os.listdir(truth_dir)):
        if not filename.endswith(".json"):
            continue

        with open(f"{truth_dir}/{filename}") as f:
            truth = json.load(f)
        with open(f"{vendor_dir}/{filename}") as f:
            hypothesis = json.load(f)

        results = batch.add_evaluation(filename, truth, hypothesis, calculate_der=False)
        print(f"   ✓ {filename}: WER={results['wer']:.2%}")

    # Export and show stats
    batch.export_to_csv(f"example_data/results/{vendor}_only.csv")
    stats = batch.get_summary_stats()

    print(f"\n   📈 Summary: Avg WER={stats['wer']['mean']:.2%}, "
          f"Files={stats['wer']['count']}")


def process_with_error_handling():
    """Example with robust error handling."""
    print("\n\n" + "=" * 70)
    print("Method 3: With Error Handling")
    print("=" * 70)

    benchmark = STTBenchmark()
    vendor = "vendor_a"

    truth_dir = "example_data/truth/"
    vendor_dir = f"example_data/vendors/{vendor}/"

    print(f"\n📊 Processing with error handling...\n")

    successful = 0
    failed = 0
    skipped = 0

    batch = BatchEvaluator(benchmark)

    for filename in sorted(os.listdir(truth_dir)):
        if not filename.endswith(".json"):
            continue

        truth_path = f"{truth_dir}/{filename}"
        vendor_path = f"{vendor_dir}/{filename}"

        # Check if vendor file exists
        if not os.path.exists(vendor_path):
            print(f"   ⚠️  {filename}: Vendor file not found, skipping")
            skipped += 1
            continue

        try:
            # Load files
            with open(truth_path) as f:
                truth = json.load(f)
            with open(vendor_path) as f:
                hypothesis = json.load(f)

            # Validate data
            if not truth or not hypothesis:
                print(f"   ⚠️  {filename}: Empty transcript, skipping")
                skipped += 1
                continue

            # Evaluate
            results = batch.add_evaluation(filename, truth, hypothesis, calculate_der=False)
            print(f"   ✓ {filename}: WER={results['wer']:.2%}")
            successful += 1

        except json.JSONDecodeError as e:
            print(f"   ❌ {filename}: Invalid JSON - {e}")
            failed += 1
        except KeyError as e:
            print(f"   ❌ {filename}: Missing required field - {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ {filename}: Unexpected error - {e}")
            failed += 1

    # Summary
    print(f"\n   📈 Processing Summary:")
    print(f"      Successful: {successful}")
    print(f"      Failed: {failed}")
    print(f"      Skipped: {skipped}")
    print(f"      Total: {successful + failed + skipped}")

    if successful > 0:
        batch.export_to_csv("example_data/results/with_error_handling.csv")
        stats = batch.get_summary_stats()
        print(f"      Average WER: {stats['wer']['mean']:.2%}")


def cleanup_example_data():
    """Remove example data (optional)."""
    import shutil

    response = input("\n\nRemove example data directory? (y/n): ")
    if response.lower() == 'y':
        shutil.rmtree("example_data")
        print("✓ Example data removed")
    else:
        print("✓ Example data kept in 'example_data/' directory")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STT Benchmarking: Batch Processing Example")
    print("=" * 70)
    print("\nThis example demonstrates processing multiple audio files")
    print("across multiple STT vendors.\n")

    # Setup example data
    setup_example_data()

    # Run different processing methods
    process_by_vendor()
    process_single_vendor_example()
    process_with_error_handling()

    # Final summary
    print("\n" + "=" * 70)
    print("✓ All processing complete!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - example_data/results/vendor_a_results.csv")
    print("  - example_data/results/vendor_b_results.csv")
    print("  - example_data/results/vendor_c_results.csv")
    print("  - example_data/results/comparison_summary.csv")
    print("  - example_data/results/vendor_a_only.csv")
    print("  - example_data/results/with_error_handling.csv")

    # Optional cleanup
    cleanup_example_data()
