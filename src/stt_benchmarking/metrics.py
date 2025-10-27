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

        # Group by speaker and concatenate text
        # meeteval expects dict format: {speaker_id: "concatenated text"}
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

        # Use meeteval's proper CP-WER calculation with Hungarian algorithm
        # This finds the optimal speaker permutation automatically
        from meeteval.wer.wer.cp import cp_word_error_rate

        # Count speakers
        ref_speakers = len(reference.get_speakers())
        hyp_speakers = len(hypothesis.get_speakers())

        try:
            result = cp_word_error_rate(ref_speaker_texts, hyp_speaker_texts)

            # Extract results from meeteval's CPErrorRate object
            cp_wer = result.error_rate
            total_errors = result.errors
            total_ref_words = result.length
            assignment = result.assignment

            return {
                "cp_wer": cp_wer,
                "total_errors": total_errors,
                "total_reference_words": total_ref_words,
                "insertions": result.insertions,
                "deletions": result.deletions,
                "substitutions": result.substitutions,
                "missed_speaker": result.missed_speaker,
                "falarm_speaker": result.falarm_speaker,
                "scored_speaker": result.scored_speaker,
                "ref_num_speakers": ref_speakers,
                "hyp_num_speakers": hyp_speakers,
                "speaker_count_correct": 1 if ref_speakers == hyp_speakers else 0,
                "optimal_assignment": assignment,  # For debugging/analysis
            }
        except RuntimeError as e:
            # meeteval has a safety limit on number of speakers
            # If exceeded, use greedy approximation instead
            if "too many speakers" in str(e).lower() or "are you sure" in str(e).lower():
                # Fall back to greedy assignment (not globally optimal, but close)
                return CPWERMetrics._calculate_greedy_cpwer(
                    reference, hypothesis,
                    ref_speaker_texts, hyp_speaker_texts,
                    ref_speakers, hyp_speakers
                )
            else:
                raise  # Re-raise if it's a different error

    @staticmethod
    def _calculate_greedy_cpwer(
        reference: Transcript,
        hypothesis: Transcript,
        ref_speaker_texts: Dict[str, str],
        hyp_speaker_texts: Dict[str, str],
        ref_speakers: int,
        hyp_speakers: int
    ) -> Dict[str, Any]:
        """Calculate approximate CP-WER using greedy assignment (for >20 speakers).

        This is used as a fallback when the optimal Hungarian algorithm exceeds
        computational limits. The greedy approach is not globally optimal but
        provides a reasonable approximation.

        Args:
            reference: Reference transcript
            hypothesis: Hypothesis transcript
            ref_speaker_texts: Dictionary of reference speaker texts
            hyp_speaker_texts: Dictionary of hypothesis speaker texts
            ref_speakers: Number of reference speakers
            hyp_speakers: Number of hypothesis speakers

        Returns:
            Dictionary with approximate CP-WER metrics
        """
        # Calculate WER for all possible pairings
        wer_matrix = {}
        for ref_spk, ref_text in ref_speaker_texts.items():
            wer_matrix[ref_spk] = {}

            # Skip empty reference speakers
            ref_text_clean = ref_text.strip()
            if not ref_text_clean:
                for hyp_spk in hyp_speaker_texts.keys():
                    wer_matrix[ref_spk][hyp_spk] = {
                        'wer': float('inf'),
                        'errors': 0,
                        'substitutions': 0,
                        'deletions': 0,
                        'insertions': 0,
                        'ref_words': 0
                    }
                continue

            for hyp_spk, hyp_text in hyp_speaker_texts.items():
                hyp_text_clean = hyp_text.strip()

                # Handle empty hypothesis text
                if not hyp_text_clean:
                    ref_words = len(ref_text_clean.split())
                    wer_matrix[ref_spk][hyp_spk] = {
                        'wer': 1.0,  # 100% error
                        'errors': ref_words,
                        'substitutions': 0,
                        'deletions': ref_words,
                        'insertions': 0,
                        'ref_words': ref_words
                    }
                else:
                    measures = jiwer.compute_measures(ref_text_clean, hyp_text_clean)
                    wer_matrix[ref_spk][hyp_spk] = {
                        'wer': measures['wer'],
                        'errors': measures['substitutions'] + measures['deletions'] + measures['insertions'],
                        'substitutions': measures['substitutions'],
                        'deletions': measures['deletions'],
                        'insertions': measures['insertions'],
                        'ref_words': len(ref_text_clean.split())
                    }

        # Greedy assignment: iteratively pick best available match
        assignment = []
        matched_hyp = set()
        total_errors = 0
        total_ref_words = 0
        total_substitutions = 0
        total_deletions = 0
        total_insertions = 0

        # Sort reference speakers by word count (descending) for better greedy results
        ref_speakers_sorted = sorted(
            ref_speaker_texts.keys(),
            key=lambda s: len(ref_speaker_texts[s].split()),
            reverse=True
        )

        for ref_spk in ref_speakers_sorted:
            ref_text = ref_speaker_texts[ref_spk].strip()

            # Skip empty reference speakers
            if not ref_text:
                assignment.append((ref_spk, None))
                continue

            ref_words = len(ref_text.split())
            total_ref_words += ref_words

            # Find best unmatched hypothesis speaker
            best_hyp = None
            best_wer = float('inf')
            best_metrics = None

            for hyp_spk in hyp_speaker_texts.keys():
                if hyp_spk not in matched_hyp:
                    metrics = wer_matrix[ref_spk][hyp_spk]
                    if metrics['wer'] < best_wer:
                        best_wer = metrics['wer']
                        best_hyp = hyp_spk
                        best_metrics = metrics

            if best_hyp:
                # Match found
                assignment.append((ref_spk, best_hyp))
                matched_hyp.add(best_hyp)
                total_errors += best_metrics['errors']
                total_substitutions += best_metrics['substitutions']
                total_deletions += best_metrics['deletions']
                total_insertions += best_metrics['insertions']
            else:
                # No hypothesis speaker available - count as missed speaker
                assignment.append((ref_spk, None))
                total_errors += ref_words  # All words are deletions
                total_deletions += ref_words

        # Count false alarm speakers (hypothesis speakers not matched)
        for hyp_spk in hyp_speaker_texts.keys():
            if hyp_spk not in matched_hyp:
                assignment.append((None, hyp_spk))
                hyp_text = hyp_speaker_texts[hyp_spk].strip()
                if hyp_text:  # Only count non-empty hypothesis speakers
                    hyp_words = len(hyp_text.split())
                    total_errors += hyp_words  # All words are insertions
                    total_insertions += hyp_words

        # Calculate CP-WER
        cp_wer = total_errors / total_ref_words if total_ref_words > 0 else 0.0

        # Count missed and false alarm speakers
        missed_speaker = sum(1 for r, h in assignment if r and not h)
        falarm_speaker = sum(1 for r, h in assignment if not r and h)
        scored_speaker = sum(1 for r, h in assignment if r and h)

        return {
            "cp_wer": cp_wer,
            "total_errors": total_errors,
            "total_reference_words": total_ref_words,
            "insertions": total_insertions,
            "deletions": total_deletions,
            "substitutions": total_substitutions,
            "missed_speaker": missed_speaker,
            "falarm_speaker": falarm_speaker,
            "scored_speaker": scored_speaker,
            "ref_num_speakers": ref_speakers,
            "hyp_num_speakers": hyp_speakers,
            "speaker_count_correct": 1 if ref_speakers == hyp_speakers else 0,
            "optimal_assignment": tuple(assignment),
            "cp_wer_approximation": "greedy",  # Flag that this is approximate
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
