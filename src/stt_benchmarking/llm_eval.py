"""LLM-based qualitative evaluation using AssemblyAI's LLM Gateway."""

import os
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from .models import Transcript

# Load environment variables from .env file
load_dotenv()


class LLMEvaluator:
    """Evaluate transcription quality using LLMs via AssemblyAI's gateway."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        evaluator_models: Optional[List[str]] = None,
        consolidator_model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4000
    ):
        """Initialize LLM evaluator.

        Args:
            api_key: AssemblyAI API key (defaults to ASSEMBLYAI_API_KEY env var)
            evaluator_models: List of models to use for evaluation
            consolidator_model: Model to use for consolidating evaluations
            max_tokens: Maximum tokens for LLM responses
        """
        self.api_key = api_key or os.environ.get('ASSEMBLYAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "AssemblyAI API key required. Set ASSEMBLYAI_API_KEY environment "
                "variable or pass api_key parameter."
            )

        self.gateway_url = "https://llm-gateway.assemblyai.com/v1/chat/completions"
        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json"
        }

        self.evaluator_models = evaluator_models or [
            "claude-sonnet-4-5-20250929",
            "gpt-5",
            "gemini-2.5-pro"
        ]
        self.consolidator_model = consolidator_model
        self.max_tokens = max_tokens

    def format_transcript(
        self,
        transcript: Transcript,
        label: str,
        include_timestamps: bool = True
    ) -> str:
        """Format transcript for LLM evaluation.

        Args:
            transcript: Transcript to format
            label: Label for this transcript (e.g., "Ground Truth", "Vendor A")
            include_timestamps: Whether to include timestamps

        Returns:
            Formatted transcript string
        """
        lines = [f"=== {label} ===\n"]

        for utt in transcript:
            if include_timestamps and utt.start_time is not None:
                minutes = int(utt.start_time // 60)
                seconds = int(utt.start_time % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                lines.append(f"{timestamp} {utt.speaker}: {utt.text}")
            else:
                lines.append(f"{utt.speaker}: {utt.text}")

        return "\n".join(lines)

    def call_llm(self, model: str, prompt: str) -> str:
        """Call AssemblyAI LLM Gateway.

        Args:
            model: Model identifier
            prompt: Prompt to send

        Returns:
            LLM response text

        Raises:
            requests.HTTPError: If API call fails
        """
        response = requests.post(
            self.gateway_url,
            headers=self.headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.max_tokens
            }
        )

        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    def create_evaluation_prompt(
        self,
        reference: Transcript,
        hypothesis: Transcript,
        vendor_name: str = "Vendor",
        reference_label: str = "Ground Truth"
    ) -> str:
        """Create evaluation prompt for LLM.

        Args:
            reference: Reference transcript
            hypothesis: Hypothesis transcript
            vendor_name: Name of the vendor being evaluated
            reference_label: Label for reference transcript

        Returns:
            Evaluation prompt
        """
        ref_text = self.format_transcript(reference, reference_label)
        hyp_text = self.format_transcript(hypothesis, vendor_name)

        prompt = f"""You are an expert in evaluating speech-to-text transcription quality, particularly focusing on:
1. Word accuracy (correct transcription of spoken words)
2. Speaker diarization (correctly identifying who said what)
3. Temporal accuracy (when things were said, if timestamps available)
4. Overall coherence and readability

Below are two transcripts of the same audio:
1. {reference_label} (human-verified correct transcription)
2. {vendor_name} (automated transcription to evaluate)

{ref_text}

{hyp_text}

Please evaluate the {vendor_name} transcription quality and provide:
1. An overall quality score from 1-10 (10 being perfect)
2. Key strengths of the transcription
3. Key weaknesses or errors
4. Specific examples highlighting important differences
5. Assessment of speaker diarization quality
6. Your overall recommendation on whether this transcription quality is acceptable

Be specific and cite examples from the transcripts."""

        return prompt

    def evaluate_single(
        self,
        reference: Transcript,
        hypothesis: Transcript,
        vendor_name: str = "Vendor",
        file_identifier: str = "audio"
    ) -> Dict[str, Any]:
        """Evaluate a single transcript using multiple LLMs.

        Args:
            reference: Reference transcript
            hypothesis: Hypothesis transcript
            vendor_name: Name of vendor
            file_identifier: File identifier for logging

        Returns:
            Dictionary with evaluations from each model
        """
        print(f"\n  Running LLM evaluation for {file_identifier} ({vendor_name})...")

        prompt = self.create_evaluation_prompt(
            reference,
            hypothesis,
            vendor_name
        )

        evaluations = {}

        for model in self.evaluator_models:
            try:
                print(f"    Calling {model}...")
                evaluation = self.call_llm(model, prompt)
                evaluations[model] = evaluation
            except Exception as e:
                print(f"    Error with {model}: {e}")
                evaluations[model] = f"Error: {str(e)}"

        return evaluations

    def extract_score(self, evaluation_text: str) -> Optional[float]:
        """Extract numerical score from evaluation text.

        Args:
            evaluation_text: LLM evaluation response

        Returns:
            Score between 1-10, or None if not found
        """
        import re

        # Look for patterns like "score: 8", "8/10", "rating of 7", etc.
        patterns = [
            r'score[:\s]+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*/\s*10',
            r'rating[:\s]+(\d+(?:\.\d+)?)',
            r'quality[:\s]+(\d+(?:\.\d+)?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, evaluation_text.lower())
            if match:
                score = float(match.group(1))
                if 1 <= score <= 10:
                    return score

        return None

    def consolidate_evaluations(
        self,
        evaluations: Dict[str, str],
        vendor_name: str,
        file_identifier: str
    ) -> str:
        """Consolidate multiple evaluations into a summary.

        Args:
            evaluations: Dictionary of model -> evaluation text
            vendor_name: Name of vendor
            file_identifier: File identifier

        Returns:
            Consolidated evaluation summary
        """
        print(f"    Consolidating evaluations...")

        evals_text = "\n\n".join([
            f"=== EVALUATION FROM {model.upper()} ===\n{eval_text}"
            for model, eval_text in evaluations.items()
            if not eval_text.startswith("Error:")
        ])

        prompt = f"""You are tasked with synthesizing multiple expert evaluations of speech-to-text transcription quality.

