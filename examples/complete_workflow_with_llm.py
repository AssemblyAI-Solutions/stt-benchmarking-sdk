"""
Complete workflow example: Quantitative metrics + LLM vibe eval with full export.

This shows the complete pipeline:
1. Run standard benchmarking (WER, CP-WER, DER, speaker counts)
2. Run LLM vibe eval
3. Export CSV with vibe scores
4. Export full LLM descriptions/rankings to text files
"""

import os
import json
from pathlib import Path
from stt_benchmarking import (
    STTBenchmark,
    BatchEvaluator,
    LLMEvaluator,
    ResultsExporter,
    LLMResultsExporter,
    export_llm_results_with_csv
)


def setup_example_data():
    """Create example data."""
    Path("complete_workflow_data/truth").mkdir(parents=True, exist_ok=True)
    Path("complete_workflow_data/vendors/vendor_a").mkdir(parents=True, exist_ok=True)
    Path("complete_workflow_data/vendors/vendor_b").mkdir(parents=True, exist_ok=True)
    Path("complete_workflow_data/results").mkdir(parents=True, exist_ok=True)

    # Sample transcripts
    files_data = {
        "meeting_001.json": {
            "truth": [
                {"speaker": "CEO", "text": "Let's discuss the quarterly results", "start_time": 0.0, "end_time": 3.0},
                {"speaker": "CFO", "text": "Revenue is up fifteen percent", "start_time": 3.5, "end_time": 6.0},
            ],
            "vendor_a": [
                {"speaker": "spk_0", "text": "lets discuss the quarterly results", "start_time": 0.0, "end_time": 3.0},
                {"speaker": "spk_1", "text": "revenue is up 15 percent", "start_time": 3.5, "end_time": 6.0},
            ],
            "vendor_b": [
                {"speaker": "Speaker_1", "text": "lets discuss the quarterly results revenue is up 15%", "start_time": 0.0, "end_time": 6.2},
            ]
        },
        "meeting_002.json": {
            "truth": [
                {"speaker": "Manager", "text": "What are the action items from today", "start_time": 0.0, "end_time": 2.5},
                {"speaker": "TeamLead", "text": "We need to finalize the budget by Friday", "start_time": 3.0, "end_time": 5.5},
            ],
            "vendor_a": [
                {"speaker": "spk_0", "text": "what are the action items from today", "start_time": 0.0, "end_time": 2.5},
                {"speaker": "spk_1", "text": "we need to finalize the budget by friday", "start_time": 3.0, "end_time": 5.5},
            ],
            "vendor_b": [
                {"speaker": "Speaker_1", "text": "what are the action items from today", "start_time": 0.0, "end_time": 2.5},
                {"speaker": "Speaker_1", "text": "we need to finalize the budget by friday", "start_time": 3.0, "end_time": 5.5},
            ]
        }
    }

    for filename, data in files_data.items():
        with open(f"complete_workflow_data/truth/{filename}", "w") as f:
            json.dump(data["truth"], f, indent=2)
        with open(f"complete_workflow_data/vendors/vendor_a/{filename}", "w") as f:
            json.dump(data["vendor_a"], f, indent=2)
        with open(f"complete_workflow_data/vendors/vendor_b/{filename}", "w") as f:
            json.dump(data["vendor_b"], f, indent=2)

    print("✓ Example data created\n")


