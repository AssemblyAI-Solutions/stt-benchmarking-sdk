#!/usr/bin/env python3
"""Full Benchmarking Recipe

Combines all tools into one workflow:
1. Transcribe audio (AssemblyAI)
2. Calculate Semantic WER
3. Calculate Missed Entity Rate
4. Run LLM Qualitative Evaluation
5. Export results to CSV

Usage:
  python examples/full_benchmark_example.py

Requires audio files in data/audio/ with matching truth files in data/truth/.
"""

import csv
from pathlib import Path
from stt_benchmarking import (
    Transcript,
    Transcriber,
    SemanticWERMetrics,
    MissedEntityRate,
    LLMEvaluator,
    LLMResultsExporter,
    load_semantic_word_list,
)

WORD_LIST_PATH = "data/semantic_word_list.json"
RESULTS_DIR = Path("results")


def run_full_benchmark(
    audio_path: str,
    truth_path: str,
    transcriber: Transcriber,
    mer: MissedEntityRate,
    llm_eval: LLMEvaluator,
    word_list,
) -> dict:
    file_name = Path(audio_path).stem
    truth = Path(truth_path).read_text().strip()

    print(f"\n{'=' * 60}")
    print(f"Full Benchmark: {file_name}")
    print(f"{'=' * 60}")

    # 1. Transcribe
    print(f"\n[1/4] Transcribing with AssemblyAI...")
    prediction = transcriber.transcribe(audio_path, provider="assemblyai")

    # 2. Semantic WER
    print(f"\n[2/4] Calculating Semantic WER...")
    wer_result = SemanticWERMetrics.calculate(truth, prediction, semantic_word_list=word_list)
    print(f"  WER: {wer_result['wer']:.2%}")

    # 3. Missed Entity Rate
    print(f"\n[3/4] Calculating Missed Entity Rate...")
    entity_result = mer.calculate(truth, prediction)
    print(f"  Missed Entity Rate: {entity_result['missed_entity_rate']:.2%}")

    if entity_result["missed_entities"]:
        for e in entity_result["missed_entities"]:
            print(f"    Missing: {e['entity']} ({e['type']})")

    # 4. LLM Evaluation
    print(f"\n[4/4] Running LLM Evaluation...")
    llm_result = llm_eval.evaluate_and_score(
        reference=Transcript.from_list([{"speaker": "truth", "text": truth}]),
        hypothesis=Transcript.from_list([{"speaker": "prediction", "text": prediction}]),
        vendor_name="AssemblyAI",
        file_identifier=file_name,
    )
    vibe_score = llm_result.get("vibe_score")
    if vibe_score:
        print(f"  Vibe Score: {vibe_score:.1f}/10")

    return {
        "file_name": file_name,
        "wer": wer_result["wer"],
        "mer": wer_result["mer"],
        "insertions": wer_result["insertions"],
        "deletions": wer_result["deletions"],
        "substitutions": wer_result["substitutions"],
        "hits": wer_result["hits"],
        "missed_entity_rate": entity_result["missed_entity_rate"],
        "total_entities": entity_result["total_entities"],
        "missed_entities_count": len(entity_result["missed_entities"]),
        "missed_entities_list": ", ".join(
            f"{e['entity']} ({e['type']})" for e in entity_result["missed_entities"]
        ),
        "found_entities_list": ", ".join(
            f"{e['entity']} ({e['type']})" for e in entity_result["found_entities"]
        ),
        "vibe_score": vibe_score,
        "llm_consolidation": llm_result.get("consolidation", ""),
        "truth_text": truth,
        "prediction_text": prediction,
        "truth_normalized": wer_result["reference_normalized"],
        "prediction_normalized": wer_result["hypothesis_normalized"],
        "_llm_result": llm_result,  # full LLM result for markdown export
    }


def main():
    print("=" * 60)
    print("Full Benchmarking Recipe")
    print("=" * 60)

    audio_dir = Path("data/audio")
    truth_dir = Path("data/truth")

    pairs = []
    if audio_dir.exists() and truth_dir.exists():
        for audio_file in sorted(audio_dir.iterdir()):
            if audio_file.name.startswith(".") or not audio_file.is_file():
                continue
            truth_file = truth_dir / f"{audio_file.stem}.txt"
            if truth_file.exists():
                pairs.append((str(audio_file), str(truth_file)))

    if not pairs:
        print("\n  No audio/truth file pairs found in data/")
        print("  Add matching files: data/audio/sample.mp3 + data/truth/sample.txt")
        return

    word_list = load_semantic_word_list(WORD_LIST_PATH)
    transcriber = Transcriber()
    mer = MissedEntityRate()
    llm_eval = LLMEvaluator()

    print(f"\n  Found {len(pairs)} file pair(s)")

    results = []
    for audio_path, truth_path in pairs:
        result = run_full_benchmark(
            audio_path, truth_path, transcriber, mer, llm_eval, word_list
        )
        results.append(result)

    # Summary
    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    for r in results:
        print(f"\n  {r['file_name']}:")
        print(f"    WER: {r['wer']:.2%} | Missed Entities: {r['missed_entity_rate']:.2%} | Vibe: {r['vibe_score']}")

    # Export
    RESULTS_DIR.mkdir(exist_ok=True)

    # CSV (exclude internal _llm_result field)
    csv_path = RESULTS_DIR / "full_benchmark.csv"
    csv_fields = [k for k in results[0].keys() if not k.startswith("_")]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"\n  CSV exported to {csv_path}")

    # Markdown files for LLM evaluations
    for r in results:
        md_path = RESULTS_DIR / f"{r['file_name']}_llm_eval.md"
        LLMResultsExporter.to_markdown_file(
            r["_llm_result"],
            md_path,
            vendor_name="AssemblyAI",
            file_identifier=r["file_name"],
        )
        print(f"  LLM eval saved to {md_path}")


if __name__ == "__main__":
    main()
