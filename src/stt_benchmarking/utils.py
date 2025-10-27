"""Utility functions for loading and converting transcript files."""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Union
from .models import Transcript


class TranscriptLoader:
    """Utilities for loading transcripts from various file formats."""

    @staticmethod
    def from_json(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Load transcript from JSON file.

        Expected format:
        [
            {"speaker": "...", "text": "...", "start_time": ..., "end_time": ...},
            ...
        ]

        Args:
            file_path: Path to JSON file

        Returns:
            List of utterance dictionaries
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"Expected list of utterances, got {type(data)}")

        return data

    @staticmethod
    def from_csv(
        file_path: Union[str, Path],
        speaker_column: str = "speaker",
        text_column: str = "text",
        start_time_column: str = None,
        end_time_column: str = None
    ) -> List[Dict[str, Any]]:
        """Load transcript from CSV file.

        Args:
            file_path: Path to CSV file
            speaker_column: Name of speaker column
            text_column: Name of text column
            start_time_column: Optional name of start_time column
            end_time_column: Optional name of end_time column

        Returns:
            List of utterance dictionaries
        """
        utterances = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                utterance = {
                    "speaker": row[speaker_column],
                    "text": row[text_column]
                }

                if start_time_column and start_time_column in row:
                    utterance["start_time"] = float(row[start_time_column])

                if end_time_column and end_time_column in row:
                    utterance["end_time"] = float(row[end_time_column])

                utterances.append(utterance)

        return utterances

    @staticmethod
    def from_text(
        file_path: Union[str, Path],
        default_speaker: str = "Speaker"
    ) -> List[Dict[str, Any]]:
        """Load transcript from plain text file (one utterance per line).

        Format:
            Speaker A: Hello world
            Speaker B: Hi there
            Speaker A: How are you

        Or without speaker labels (uses default_speaker):
            Hello world
            Hi there
            How are you

        Args:
            file_path: Path to text file
            default_speaker: Default speaker name if not specified in line

        Returns:
            List of utterance dictionaries
        """
        utterances = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                # Check if line has speaker label
                if ':' in line:
                    parts = line.split(':', 1)
                    speaker = parts[0].strip()
                    text = parts[1].strip()
                else:
                    speaker = f"{default_speaker}_{line_num}"
                    text = line

                utterances.append({
                    "speaker": speaker,
                    "text": text
                })

        return utterances

    @staticmethod
    def from_srt(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Load transcript from SRT subtitle file.

        Args:
            file_path: Path to SRT file

        Returns:
            List of utterance dictionaries with timestamps
        """
        utterances = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into subtitle blocks
        blocks = content.strip().split('\n\n')

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue

            # Parse timestamp line (e.g., "00:00:01,000 --> 00:00:03,000")
            timestamp_line = lines[1]
            if '-->' not in timestamp_line:
                continue

            start_str, end_str = timestamp_line.split('-->')
            start_time = TranscriptLoader._parse_srt_timestamp(start_str.strip())
            end_time = TranscriptLoader._parse_srt_timestamp(end_str.strip())

            # Text is everything after timestamp line
            text = ' '.join(lines[2:])

            utterances.append({
                "speaker": "Speaker",  # SRT doesn't have speaker info
                "text": text,
                "start_time": start_time,
                "end_time": end_time
            })

        return utterances

    @staticmethod
    def _parse_srt_timestamp(timestamp: str) -> float:
        """Parse SRT timestamp to seconds.

        Args:
            timestamp: Timestamp string like "00:00:01,000"

        Returns:
            Time in seconds
        """
        # Format: HH:MM:SS,mmm
        time_part, ms_part = timestamp.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)

        return h * 3600 + m * 60 + s + ms / 1000.0

    @staticmethod
    def auto_detect_format(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Automatically detect file format and load transcript.

        Args:
            file_path: Path to transcript file

        Returns:
            List of utterance dictionaries

        Raises:
            ValueError: If file format cannot be determined
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == '.json':
            return TranscriptLoader.from_json(file_path)
        elif suffix == '.csv':
            return TranscriptLoader.from_csv(file_path)
        elif suffix == '.txt':
            return TranscriptLoader.from_text(file_path)
        elif suffix == '.srt':
            return TranscriptLoader.from_srt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")


class TranscriptWriter:
    """Utilities for writing transcripts to various file formats."""

    @staticmethod
    def to_json(
        utterances: List[Dict[str, Any]],
        file_path: Union[str, Path],
        indent: int = 2
    ) -> None:
        """Write transcript to JSON file.

        Args:
            utterances: List of utterance dictionaries
            file_path: Output file path
            indent: JSON indentation level
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(utterances, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def to_csv(
        utterances: List[Dict[str, Any]],
        file_path: Union[str, Path],
        include_timestamps: bool = True
    ) -> None:
        """Write transcript to CSV file.

        Args:
            utterances: List of utterance dictionaries
            file_path: Output file path
            include_timestamps: Whether to include timestamp columns
        """
        if not utterances:
            return

        # Determine fieldnames
        fieldnames = ['speaker', 'text']
        if include_timestamps:
            fieldnames.extend(['start_time', 'end_time'])

        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for utt in utterances:
                row = {k: utt.get(k, '') for k in fieldnames}
                writer.writerow(row)

    @staticmethod
    def to_text(
        utterances: List[Dict[str, Any]],
        file_path: Union[str, Path],
        include_speaker: bool = True
    ) -> None:
        """Write transcript to plain text file.

        Args:
            utterances: List of utterance dictionaries
            file_path: Output file path
            include_speaker: Whether to include speaker labels
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            for utt in utterances:
                if include_speaker:
                    f.write(f"{utt['speaker']}: {utt['text']}\n")
                else:
                    f.write(f"{utt['text']}\n")


def validate_transcript(utterances: List[Dict[str, Any]]) -> bool:
    """Validate transcript format.

    Args:
        utterances: List of utterance dictionaries

    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(utterances, list):
        raise ValueError("Transcript must be a list")

    if len(utterances) == 0:
        raise ValueError("Transcript is empty")

    for i, utt in enumerate(utterances):
        if not isinstance(utt, dict):
            raise ValueError(f"Utterance {i} is not a dictionary")

        if 'speaker' not in utt:
            raise ValueError(f"Utterance {i} missing 'speaker' field")

        if 'text' not in utt:
            raise ValueError(f"Utterance {i} missing 'text' field")

        if not isinstance(utt['speaker'], str):
            raise ValueError(f"Utterance {i} 'speaker' must be string")

        if not isinstance(utt['text'], str):
            raise ValueError(f"Utterance {i} 'text' must be string")

        # Validate optional timestamps
        if 'start_time' in utt:
            if not isinstance(utt['start_time'], (int, float)):
                raise ValueError(f"Utterance {i} 'start_time' must be number")

        if 'end_time' in utt:
            if not isinstance(utt['end_time'], (int, float)):
                raise ValueError(f"Utterance {i} 'end_time' must be number")

        if 'start_time' in utt and 'end_time' in utt:
            if utt['start_time'] > utt['end_time']:
                raise ValueError(f"Utterance {i} start_time > end_time")

    return True
