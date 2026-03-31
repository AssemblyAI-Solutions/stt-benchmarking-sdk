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

    def semantic_verify(
        self,
        missed_entities: List[Dict],
        hypothesis_text: str,
    ) -> Dict[str, Dict]:
        """Ask an LLM whether 'missed' entities are actually present semantically.

        Args:
            missed_entities: Entities that failed exact match.
            hypothesis_text: The predicted transcription text.

        Returns:
            Dict keyed by entity string with {"present": bool, "reason": str,
            "match": str | None} for each entity.
        """
        if not missed_entities:
            return {}

        entity_list = "\n".join(
            f'- "{e["entity"]}" ({e["type"]})' for e in missed_entities
        )

        prompt = f"""You are a medical transcription QA reviewer. Below is a predicted transcription and a list of entities that were NOT found by exact string match.

For each entity, determine whether it is **semantically present** in the predicted text — meaning the same concept appears but is spelled differently, abbreviated, or paraphrased. For example:
- "T6-seven" vs "T6-7" → semantically present (same vertebral level)
- "annular tear" vs "anular tear" → semantically present (spelling variant)
- "paracentral" vs "central" → NOT the same (paracentral is more specific)
- "diaphragm" not mentioned at all → NOT present

Predicted transcription:
{hypothesis_text}

Entities to verify:
{entity_list}

Return ONLY a JSON array. Each element must have:
- "entity": the original entity string
- "present": true or false
- "reason": brief explanation
- "match": the text in the prediction that matches (or null if not present)

Example: [{{"entity": "T6-seven", "present": true, "reason": "Written as T6-7", "match": "T6-7"}}]"""

        response = self.evaluator.call_llm(EXTRACTION_MODEL, prompt)
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if not match:
            return {}

        results = {}
        for item in json.loads(match.group(0)):
            results[item["entity"].lower().strip()] = item
        return results

    def calculate(
        self,
        reference_text: str,
        hypothesis_text: str,
        entity_types: Optional[List[str]] = None,
        semantic_check: bool = False,
    ) -> Dict:
        """Calculate the rate of reference entities missing from the hypothesis.

        Args:
            reference_text: Ground truth text.
            hypothesis_text: Predicted text.
            entity_types: Entity categories to extract.
            semantic_check: If True, use an LLM to verify whether
                entities that failed exact match are semantically present.

        Returns:
            Dict with missed_entity_rate, total_entities,
            missed_entities, found_entities,
            reference_entities, hypothesis_entities.
            When semantic_check is True, also includes
            semantic_missed_entity_rate, semantic_missed_entities,
            semantic_found_entities, and semantic_verdicts.
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
        hyp_text_lower = hypothesis_text.lower()

        missed, found, seen = [], [], set()
        for entity in ref_entities:
            key = entity["entity"].lower().strip()
            if key in seen:
                continue
            seen.add(key)
            # Check extracted entities first, then fall back to substring match
            # against the raw hypothesis text
            if key in hyp_set or key in hyp_text_lower:
                found.append(entity)
            else:
                missed.append(entity)

        total = len(found) + len(missed)
        rate = len(missed) / total if total > 0 else 0.0

        result = {
            "missed_entity_rate": rate,
            "total_entities": total,
            "missed_entities": missed,
            "found_entities": found,
            "reference_entities": ref_entities,
            "hypothesis_entities": hyp_entities,
        }

        if semantic_check and missed:
            print("  Verifying missed entities with semantic check...")
            verdicts = self.semantic_verify(missed, hypothesis_text)

            semantic_found = []
            semantic_missed = []
            for entity in missed:
                key = entity["entity"].lower().strip()
                verdict = verdicts.get(key, {})
                if verdict.get("present", False):
                    entity_with_verdict = {**entity, "semantic_match": verdict.get("match"), "reason": verdict.get("reason")}
                    semantic_found.append(entity_with_verdict)
                else:
                    semantic_missed.append(entity)

            semantic_total_missed = len(semantic_missed)
            semantic_rate = semantic_total_missed / total if total > 0 else 0.0

            result["semantic_missed_entity_rate"] = semantic_rate
            result["semantic_found_entities"] = semantic_found
            result["semantic_missed_entities"] = semantic_missed
            result["semantic_verdicts"] = verdicts

        return result
