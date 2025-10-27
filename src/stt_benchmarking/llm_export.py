"""Export utilities for LLM evaluation results."""

from pathlib import Path
from typing import Dict, List, Any, Union
import json


class LLMResultsExporter:
    """Export LLM evaluation results in various formats."""

    @staticmethod
    def to_text_file(
        result: Dict[str, Any],
        output_path: Union[str, Path],
        vendor_name: str = "Vendor",
        file_identifier: str = "audio"
    ) -> None:
        """Export LLM evaluation to readable text file.

        Args:
            result: Result from LLMEvaluator.evaluate_and_score()
            output_path: Path to output text file
            vendor_name: Vendor name
            file_identifier: File identifier
        """
        output_path = Path(output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"LLM VIBE EVAL: {vendor_name} - {file_identifier}\n")
            f.write("=" * 80 + "\n\n")

            # Vibe score
            if result.get('vibe_score'):
                f.write(f"📊 VIBE SCORE: {result['vibe_score']}/10\n")
                f.write("\n")

            # Consolidated evaluation
            if result.get('consolidation'):
                f.write("=" * 80 + "\n")
                f.write("CONSOLIDATED EVALUATION (Multi-Model Consensus)\n")
                f.write("=" * 80 + "\n\n")
                f.write(result['consolidation'])
                f.write("\n\n")

            # Individual evaluations
            if result.get('individual_evaluations'):
                for model, evaluation in result['individual_evaluations'].items():
                    f.write("=" * 80 + "\n")
                    f.write(f"INDIVIDUAL EVALUATION: {model.upper()}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(evaluation)
                    f.write("\n\n")

    @staticmethod
    def to_json_file(
        result: Dict[str, Any],
        output_path: Union[str, Path],
        vendor_name: str = "Vendor",
        file_identifier: str = "audio"
    ) -> None:
        """Export LLM evaluation to JSON file.

        Args:
            result: Result from LLMEvaluator.evaluate_and_score()
            output_path: Path to output JSON file
            vendor_name: Vendor name
            file_identifier: File identifier
        """
        output_path = Path(output_path)

        export_data = {
            "vendor": vendor_name,
            "file": file_identifier,
            "vibe_score": result.get('vibe_score'),
            "consolidation": result.get('consolidation'),
            "individual_evaluations": result.get('individual_evaluations', {})
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def to_markdown_file(
        result: Dict[str, Any],
        output_path: Union[str, Path],
        vendor_name: str = "Vendor",
        file_identifier: str = "audio"
    ) -> None:
        """Export LLM evaluation to Markdown file.

        Args:
            result: Result from LLMEvaluator.evaluate_and_score()
            output_path: Path to output Markdown file
            vendor_name: Vendor name
            file_identifier: File identifier
        """
        output_path = Path(output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# LLM Vibe Eval: {vendor_name}\n\n")
            f.write(f"**File:** {file_identifier}\n\n")

            # Vibe score
            if result.get('vibe_score'):
                score = result['vibe_score']
                f.write(f"## Vibe Score: {score}/10\n\n")

                # Add visual indicator
                if score >= 9:
                    emoji = "🟢"
                    rating = "Excellent"
                elif score >= 7:
                    emoji = "🟡"
                    rating = "Good"
                elif score >= 5:
                    emoji = "🟠"
                    rating = "Acceptable"
                else:
                    emoji = "🔴"
                    rating = "Poor"

                f.write(f"{emoji} **{rating}**\n\n")

            # Consolidated evaluation
            if result.get('consolidation'):
                f.write("## Consolidated Evaluation\n\n")
                f.write("*Multi-model consensus summary*\n\n")
                f.write(result['consolidation'])
                f.write("\n\n")

            # Individual evaluations
            if result.get('individual_evaluations'):
                f.write("## Individual Model Evaluations\n\n")

                for model, evaluation in result['individual_evaluations'].items():
                    f.write(f"### {model}\n\n")
                    f.write(evaluation)
                    f.write("\n\n")

    @staticmethod
    def batch_to_text_report(
        results: List[Dict[str, Any]],
        output_path: Union[str, Path],
        title: str = "Batch LLM Evaluation Report"
    ) -> None:
        """Export batch of LLM evaluations to single text report.

        Args:
            results: List of dicts with 'vendor', 'file', and LLM result data
            output_path: Path to output text file
            title: Report title
        """
        output_path = Path(output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"{title}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total Files Evaluated: {len(results)}\n\n")

            # Summary table
            f.write("SUMMARY OF VIBE SCORES\n")
            f.write("-" * 80 + "\n")
            for r in results:
                vendor = r.get('vendor', 'Unknown')
                file = r.get('file', 'Unknown')
                score = r.get('vibe_score', 'N/A')
                f.write(f"{file:<30} {vendor:<20} {score}/10\n")

            f.write("\n\n")

            # Individual detailed evaluations
            for i, r in enumerate(results, 1):
                f.write("\n" + "#" * 80 + "\n")
                f.write(f"EVALUATION {i}/{len(results)}\n")
                f.write("#" * 80 + "\n\n")

                vendor = r.get('vendor', 'Unknown')
                file = r.get('file', 'Unknown')
                score = r.get('vibe_score')

                f.write(f"Vendor: {vendor}\n")
                f.write(f"File: {file}\n")
                if score:
                    f.write(f"Vibe Score: {score}/10\n")
                f.write("\n")

                # Consolidated evaluation
                if r.get('consolidation'):
                    f.write("-" * 80 + "\n")
                    f.write("CONSOLIDATED EVALUATION\n")
                    f.write("-" * 80 + "\n\n")
                    f.write(r['consolidation'])
                    f.write("\n\n")

    @staticmethod
    def comparison_to_text_file(
        comparison: Dict[str, Any],
        output_path: Union[str, Path]
    ) -> None:
        """Export vendor comparison to text file.

        Args:
            comparison: Result from evaluate_vendor_comparison()
            output_path: Path to output text file
        """
        output_path = Path(output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"VENDOR COMPARISON: {comparison.get('file', 'Unknown')}\n")
            f.write("=" * 80 + "\n\n")

            # Vendor scores if available
            if comparison.get('vendor_scores'):
                f.write("VIBE SCORES\n")
                f.write("-" * 80 + "\n")
                for vendor, score in sorted(
                    comparison['vendor_scores'].items(),
                    key=lambda x: x[1],
                    reverse=True
                ):
                    f.write(f"{vendor:<30} {score}/10\n")
                f.write("\n\n")

            # Comparison text
            if comparison.get('comparison'):
                f.write("COMPARATIVE ANALYSIS\n")
                f.write("-" * 80 + "\n\n")
                f.write(comparison['comparison'])
                f.write("\n")


def export_llm_results_with_csv(
    csv_path: Union[str, Path],
    llm_results: List[Dict[str, Any]],
    output_dir: Union[str, Path] = "llm_evaluations"
) -> None:
    """Export LLM results alongside CSV.

    Creates a directory with individual text files for each evaluation
    plus a combined report.

    Args:
        csv_path: Path to CSV file (for reference)
        llm_results: List of LLM evaluation results
        output_dir: Directory to save LLM evaluation files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    exporter = LLMResultsExporter()

    # Export individual files
    for result in llm_results:
        vendor = result.get('vendor', 'vendor')
        file = result.get('file', 'audio')

        # Sanitize filename
        safe_vendor = vendor.replace('/', '_').replace(' ', '_')
        safe_file = file.replace('/', '_').replace(' ', '_')

        # Text file
        text_path = output_dir / f"{safe_file}_{safe_vendor}_vibe_eval.txt"
        exporter.to_text_file(result, text_path, vendor, file)

        # JSON file
        json_path = output_dir / f"{safe_file}_{safe_vendor}_vibe_eval.json"
        exporter.to_json_file(result, json_path, vendor, file)

    # Combined report
    report_path = output_dir / "combined_vibe_eval_report.txt"
    exporter.batch_to_text_report(llm_results, report_path)

    print(f"\n✓ LLM evaluations exported to: {output_dir}/")
    print(f"  - {len(llm_results)} individual files (TXT + JSON)")
    print(f"  - Combined report: combined_vibe_eval_report.txt")
