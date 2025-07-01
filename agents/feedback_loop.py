"""
Feedback loop implementation for continuous improvement
"""

from typing import Dict, Any, List, TYPE_CHECKING
from datetime import datetime
import numpy as np


from .anomaly_correction_agent import AnomalyDetectorAgent, CorrectionDecision


class FeedbackLoop:
    """
    Manages the feedback loop between agent corrections and human validation
    """

    def __init__(self, agent: AnomalyDetectorAgent):
        self.agent = agent
        self.pending_validations = {}
        self.metrics = {
            "total_corrections": 0,
            "accepted_corrections": 0,
            "rejected_corrections": 0,
            "accuracy": 1.0,
        }

    async def process_document(
        self, extracted_json: Dict[str, Any], document_id: str
    ) -> Dict[str, Any]:
        """Process document through correction pipeline"""
        # Run auto-correction
        corrected_json, corrections = await self.agent.detect_and_correct(extracted_json)

        # Store for validation
        self.pending_validations[document_id] = {
            "original": extracted_json,
            "corrected": corrected_json,
            "corrections": corrections,
            "timestamp": datetime.utcnow(),
        }

        # Update metrics
        self.metrics["total_corrections"] += len(corrections)

        return {
            "document_id": document_id,
            "corrected_data": corrected_json,
            "corrections_made": len(corrections),
            "confidence": np.mean([c.confidence for c in corrections]) if corrections else 1.0,
        }

    async def receive_validation(self, document_id: str, validated_json: Dict[str, Any]):
        """Receive validation from DataOps team"""
        if document_id not in self.pending_validations:
            return

        pending = self.pending_validations[document_id]
        corrections = pending["corrections"]
        corrected = pending["corrected"]
        original = pending["original"]

        # Track which fields were corrected
        corrected_fields = {c.field for c in corrections}
        # Compare corrections with validated data
        for correction in corrections:
            field = correction.field
            if field in validated_json:
                if validated_json[field] == correction.corrected_value:
                    self.metrics["accepted_corrections"] += 1
                else:
                    self.metrics["rejected_corrections"] += 1

        # NEW: Penalize missed corrections (fields that differ in validated vs corrected, but not in corrections)
        for field in validated_json:
            if field not in corrected_fields and field in original:
                if validated_json[field] != corrected.get(field, original[field]):
                    self.metrics["rejected_corrections"] += 1
                    # Teach agent from missed correction
                    self.agent._learn_new_pattern(field, original[field], validated_json[field], original)

        # Update agent with ground truth
        self.agent._update_patterns(original, validated_json, corrections)

        # Update accuracy metric
        total = self.metrics["accepted_corrections"] + self.metrics["rejected_corrections"]
        if total > 0:
            self.metrics["accuracy"] = self.metrics["accepted_corrections"] / total

        # Clean up
        del self.pending_validations[document_id]
