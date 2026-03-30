#!/usr/bin/env python3
"""AssemblyAI vs OpenAI Whisper Comparison

Transcribes the same audio with both AssemblyAI and OpenAI Whisper,
then runs semantic WER on both to compare accuracy side by side.

Usage:
  python examples/whisper_comparison_example.py

Requires audio files in data/audio/ with matching truth files in data/truth/.
Requires both ASSEMBLYAI_API_KEY and OPENAI_API_KEY in .env.
"""

from pathlib import Path
from stt_benchmarking import Transcriber, SemanticWERMetrics, load_semantic_word_list

WORD_LIST_PATH = "data/semantic_word_list.json"


def main():
    print("=" * 60)
    print("AssemblyAI vs OpenAI Whisper Comparison")
    print("=" * 60)

    audio_dir = Path("data/audio")
    truth_dir = Path("data/truth")

    if not audio_dir.exists() or not truth_dir.exists():
        print("\n  Create data/audio/ and data/truth/ directories with matching files.")
        return

    pairs = []
    for audio_file in sorted(audio_dir.iterdir()):
        if audio_file.name.startswith(".") or not audio_file.is_file():
            continue
        truth_file = truth_dir / f"{audio_file.stem}.txt"
        if truth_file.exists():
            pairs.append((audio_file, truth_file))

    if not pairs:
        print("\n  No audio/truth file pairs found in data/")
        print("  Add matching files: data/audio/sample.mp3 + data/truth/sample.txt")
        return

    word_list = load_semantic_word_list(WORD_LIST_PATH)
    transcriber = Transcriber()

    for audio_file, truth_file in pairs:
        truth = truth_file.read_text().strip()

        print(f"\n  Audio: {audio_file.name}")
        print(f"  Truth: {len(truth.split())} words")

        print(f"\n--- Transcribing with AssemblyAI ---")
        aai_text = transcriber.transcribe(str(audio_file), provider="assemblyai")

        print(f"\n--- Transcribing with OpenAI Whisper ---")
        oai_text = transcriber.transcribe(str(audio_file), provider="openai")

        aai_result = SemanticWERMetrics.calculate(truth, aai_text, semantic_word_list=word_list)
        oai_result = SemanticWERMetrics.calculate(truth, oai_text, semantic_word_list=word_list)

        print(f"\n{'=' * 60}")
        print(f"Results: {audio_file.stem}")
        print(f"{'=' * 60}")
        print(f"\n  {'Metric':<20} {'AssemblyAI':>12} {'Whisper':>12}")
        print(f"  {'-'*44}")
        print(f"  {'WER':<20} {aai_result['wer']:>11.2%} {oai_result['wer']:>11.2%}")
        print(f"  {'MER':<20} {aai_result['mer']:>11.2%} {oai_result['mer']:>11.2%}")
        print(f"  {'WIL':<20} {aai_result['wil']:>11.2%} {oai_result['wil']:>11.2%}")
        print(f"  {'Insertions':<20} {aai_result['insertions']:>12} {oai_result['insertions']:>12}")
        print(f"  {'Deletions':<20} {aai_result['deletions']:>12} {oai_result['deletions']:>12}")
        print(f"  {'Substitutions':<20} {aai_result['substitutions']:>12} {oai_result['substitutions']:>12}")
        print(f"  {'Hits':<20} {aai_result['hits']:>12} {oai_result['hits']:>12}")


if __name__ == "__main__":
    main()
