"""Audio transcription via AssemblyAI and OpenAI Whisper."""

import os
import time
from pathlib import Path
from typing import Dict, Literal, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class Transcriber:
    """Transcribe audio files using AssemblyAI or OpenAI Whisper."""

    ASSEMBLYAI_BASE_URL = "https://api.assemblyai.com"
    OPENAI_URL = "https://api.openai.com/v1/audio/transcriptions"

    def __init__(
        self,
        assemblyai_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        assemblyai_config: Optional[Dict] = None,
    ):
        """Initialize transcriber.

        Args:
            assemblyai_api_key: AssemblyAI API key. Defaults to ASSEMBLYAI_API_KEY env var.
            openai_api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            assemblyai_config: AssemblyAI transcription config. Defaults to universal-3-pro.
        """
        self.assemblyai_api_key = assemblyai_api_key or os.getenv("ASSEMBLYAI_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.assemblyai_config = assemblyai_config or {
            "speech_models": ["universal-3-pro"],
            "language_detection": True,
        }

    def transcribe(
        self,
        audio_path: str,
        provider: Literal["assemblyai", "openai"] = "assemblyai",
    ) -> str:
        """Transcribe an audio file and return plain text.

        Args:
            audio_path: Path to audio file.
            provider: "assemblyai" or "openai".

        Returns:
            Plain text transcription.
        """
        if provider == "assemblyai":
            return self._transcribe_assemblyai(audio_path)
        elif provider == "openai":
            return self._transcribe_openai(audio_path)
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'assemblyai' or 'openai'.")

    def _transcribe_assemblyai(self, audio_path: str) -> str:
        if not self.assemblyai_api_key:
            raise ValueError("ASSEMBLYAI_API_KEY required. Set it in .env or pass to constructor.")

        headers = {"authorization": self.assemblyai_api_key}

        # Upload
        print(f"  [AssemblyAI] Uploading {Path(audio_path).name}...")
        with open(audio_path, "rb") as f:
            resp = requests.post(
                f"{self.ASSEMBLYAI_BASE_URL}/v2/upload", headers=headers, data=f
            )
        resp.raise_for_status()
        audio_url = resp.json()["upload_url"]

        # Submit
        print(f"  [AssemblyAI] Submitting transcription...")
        resp = requests.post(
            f"{self.ASSEMBLYAI_BASE_URL}/v2/transcript",
            headers={**headers, "content-type": "application/json"},
            json={"audio_url": audio_url, **self.assemblyai_config},
        )
        resp.raise_for_status()
        transcript_id = resp.json()["id"]

        # Poll
        print(f"  [AssemblyAI] Waiting (ID: {transcript_id})...")
        while True:
            resp = requests.get(
                f"{self.ASSEMBLYAI_BASE_URL}/v2/transcript/{transcript_id}",
                headers=headers,
            )
            resp.raise_for_status()
            result = resp.json()

            if result["status"] == "completed":
                text = result.get("text", "")
                print(f"  [AssemblyAI] Done ({len(text.split())} words)")
                return text
            elif result["status"] == "error":
                raise RuntimeError(
                    f"Transcription failed: {result.get('error', 'Unknown error')}"
                )

            print(f"  [AssemblyAI] Status: {result['status']}...")
            time.sleep(3)

    def _transcribe_openai(self, audio_path: str) -> str:
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY required. Set it in .env or pass to constructor.")

        print(f"  [OpenAI] Transcribing {Path(audio_path).name} with whisper-1...")
        with open(audio_path, "rb") as f:
            resp = requests.post(
                self.OPENAI_URL,
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                files={"file": (Path(audio_path).name, f)},
                data={"model": "whisper-1"},
            )

        resp.raise_for_status()
        text = resp.json()["text"]
        print(f"  [OpenAI] Done ({len(text.split())} words)")
        return text
