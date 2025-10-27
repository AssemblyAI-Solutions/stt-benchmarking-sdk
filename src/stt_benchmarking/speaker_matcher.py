"""Speaker matching functionality using fuzzy string matching."""

from typing import Dict, List
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

    def match_and_align(
        self,
        reference: Transcript,
        hypothesis: Transcript
    ) -> Transcript:
        """Match speakers and return hypothesis with aligned speaker labels.

        Args:
            reference: Reference (ground truth) transcript
            hypothesis: Hypothesis (predicted) transcript

        Returns:
            Hypothesis transcript with speaker labels aligned to reference
        """
        mapping = self.match_speakers(reference, hypothesis)
        return self.apply_speaker_mapping(hypothesis, mapping)
