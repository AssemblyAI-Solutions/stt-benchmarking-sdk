"""Voice Activity Detection utilities for detecting speech boundaries in audio files."""

import wave
import webrtcvad


def detect_speech_end_time(audio_path: str, aggressiveness: int = 3) -> float:
    """Detect when speech ends in an audio file using WebRTC VAD.

    Args:
        audio_path: Path to the WAV file (must be 16kHz mono 16-bit PCM)
        aggressiveness: VAD aggressiveness (0-3, higher = more aggressive filtering)

    Returns:
        Time in seconds when speech ends (last speech frame detected)
    """
    vad = webrtcvad.Vad(aggressiveness)

    with wave.open(audio_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        assert sample_rate == 16000, f"Audio must be 16kHz, got {sample_rate}Hz"
        assert wf.getnchannels() == 1, f"Audio must be mono, got {wf.getnchannels()} channels"
        assert wf.getsampwidth() == 2, f"Audio must be 16-bit, got {wf.getsampwidth() * 8}-bit"

        frame_duration_ms = 30
        frame_size = int(sample_rate * frame_duration_ms / 1000) * 2  # 2 bytes per sample

        last_speech_time = 0.0
        current_time = 0.0

        while True:
            frame = wf.readframes(int(sample_rate * frame_duration_ms / 1000))
            if len(frame) < frame_size:
                break

            is_speech = vad.is_speech(frame, sample_rate)

            if is_speech:
                last_speech_time = current_time + (frame_duration_ms / 1000.0)

            current_time += frame_duration_ms / 1000.0

    return last_speech_time


def add_silence_to_audio(
    audio_data: bytes,
    duration_ms: int = 1000,
    sample_rate: int = 16000
) -> bytes:
    """Append silence to raw audio data.

    Args:
        audio_data: Raw audio bytes (16-bit PCM)
        duration_ms: Amount of silence to add in milliseconds
        sample_rate: Sample rate of the audio

    Returns:
        Audio data with silence appended
    """
    num_samples = int(sample_rate * duration_ms / 1000)
    silence = b'\x00\x00' * num_samples
    return audio_data + silence
