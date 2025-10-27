"""Export functionality for benchmarking results."""

import csv
from pathlib import Path
from typing import Dict, Any, List, Union, Optional


class ResultsExporter:
    """Export benchmarking results to various formats."""

    @staticmethod
    def to_csv(
        results: Union[Dict[str, Any], List[Dict[str, Any]]],
        output_path: Union[str, Path],
        file_identifiers: Optional[Union[str, List[str]]] = None,
        append: bool = False
    ) -> None:
        """Export metrics to CSV file.

        Args:
            results: Single results dict or list of results dicts
            output_path: Path to output CSV file
            file_identifiers: Optional file identifier(s) to include in CSV (e.g., filename)
            append: If True, append to existing file; if False, create new file

        Example:
            # Single file
            results = benchmark.evaluate(ref, hyp)
            ResultsExporter.to_csv(results, "metrics.csv", file_identifiers="file1.json")

            # Multiple files
            all_results = [result1, result2, result3]
            file_names = ["file1.json", "file2.json", "file3.json"]
            ResultsExporter.to_csv(all_results, "metrics.csv", file_identifiers=file_names)
        """
        output_path = Path(output_path)

        # Normalize inputs to lists
        if isinstance(results, dict):
            results = [results]

        if file_identifiers is None:
            file_identifiers = [f"result_{i+1}" for i in range(len(results))]
        elif isinstance(file_identifiers, str):
            file_identifiers = [file_identifiers]

        if len(file_identifiers) != len(results):
            raise ValueError(
                f"Number of file_identifiers ({len(file_identifiers)}) "
                f"must match number of results ({len(results)})"
            )

        # Determine all possible metric keys
        all_keys = set()
        for result in results:
            all_keys.update(result.keys())

        # Sort keys for consistent column order
        metric_keys = sorted(all_keys)

        # Prepare rows
        rows = []
        for file_id, result in zip(file_identifiers, results):
            row = {"file": file_id}
            for key in metric_keys:
                row[key] = result.get(key, "")
            rows.append(row)

        # Write to CSV
        mode = 'a' if append else 'w'
        file_exists = output_path.exists() and append

        with open(output_path, mode, newline='', encoding='utf-8') as f:
            fieldnames = ["file"] + metric_keys
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # Write header only if creating new file or file doesn't exist
            if not file_exists:
                writer.writeheader()

            writer.writerows(rows)

    @staticmethod
    def results_to_flat_dict(
        results: Dict[str, Any],
        prefix: str = ""
    ) -> Dict[str, Any]:
        """Flatten nested results dictionary for easier export.

        Args:
            results: Results dictionary (potentially nested)
            prefix: Prefix for keys (used in recursion)

        Returns:
            Flattened dictionary with dot-separated keys
        """
        flat = {}
        for key, value in results.items():
            new_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                flat.update(ResultsExporter.results_to_flat_dict(value, new_key))
            else:
                flat[new_key] = value

        return flat

    @staticmethod
    def format_for_export(results: Dict[str, Any], precision: int = 4) -> Dict[str, Any]:
        """Format results for export (round floats, etc.).

        Args:
            results: Results dictionary
            precision: Number of decimal places for floats

        Returns:
            Formatted results dictionary
        """
        formatted = {}
        for key, value in results.items():
            if isinstance(value, float):
                formatted[key] = round(value, precision)
            elif isinstance(value, dict):
                formatted[key] = ResultsExporter.format_for_export(value, precision)
            else:
                formatted[key] = value

        return formatted


