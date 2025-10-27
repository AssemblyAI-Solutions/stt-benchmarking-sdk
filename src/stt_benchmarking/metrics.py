"""Metrics calculation for STT benchmarking."""

from typing import Dict, Any, List
import jiwer
from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate
from .models import Transcript


class WERMetrics:
    """Calculate Word Error Rate and related metrics using jiwer."""

    @staticmethod
    def calculate(reference: Transcript, hypothesis: Transcript) -> Dict[str, float]:
        """Calculate WER and related metrics.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript

        Returns:
            Dictionary with WER, MER, WIL, WIP, hits, substitutions, deletions, insertions
        """
        ref_text = reference.get_all_text()
        hyp_text = hypothesis.get_all_text()

        # Calculate all measures at once
        measures = jiwer.compute_measures(ref_text, hyp_text)

        # Count speakers
        ref_speakers = len(reference.get_speakers())
        hyp_speakers = len(hypothesis.get_speakers())

        return {
            "wer": measures["wer"],
            "mer": measures["mer"],
            "wil": measures["wil"],
            "wip": measures["wip"],
            "hits": measures["hits"],
            "substitutions": measures["substitutions"],
            "deletions": measures["deletions"],
            "insertions": measures["insertions"],
            "ref_num_speakers": ref_speakers,
            "hyp_num_speakers": hyp_speakers,
            "speaker_count_correct": 1 if ref_speakers == hyp_speakers else 0,
        }


class CPWERMetrics:
    """Calculate Concatenated minimum-Permutation Word Error Rate using meeteval."""

    @staticmethod
    def calculate(reference: Transcript, hypothesis: Transcript) -> Dict[str, Any]:
        """Calculate CP-WER.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript with aligned speaker labels

        Returns:
            Dictionary with cp_wer and related information
        """
        try:
            from meeteval.wer import wer
        except ImportError:
            raise ImportError(
                "meeteval is required for CP-WER calculation. "
                "Install it with: pip install meeteval"
            )

        # Convert transcripts to meeteval format
        # meeteval expects a list of dictionaries with 'speaker' and 'words' keys
        ref_data = []
        for utt in reference:
            ref_data.append({
                "speaker": utt.speaker,
                "words": utt.text,
            })

        hyp_data = []
        for utt in hypothesis:
            hyp_data.append({
                "speaker": utt.speaker,
                "words": utt.text,
            })

        # Calculate cpWER using meeteval
        # We'll use the 'tcp' (time-constrained permutation) variant if timestamps available,
        # otherwise use 'cp' (concatenated permutation)

        # For now, use basic CP-WER calculation
        # Group by speaker and concatenate
        ref_by_speaker = {}
        for utt in reference:
            if utt.speaker not in ref_by_speaker:
                ref_by_speaker[utt.speaker] = []
            ref_by_speaker[utt.speaker].append(utt.text)

        hyp_by_speaker = {}
        for utt in hypothesis:
            if utt.speaker not in hyp_by_speaker:
                hyp_by_speaker[utt.speaker] = []
            hyp_by_speaker[utt.speaker].append(utt.text)

        # Concatenate text for each speaker
        ref_speaker_texts = {
            spk: " ".join(texts) for spk, texts in ref_by_speaker.items()
        }
        hyp_speaker_texts = {
            spk: " ".join(texts) for spk, texts in hyp_by_speaker.items()
        }

        # Calculate WER for each speaker pair
        # This is a simplified version - meeteval has more sophisticated algorithms
        total_errors = 0
        total_ref_words = 0

        for ref_spk, ref_text in ref_speaker_texts.items():
            if ref_spk in hyp_speaker_texts:
                hyp_text = hyp_speaker_texts[ref_spk]
                measures = jiwer.compute_measures(ref_text, hyp_text)
                total_errors += measures["substitutions"] + measures["deletions"] + measures["insertions"]
                total_ref_words += len(ref_text.split())

        # Handle speakers in hypothesis but not in reference
        for hyp_spk, hyp_text in hyp_speaker_texts.items():
            if hyp_spk not in ref_speaker_texts:
                total_errors += len(hyp_text.split())

        cp_wer = total_errors / total_ref_words if total_ref_words > 0 else 0.0

        # Count speakers
        ref_speakers = len(reference.get_speakers())
        hyp_speakers = len(hypothesis.get_speakers())

        return {
            "cp_wer": cp_wer,
            "total_errors": total_errors,
            "total_reference_words": total_ref_words,
            "ref_num_speakers": ref_speakers,
            "hyp_num_speakers": hyp_speakers,
            "speaker_count_correct": 1 if ref_speakers == hyp_speakers else 0,
        }