def complete_workflow():
    """Run complete benchmarking + LLM eval workflow."""
    print("=" * 80)
    print("COMPLETE WORKFLOW: Quantitative + Qualitative Evaluation")
    print("=" * 80)

    benchmark = STTBenchmark()
    vendors = ["vendor_a", "vendor_b"]

    truth_dir = "complete_workflow_data/truth/"
    results_dir = "complete_workflow_data/results/"

    # Check for API key
    has_api_key = bool(os.environ.get('ASSEMBLYAI_API_KEY'))

    if not has_api_key:
        print("\n⚠️  ASSEMBLYAI_API_KEY not set. Will run quantitative metrics only.")
        print("   Set your API key to enable LLM vibe eval.\n")

    # Process each vendor
    for vendor in vendors:
        print(f"\n{'='*80}")
        print(f"Processing: {vendor}")
        print(f"{'='*80}\n")

        batch = BatchEvaluator(benchmark)
        vendor_dir = f"complete_workflow_data/vendors/{vendor}/"

        # Store LLM results separately
        llm_results = []

        # Process all files
        import os as os_module
        for filename in sorted(os_module.listdir(truth_dir)):
            if not filename.endswith(".json"):
                continue

            # Load transcripts
            with open(f"{truth_dir}/{filename}") as f:
                truth = json.load(f)
            with open(f"{vendor_dir}/{filename}") as f:
                hypothesis = json.load(f)

            # 1. Quantitative metrics
            results = batch.add_evaluation(
                filename,
                truth,
                hypothesis,
                calculate_der=True
            )

            print(f"  ✓ {filename}:")
            print(f"      WER: {results['wer']:.2%}, CP-WER: {results['cp_wer']:.2%}")
            print(f"      Speakers: {results['ref_num_speakers']} → {results['hyp_num_speakers']}")

            # 2. LLM vibe eval (if API key available)
            if has_api_key:
                from stt_benchmarking import Transcript

                truth_transcript = Transcript.from_list(truth)
                hyp_transcript = Transcript.from_list(hypothesis)

                # Initialize evaluator (use single model for speed in example)
                evaluator = LLMEvaluator(
                    evaluator_models=["claude-sonnet-4-5-20250929"]
                )

                print(f"      Running LLM vibe eval...")
                vibe_result = evaluator.evaluate_and_score(
                    reference=truth_transcript,
                    hypothesis=hyp_transcript,
                    vendor_name=vendor,
                    file_identifier=filename
                )

                # Add vibe score to batch results
                batch.results[-1]['vibe_score'] = vibe_result['vibe_score']

                # Store full LLM result for detailed export
                llm_results.append({
                    'vendor': vendor,
                    'file': filename,
                    'vibe_score': vibe_result['vibe_score'],
                    'consolidation': vibe_result['consolidation'],
                    'individual_evaluations': vibe_result['individual_evaluations']
                })

                print(f"      Vibe Score: {vibe_result['vibe_score']}/10")

        # 3. Export quantitative CSV (with vibe scores if available)
        csv_path = f"{results_dir}/{vendor}_results.csv"
        batch.export_to_csv(csv_path, precision=4)
        print(f"\n✓ Quantitative metrics exported to: {csv_path}")

        # 4. Export full LLM evaluations (descriptions, rankings, etc.)
        if llm_results:
            llm_dir = f"{results_dir}/{vendor}_llm_evaluations"
            export_llm_results_with_csv(
                csv_path,
                llm_results,
                output_dir=llm_dir
            )

        # 5. Get and display summary
        stats = batch.get_summary_stats()
        print(f"\n📊 Summary for {vendor}:")
        print(f"    Files: {stats['wer']['count']}")
        print(f"    Avg WER: {stats['wer']['mean']:.2%}")
        print(f"    Avg CP-WER: {stats['cp_wer']['mean']:.2%}")
        print(f"    Speaker ID Accuracy: {stats['speaker_count_correct']['mean']:.1%}")

        if has_api_key and 'vibe_score' in stats:
            print(f"    Avg Vibe Score: {stats['vibe_score']['mean']:.1f}/10")

    print(f"\n\n{'='*80}")
    print("All Processing Complete!")
    print(f"{'='*80}\n")

    # Show what was generated
    print("Generated Files:")
    print("\n1. Quantitative Metrics (CSV):")
    print("   - complete_workflow_data/results/vendor_a_results.csv")
    print("   - complete_workflow_data/results/vendor_b_results.csv")

    if has_api_key:
        print("\n2. LLM Evaluations (Text + JSON):")
        print("   - complete_workflow_data/results/vendor_a_llm_evaluations/")
        print("     • meeting_001.json_vendor_a_vibe_eval.txt")
        print("     • meeting_001.json_vendor_a_vibe_eval.json")
        print("     • meeting_002.json_vendor_a_vibe_eval.txt")
        print("     • meeting_002.json_vendor_a_vibe_eval.json")
        print("     • combined_vibe_eval_report.txt")
        print("   - complete_workflow_data/results/vendor_b_llm_evaluations/")
        print("     • (same structure)")

    # Show CSV example
    print("\n" + "="*80)
    print("CSV Output Example (vendor_a_results.csv):")
    print("="*80)
    print("file,wer,cp_wer,der,ref_num_speakers,hyp_num_speakers,speaker_count_correct,vibe_score")
    print("meeting_001.json,0.0123,0.0145,0.0089,2,2,1,8.5")
    print("meeting_002.json,0.0234,0.0267,0.0156,2,2,1,7.8")

    # Show text file example
    if has_api_key:
        print("\n" + "="*80)
        print("LLM Evaluation Text File Example (meeting_001.json_vendor_a_vibe_eval.txt):")
        print("="*80)
        print("""
================================================================================
LLM VIBE EVAL: vendor_a - meeting_001.json
================================================================================

📊 VIBE SCORE: 8.5/10

================================================================================
CONSOLIDATED EVALUATION (Multi-Model Consensus)
================================================================================

CONSENSUS SCORE: 8.5/10

Areas of Agreement:
The transcription demonstrates excellent word accuracy with perfect speaker
diarization. All evaluators agreed that this is a high-quality transcription
suitable for professional use.

Key Strengths:
- Perfect speaker identification (2 speakers correctly identified)
- Excellent word accuracy (~98%)
- Proper temporal alignment
- Good handling of numbers ("fifteen percent" → "15 percent")

Key Weaknesses:
- Minor normalization differences (capitalization)
- Could improve punctuation for readability

Recommendation:
This transcription quality is excellent and suitable for all professional
use cases including meeting minutes, analysis, and archival purposes.

================================================================================
INDIVIDUAL EVALUATION: CLAUDE-SONNET-4-5-20250929
================================================================================

[Full detailed evaluation from Claude...]
        """)


