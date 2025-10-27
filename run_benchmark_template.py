"""
Template script for running STT benchmarking on your data.

INSTRUCTIONS:
1. Organize your files as described in DIRECTORY_STRUCTURE.md
2. Update the configuration section below
3. Run: python run_benchmark_template.py
"""

import os
import json
from pathlib import Path
from stt_benchmarking import STTBenchmark, BatchEvaluator, TranscriptLoader

# ============================================================================
# CONFIGURATION - Update these paths for your data
# ============================================================================

# Directory containing ground truth transcripts
TRUTH_DIR = "truth/"

# Directory containing vendor transcripts (subdirectories by vendor)
VENDORS_DIR = "vendors/"

# List of vendor names (subdirectory names under VENDORS_DIR)
VENDORS = ["vendor_a", "vendor_b", "vendor_c"]

# Output directory for results
RESULTS_DIR = "results/"

# File extension of transcript files
FILE_EXTENSION = ".json"

# Evaluation options
CALCULATE_DER = False  # Set to True if you have timestamps
NORMALIZE_TEXT = True  # Set to False to disable normalization
MATCH_SPEAKERS = True  # Set to False to disable speaker matching
SPEAKER_THRESHOLD = 80.0  # Fuzzy matching threshold (0-100)

# ============================================================================
# Main Processing
# ============================================================================

def main():
    """Run benchmarking on all vendors."""

    # Create results directory
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize benchmark
    print("Initializing STT Benchmark...")
    benchmark = STTBenchmark(
        normalize=NORMALIZE_TEXT,
        match_speakers=MATCH_SPEAKERS,
        speaker_matching_threshold=SPEAKER_THRESHOLD
    )

    print(f"\nConfiguration:")
    print(f"  Truth directory: {TRUTH_DIR}")
    print(f"  Vendors directory: {VENDORS_DIR}")
    print(f"  Vendors: {', '.join(VENDORS)}")
    print(f"  Results directory: {RESULTS_DIR}")
    print(f"  Calculate DER: {CALCULATE_DER}")
    print(f"  Normalize text: {NORMALIZE_TEXT}")
    print(f"  Match speakers: {MATCH_SPEAKERS}")
    print()

    all_vendor_stats = {}
    all_vendor_summaries = []

    # Process each vendor
    for vendor in VENDORS:
        print("=" * 70)
        print(f"Processing: {vendor}")
        print("=" * 70)

        batch = BatchEvaluator(benchmark)
        vendor_dir = f"{VENDORS_DIR}/{vendor}/"

        # Check if vendor directory exists
        if not os.path.exists(vendor_dir):
            print(f"⚠️  Warning: Directory {vendor_dir} not found, skipping...")
            continue

        # Get all truth files
        truth_files = sorted([f for f in os.listdir(TRUTH_DIR)
                             if f.endswith(FILE_EXTENSION)])

        if not truth_files:
            print(f"⚠️  Warning: No files found in {TRUTH_DIR}")
            continue

        # Process each file
        successful = 0
        failed = 0

        for filename in truth_files:
            truth_path = f"{TRUTH_DIR}/{filename}"
            vendor_path = f"{vendor_dir}/{filename}"

            # Check if vendor file exists
            if not os.path.exists(vendor_path):
                print(f"  ⚠️  {filename}: Vendor file not found, skipping")
                failed += 1
                continue

            try:
                # Load transcripts
                # Uses auto-detection based on file extension
                truth = TranscriptLoader.auto_detect_format(truth_path)
                hypothesis = TranscriptLoader.auto_detect_format(vendor_path)

                # Evaluate
                results = batch.add_evaluation(
                    filename,
                    truth,
                    hypothesis,
                    calculate_der=CALCULATE_DER
                )

                print(f"  ✓ {filename}: WER={results['wer']:.2%}, "
                      f"CP-WER={results['cp_wer']:.2%}")
                successful += 1

            except Exception as e:
                print(f"  ❌ {filename}: Error - {e}")
                failed += 1
                continue

        # Export results
        if successful > 0:
            output_file = f"{RESULTS_DIR}/{vendor}_results.csv"
            batch.export_to_csv(output_file, precision=4)
            print(f"\n✓ Results exported to: {output_file}")

            # Get statistics
            stats = batch.get_summary_stats()
            all_vendor_stats[vendor] = stats

            # Get vendor summary
            summary = batch.get_vendor_summary(vendor)
            all_vendor_summaries.append(summary)

            print(f"\nSummary for {vendor}:")
            print(f"  Files processed: {successful}/{len(truth_files)}")
            print(f"  Failed: {failed}")
            print(f"  Average WER: {stats['wer']['mean']:.2%}")
            print(f"  Min WER: {stats['wer']['min']:.2%}")
            print(f"  Max WER: {stats['wer']['max']:.2%}")
            print(f"  Average CP-WER: {stats['cp_wer']['mean']:.2%}")

            # Show speaker identification accuracy if available
            if 'speaker_count_correct' in stats:
                speaker_acc = stats['speaker_count_correct']['mean']
                print(f"  Speaker ID Accuracy: {speaker_acc:.1%}")
                print(f"    (Correct speaker count in {speaker_acc*100:.0f}% of files)")
        else:
            print(f"\n❌ No files successfully processed for {vendor}")

        print()

    # Overall summary
    if all_vendor_stats:
        print("=" * 70)
        print("Overall Vendor Comparison")
        print("=" * 70)
        print(f"\n{'Vendor':<20} {'Avg WER':<12} {'Min WER':<12} {'Max WER':<12}")
        print("-" * 70)

        # Sort by average WER
        sorted_vendors = sorted(all_vendor_stats.items(),
                               key=lambda x: x[1]['wer']['mean'])

        for vendor, stats in sorted_vendors:
            print(f"{vendor:<20} {stats['wer']['mean']:<12.2%} "
                  f"{stats['wer']['min']:<12.2%} {stats['wer']['max']:<12.2%}")

        # Export vendor summary CSV
        if all_vendor_summaries:
            from stt_benchmarking import ResultsExporter
            summary_csv = f"{RESULTS_DIR}/vendor_summary.csv"
            ResultsExporter.to_csv(
                all_vendor_summaries,
                summary_csv,
                file_identifiers=[s["vendor"] for s in all_vendor_summaries]
            )
            print(f"\n✓ Vendor summary exported to: {summary_csv}")

        print()
        print(f"✓ All results saved in: {RESULTS_DIR}")
        print("\nGenerated files:")
        for vendor in VENDORS:
            if vendor in all_vendor_stats:
                print(f"  - {vendor}_results.csv (per-file metrics)")
        if all_vendor_summaries:
            print(f"  - vendor_summary.csv (vendor averages with speaker ID accuracy)")
    else:
        print("❌ No vendors were successfully processed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise
