"""Missed Entity Rate calculation via AssemblyAI LLM Gateway."""

import json
import re
from typing import Dict, List, Optional
from .llm_eval import LLMEvaluator


DEFAULT_ENTITY_TYPES = [
    "person_name",
    "drug_name",
    "medical_condition",
    "procedure",
    "organization",
    "location",
    "number",
    "date",
    "abbreviation",
]

EXTRACTION_MODEL = "claude-sonnet-4-5-20250929"


class MissedEntityRate:
    """Calculate missed entity rate between reference and hypothesis text.

    Uses AssemblyAI LLM Gateway to extract entities, then compares
    which reference entities are missing from the hypothesis.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with AssemblyAI API key.

        Args:
            api_key: AssemblyAI API key. Defaults to ASSEMBLYAI_API_KEY env var.
        """
        self.evaluator = LLMEvaluator(api_key=api_key)

    def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Extract named entities from text using LLM Gateway.

        Args:
            text: Input text.
            entity_types: Categories to extract. Defaults to medical + general types.

        Returns:
            List of {"entity": str, "type": str} dicts.
        """
        if not text.strip():
            return []

        types_str = ", ".join(entity_types or DEFAULT_ENTITY_TYPES)
        prompt = f"""Extract all named entities from the following text.
Return ONLY a JSON array of objects with "entity" and "type" keys.
Do not include any other text or explanation.

Entity types to extract: {types_str}

Text: {text}

Return format example: [{{"entity": "metformin", "type": "drug_name"}}, {{"entity": "Dr. Smith", "type": "person_name"}}]"""

        response = self.evaluator.call_llm(EXTRACTION_MODEL, prompt)

        match = re.search(r"\[.*\]", response, re.DOTALL)
        if not match:
            raise ValueError(
                f"Could not parse entity JSON from LLM response: {response[:200]}"
            )

        return json.loads(match.group(0))

    def calculate(
        self,
        reference_text: str,
        hypothesis_text: str,
        entity_types: Optional[List[str]] = None,
    ) -> Dict:
        """Calculate the rate of reference entities missing from the hypothesis.

        Args:
            reference_text: Ground truth text.
            hypothesis_text: Predicted text.
            entity_types: Entity categories to extract.

        Returns:
            Dict with missed_entity_rate, total_entities,
            missed_entities, found_entities,
            reference_entities, hypothesis_entities.
        """
        print("  Extracting entities from reference...")
        ref_entities = self.extract_entities(reference_text, entity_types)

        print("  Extracting entities from hypothesis...")
        hyp_entities = self.extract_entities(hypothesis_text, entity_types)

        if not ref_entities:
            return {
                "missed_entity_rate": 0.0,
                "total_entities": 0,
                "missed_entities": [],
                "found_entities": [],
                "reference_entities": [],
                "hypothesis_entities": hyp_entities,
            }

        hyp_set = {e["entity"].lower().strip() for e in hyp_entities}

        missed, found, seen = [], [], set()
        for entity in ref_entities:
            key = entity["entity"].lower().strip()
            if key in seen:
                continue
            seen.add(key)
            (found if key in hyp_set else missed).append(entity)

        total = len(found) + len(missed)
        rate = len(missed) / total if total > 0 else 0.0

        return {
            "missed_entity_rate": rate,
            "total_entities": total,
            "missed_entities": missed,
            "found_entities": found,
            "reference_entities": ref_entities,
            "hypothesis_entities": hyp_entities,
        }
