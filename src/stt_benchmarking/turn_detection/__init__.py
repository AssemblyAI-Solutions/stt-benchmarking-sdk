"""Turn detection benchmarking for AssemblyAI streaming APIs."""

from .models import (
    TurnSample,
    TurnDetectionResult,
    SUPPORTED_MODELS,
    STREAMING_PRESETS,
    U3_PRO_PRESETS,
    get_presets_for_model,
)
from .detector import AssemblyAIStreamingDetector
from .metrics import TurnDetectionMetrics
from .benchmark import TurnDetectionBenchmark
from .export import TurnDetectionExporter
from .vad import detect_speech_end_time, add_silence_to_audio

__all__ = [
    "TurnSample",
    "TurnDetectionResult",
    "SUPPORTED_MODELS",
    "STREAMING_PRESETS",
    "U3_PRO_PRESETS",
    "get_presets_for_model",
    "AssemblyAIStreamingDetector",
    "TurnDetectionMetrics",
    "TurnDetectionBenchmark",
    "TurnDetectionExporter",
    "detect_speech_end_time",
    "add_silence_to_audio",
]
