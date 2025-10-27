"""Examples of exporting benchmarking results to CSV."""

from stt_benchmarking import STTBenchmark, ResultsExporter, BatchEvaluator


def example_single_file_export():
    """Export results from a single file to CSV."""
    print("=" * 60)
    print("Example 1: Single File Export")
    print("=" * 60)

    reference = [
        {"speaker": "Alice", "text": "Hello world how are you today"},
        {"speaker": "Bob", "text": "I am doing great thank you"},
    ]

    hypothesis = [
        {"speaker": "spk_0", "text": "hello world how are you today"},
        {"speaker": "spk_1", "text": "i am doing great thank you"},
    ]

    # Evaluate
    benchmark = STTBenchmark()
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    # Export to CSV
    ResultsExporter.to_csv(
        results,
        output_path="single_file_metrics.csv",
        file_identifiers="conversation_001.json"
    )

    print("\nResults exported to: single_file_metrics.csv")
    print(f"WER: {results['wer']:.2%}")
    print(f"CP-WER: {results['cp_wer']:.2%}")


def example_multiple_files_export():
    """Export results from multiple files to CSV."""
    print("\n" + "=" * 60)
    print("Example 2: Multiple Files Export")
    print("=" * 60)

    # Simulate multiple files
    test_files = {
        "conversation_001.json": {
            "reference": [
                {"speaker": "A", "text": "Hello how are you"},
                {"speaker": "B", "text": "I am fine thanks"},
            ],
            "hypothesis": [
                {"speaker": "spk_0", "text": "hello how are you"},
                {"speaker": "spk_1", "text": "i am fine thanks"},
            ]
        },
        "conversation_002.json": {
            "reference": [
                {"speaker": "A", "text": "What is your name"},
                {"speaker": "B", "text": "My name is John"},
            ],
            "hypothesis": [
                {"speaker": "spk_0", "text": "what is your name"},
                {"speaker": "spk_1", "text": "my name is john"},
            ]
        },
        "conversation_003.json": {
            "reference": [
                {"speaker": "A", "text": "The weather is nice today"},
                {"speaker": "B", "text": "Yes it is very sunny"},
            ],
            "hypothesis": [
                {"speaker": "spk_0", "text": "the weather is nice today"},
                {"speaker": "spk_1", "text": "yes it is very sunny"},
            ]
        }
    }

    # Evaluate all files
    benchmark = STTBenchmark()
    all_results = []
    file_names = []

    for filename, data in test_files.items():
        results = benchmark.evaluate(
            data["reference"],
            data["hypothesis"],
            calculate_der=False
        )
        all_results.append(results)
        file_names.append(filename)
        print(f"\n  {filename}: WER={results['wer']:.2%}, CP-WER={results['cp_wer']:.2%}")

    # Export all results to single CSV
    ResultsExporter.to_csv(
        all_results,
        output_path="multiple_files_metrics.csv",
        file_identifiers=file_names
    )

    print("\n✓ All results exported to: multiple_files_metrics.csv")


def example_batch_evaluator():
    """Use BatchEvaluator for convenient batch processing and export."""
    print("\n" + "=" * 60)
    print("Example 3: Using BatchEvaluator")
    print("=" * 60)

    # Create batch evaluator
    benchmark = STTBenchmark()
    batch = BatchEvaluator(benchmark)

    # Add multiple evaluations
    test_cases = [
        ("file_001.json", [
            {"speaker": "A", "text": "Hello world"},
            {"speaker": "B", "text": "Hi there"},
        ], [
            {"speaker": "spk_0", "text": "hello world"},
            {"speaker": "spk_1", "text": "hi there"},
        ]),
        ("file_002.json", [
            {"speaker": "A", "text": "Good morning everyone"},
            {"speaker": "B", "text": "Good morning to you too"},
        ], [
            {"speaker": "spk_0", "text": "good morning everyone"},
            {"speaker": "spk_1", "text": "good morning to you too"},
        ]),
        ("file_003.json", [
            {"speaker": "A", "text": "How are you doing today"},
            {"speaker": "B", "text": "I am doing well thank you"},
        ], [
            {"speaker": "spk_0", "text": "how are you doing today"},
            {"speaker": "spk_1", "text": "i am doing well thank you"},
        ]),
    ]

    print("\nEvaluating files:")
    for file_id, reference, hypothesis in test_cases:
        results = batch.add_evaluation(
            file_id,
            reference,
            hypothesis,
            calculate_der=False
        )
        print(f"  {file_id}: WER={results['wer']:.2%}")

    # Export to CSV
    batch.export_to_csv("batch_metrics.csv", precision=4)
    print("\n✓ Batch results exported to: batch_metrics.csv")

    # Get summary statistics
    stats = batch.get_summary_stats()
    print("\nSummary Statistics:")
    print(f"  Average WER: {stats['wer']['mean']:.2%}")
    print(f"  Min WER: {stats['wer']['min']:.2%}")
    print(f"  Max WER: {stats['wer']['max']:.2%}")
    print(f"  Average CP-WER: {stats['cp_wer']['mean']:.2%}")


