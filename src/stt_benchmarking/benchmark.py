"""Main benchmarking interface for STT evaluation."""

from typing import Dict, Any, List, Optional, Union
from .models import Transcript
from .normalizer import TextNormalizer
from .speaker_matcher import SpeakerMatcher
from .metrics import WERMetrics, CPWERMetrics, DERMetrics


class STTBenchmark:
    """Main class for benchmarking STT systems."""

    def __init__(
        self,
        normalize: bool = True,
        match_speakers: bool = True,
        speaker_matching_threshold: float = 80.0
    ):
        """Initialize STT Benchmark.

        Args:
            normalize: Whether to normalize text using whisper_normalizer
            match_speakers: Whether to automatically match speaker labels
            speaker_matching_threshold: Minimum fuzzy matching score for speaker matching
        """
        self.normalize = normalize
        self.match_speakers = match_speakers

        self.normalizer = TextNormalizer() if normalize else None
        self.speaker_matcher = SpeakerMatcher(threshold=speaker_matching_threshold) if match_speakers else None

    def evaluate(
        self,
        reference: Union[List[Dict[str, Any]], Transcript],
        hypothesis: Union[List[Dict[str, Any]], Transcript],
        calculate_wer: bool = True,
        calculate_cp_wer: bool = True,
        calculate_der: bool = True,
    ) -> Dict[str, Any]:
        """Evaluate hypothesis against reference transcript.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript
            calculate_wer: Whether to calculate WER and related metrics
            calculate_cp_wer: Whether to calculate CP-WER
            calculate_der: Whether to calculate DER

        Returns:
            Dictionary containing all calculated metrics
        """
        # Convert to Transcript objects if needed
        if isinstance(reference, list):
            reference = Transcript.from_list(reference)
        if isinstance(hypothesis, list):
            hypothesis = Transcript.from_list(hypothesis)

        # Normalize text if enabled
        if self.normalize:
            reference = self.normalizer.normalize_transcript(reference)
            hypothesis = self.normalizer.normalize_transcript(hypothesis)

        # Match speakers if enabled
        if self.match_speakers:
            hypothesis = self.speaker_matcher.match_and_align(reference, hypothesis)

        # Calculate metrics
        results = {}

        if calculate_wer:
            wer_results = WERMetrics.calculate(reference, hypothesis)
            results.update(wer_results)

        if calculate_cp_wer:
            cp_wer_results = CPWERMetrics.calculate(reference, hypothesis)
            results.update(cp_wer_results)

        if calculate_der:
            try:
                der_results = DERMetrics.calculate(reference, hypothesis)
                results.update(der_results)
            except ValueError:
                # If timestamps not available, use simplified metric
                der_results = DERMetrics.calculate_without_timestamps(reference, hypothesis)
                results.update(der_results)

        return results

    def evaluate_wer_only(
        self,
        reference: Union[List[Dict[str, Any]], Transcript],
        hypothesis: Union[List[Dict[str, Any]], Transcript],
    ) -> Dict[str, float]:
        """Evaluate only WER metrics (faster than full evaluation).

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript

        Returns:
            Dictionary containing WER metrics
        """
        return self.evaluate(
            reference,
            hypothesis,
            calculate_wer=True,
            calculate_cp_wer=False,
            calculate_der=False
        )

    def evaluate_diarization_only(
        self,
        reference: Union[List[Dict[str, Any]], Transcript],
        hypothesis: Union[List[Dict[str, Any]], Transcript],
    ) -> Dict[str, float]:
        """Evaluate only diarization metrics (CP-WER and DER).

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript

        Returns:
            Dictionary containing diarization metrics
        """
        return self.evaluate(
            reference,
            hypothesis,
            calculate_wer=False,
            calculate_cp_wer=True,
            calculate_der=True
        )

    def get_speaker_mapping(
        self,
        reference: Union[List[Dict[str, Any]], Transcript],
        hypothesis: Union[List[Dict[str, Any]], Transcript],
    ) -> Dict[str, str]:
        """Get the speaker label mapping between hypothesis and reference.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript

        Returns:
            Dictionary mapping hypothesis speaker labels to reference labels
        """
        if isinstance(reference, list):
            reference = Transcript.from_list(reference)
        if isinstance(hypothesis, list):
            hypothesis = Transcript.from_list(hypothesis)

        if not self.speaker_matcher:
            raise ValueError("Speaker matching is disabled. Initialize with match_speakers=True")

        return self.speaker_matcher.match_speakers(reference, hypothesis)