class BatchEvaluator:
    """Helper class for evaluating multiple files and exporting results."""

    def __init__(self, benchmark):
        """Initialize batch evaluator.

        Args:
            benchmark: STTBenchmark instance to use for evaluation
        """
        self.benchmark = benchmark
        self.results = []
        self.file_identifiers = []

    def add_evaluation(
        self,
        file_identifier: str,
        reference: Any,
        hypothesis: Any,
        **eval_kwargs
    ) -> Dict[str, Any]:
        """Evaluate a single file and store results.

        Args:
            file_identifier: Identifier for this file (e.g., filename)
            reference: Reference transcript
            hypothesis: Hypothesis transcript
            **eval_kwargs: Additional arguments to pass to benchmark.evaluate()

        Returns:
            Results dictionary
        """
        results = self.benchmark.evaluate(reference, hypothesis, **eval_kwargs)
        self.results.append(results)
        self.file_identifiers.append(file_identifier)
        return results

    def export_to_csv(
        self,
        output_path: Union[str, Path],
        precision: int = 4
    ) -> None:
        """Export all collected results to CSV.

        Args:
            output_path: Path to output CSV file
            precision: Number of decimal places for floats
        """
        formatted_results = [
            ResultsExporter.format_for_export(r, precision)
            for r in self.results
        ]

        ResultsExporter.to_csv(
            formatted_results,
            output_path,
            file_identifiers=self.file_identifiers
        )

    def get_summary_stats(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics across all evaluated files.

        Returns:
            Dictionary with mean, min, max for each metric
        """
        if not self.results:
            return {}

        # Collect all metrics
        all_metrics = {}
        for result in self.results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    if key not in all_metrics:
                        all_metrics[key] = []
                    all_metrics[key].append(value)

        # Calculate statistics
        stats = {}
        for metric, values in all_metrics.items():
            stats[metric] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }

        return stats

    def export_summary_to_csv(
        self,
        output_path: Union[str, Path],
        vendor_name: str = "vendor",
        precision: int = 4
    ) -> None:
        """Export summary statistics to CSV (single row with averages).

        Args:
            output_path: Path to output CSV file
            vendor_name: Name/identifier for this vendor
            precision: Number of decimal places for floats
        """
        if not self.results:
            return

        stats = self.get_summary_stats()

        # Build summary row
        summary = {"vendor": vendor_name}

        # Add key metrics
        for metric in ["wer", "mer", "cp_wer", "der", "speaker_error_rate"]:
            if metric in stats:
                summary[f"avg_{metric}"] = round(stats[metric]["mean"], precision)
                summary[f"min_{metric}"] = round(stats[metric]["min"], precision)
                summary[f"max_{metric}"] = round(stats[metric]["max"], precision)

        # Add speaker identification accuracy
        if "speaker_count_correct" in stats:
            speaker_id_accuracy = stats["speaker_count_correct"]["mean"]
            summary["speaker_id_accuracy"] = round(speaker_id_accuracy, precision)

        # Add average speaker counts
        if "ref_num_speakers" in stats:
            summary["avg_ref_speakers"] = round(stats["ref_num_speakers"]["mean"], precision)
        if "hyp_num_speakers" in stats:
            summary["avg_hyp_speakers"] = round(stats["hyp_num_speakers"]["mean"], precision)

        # Add file count
        summary["num_files"] = stats[list(stats.keys())[0]]["count"]

        # Export to CSV
        ResultsExporter.to_csv(
            [summary],
            output_path,
            file_identifiers=[vendor_name]
        )

    def get_vendor_summary(self, vendor_name: str = "vendor") -> Dict[str, Any]:
        """Get vendor summary with averages and speaker identification accuracy.

        Args:
            vendor_name: Name/identifier for this vendor

        Returns:
            Dictionary with vendor summary statistics
        """
        if not self.results:
            return {}

        stats = self.get_summary_stats()

        summary = {"vendor": vendor_name}

        # Add key metrics
        for metric in ["wer", "mer", "cp_wer", "der", "speaker_error_rate"]:
            if metric in stats:
                summary[f"avg_{metric}"] = stats[metric]["mean"]
                summary[f"min_{metric}"] = stats[metric]["min"]
                summary[f"max_{metric}"] = stats[metric]["max"]

        # Speaker identification accuracy (% of files with correct speaker count)
        if "speaker_count_correct" in stats:
            summary["speaker_id_accuracy"] = stats["speaker_count_correct"]["mean"]

        # Average speaker counts
        if "ref_num_speakers" in stats:
            summary["avg_ref_speakers"] = stats["ref_num_speakers"]["mean"]
        if "hyp_num_speakers" in stats:
            summary["avg_hyp_speakers"] = stats["hyp_num_speakers"]["mean"]

        summary["num_files"] = stats[list(stats.keys())[0]]["count"]

        return summary

    def clear(self) -> None:
        """Clear all stored results."""
        self.results = []
        self.file_identifiers = []
