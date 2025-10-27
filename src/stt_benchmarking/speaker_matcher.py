"""Speaker matching functionality using optimal permutation from CP-WER."""

from typing import Dict, List, Optional
from thefuzz import fuzz
from .models import Transcript, Utterance


class SpeakerMatcher:
    """Matches speaker labels between reference and hypothesis transcripts using fuzzy matching."""

    def __init__(self, threshold: float = 80.0):
        """Initialize speaker matcher.

        Args:
            threshold: Minimum fuzzy matching score (0-100) to consider speakers as matching
        """
        self.threshold = threshold

    def match_speakers(
        self,
        reference: Transcript,
        hypothesis: Transcript
    ) -> Dict[str, str]:
        """Match hypothesis speaker labels to reference speaker labels.

        This method concatenates all text for each speaker and uses fuzzy matching
        to find the best alignment between hypothesis and reference speakers.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript

        Returns:
            Dictionary mapping hypothesis speaker labels to reference speaker labels
        """
        ref_speakers = reference.get_speakers()
        hyp_speakers = hypothesis.get_speakers()

        # Build speaker text profiles
        ref_profiles = {
            spk: reference.get_text_by_speaker(spk)
            for spk in ref_speakers
        }

        hyp_profiles = {
            spk: hypothesis.get_text_by_speaker(spk)
            for spk in hyp_speakers
        }

        # Compute similarity matrix
        speaker_mapping = {}

        for hyp_spk, hyp_text in hyp_profiles.items():
            best_match = None
            best_score = 0.0

            for ref_spk, ref_text in ref_profiles.items():
                # Skip if reference speaker already matched
                if ref_spk in speaker_mapping.values():
                    continue

                # Use token_sort_ratio for better matching with different word orders
                score = fuzz.token_sort_ratio(hyp_text.lower(), ref_text.lower())

                if score > best_score and score >= self.threshold:
                    best_score = score
                    best_match = ref_spk

            # Map to best match or keep original if no good match found
            speaker_mapping[hyp_spk] = best_match if best_match else hyp_spk

        return speaker_mapping

    def apply_speaker_mapping(
        self,
        transcript: Transcript,
        mapping: Dict[str, str]
    ) -> Transcript:
        """Apply speaker label mapping to a transcript.

        Args:
            transcript: Transcript to modify
            mapping: Dictionary mapping old speaker labels to new labels

        Returns:
            New Transcript with updated speaker labels
        """
        new_utterances = []
        for utt in transcript:
            new_speaker = mapping.get(utt.speaker, utt.speaker)
            new_utterances.append(
                Utterance(
                    speaker=new_speaker,
                    text=utt.text,
                    start_time=utt.start_time,
                    end_time=utt.end_time
                )
            )
        return Transcript(new_utterances)

    def match_speakers_using_cpwer(
        self,
        reference: Transcript,
        hypothesis: Transcript
    ) -> Dict[str, str]:
        """Match hypothesis speaker labels to reference using optimal CP-WER assignment.

        This method uses meeteval's CP-WER calculation which finds the optimal
        speaker permutation using the Hungarian algorithm. This is more accurate
        than fuzzy text matching.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript

        Returns:
            Dictionary mapping hypothesis speaker labels to reference speaker labels
        """
        try:
            from meeteval.wer.wer.cp import cp_word_error_rate
        except ImportError:
            # Fall back to fuzzy matching if meeteval not available
            return self.match_speakers(reference, hypothesis)

        # Group by speaker and concatenate text
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

        try:
            # Get optimal assignment from CP-WER
            result = cp_word_error_rate(ref_speaker_texts, hyp_speaker_texts)

            # Convert assignment to mapping dictionary
            # assignment is a tuple of (ref_speaker, hyp_speaker) pairs
            speaker_mapping = {}
            for ref_spk, hyp_spk in result.assignment:
                if hyp_spk is not None:
                    # Map hypothesis speaker to reference speaker
                    speaker_mapping[hyp_spk] = ref_spk if ref_spk is not None else hyp_spk
                # If hyp_spk is None, this is a missed speaker (no mapping needed)

            # For any hypothesis speakers not in assignment, keep original label
            for hyp_spk in hyp_by_speaker.keys():
                if hyp_spk not in speaker_mapping:
                    speaker_mapping[hyp_spk] = hyp_spk

            return speaker_mapping
        except RuntimeError as e:
            # If too many speakers, use greedy matching instead of fuzzy matching
            if "too many speakers" in str(e).lower() or "are you sure" in str(e).lower():
                return self._greedy_speaker_matching(
                    ref_speaker_texts, hyp_speaker_texts, hyp_by_speaker
                )
            else:
                raise

    def _greedy_speaker_matching(
        self,
        ref_speaker_texts: Dict[str, str],
        hyp_speaker_texts: Dict[str, str],
        hyp_by_speaker: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Greedy speaker matching for cases with >20 speakers.

        Args:
            ref_speaker_texts: Dictionary mapping reference speakers to concatenated text
            hyp_speaker_texts: Dictionary mapping hypothesis speakers to concatenated text
            hyp_by_speaker: Dictionary mapping hypothesis speakers to utterance list

        Returns:
            Dictionary mapping hypothesis speaker labels to reference speaker labels
        """
        import jiwer

        # Calculate WER matrix
        wer_matrix = {}
        for ref_spk, ref_text in ref_speaker_texts.items():
            wer_matrix[ref_spk] = {}
            ref_text_clean = ref_text.strip()

            # Skip empty reference speakers
            if not ref_text_clean:
                for hyp_spk in hyp_speaker_texts.keys():
                    wer_matrix[ref_spk][hyp_spk] = float('inf')
                continue

            for hyp_spk, hyp_text in hyp_speaker_texts.items():
                hyp_text_clean = hyp_text.strip()

                # Handle empty hypothesis text
                if not hyp_text_clean:
                    wer_matrix[ref_spk][hyp_spk] = 1.0  # 100% error
                else:
                    measures = jiwer.compute_measures(ref_text_clean, hyp_text_clean)
                    wer_matrix[ref_spk][hyp_spk] = measures['wer']

        # Greedy assignment: match biggest speakers first
        speaker_mapping = {}
        matched_ref = set()

        # Sort hypothesis speakers by word count (descending)
        hyp_speakers_sorted = sorted(
            hyp_speaker_texts.keys(),
            key=lambda s: len(hyp_speaker_texts[s].split()),
            reverse=True
        )

        for hyp_spk in hyp_speakers_sorted:
            # Find best unmatched reference speaker
            best_ref = None
            best_wer = float('inf')

            for ref_spk in ref_speaker_texts.keys():
                if ref_spk not in matched_ref:
                    wer = wer_matrix[ref_spk][hyp_spk]
                    if wer < best_wer:
                        best_wer = wer
                        best_ref = ref_spk

            if best_ref:
                speaker_mapping[hyp_spk] = best_ref
                matched_ref.add(best_ref)
            else:
                # No reference speaker available
                speaker_mapping[hyp_spk] = hyp_spk

        return speaker_mapping

    def match_and_align(
        self,
        reference: Transcript,
        hypothesis: Transcript,
        use_cpwer: bool = True
    ) -> Transcript:
        """Match speakers and return hypothesis with aligned speaker labels.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript
            use_cpwer: If True, use CP-WER optimal assignment (recommended).
                      If False, use fuzzy text matching (legacy method).

        Returns:
            Hypothesis transcript with speaker labels aligned to reference
        """
        if use_cpwer:
            mapping = self.match_speakers_using_cpwer(reference, hypothesis)
        else:
            mapping = self.match_speakers(reference, hypothesis)
        return self.apply_speaker_mapping(hypothesis, mapping)
