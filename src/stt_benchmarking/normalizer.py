"""Text normalization utilities using whisper_normalizer."""

from typing import List, Optional
from whisper_normalizer.english import EnglishTextNormalizer
from .models import Transcript, Utterance
from .semantic_normalizer import apply_semantic_replacements, load_semantic_word_list


class TextNormalizer:
    """Normalizes transcript text using Whisper's English text normalizer.

    Optionally applies semantic word list replacements after Whisper normalization.
    """

    def __init__(
        self,
        semantic_word_list_path: Optional[str] = None,
        semantic_word_list: Optional[List[List[str]]] = None,
    ):
        """Initialize the text normalizer.

        Args:
            semantic_word_list_path: Path to semantic word list JSON file.
            semantic_word_list: Direct word list (overrides path).
        """
        self.normalizer = EnglishTextNormalizer()
        self.semantic_word_list = semantic_word_list
        if self.semantic_word_list is None and semantic_word_list_path:
            self.semantic_word_list = load_semantic_word_list(semantic_word_list_path)

    def normalize_text(self, text: str) -> str:
        """Normalize a single text string.

        Applies Whisper normalization first, then semantic replacements
        if a semantic word list was provided.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text
        """
        text = self.normalizer(text)
        if self.semantic_word_list:
            text = apply_semantic_replacements(text, self.semantic_word_list)
        return text

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
