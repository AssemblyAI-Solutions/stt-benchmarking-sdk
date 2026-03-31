"""STT Benchmarking SDK for evaluating speech-to-text systems."""

from .models import Utterance, Transcript
from .benchmark import STTBenchmark
from .speaker_matcher import SpeakerMatcher
from .metrics import WERMetrics, CPWERMetrics, DERMetrics
from .export import ResultsExporter, BatchEvaluator
from .utils import TranscriptLoader, TranscriptWriter, validate_transcript
from .llm_eval import LLMEvaluator, evaluate_vendor_comparison
from .llm_export import LLMResultsExporter, export_llm_results_with_csv
from .semantic_normalizer import load_semantic_word_list, apply_semantic_replacements
from .semantic_wer import SemanticWERMetrics
from .missed_entity_rate import MissedEntityRate
from .transcriber import Transcriber

__version__ = "0.1.0"

__all__ = [
    "Utterance",
    "Transcript",
    "STTBenchmark",
    "SpeakerMatcher",
    "WERMetrics",
    "CPWERMetrics",
    "DERMetrics",
    "ResultsExporter",
    "BatchEvaluator",
    "TranscriptLoader",
    "TranscriptWriter",
    "validate_transcript",
    "LLMEvaluator",
    "evaluate_vendor_comparison",
    "LLMResultsExporter",
    "export_llm_results_with_csv",
    "SemanticWERMetrics",
    "MissedEntityRate",
    "Transcriber",
    "load_semantic_word_list",
    "apply_semantic_replacements",
]
