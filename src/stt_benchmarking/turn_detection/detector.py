"""AssemblyAI streaming detector for turn-end detection benchmarking."""

import time
import threading
from typing import List, Optional

from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingParameters,
    StreamingClientOptions,
    StreamingEvents,
    TurnEvent,
)
from assemblyai.streaming.v3.models import SpeechModel

from .models import (
    TurnDetectionResult,
    SUPPORTED_MODELS,
    _CONFIDENCE_BASED_MODELS,
    get_presets_for_model,
)
from .vad import detect_speech_end_time, add_silence_to_audio


class AssemblyAIStreamingDetector:
    """Streams audio to AssemblyAI and evaluates turn-end detection.

    Supports confidence-based models (universal-streaming-multilingual,
    universal-streaming-english) and punctuation-based models (u3-rt-pro).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "universal-streaming-multilingual",
        preset: str = "balanced",
        sample_rate: int = 16000,
    ):
        """Initialize the detector.

        Args:
            api_key: AssemblyAI API key
            model: Speech model ID - "universal-streaming-multilingual",
                   "universal-streaming-english", or "u3-rt-pro"
            preset: Preset name - "aggressive", "balanced", or "conservative"
            sample_rate: Audio sample rate in Hz (must match audio files)
        """
        if not api_key:
            raise ValueError("AssemblyAI API key is required")

        if model not in SUPPORTED_MODELS:
            raise ValueError(
                f"Unknown model '{model}'. Supported models: {SUPPORTED_MODELS}"
            )

        self.api_key = api_key
        self.model = model
        self.sample_rate = sample_rate

        presets = get_presets_for_model(model)

        if preset not in presets:
            raise ValueError(
                f"Unknown preset '{preset}' for model '{model}'. "
                f"Must be one of: {list(presets.keys())}"
            )

        self.preset = preset
        self.preset_config = presets[preset]

    def _build_streaming_params(self) -> StreamingParameters:
        """Build StreamingParameters based on model and preset."""
        if self.model in _CONFIDENCE_BASED_MODELS:
            return StreamingParameters(
                sample_rate=self.sample_rate,
                speech_model=self.model,
                end_of_turn_confidence_threshold=self.preset_config["end_of_turn_confidence_threshold"],
                min_turn_silence=self.preset_config["min_turn_silence"],
                max_turn_silence=self.preset_config["max_turn_silence"],
            )
        else:  # u3-rt-pro
            return StreamingParameters(
                sample_rate=self.sample_rate,
                speech_model=self.model,
                min_turn_silence=self.preset_config["min_turn_silence"],
                max_turn_silence=self.preset_config["max_turn_silence"],
            )

    def process_audio_file(
        self,
        audio_path: str,
        vad_window_ms: int = 1000,
        silence_padding_ms: int = 1000,
        verbose: bool = False,
    ) -> TurnDetectionResult:
        """Stream an audio file and detect turn-ends.

        Streams audio at real-time speed, captures turn events, and evaluates
        whether a turn-end was detected within a VAD-based window after speech ends.

        Args:
            audio_path: Path to WAV file (16kHz mono 16-bit PCM)
            vad_window_ms: Detection window in ms after VAD-detected speech end
            silence_padding_ms: Silence to append after audio (gives model processing time)
            verbose: Print debug info during streaming

        Returns:
            TurnDetectionResult with detection outcome
        """
        speech_end_time_seconds = detect_speech_end_time(audio_path)
        if verbose:
            print(f"  VAD detected speech end at: {speech_end_time_seconds:.3f}s")

        turns: List[dict] = []
        session_ended = threading.Event()

        def on_begin(client, event):
            pass

        def on_turn(client, event):
            turns.append({
                'event': event,
                'timestamp': time.time(),
                'end_of_turn': event.end_of_turn,
                'confidence': event.end_of_turn_confidence,
                'transcript': event.transcript,
            })

        def on_termination(client, event):
            session_ended.set()

        def on_error(client, error):
            if verbose:
                print(f"  Streaming error: {error}")
            session_ended.set()

        params = self._build_streaming_params()

        client = StreamingClient(
            options=StreamingClientOptions(api_key=self.api_key)
        )

        client.on(StreamingEvents.Begin, on_begin)
        client.on(StreamingEvents.Turn, on_turn)
        client.on(StreamingEvents.Termination, on_termination)
        client.on(StreamingEvents.Error, on_error)

        client.connect(params)

        # Read and prepare audio
        with open(audio_path, 'rb') as f:
            audio_data = f.read()

        # Skip WAV header
        if audio_data[:4] == b'RIFF':
            audio_data = audio_data[44:]

        audio_data = add_silence_to_audio(audio_data, duration_ms=silence_padding_ms)

        bytes_per_ms = self.sample_rate * 2 / 1000  # 16-bit mono
        audio_duration_ms = len(audio_data) / bytes_per_ms

        # Stream at real-time speed
        chunk_size = 2048  # 1024 frames * 2 bytes per sample
        stream_start_time = time.time()
        bytes_sent = 0

        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            bytes_sent += len(chunk)
            samples_sent = bytes_sent / 2
            target_time = stream_start_time + (samples_sent / self.sample_rate)

            client.stream(chunk)

            sleep_time = target_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

        if verbose:
            audio_end_time = time.time()
            actual_duration = audio_end_time - stream_start_time
            expected_duration = audio_duration_ms / 1000
            print(f"  Streaming: expected={expected_duration:.3f}s, actual={actual_duration:.3f}s, "
                  f"drift={abs(expected_duration - actual_duration)*1000:.1f}ms")

        # Brief pause for final processing
        time.sleep(0.2)

        try:
            client.disconnect(terminate=True)
        except Exception:
            pass

        # Evaluate using VAD-based window
        speech_end_timestamp = stream_start_time + speech_end_time_seconds
        vad_window_seconds = vad_window_ms / 1000.0
        vad_detection_window = speech_end_timestamp + vad_window_seconds

        end_of_turn_detected = False
        end_of_turn_confidence = 0.0
        transcript = ""

        if turns:
            if verbose:
                print(f"  Total turn events: {len(turns)}")
                print(f"  Speech ended at: {speech_end_timestamp:.2f}")
                for i, t in enumerate(turns):
                    time_after_speech = t['timestamp'] - speech_end_timestamp
                    print(f"    Turn {i}: end_of_turn={t['end_of_turn']}, "
                          f"confidence={t['confidence']:.4f}, "
                          f"time_after_speech_end={time_after_speech:.3f}s")

            non_empty_turns = [t for t in turns if t['transcript']]
            if non_empty_turns:
                transcript = non_empty_turns[-1]['transcript']

            eot_events = [t for t in turns if t['end_of_turn']]
            eot_in_window = [t for t in eot_events if t['timestamp'] <= vad_detection_window]

            if verbose:
                print(f"  End-of-turn events: {len(eot_events)}")
                print(f"  End-of-turn within {vad_window_ms}ms window: {len(eot_in_window)}")

            if eot_in_window:
                end_of_turn_detected = True
                end_of_turn_confidence = eot_in_window[-1]['confidence']
            else:
                end_of_turn_confidence = eot_events[0]['confidence'] if eot_events else 0.0

        return TurnDetectionResult(
            end_of_turn_detected=end_of_turn_detected,
            end_of_turn_confidence=end_of_turn_confidence,
            transcript=transcript,
            audio_duration_ms=audio_duration_ms,
            speech_end_time=speech_end_time_seconds,
        )
