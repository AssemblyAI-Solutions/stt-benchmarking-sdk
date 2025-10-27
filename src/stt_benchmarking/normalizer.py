"""Text normalization utilities using whisper_normalizer."""

from whisper_normalizer.english import EnglishTextNormalizer
from .models import Transcript, Utterance


class TextNormalizer:
    """Normalizes transcript text using Whisper's English text normalizer."""

    def __init__(self):
        """Initialize the text normalizer."""
        self.normalizer = EnglishTextNormalizer()

    def normalize_text(self, text: str) -> str:
        """Normalize a single text string.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text
        """
        return self.normalizer(text)

    def normalize_utterance(self, utterance: Utterance) -> Utterance:
        """Normalize an utterance's text.

        Args:
            utterance: Utterance to normalize

        Returns:
            New Utterance with normalized text
        """
        return Utterance(
            speaker=utterance.speaker,
            text=self.normalize_text(utterance.text),
            start_time=utterance.start_time,
            end_time=utterance.end_time
        )

    def normalize_transcript(self, transcript: Transcript) -> Transcript:
        """Normalize all text in a transcript.

        Args:
            transcript: Transcript to normalize

        Returns:
            New Transcript with all text normalized
        """
        normalized_utterances = [
            self.normalize_utterance(utt) for utt in transcript
        ]
        return Transcript(normalized_utterances)
