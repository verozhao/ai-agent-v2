"""
Feedback loop implementation for continuous improvement
"""

from typing import Dict, Any
from datetime import datetime
import numpy as np


from .anomaly_correction_agent import AnomalyDetectorAgent


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
        
        # Track correction accuracy by type
        correct_corrections = 0
        incorrect_corrections = 0
        
        # Compare corrections with validated data
        for correction in corrections:
            field = correction.field
            if field in validated_json:
                if validated_json[field] == correction.corrected_value:
                    self.metrics["accepted_corrections"] += 1
                    correct_corrections += 1
                else:
                    self.metrics["rejected_corrections"] += 1
                    incorrect_corrections += 1
                    # Learn from wrong correction
                    self.agent._learn_new_pattern(field, correction.corrected_value, validated_json[field], original)

        # Penalize missed corrections (fields that differ in validated vs corrected, but not in corrections)
        missed_corrections = 0
        for field in validated_json:
            if field not in corrected_fields and field in original:
                if validated_json[field] != corrected.get(field, original[field]):
                    self.metrics["rejected_corrections"] += 1
                    missed_corrections += 1
                    # Teach agent from missed correction with domain knowledge
                    if field == 'equity' and all(k in original for k in ['assets', 'liabilities']):
                        # Teach accounting equation
                        self.agent._learn_new_pattern(field, original[field], validated_json[field], original)
                    elif 'total' in field.lower():
                        # Teach cumulative pattern
                        self.agent._learn_new_pattern(field, original[field], validated_json[field], original)
                    else:
                        self.agent._learn_new_pattern(field, original[field], validated_json[field], original)
        
        # Enhanced metrics tracking
        self.metrics.setdefault("correction_breakdown", {
            "correct_corrections": 0,
            "incorrect_corrections": 0, 
            "missed_corrections": 0
        })
        self.metrics["correction_breakdown"]["correct_corrections"] += correct_corrections
        self.metrics["correction_breakdown"]["incorrect_corrections"] += incorrect_corrections
        self.metrics["correction_breakdown"]["missed_corrections"] += missed_corrections

        # Update agent with ground truth
        self.agent._update_patterns(original, validated_json, corrections)

        # Update accuracy metric
        total = self.metrics["accepted_corrections"] + self.metrics["rejected_corrections"]
        if total > 0:
            self.metrics["accuracy"] = self.metrics["accepted_corrections"] / total

        del self.pending_validations[document_id]