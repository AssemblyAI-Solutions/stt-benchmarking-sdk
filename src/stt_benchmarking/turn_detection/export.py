"""Export functionality for turn detection benchmark results."""

import csv
import json
from pathlib import Path
from typing import Dict, Any, Union


class TurnDetectionExporter:
    """Export turn detection benchmark results to CSV and JSON."""

    @staticmethod
    def to_csv(
        benchmark_results: Dict[str, Any],
        output_path: Union[str, Path],
    ) -> None:
        """Export per-sample results to CSV.

        Args:
            benchmark_results: Output from TurnDetectionBenchmark.evaluate_samples()
            output_path: Path to output CSV file
        """
        output_path = Path(output_path)

        rows = []
        model = benchmark_results["model"]
        vad_window = benchmark_results["vad_window_ms"]

        for preset_name, preset_data in benchmark_results["presets"].items():
            for sample in preset_data["per_sample"]:
                rows.append({
                    "model": model,
                    "preset": preset_name,
                    "vad_window_ms": vad_window,
                    "sample_id": sample["sample_id"],
                    "ground_truth": sample["ground_truth"],
                    "detected": sample["detected"],
                    "correct": sample["correct"],
                    "classification": sample["classification"],
                    "confidence": sample["confidence"],
                })

        if not rows:
            return

        fieldnames = list(rows[0].keys())
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def metrics_to_csv(
        benchmark_results: Dict[str, Any],
        output_path: Union[str, Path],
        append: bool = False,
    ) -> None:
        """Export aggregate metrics (confusion matrix) to CSV.

        Args:
            benchmark_results: Output from TurnDetectionBenchmark.evaluate_samples()
            output_path: Path to output CSV file
            append: If True, append to existing file
        """
        output_path = Path(output_path)

        rows = []
        model = benchmark_results["model"]
        vad_window = benchmark_results["vad_window_ms"]

        for preset_name, preset_data in benchmark_results["presets"].items():
            m = preset_data["metrics"]
            rows.append({
                "model": model,
                "preset": preset_name,
                "vad_window_ms": vad_window,
                "tp": m["tp"],
                "fp": m["fp"],
                "tn": m["tn"],
                "fn": m["fn"],
                "total": m["total"],
                "accuracy": f"{m['accuracy']:.4f}",
                "precision": f"{m['precision']:.4f}",
                "recall": f"{m['recall']:.4f}",
                "f1_score": f"{m['f1_score']:.4f}",
            })

        if not rows:
            return

        fieldnames = list(rows[0].keys())
        mode = 'a' if append else 'w'
        file_exists = output_path.exists() and append

        with open(output_path, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def to_json(
        benchmark_results: Dict[str, Any],
        output_path: Union[str, Path],
    ) -> None:
        """Export full results to JSON.

        Serializes TurnDetectionResult objects to dictionaries.

        Args:
            benchmark_results: Output from TurnDetectionBenchmark.evaluate_samples()
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)

        serializable = {
            "model": benchmark_results["model"],
            "vad_window_ms": benchmark_results["vad_window_ms"],
            "num_samples": benchmark_results["num_samples"],
            "presets": {},
        }

        for preset_name, preset_data in benchmark_results["presets"].items():
            serializable["presets"][preset_name] = {
                "per_sample": preset_data["per_sample"],
                "metrics": preset_data["metrics"],
                "results": [
                    {
                        "end_of_turn_detected": r.end_of_turn_detected,
                        "end_of_turn_confidence": r.end_of_turn_confidence,
                        "transcript": r.transcript,
                        "audio_duration_ms": r.audio_duration_ms,
                        "speech_end_time": r.speech_end_time,
                    }
                    for r in preset_data["results"]
                ],
            }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2)
