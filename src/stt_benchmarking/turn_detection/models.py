"""Data models for turn detection benchmarking."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TurnSample:
    """A single audio sample with ground truth for turn detection.

    Attributes:
        id: Unique identifier for the sample
        audio_path: Path to the WAV file (16kHz mono 16-bit PCM)
        ground_truth: True = turn-shift (speaker finished), False = turn-hold (speaker continues)
        turn_label: Human-readable label (e.g. "TURN_SHIFT", "TURN_HOLD")
        language: ISO 639-3 language code (e.g. "eng")
    """
    id: str
    audio_path: str
    ground_truth: bool
    turn_label: str = ""
    language: str = "eng"


@dataclass
class TurnDetectionResult:
    """Result from processing a single audio file for turn detection.

    Attributes:
        end_of_turn_detected: Whether a turn-end was detected within the VAD window
        end_of_turn_confidence: Confidence score of the detected turn-end (0.0 if none)
        transcript: Transcribed text from the streaming session
        audio_duration_ms: Total duration of streamed audio in milliseconds
        speech_end_time: VAD-detected speech end time in seconds
    """
    end_of_turn_detected: bool
    end_of_turn_confidence: float
    transcript: str
    audio_duration_ms: float
    speech_end_time: float


# All supported speech models
SUPPORTED_MODELS = [
    "universal-streaming-multilingual",
    "universal-streaming-english",
    "u3-rt-pro",
]

# Models that use confidence-based turn detection params
_CONFIDENCE_BASED_MODELS = {
    "universal-streaming-multilingual",
    "universal-streaming-english",
}

# Models that use punctuation-based turn detection params
_PUNCTUATION_BASED_MODELS = {
    "u3-rt-pro",
}

# Presets for confidence-based models (universal-streaming-multilingual, universal-streaming-english)
STREAMING_PRESETS = {
    "aggressive": {
        "end_of_turn_confidence_threshold": 0.4,
        "min_turn_silence": 160,
        "max_turn_silence": 400,
    },
    "balanced": {
        "end_of_turn_confidence_threshold": 0.4,
        "min_turn_silence": 400,
        "max_turn_silence": 1280,
    },
    "conservative": {
        "end_of_turn_confidence_threshold": 0.7,
        "min_turn_silence": 800,
        "max_turn_silence": 3600,
    },
}

# Presets for u3-rt-pro (punctuation-based turn detection)
U3_PRO_PRESETS = {
    "aggressive": {
        "min_turn_silence": 50,
        "max_turn_silence": 400,
    },
    "balanced": {
        "min_turn_silence": 100,
        "max_turn_silence": 1000,
    },
    "conservative": {
        "min_turn_silence": 200,
        "max_turn_silence": 2000,
    },
}


def get_presets_for_model(model: str) -> dict:
    """Return the preset dict for a given model."""
    if model in _CONFIDENCE_BASED_MODELS:
        return STREAMING_PRESETS
    elif model in _PUNCTUATION_BASED_MODELS:
        return U3_PRO_PRESETS
    else:
        raise ValueError(
            f"Unknown model '{model}'. Supported models: {SUPPORTED_MODELS}"
        )