def show_manual_export_examples():
    """Show how to manually export LLM results in different formats."""
    print("\n" + "="*80)
    print("Manual Export Options")
    print("="*80)

    print("""
The SDK provides multiple ways to export LLM evaluations:

1. AUTOMATIC (Recommended):
   export_llm_results_with_csv(csv_path, llm_results, output_dir)
   → Exports TXT + JSON + combined report

2. INDIVIDUAL TEXT FILE:
   LLMResultsExporter.to_text_file(result, path, vendor, file)

3. INDIVIDUAL JSON FILE:
   LLMResultsExporter.to_json_file(result, path, vendor, file)

4. MARKDOWN FILE:
   LLMResultsExporter.to_markdown_file(result, path, vendor, file)

5. COMBINED REPORT:
   LLMResultsExporter.batch_to_text_report(results, path, title)

6. COMPARISON FILE:
   LLMResultsExporter.comparison_to_text_file(comparison, path)

Example:

    # Get LLM evaluation
    result = evaluator.evaluate_and_score(truth, hypothesis, "Vendor A", "audio_001")

    # Export as text
    LLMResultsExporter.to_text_file(
        result,
        "vendor_a_audio_001_vibe.txt",
        "Vendor A",
        "audio_001"
    )

    # Export as JSON (for programmatic access)
    LLMResultsExporter.to_json_file(
        result,
        "vendor_a_audio_001_vibe.json",
        "Vendor A",
        "audio_001"
    )

    # Export as Markdown (for documentation)
    LLMResultsExporter.to_markdown_file(
        result,
        "vendor_a_audio_001_vibe.md",
        "Vendor A",
        "audio_001"
    )
    """)


def main():
    """Run complete workflow example."""
    setup_example_data()
    complete_workflow()
    show_manual_export_examples()

    # Cleanup
    import shutil
    print("\n")
    response = input("Remove example data? (y/n): ")
    if response.lower() == 'y':
        shutil.rmtree("complete_workflow_data")
        print("✓ Example data removed")


if __name__ == "__main__":
    main()
