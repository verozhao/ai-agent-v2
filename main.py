"""
Main execution entry point for the Anomaly Detection & Auto-Correction Agent
"""

import asyncio
import json
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import AnomalyDetectorAgent, FeedbackLoop

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main execution function"""
    logger.info("Starting Anomaly Detection & Auto-Correction Agent")
    
    # Initialize agent
    agent = AnomalyDetectorAgent()
    feedback_loop = FeedbackLoop(agent)
    
    # Generate test case
    ground_truth = {
        "fund_name": "Blackstone Capital Partners VII",
        "investment_date": "2019-03-15",
        "exit_date": "2024-01-20",
        "irr": "24.5%",
        "multiple": "2.8x",
        "investment_amount": 50000000,
        "exit_value": 140000000
    }
    
    # Generate corrupted JSON (common errors)
    corrupted_json = {
        "fund_name": "2019-03-15",  # Date in fund name field
        "investment_date": "Blackstone Capital Partners VII",  # Fund name in date field
        "exit_date": "2024-01-20",
        "irr": "45.2%",  # Wrong IRR
        "multiple": "2.8x",
        "investment_amount": "50000000",
        "exit_value": 140000000
    }
    
    print("\n" + "="*60)
    print("ANOMALY DETECTION & AUTO-CORRECTION TEST")
    print("="*60)
    
    print("\nOriginal corrupted JSON:")
    print(json.dumps(corrupted_json, indent=2))
    
    # Process through agent
    result = await feedback_loop.process_document(corrupted_json, "test_001")
    
    print("\nCorrected JSON:")
    print(json.dumps(result["corrected_data"], indent=2))
    
    print(f"\nCorrections made: {result['corrections_made']}")
    print(f"Confidence: {result['confidence']:.2f}")
    
    # Simulate DataOps validation
    await feedback_loop.receive_validation("test_001", ground_truth)
    
    print(f"\nFeedback loop metrics:")
    print(f"Total corrections: {feedback_loop.metrics['total_corrections']}")
    print(f"Accepted: {feedback_loop.metrics['accepted_corrections']}")
    print(f"Rejected: {feedback_loop.metrics['rejected_corrections']}")
    print(f"Accuracy: {feedback_loop.metrics['accuracy']:.2%}")
    
    print("\n✓ Agent test completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())