#!/usr/bin/env python3
"""Missed Entity Rate Example (Medical)

Demonstrates how to measure whether critical entities (drug names,
conditions, procedures) are preserved in transcription.

Usage:
  python examples/missed_entity_rate_example.py

If audio/truth files exist in data/audio/ and data/truth/,
transcribes and evaluates those. Otherwise uses hardcoded medical samples.
"""

from pathlib import Path
from stt_benchmarking import MissedEntityRate

SAMPLE_TRUTH = """The patient, Mrs. Johnson, presented with uncontrolled type 2 diabetes
and hypertension. Current medications include metformin 1000mg twice daily,
lisinopril 20mg daily, and atorvastatin 40mg at bedtime. Lab results showed
HbA1c of 8.2% and LDL cholesterol of 142. We discussed adding empagliflozin
10mg daily and referred to Dr. Patel in endocrinology for further evaluation.
Blood pressure was 158/92 mmHg. BMI is 31.4."""

SAMPLE_PREDICTION = """The patient, Mrs. Johnson, presented with uncontrolled type 2 diabetes
and hypertension. Current medications include metformin 1000mg twice daily,
lisinopril 20mg daily, and a statin 40mg at bedtime. Lab results showed
HbA1c of 8.2% and LDL cholesterol of 142. We discussed adding a new medication
10mg daily and referred to Dr. Patel in endocrinology for further evaluation.
Blood pressure was 158/92. BMI is 31.4."""


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


def print_results(result: dict, label: str):
    print(f"\n--- {label} ---")
    print(f"  Missed Entity Rate: {result['missed_entity_rate']:.2%}")
    print(f"  Total entities: {result['total_entities']}")

    if result["missed_entities"]:
        print(f"\n  MISSED ({len(result['missed_entities'])}):")
        for e in result["missed_entities"]:
            print(f"    - {e['entity']} ({e['type']})")

    if result["found_entities"]:
        print(f"\n  Found ({len(result['found_entities'])}):")
        for e in result["found_entities"]:
            print(f"    - {e['entity']} ({e['type']})")


def main():
    print("=" * 60)
    print("Missed Entity Rate (Medical)")
    print("=" * 60)

    mer = MissedEntityRate()
    pairs = find_data_pairs()

    if pairs:
        from stt_benchmarking import Transcriber
        transcriber = Transcriber()

        for audio_file, truth_file in pairs:
            truth = truth_file.read_text().strip()
            print(f"\n  Transcribing {audio_file.name}...")
            prediction = transcriber.transcribe(str(audio_file), provider="assemblyai")
            result = mer.calculate(truth, prediction)
            print_results(result, audio_file.stem)
    else:
        print("\n  No audio/truth files in data/ — using hardcoded medical sample")
        result = mer.calculate(SAMPLE_TRUTH, SAMPLE_PREDICTION)
        print_results(result, "Medical sample")


if __name__ == "__main__":
    main()
