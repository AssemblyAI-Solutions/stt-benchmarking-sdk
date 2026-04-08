"""Turn detection benchmark orchestrator."""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import TurnSample, TurnDetectionResult, SUPPORTED_MODELS, get_presets_for_model
from .detector import AssemblyAIStreamingDetector
from .metrics import TurnDetectionMetrics


class TurnDetectionBenchmark:
    """Orchestrates turn detection benchmarking across samples and presets.

    Streams audio files to AssemblyAI's streaming API and evaluates turn-end
    detection accuracy using VAD-based evaluation windows.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "universal-streaming-multilingual",
        presets: Optional[List[str]] = None,
        vad_window_ms: int = 1000,
        sample_rate: int = 16000,
        max_workers: int = 5,
        max_retries: int = 3,
        verbose: bool = False,
    ):
        """Initialize the benchmark.

        Args:
            api_key: AssemblyAI API key
            model: Speech model ID - "universal-streaming-multilingual",
                   "universal-streaming-english", or "u3-rt-pro"
            presets: List of preset names to test. Defaults to all 3 for the model.
            vad_window_ms: VAD detection window in ms (e.g. 350, 700, 1000)
            sample_rate: Audio sample rate in Hz
            max_workers: Max concurrent samples to process
            max_retries: Max retries per sample on failure
            verbose: Print detailed output during streaming
        """
        self.api_key = api_key
        self.model = model
        self.vad_window_ms = vad_window_ms
        self.sample_rate = sample_rate
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.verbose = verbose

        model_presets = get_presets_for_model(model)
        all_presets = list(model_presets.keys())

        self.presets = presets if presets is not None else all_presets

        for p in self.presets:
            if p not in all_presets:
                raise ValueError(f"Unknown preset '{p}' for model '{model}'. Options: {all_presets}")

    def evaluate_sample(
        self,
        sample: TurnSample,
        preset: str,
    ) -> TurnDetectionResult:
        """Evaluate a single sample with a single preset.

        Args:
            sample: TurnSample with audio path and ground truth
            preset: Preset name to use

        Returns:
            TurnDetectionResult
        """
        detector = AssemblyAIStreamingDetector(
            api_key=self.api_key,
            model=self.model,
            preset=preset,
            sample_rate=self.sample_rate,
        )
        return detector.process_audio_file(
            sample.audio_path,
            vad_window_ms=self.vad_window_ms,
            verbose=self.verbose,
        )

    def _evaluate_sample_with_retries(
        self,
        sample: TurnSample,
        preset: str,
    ) -> Optional[TurnDetectionResult]:
        """Evaluate with retries on failure."""
        for attempt in range(self.max_retries):
            try:
                return self.evaluate_sample(sample, preset)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    retry_delay = 5 * (attempt + 1)
                    if self.verbose:
                        print(f"  [{preset}] Retry {attempt + 1} (wait {retry_delay}s): {e}")
                    time.sleep(retry_delay)
                else:
                    print(f"  [{preset}] Failed after {self.max_retries} attempts: {e}")
        return None

    def evaluate_samples(
        self,
        samples: List[TurnSample],
        presets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Evaluate multiple samples across presets with concurrent execution.

        Args:
            samples: List of TurnSample objects
            presets: Presets to test (defaults to self.presets)

        Returns:
            Dictionary with structure:
            {
                "model": str,
                "vad_window_ms": int,
                "num_samples": int,
                "presets": {
                    "preset_name": {
                        "results": [TurnDetectionResult, ...],
                        "per_sample": [{"sample_id": ..., "ground_truth": ..., ...}, ...],
                        "metrics": {"tp": ..., "fp": ..., "accuracy": ..., ...}
                    }
                }
            }
        """
        presets = presets or self.presets

        output = {
            "model": self.model,
            "vad_window_ms": self.vad_window_ms,
            "num_samples": len(samples),
            "presets": {},
        }

        for preset in presets:
            print(f"\nEvaluating preset: {preset} ({len(samples)} samples, "
                  f"max {self.max_workers} concurrent)")

            results: List[Optional[TurnDetectionResult]] = [None] * len(samples)
            ground_truths: List[bool] = [s.ground_truth for s in samples]

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_idx = {}
                for idx, sample in enumerate(samples):
                    future = executor.submit(
                        self._evaluate_sample_with_retries, sample, preset
                    )
                    future_to_idx[future] = idx

                completed = 0
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        results[idx] = future.result()
                    except Exception as e:
                        print(f"  Sample {samples[idx].id} error: {e}")
                        results[idx] = None

                    completed += 1
                    if completed % 10 == 0 or completed == len(samples):
                        print(f"  Progress: {completed}/{len(samples)}")

            # Filter out failed samples
            valid_results = []
            valid_ground_truths = []
            per_sample = []

            for idx, (result, gt) in enumerate(zip(results, ground_truths)):
                sample = samples[idx]
                if result is not None:
                    valid_results.append(result)
                    valid_ground_truths.append(gt)
                    sample_eval = TurnDetectionMetrics.calculate_per_sample(result, gt)
                    sample_eval["sample_id"] = sample.id
                    per_sample.append(sample_eval)
                else:
                    per_sample.append({
                        "sample_id": sample.id,
                        "ground_truth": gt,
                        "detected": None,
                        "correct": None,
                        "classification": "ERROR",
                        "confidence": None,
                    })

            metrics = TurnDetectionMetrics.calculate(valid_results, valid_ground_truths)
            failed_count = len(samples) - len(valid_results)
            if failed_count > 0:
                metrics["failed_samples"] = failed_count

            print(f"  Accuracy: {metrics['accuracy']:.1%} | "
                  f"Precision: {metrics['precision']:.1%} | "
                  f"Recall: {metrics['recall']:.1%} | "
                  f"F1: {metrics['f1_score']:.1%}")

            output["presets"][preset] = {
                "results": valid_results,
                "per_sample": per_sample,
                "metrics": metrics,
            }

        return output

    def evaluate_dataset(
        self,
        samples_json_path: Union[str, Path],
        presets: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Load samples from a JSON file and evaluate.

        Expected JSON format: list of objects with keys:
            - id: str
            - audio_path: str
            - endpoint_bool: bool (ground truth)
            - turn_label: str (optional, e.g. "TURN_SHIFT")
            - language: str (optional, e.g. "eng")

        Args:
            samples_json_path: Path to samples JSON file
            presets: Presets to test (defaults to self.presets)
            limit: Max number of samples to evaluate (None = all)

        Returns:
            Same structure as evaluate_samples()
        """
        with open(samples_json_path, 'r') as f:
            raw_samples = json.load(f)

        if limit is not None:
            raw_samples = raw_samples[:limit]

        samples = [
            TurnSample(
                id=s["id"],
                audio_path=s["audio_path"],
                ground_truth=s["endpoint_bool"],
                turn_label=s.get("turn_label", ""),
                language=s.get("language", "eng"),
            )
            for s in raw_samples
        ]

        print(f"Loaded {len(samples)} samples from {samples_json_path}")
        print(f"Model: {self.model} | VAD window: {self.vad_window_ms}ms | "
              f"Presets: {presets or self.presets}")

        return self.evaluate_samples(samples, presets)
