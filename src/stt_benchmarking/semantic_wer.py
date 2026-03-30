"""Semantic Word Error Rate calculation."""

from typing import Dict, List, Optional
from jiwer import process_words
from .normalizer import TextNormalizer
from .semantic_normalizer import load_semantic_word_list


class SemanticWERMetrics:
    """Calculate WER with semantic word list normalization.

    Unlike WERMetrics which works on Transcript objects,
    SemanticWERMetrics works on plain text strings and applies
    semantic equivalence rules before comparison.
    """

    @staticmethod
    def calculate(
        reference_text: str,
        hypothesis_text: str,
        semantic_word_list_path: Optional[str] = None,
        semantic_word_list: Optional[List[List[str]]] = None,
    ) -> Dict:
        """Calculate WER with semantic normalization.

        Args:
            reference_text: Ground truth text.
            hypothesis_text: Predicted text.
            semantic_word_list_path: Path to semantic word list JSON.
            semantic_word_list: Direct word list (overrides path).

        Returns:
            Dict with wer, mer, wil, wip, insertions, deletions,
            substitutions, hits, reference_normalized, hypothesis_normalized.
        """
        word_list = semantic_word_list
        if word_list is None and semantic_word_list_path:
            word_list = load_semantic_word_list(semantic_word_list_path)

        normalizer = TextNormalizer(semantic_word_list=word_list)

        ref_normalized = normalizer.normalize_text(reference_text)
        hyp_normalized = normalizer.normalize_text(hypothesis_text)

        if not ref_normalized or not hyp_normalized:
            return {
                "wer": 1.0,
                "mer": 1.0,
                "wil": 1.0,
                "wip": 0.0,
                "insertions": 0,
                "deletions": 0,
                "substitutions": 0,
                "hits": 0,
                "reference_normalized": ref_normalized,
                "hypothesis_normalized": hyp_normalized,
            }

        output = process_words(ref_normalized, hyp_normalized)

        return {
            "wer": output.wer,
            "mer": output.mer,
            "wil": output.wil,
            "wip": output.wip,
            "insertions": output.insertions,
            "deletions": output.deletions,
            "substitutions": output.substitutions,
            "hits": output.hits,
            "reference_normalized": ref_normalized,
            "hypothesis_normalized": hyp_normalized,
        }
