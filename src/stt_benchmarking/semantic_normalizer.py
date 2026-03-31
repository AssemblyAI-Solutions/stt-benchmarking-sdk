"""Semantic word list normalization for STT benchmarking."""

import json
from pathlib import Path
from typing import List


def load_semantic_word_list(path: str) -> List[List[str]]:
    """Load semantic word equivalence list from JSON file.

    Args:
        path: Path to JSON file containing word groups.

    Returns:
        List of word groups, where index 0 is canonical form.
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Semantic word list not found: {path}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_semantic_replacements(text: str, semantic_word_list: List[List[str]]) -> str:
    """Replace semantic variants with canonical forms.

    For each word group, all variants (index 1+) are replaced
    with the canonical form (index 0).

    Args:
        text: Text to apply replacements to.
        semantic_word_list: List of word groups.

    Returns:
        Text with semantic replacements applied.
    """
    for word_group in semantic_word_list:
        if len(word_group) < 2:
            continue
        canonical = word_group[0].lower()
        for variant in word_group[1:]:
            text = text.replace(variant.lower(), canonical)
    return text
