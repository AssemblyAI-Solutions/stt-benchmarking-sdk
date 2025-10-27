"""Demonstration of automatic text normalization in the SDK."""

from stt_benchmarking import STTBenchmark


def example_normalization_happens_automatically():
    """Shows that text normalization happens automatically inside the SDK."""
    print("=" * 70)
    print("Text Normalization - Happens Automatically!")
    print("=" * 70)

    # Reference with various formatting
    reference = [
        {"speaker": "Doctor", "text": "What's your name? How old are you?"},
        {"speaker": "Patient", "text": "My name is John. I'm 45 years old."},
        {"speaker": "Doctor", "text": "You have 2 prescriptions to pick up."},
    ]

    # Hypothesis with different formatting
    # (lowercase, no punctuation, numbers as words)
    hypothesis = [
        {"speaker": "spk_0", "text": "whats your name how old are you"},
        {"speaker": "spk_1", "text": "my name is john im forty five years old"},
        {"speaker": "spk_0", "text": "you have two prescriptions to pick up"},
    ]

    print("\n📋 REFERENCE (as provided - with punctuation, capitalization):")
    for utt in reference:
        print(f"  {utt['speaker']}: \"{utt['text']}\"")

    print("\n📋 HYPOTHESIS (as provided - no punctuation, lowercase):")
    for utt in hypothesis:
        print(f"  {utt['speaker']}: \"{utt['text']}\"")

    # Evaluate with automatic normalization (default)
    print("\n⚙️  Evaluating with automatic normalization (default)...")
    benchmark_normalized = STTBenchmark(normalize=True)
    results_normalized = benchmark_normalized.evaluate(
        reference,
        hypothesis,
        calculate_der=False
    )

    print(f"\n✅ Results with normalization:")
    print(f"   WER: {results_normalized['wer']:.2%}")
    print(f"   Substitutions: {results_normalized['substitutions']}")
    print(f"   Deletions: {results_normalized['deletions']}")
    print(f"   Insertions: {results_normalized['insertions']}")
    print(f"   → Normalization handles punctuation, case, and number variations!")

    # Compare with no normalization
    print("\n⚙️  Evaluating WITHOUT normalization...")
    benchmark_no_norm = STTBenchmark(normalize=False)
    results_no_norm = benchmark_no_norm.evaluate(
        reference,
        hypothesis,
        calculate_der=False
    )

    print(f"\n❌ Results without normalization:")
    print(f"   WER: {results_no_norm['wer']:.2%}")
    print(f"   Substitutions: {results_no_norm['substitutions']}")
    print(f"   Deletions: {results_no_norm['deletions']}")
    print(f"   Insertions: {results_no_norm['insertions']}")
    print(f"   → Without normalization, formatting differences count as errors!")


def example_what_normalization_does():
    """Show what the normalizer does to text."""
    print("\n" + "=" * 70)
    print("What Does Normalization Do?")
    print("=" * 70)

    from stt_benchmarking.normalizer import TextNormalizer

    normalizer = TextNormalizer()

    examples = [
        "What's your name? How old are you?",
        "I'm 45 years old.",
        "You have 2 prescriptions.",
        "The cost is $123.45.",
        "Call me at 555-1234.",
        "HELLO WORLD!",
        "Dr. Smith will see you now.",
    ]

    print("\nOriginal → Normalized:")
    print("-" * 70)
    for text in examples:
        normalized = normalizer.normalize_text(text)
        print(f"  \"{text}\"")
        print(f"  → \"{normalized}\"")
        print()


def example_raw_transcripts():
    """Show that you can provide completely raw transcripts."""
    print("=" * 70)
    print("You Can Provide Raw Transcripts!")
    print("=" * 70)

    # Completely raw reference transcript
    reference = [
        {"speaker": "SPEAKER_1", "text": "Hello, World! How are you doing today?"},
        {"speaker": "SPEAKER_2", "text": "I'm doing GREAT, thank you! What about you?"},
        {"speaker": "SPEAKER_1", "text": "Pretty good, thanks for asking!!!"},
    ]

    # Raw hypothesis transcript with totally different formatting
    hypothesis = [
        {"speaker": "spk_a", "text": "hello world how are you doing today"},
        {"speaker": "spk_b", "text": "im doing great thank you what about you"},
        {"speaker": "spk_a", "text": "pretty good thanks for asking"},
    ]

    print("\n✨ NO PRE-PROCESSING REQUIRED!")
    print("   Just pass your raw transcripts to the SDK:")
    print()
    print("   reference = load_from_vendor_a()  # Raw format")
    print("   hypothesis = load_from_vendor_b()  # Different raw format")
    print("   results = benchmark.evaluate(reference, hypothesis)")
    print()

    # Evaluate
    benchmark = STTBenchmark()
    results = benchmark.evaluate(reference, hypothesis, calculate_der=False)

    print(f"📊 Results:")
    print(f"   WER: {results['wer']:.2%}")
    print(f"   CP-WER: {results['cp_wer']:.2%}")
    print()
    print("   ✓ Text normalization: automatic")
    print("   ✓ Speaker matching: automatic")
    print("   ✓ Metrics calculation: done!")


if __name__ == "__main__":
    example_normalization_happens_automatically()
    example_what_normalization_does()
    example_raw_transcripts()

    print("\n" + "=" * 70)
    print("KEY TAKEAWAY:")
    print("=" * 70)
    print("""
You do NOT need to normalize your text before passing it to the SDK!

The SDK automatically:
1. Normalizes both reference and hypothesis transcripts
2. Matches speaker labels between transcripts
3. Calculates all metrics fairly

Just provide your raw transcript data in the format:
    [{"speaker": "...", "text": "..."}, ...]

And the SDK handles the rest!
""")
