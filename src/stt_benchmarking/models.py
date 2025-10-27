"""Data models for STT benchmarking."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Utterance:
    """Represents a single utterance in a transcript.

    Attributes:
        speaker: Speaker identifier/label
        text: Transcribed text content
        start_time: Optional start time in seconds
        end_time: Optional end time in seconds
    """
    speaker: str
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Utterance":
        """Create an Utterance from a dictionary.

        Args:
            data: Dictionary with keys 'speaker', 'text', and optionally 'start_time', 'end_time'

        Returns:
            Utterance instance
        """
        return cls(
            speaker=data["speaker"],
            text=data["text"],
            start_time=data.get("start_time"),
            end_time=data.get("end_time")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Utterance to dictionary.

        Returns:
            Dictionary representation
        """
        result = {
            "speaker": self.speaker,
            "text": self.text
        }
        if self.start_time is not None:
            result["start_time"] = self.start_time
        if self.end_time is not None:
            result["end_time"] = self.end_time
        return result


class Transcript:
    """Represents a complete transcript as a list of utterances.

    Attributes:
        utterances: List of Utterance objects in chronological order
    """

    def __init__(self, utterances: List[Utterance]):
        """Initialize transcript.

        Args:
            utterances: List of Utterance objects
        """
        self.utterances = utterances

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "Transcript":
        """Create a Transcript from a list of dictionaries.

        Args:
            data: List of dictionaries, each with 'speaker' and 'text' keys

        Returns:
            Transcript instance
        """
        utterances = [Utterance.from_dict(item) for item in data]
        return cls(utterances)

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert Transcript to list of dictionaries.

        Returns:
            List of dictionary representations
        """
        return [utt.to_dict() for utt in self.utterances]

    def get_speakers(self) -> List[str]:
        """Get list of unique speakers in the transcript.

        Returns:
            List of unique speaker identifiers
        """
        return list(set(utt.speaker for utt in self.utterances))

    def get_text_by_speaker(self, speaker: str) -> str:
        """Get all text from a specific speaker concatenated together.

        Args:
            speaker: Speaker identifier

        Returns:
            Concatenated text from all utterances by this speaker
        """
        texts = [utt.text for utt in self.utterances if utt.speaker == speaker]
        return " ".join(texts)

    def get_all_text(self) -> str:
        """Get all text concatenated in order.

        Returns:
            All transcript text concatenated
        """
        return " ".join(utt.text for utt in self.utterances)

    def __len__(self) -> int:
        """Return number of utterances."""
        return len(self.utterances)

    def __iter__(self):
        """Iterate over utterances."""
        return iter(self.utterances)

    def __getitem__(self, index: int) -> Utterance:
        """Get utterance by index."""
        return self.utterances[index]
