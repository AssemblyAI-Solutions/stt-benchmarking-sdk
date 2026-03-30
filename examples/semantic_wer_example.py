#!/usr/bin/env python3
"""Semantic Word Error Rate Example

Demonstrates how semantic normalization prevents false WER penalties
when the model uses equivalent but different word forms.

Usage:
  python examples/semantic_wer_example.py

If audio/truth files exist in data/audio/ and data/truth/,
transcribes and evaluates those. Otherwise uses hardcoded samples.
"""

from pathlib import Path
from stt_benchmarking import SemanticWERMetrics, load_semantic_word_list

SAMPLE_TRUTH = """The patient said everything is all right. We discussed the health care plan
and agreed to set up a follow-up appointment for next week."""

SAMPLE_PREDICTION = """The patient said everything is alright. We discussed the healthcare plan
and agreed to setup a follow-up appointment for next week."""

WORD_LIST_PATH = "data/semantic_word_list.json"


def find_data_pairs():
    audio_dir = Path("data/audio")
    truth_dir = Path("data/truth")
    if not audio_dir.exists() or not truth_dir.exists():
        return []
    pairs = []
    for audio_file in sorted(audio_dir.iterdir()):
        if audio_file.name.startswith(".") or not audio_file.is_file():
            continue
        truth_file = truth_dir / f"{audio_file.stem}.txt"
        if truth_file.exists():
            pairs.append((audio_file, truth_file))
    return pairs


def run_comparison(truth: str, prediction: str, label: str):
    word_list = load_semantic_word_list(WORD_LIST_PATH)

    print(f"\n--- {label} ---")
    print(f"  Truth:      {truth[:120]}{'...' if len(truth) > 120 else ''}")
    print(f"  Prediction: {prediction[:120]}{'...' if len(prediction) > 120 else ''}")

    # Without semantic normalization
    result_raw = SemanticWERMetrics.calculate(truth, prediction)
    print(f"\n  Without semantic normalization:")
    print(f"    WER: {result_raw['wer']:.4f} ({result_raw['wer']*100:.2f}%)")
    print(f"    Insertions: {result_raw['insertions']}, Deletions: {result_raw['deletions']}, Substitutions: {result_raw['substitutions']}")

    # With semantic normalization
    result = SemanticWERMetrics.calculate(truth, prediction, semantic_word_list=word_list)
    print(f"\n  With semantic normalization:")
    print(f"    WER: {result['wer']:.4f} ({result['wer']*100:.2f}%)")
    print(f"    Insertions: {result['insertions']}, Deletions: {result['deletions']}, Substitutions: {result['substitutions']}")
    print(f"    Hits: {result['hits']}")


def main():
    print("=" * 60)
    print("Semantic Word Error Rate")
    print("=" * 60)

    word_list = load_semantic_word_list(WORD_LIST_PATH)
    print(f"\n  Semantic word groups ({len(word_list)}):")
    for group in word_list:
        print(f"    {group[0]} = {', '.join(group[1:])}")

    pairs = find_data_pairs()

    if pairs:
        from stt_benchmarking import Transcriber
        transcriber = Transcriber()

        for audio_file, truth_file in pairs:
            truth = truth_file.read_text().strip()
            print(f"\n  Transcribing {audio_file.name}...")
            prediction = transcriber.transcribe(str(audio_file), provider="assemblyai")
            run_comparison(truth, prediction, audio_file.stem)
    else:
        print("\n  No audio/truth files in data/ — using hardcoded sample")
        run_comparison(SAMPLE_TRUTH, SAMPLE_PREDICTION, "Sample")


if __name__ == "__main__":
    main()
