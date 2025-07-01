"""
Main execution entry point for the Anomaly Detection & Auto-Correction Agent
"""

import asyncio
import json
import logging
import sys
import os
import importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import AnomalyDetectorAgent, FeedbackLoop

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_test_cases():
    spec = importlib.util.spec_from_file_location("generate_test_data", "scripts/generate_test_data.py")
    test_data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_data)
    return test_data.generate_all_test_cases()

async def main():
    """Main execution function"""
    logger.info("Starting Anomaly Detection & Auto-Correction Agent")
    
    # Initialize agent
    agent = AnomalyDetectorAgent()
    feedback_loop = FeedbackLoop(agent)
    test_cases = load_test_cases()
    for i, case in enumerate(test_cases):
        print(f"\n{'='*30}\nTEST CASE {i+1}\n{'='*30}")
        extracted = case['extracted']
        audited = case['audited']
        print("Extracted (raw):", extracted)
        result = await feedback_loop.process_document(extracted, f"doc_{i+1}")
        corrections = feedback_loop.pending_validations[f"doc_{i+1}"]["corrections"]
        if corrections:
            print("Auto-corrected:", result["corrected_data"])
            print("Corrections:")
            for c in corrections:
                print(f"  Field: {c.field}, Original: {c.original_value}, Corrected: {c.corrected_value}, Reason: {c.reasoning}, Confidence: {c.confidence}")
        else:
            print("No auto-correction. Sending to human audit (simulated).")
        # Simulate human audit (always use audited version)
        await feedback_loop.receive_validation(f"doc_{i+1}", audited)
        print("Audited (ground truth):", audited)
        print(f"Feedback loop metrics: {feedback_loop.metrics}")
    print("\n✓ All test cases completed!")

if __name__ == "__main__":
    asyncio.run(main())