Below are independent evaluations from different AI systems, all evaluating {vendor_name}'s transcription for file: {file_identifier}

{evals_text}

Please provide a consolidated summary that:
1. Identifies areas of agreement across evaluators
2. Notes any significant disagreements
3. Provides a final consensus quality score (1-10)
4. Gives actionable insights about transcription quality
5. Highlights the most important issues mentioned

Be concise but thorough. Focus on practical insights.
Format your response with a clear "CONSENSUS SCORE: X/10" at the beginning."""

        try:
            consolidation = self.call_llm(self.consolidator_model, prompt)
            return consolidation
        except Exception as e:
            return f"Error during consolidation: {str(e)}"

    def evaluate_and_score(
        self,
        reference: Transcript,
        hypothesis: Transcript,
        vendor_name: str = "Vendor",
        file_identifier: str = "audio"
    ) -> Dict[str, Any]:
        """Evaluate transcript and extract vibe score.

        Args:
            reference: Reference transcript
            hypothesis: Hypothesis transcript
            vendor_name: Name of vendor
            file_identifier: File identifier

        Returns:
            Dictionary with vibe_score and full evaluations
        """
        # Get evaluations
        evaluations = self.evaluate_single(
            reference,
            hypothesis,
            vendor_name,
            file_identifier
        )

        # Consolidate
        consolidation = self.consolidate_evaluations(
            evaluations,
            vendor_name,
            file_identifier
        )

        # Extract score from consolidation
        vibe_score = self.extract_score(consolidation)

        # If no score in consolidation, try individual evaluations
        if vibe_score is None:
            scores = []
            for eval_text in evaluations.values():
                if not eval_text.startswith("Error:"):
                    score = self.extract_score(eval_text)
                    if score is not None:
                        scores.append(score)

            if scores:
                vibe_score = sum(scores) / len(scores)

        return {
            "vibe_score": vibe_score,
            "consolidation": consolidation,
            "individual_evaluations": evaluations
        }


def evaluate_vendor_comparison(
    evaluator: LLMEvaluator,
    reference: Transcript,
    vendor_transcripts: Dict[str, Transcript],
    file_identifier: str = "audio"
) -> Dict[str, Any]:
    """Compare multiple vendors using LLM evaluation.

    Args:
        evaluator: LLMEvaluator instance
        reference: Reference transcript
        vendor_transcripts: Dictionary of vendor_name -> transcript
        file_identifier: File identifier

    Returns:
        Dictionary with comparative evaluation
    """
    print(f"\n  Running comparative LLM evaluation for {file_identifier}...")

    # Format all transcripts
    ref_text = evaluator.format_transcript(reference, "GROUND TRUTH")

    vendor_texts = []
    for vendor_name, transcript in vendor_transcripts.items():
        vendor_texts.append(
            evaluator.format_transcript(transcript, vendor_name)
        )

    all_transcripts = "\n\n".join([ref_text] + vendor_texts)

    # Create comparative prompt
    vendor_names = ", ".join(vendor_transcripts.keys())
    prompt = f"""You are an expert in evaluating speech-to-text transcription quality.

Below are transcripts of the same audio from multiple vendors: {vendor_names}
Also included is the ground truth (human-verified correct transcription).

{all_transcripts}

Please provide:
1. An overall ranking of vendors (1st place, 2nd place, etc.)
2. A quality score (1-10) for each vendor
3. Key strengths and weaknesses of each vendor
4. Specific examples highlighting the differences
5. Your recommendation for which vendor to use

Be specific and cite examples from the transcripts."""

    # Get evaluation
    try:
        print(f"    Calling {evaluator.consolidator_model} for comparison...")
        comparison = evaluator.call_llm(evaluator.consolidator_model, prompt)

        # Extract scores for each vendor
        vendor_scores = {}
        for vendor_name in vendor_transcripts.keys():
            # Look for patterns like "Vendor A: 8/10"
            import re
            patterns = [
                rf'{vendor_name}[:\s]+(\d+(?:\.\d+)?)\s*/\s*10',
                rf'{vendor_name}[:\s]+score[:\s]+(\d+(?:\.\d+)?)',
            ]
            for pattern in patterns:
                match = re.search(pattern, comparison, re.IGNORECASE)
                if match:
                    vendor_scores[vendor_name] = float(match.group(1))
                    break

        return {
            "comparison": comparison,
            "vendor_scores": vendor_scores,
            "file": file_identifier
        }

    except Exception as e:
        return {
            "comparison": f"Error: {str(e)}",
            "vendor_scores": {},
            "file": file_identifier
        }
