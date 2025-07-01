"""
Comprehensive test suite for the feedback loop system
"""

import pytest
import json
from datetime import datetime
from agents.anomaly_correction_agent import AnomalyDetectorAgent, CorrectionDecision
from agents.feedback_loop import FeedbackLoop


class TestFeedbackLoop:
    """Test the complete feedback loop from detection to learning"""
    
    @pytest.fixture
    def agent(self):
        return AnomalyDetectorAgent()
    
    @pytest.fixture
    def feedback_loop(self, agent):
        return FeedbackLoop(agent)
    
    @pytest.mark.asyncio
    async def test_complete_feedback_cycle(self, feedback_loop):
        """Test full cycle: corrupt -> correct -> validate -> learn"""
        # Step 1: Process corrupted document
        corrupted = {
            "fund_name": "2019-03-15",
            "investment_date": "Blackstone Capital Partners VII",
            "exit_date": "2024-01-20",
            "irr": "45.2%",
            "multiple": "2.8x",
            "investment_amount": 50000000
        }
        
        result = await feedback_loop.process_document(corrupted, "test_001")
        
        # Verify corrections were made
        assert result["corrections_made"] > 0
        assert result["corrected_data"]["fund_name"] == "Blackstone Capital Partners VII"
        assert result["corrected_data"]["investment_date"] == "2019-03-15"
        
        # Step 2: Simulate DataOps validation
        ground_truth = {
            "fund_name": "Blackstone Capital Partners VII",
            "investment_date": "2019-03-15",
            "exit_date": "2024-01-20",
            "irr": "24.5%",
            "multiple": "2.8x",
            "investment_amount": 50000000
        }
        
        await feedback_loop.receive_validation("test_001", ground_truth)
        
        # Verify metrics updated
        assert feedback_loop.metrics["total_corrections"] > 0
        assert feedback_loop.metrics["accepted_corrections"] > 0
        
        # Step 3: Process similar document - should perform better
        similar_corrupted = {
            "fund_name": "2020-06-10",
            "investment_date": "Apollo Global Management",
            "exit_date": "2024-06-10",
            "irr": "40%",
            "multiple": "2.5x"
        }
        
        result2 = await feedback_loop.process_document(similar_corrupted, "test_002")
        
        # Should correct with high confidence due to learning
        assert result2["corrected_data"]["fund_name"] == "Apollo Global Management"
        assert result2["corrected_data"]["investment_date"] == "2020-06-10"
        assert result2["confidence"] > 0.9
    
    @pytest.mark.asyncio
    async def test_pattern_reinforcement(self, agent, feedback_loop):
        """Test that successful patterns are reinforced"""
        # Process multiple documents with same error pattern
        for i in range(5):
            corrupted = {
                "fund_name": f"2019-0{i+1}-15",
                "date": f"Fund ABC {i}"
            }
            
            await feedback_loop.process_document(corrupted, f"doc_{i}")
            
            # Validate each one
            ground_truth = {
                "fund_name": f"Fund ABC {i}",
                "date": f"2019-0{i+1}-15"
            }
            
            await feedback_loop.receive_validation(f"doc_{i}", ground_truth)
        
        # Check that pattern is now strongly recognized
        assert "date_fund_swap" in agent.success_patterns
        
        # New document should be corrected with very high confidence
        new_corrupted = {
            "fund_name": "2019-07-20",
            "date": "Fund XYZ"
        }
        
        corrected, corrections = await agent.detect_and_correct(new_corrupted)
        
        assert corrected["fund_name"] == "Fund XYZ"
        assert corrected["date"] == "2019-07-20"
        assert all(c.confidence > 0.95 for c in corrections)
    
    @pytest.mark.asyncio
    async def test_cross_field_validation(self, agent):
        """Test IRR calculation validation"""
        data = {
            "investment_date": "2020-01-01",
            "exit_date": "2024-01-01",
            "multiple": "2.0x",
            "irr": "50%"  # Way too high for 2x in 4 years
        }
        
        corrected, corrections = await agent.detect_and_correct(data)
        
        # Should correct IRR to approximately 18.9%
        irr_value = float(corrected["irr"].replace("%", ""))
        assert 18 < irr_value < 20
        
        # Find IRR correction
        irr_correction = next(c for c in corrections if c.field == "irr")
        assert irr_correction.confidence > 0.9
        assert "inconsistent" in irr_correction.reasoning.lower()
    
    @pytest.mark.asyncio
    async def test_learning_from_mistakes(self, agent, feedback_loop):
        """Test that agent learns from incorrect corrections"""
        # Process document
        corrupted = {
            "fund_name": "Private Equity Fund",
            "date": "Not a date",  # Unusual value
            "amount": "$1,000,000"
        }
        
        result = await feedback_loop.process_document(corrupted, "mistake_001")
        
        # Agent might make wrong correction
        # Provide correct ground truth
        ground_truth = {
            "fund_name": "Private Equity Fund",
            "date": "2024-01-15",  # Correct date was missing
            "amount": "$1,000,000"
        }
        
        await feedback_loop.receive_validation("mistake_001", ground_truth)
        
        # Process similar case
        similar = {
            "fund_name": "Venture Capital Fund",
            "date": "Invalid",
            "amount": "$2,000,000"
        }
        
        # Agent should not make the same mistake
        corrected, corrections = await agent.detect_and_correct(similar)
        
        # Should not incorrectly swap fields this time
        assert corrected["fund_name"] == "Venture Capital Fund"



