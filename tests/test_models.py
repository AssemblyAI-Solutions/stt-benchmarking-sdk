"""Tests for data models."""

import pytest
from stt_benchmarking.models import Utterance, Transcript


def test_utterance_creation():
    """Test creating an Utterance."""
    utt = Utterance(speaker="Alice", text="Hello world")
    assert utt.speaker == "Alice"
    assert utt.text == "Hello world"
    assert utt.start_time is None
    assert utt.end_time is None


def test_utterance_with_timestamps():
    """Test creating an Utterance with timestamps."""
    utt = Utterance(
        speaker="Bob",
        text="Hi there",
        start_time=0.0,
        end_time=1.5
    )
    assert utt.speaker == "Bob"
    assert utt.text == "Hi there"
    assert utt.start_time == 0.0
    assert utt.end_time == 1.5


def test_utterance_from_dict():
    """Test creating Utterance from dictionary."""
    data = {"speaker": "Alice", "text": "Hello"}
    utt = Utterance.from_dict(data)
    assert utt.speaker == "Alice"
    assert utt.text == "Hello"


def test_utterance_to_dict():
    """Test converting Utterance to dictionary."""
    utt = Utterance(speaker="Bob", text="Hi", start_time=0.0, end_time=1.0)
    data = utt.to_dict()
    assert data["speaker"] == "Bob"
    assert data["text"] == "Hi"
    assert data["start_time"] == 0.0
    assert data["end_time"] == 1.0


def test_transcript_creation():
    """Test creating a Transcript."""
    utterances = [
        Utterance(speaker="Alice", text="Hello"),
        Utterance(speaker="Bob", text="Hi"),
    ]
    transcript = Transcript(utterances)
    assert len(transcript) == 2
    assert transcript[0].speaker == "Alice"
    assert transcript[1].speaker == "Bob"


def test_transcript_from_list():
    """Test creating Transcript from list."""
    data = [
        {"speaker": "Alice", "text": "Hello"},
        {"speaker": "Bob", "text": "Hi"},
    ]
    transcript = Transcript.from_list(data)
    assert len(transcript) == 2


def test_transcript_to_list():
    """Test converting Transcript to list."""
    utterances = [
        Utterance(speaker="Alice", text="Hello"),
        Utterance(speaker="Bob", text="Hi"),
    ]
    transcript = Transcript(utterances)
    data = transcript.to_list()
    assert len(data) == 2
    assert data[0]["speaker"] == "Alice"


def test_get_speakers():
    """Test getting unique speakers."""
    utterances = [
        Utterance(speaker="Alice", text="Hello"),
        Utterance(speaker="Bob", text="Hi"),
        Utterance(speaker="Alice", text="How are you"),
    ]
    transcript = Transcript(utterances)
    speakers = transcript.get_speakers()
    assert set(speakers) == {"Alice", "Bob"}


def test_get_text_by_speaker():
    """Test getting text for a specific speaker."""
    utterances = [
        Utterance(speaker="Alice", text="Hello"),
        Utterance(speaker="Bob", text="Hi"),
        Utterance(speaker="Alice", text="How are you"),
    ]
    transcript = Transcript(utterances)
    alice_text = transcript.get_text_by_speaker("Alice")
    assert alice_text == "Hello How are you"


def test_get_all_text():
    """Test getting all text concatenated."""
    utterances = [
        Utterance(speaker="Alice", text="Hello"),
        Utterance(speaker="Bob", text="Hi"),
    ]
    transcript = Transcript(utterances)
    all_text = transcript.get_all_text()
    assert all_text == "Hello Hi"


def test_transcript_iteration():
    """Test iterating over transcript."""
    utterances = [
        Utterance(speaker="Alice", text="Hello"),
        Utterance(speaker="Bob", text="Hi"),
    ]
    transcript = Transcript(utterances)
    speakers = [utt.speaker for utt in transcript]
    assert speakers == ["Alice", "Bob"]
