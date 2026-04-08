"""Turn detection metrics (binary classification: TP/FP/TN/FN)."""

from typing import Dict, Any, List
from .models import TurnDetectionResult


class TurnDetectionMetrics:
    """Calculate turn detection accuracy metrics."""

    @staticmethod
    def calculate(
        results: List[TurnDetectionResult],
        ground_truths: List[bool],
    ) -> Dict[str, Any]:
        """Calculate aggregate turn detection metrics.

        Args:
            results: List of TurnDetectionResult from detector
            ground_truths: List of ground truth booleans (True = turn-shift, False = turn-hold)

        Returns:
            Dictionary with TP, FP, TN, FN, accuracy, precision, recall, F1-score
        """
        if len(results) != len(ground_truths):
            raise ValueError(
                f"Length mismatch: {len(results)} results vs {len(ground_truths)} ground truths"
            )

        tp = fp = tn = fn = 0

        for result, gt in zip(results, ground_truths):
            detected = result.end_of_turn_detected
            if gt and detected:
                tp += 1
            elif not gt and detected:
                fp += 1
            elif not gt and not detected:
                tn += 1
            elif gt and not detected:
                fn += 1

        total = tp + fp + tn + fn
        accuracy = ((tp + tn) / total) if total > 0 else 0.0
        precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "total": total,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }

    @staticmethod
    def calculate_per_sample(
        result: TurnDetectionResult,
        ground_truth: bool,
    ) -> Dict[str, Any]:
        """Evaluate a single sample.

        Args:
            result: TurnDetectionResult from detector
            ground_truth: True = turn-shift expected, False = turn-hold expected

        Returns:
            Dictionary with detection result and correctness
        """
        detected = result.end_of_turn_detected
        correct = detected == ground_truth

        if ground_truth and detected:
            classification = "TP"
        elif not ground_truth and detected:
            classification = "FP"
        elif not ground_truth and not detected:
            classification = "TN"
        else:
            classification = "FN"

        return {
            "ground_truth": ground_truth,
            "detected": detected,
            "correct": correct,
            "classification": classification,
            "confidence": result.end_of_turn_confidence,
        }