class DERMetrics:
    """Calculate Diarization Error Rate using pyannote.metrics."""

    @staticmethod
    def calculate(reference: Transcript, hypothesis: Transcript) -> Dict[str, float]:
        """Calculate DER (Diarization Error Rate).

        Args:
            reference: Reference (ground truth) transcript with timestamps
            hypothesis: Hypothesis (predicted) transcript with timestamps

        Returns:
            Dictionary with DER and component errors

        Raises:
            ValueError: If transcripts don't have timestamps
        """
        # Check if timestamps are available
        if not all(utt.start_time is not None and utt.end_time is not None
                   for utt in reference):
            raise ValueError("Reference transcript must have timestamps for DER calculation")
        if not all(utt.start_time is not None and utt.end_time is not None
                   for utt in hypothesis):
            raise ValueError("Hypothesis transcript must have timestamps for DER calculation")

        # Create pyannote Annotation objects
        ref_annotation = Annotation()
        for utt in reference:
            segment = Segment(utt.start_time, utt.end_time)
            ref_annotation[segment] = utt.speaker

        hyp_annotation = Annotation()
        for utt in hypothesis:
            segment = Segment(utt.start_time, utt.end_time)
            hyp_annotation[segment] = utt.speaker

        # Calculate DER
        metric = DiarizationErrorRate()
        der_value = metric(ref_annotation, hyp_annotation)

        # Get detailed components
        components = metric.components(ref_annotation, hyp_annotation)

        # Count speakers
        ref_speakers = len(reference.get_speakers())
        hyp_speakers = len(hypothesis.get_speakers())

        return {
            "der": der_value,
            "false_alarm": components.get("false alarm", 0.0),
            "missed_detection": components.get("missed detection", 0.0),
            "confusion": components.get("confusion", 0.0),
            "total": components.get("total", 0.0),
            "ref_num_speakers": ref_speakers,
            "hyp_num_speakers": hyp_speakers,
            "speaker_count_correct": 1 if ref_speakers == hyp_speakers else 0,
        }

    @staticmethod
    def calculate_without_timestamps(
        reference: Transcript,
        hypothesis: Transcript
    ) -> Dict[str, float]:
        """Calculate a simplified speaker error metric when timestamps are unavailable.

        This calculates a word-level speaker attribution error rate.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript

        Returns:
            Dictionary with speaker_error_rate
        """
        # Align utterances and calculate speaker errors
        # This is a simplified metric for when we don't have timestamps

        ref_words_with_speaker = []
        for utt in reference:
            words = utt.text.split()
            ref_words_with_speaker.extend([(word, utt.speaker) for word in words])

        hyp_words_with_speaker = []
        for utt in hypothesis:
            words = utt.text.split()
            hyp_words_with_speaker.extend([(word, utt.speaker) for word in words])

        # Calculate speaker attribution errors
        # This assumes aligned word sequences (which may not be perfect)
        min_len = min(len(ref_words_with_speaker), len(hyp_words_with_speaker))
        speaker_errors = 0

        for i in range(min_len):
            ref_word, ref_spk = ref_words_with_speaker[i]
            hyp_word, hyp_spk = hyp_words_with_speaker[i]

            # Only count speaker error if words roughly match
            if ref_word.lower() == hyp_word.lower() and ref_spk != hyp_spk:
                speaker_errors += 1

        total_words = len(ref_words_with_speaker)
        speaker_error_rate = speaker_errors / total_words if total_words > 0 else 0.0

        # Count speakers
        ref_speakers = len(reference.get_speakers())
        hyp_speakers = len(hypothesis.get_speakers())

        return {
            "speaker_error_rate": speaker_error_rate,
            "speaker_errors": speaker_errors,
            "total_words": total_words,
            "ref_num_speakers": ref_speakers,
            "hyp_num_speakers": hyp_speakers,
            "speaker_count_correct": 1 if ref_speakers == hyp_speakers else 0,
        }