def example_vendor_comparison():
    """Compare multiple vendors and export to CSV."""
    print("\n" + "=" * 60)
    print("Example 4: Vendor Comparison")
    print("=" * 60)

    # Ground truth
    reference = [
        {"speaker": "Doctor", "text": "What symptoms are you experiencing"},
        {"speaker": "Patient", "text": "I have a headache and fever"},
        {"speaker": "Doctor", "text": "How long have you had these symptoms"},
        {"speaker": "Patient", "text": "About three days now"},
    ]

    # Hypotheses from different vendors
    vendors = {
        "Vendor_A": [
            {"speaker": "spk_0", "text": "what symptoms are you experiencing"},
            {"speaker": "spk_1", "text": "i have a headache and fever"},
            {"speaker": "spk_0", "text": "how long have you had these symptoms"},
            {"speaker": "spk_1", "text": "about three days now"},
        ],
        "Vendor_B": [
            {"speaker": "Speaker_1", "text": "what symptoms are you experiencing"},
            {"speaker": "Speaker_2", "text": "i have a headache and a fever"},
            {"speaker": "Speaker_1", "text": "how long have you had these symptoms"},
            {"speaker": "Speaker_2", "text": "about 3 days now"},
        ],
        "Vendor_C": [
            {"speaker": "SPEAKER_00", "text": "what symptoms are you experiencing"},
            {"speaker": "SPEAKER_01", "text": "i have headache and fever"},
            {"speaker": "SPEAKER_00", "text": "how long have you had these symptoms"},
            {"speaker": "SPEAKER_01", "text": "about three days"},
        ],
    }

    # Evaluate all vendors
    benchmark = STTBenchmark()
    batch = BatchEvaluator(benchmark)

    print("\nVendor Performance:")
    for vendor_name, hypothesis in vendors.items():
        results = batch.add_evaluation(
            vendor_name,
            reference,
            hypothesis,
            calculate_der=False
        )
        print(f"  {vendor_name}: WER={results['wer']:.2%}, CP-WER={results['cp_wer']:.2%}")

    # Export comparison
    batch.export_to_csv("vendor_comparison.csv", precision=4)
    print("\n✓ Vendor comparison exported to: vendor_comparison.csv")


def example_append_to_csv():
    """Append results to existing CSV file."""
    print("\n" + "=" * 60)
    print("Example 5: Appending to Existing CSV")
    print("=" * 60)

    benchmark = STTBenchmark()

    # First batch
    results1 = benchmark.evaluate(
        [{"speaker": "A", "text": "First test"}],
        [{"speaker": "A", "text": "first test"}],
        calculate_der=False
    )

    ResultsExporter.to_csv(
        results1,
        "incremental_results.csv",
        file_identifiers="test_001.json",
        append=False  # Create new file
    )
    print("Created new CSV: incremental_results.csv")

    # Second batch - append
    results2 = benchmark.evaluate(
        [{"speaker": "A", "text": "Second test"}],
        [{"speaker": "A", "text": "second test"}],
        calculate_der=False
    )

    ResultsExporter.to_csv(
        results2,
        "incremental_results.csv",
        file_identifiers="test_002.json",
        append=True  # Append to existing file
    )
    print("Appended to CSV: test_002.json")

    # Third batch - append
    results3 = benchmark.evaluate(
        [{"speaker": "A", "text": "Third test"}],
        [{"speaker": "A", "text": "third test"}],
        calculate_der=False
    )

    ResultsExporter.to_csv(
        results3,
        "incremental_results.csv",
        file_identifiers="test_003.json",
        append=True  # Append to existing file
    )
    print("Appended to CSV: test_003.json")
    print("\n✓ All results in: incremental_results.csv")


def example_custom_formatting():
    """Example with custom formatting and precision."""
    print("\n" + "=" * 60)
    print("Example 6: Custom Formatting")
    print("=" * 60)

    reference = [
        {"speaker": "A", "text": "The quick brown fox jumps over the lazy dog"},
        {"speaker": "B", "text": "This is a test of the emergency broadcast system"},
    ]

    hypothesis = [
        {"speaker": "A", "text": "the quick brown fox jumps over the lazy dog"},
        {"speaker": "B", "text": "this is a test of emergency broadcast system"},
    ]

    benchmark = STTBenchmark()
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    # Format with custom precision
    formatted_results = ResultsExporter.format_for_export(results, precision=6)

    ResultsExporter.to_csv(
        formatted_results,
        "formatted_metrics.csv",
        file_identifiers="high_precision_test.json"
    )

    print("\n✓ Formatted results exported to: formatted_metrics.csv")
    print(f"  WER: {formatted_results['wer']}")
    print(f"  CP-WER: {formatted_results['cp_wer']}")


if __name__ == "__main__":
    example_single_file_export()
    example_multiple_files_export()
    example_batch_evaluator()
    example_vendor_comparison()
    example_append_to_csv()
    example_custom_formatting()

    print("\n" + "=" * 60)
    print("All CSV files created successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - single_file_metrics.csv")
    print("  - multiple_files_metrics.csv")
    print("  - batch_metrics.csv")
    print("  - vendor_comparison.csv")
    print("  - incremental_results.csv")
    print("  - formatted_metrics.csv")
