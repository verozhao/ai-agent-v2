"""
Complete demonstration of the Anomaly Detection & Auto-Correction Agent
Shows the full feedback loop in action
"""

import asyncio
import json
from datetime import datetime
from agents import AnomalyDetectorAgent, FeedbackLoop


async def run_demo():
    """Run complete demonstration of the system"""
    print("=" * 80)
    print("ANOMALY DETECTION & AUTO-CORRECTION AGENT DEMO")
    print("=" * 80)
    
    # Initialize system
    print("\n1. Initializing Agent System...")
    agent = AnomalyDetectorAgent()
    feedback_loop = FeedbackLoop(agent)
    print("✓ Agent initialized with pattern recognition and ML models")
    
    # Test Case 1: Date/Fund Name Swap
    print("\n2. Test Case 1: Date and Fund Name Swapped")
    print("-" * 40)
    
    corrupted_1 = {
        "fund_name": "2019-03-15",
        "investment_date": "Blackstone Capital Partners VII",
        "exit_date": "2024-01-20",
        "irr": "24.5%",
        "multiple": "2.8x",
        "investment_amount": 50000000,
        "exit_value": 140000000
    }
    
    print("Corrupted JSON:")
    print(json.dumps(corrupted_1, indent=2))
    
    result_1 = await feedback_loop.process_document(corrupted_1, "demo_001")
    
    print("\nCorrected JSON:")
    print(json.dumps(result_1["corrected_data"], indent=2))
    print(f"\n✓ Made {result_1['corrections_made']} corrections with {result_1['confidence']:.2%} confidence")
    
    # Test Case 2: Wrong IRR Calculation
    print("\n3. Test Case 2: Incorrect IRR Calculation")
    print("-" * 40)
    
    corrupted_2 = {
        "fund_name": "Apollo Global Management",
        "investment_date": "2020-01-01",
        "exit_date": "2024-01-01",
        "irr": "50%",  # Way too high for 2x in 4 years
        "multiple": "2.0x",
        "investment_amount": 25000000,
        "exit_value": 50000000
    }
    
    print("Corrupted JSON:")
    print(json.dumps(corrupted_2, indent=2))
    
    result_2 = await feedback_loop.process_document(corrupted_2, "demo_002")
    
    print("\nCorrected JSON:")
    print(json.dumps(result_2["corrected_data"], indent=2))
    print(f"\n✓ Corrected IRR from 50% to ~{result_2['corrected_data']['irr']}")
    
    # Simulate DataOps Validation
    print("\n4. DataOps Team Validation")
    print("-" * 40)
    
    ground_truth_1 = {
        "fund_name": "Blackstone Capital Partners VII",
        "investment_date": "2019-03-15",
        "exit_date": "2024-01-20",
        "irr": "24.5%",
        "multiple": "2.8x",
        "investment_amount": 50000000,
        "exit_value": 140000000
    }
    
    print("DataOps team validates corrections...")
    await feedback_loop.receive_validation("demo_001", ground_truth_1)
    print(f"✓ Validation received. Agent accuracy: {feedback_loop.metrics['accuracy']:.2%}")
    
    # Test Case 3: Similar Error Pattern (Should perform better)
    print("\n5. Test Case 3: Similar Pattern (After Learning)")
    print("-" * 40)
    
    corrupted_3 = {
        "fund_name": "2021-06-10",
        "investment_date": "KKR Americas Fund XII",
        "exit_date": "2024-06-10",
        "irr": "35%",
        "multiple": "1.8x"
    }
    
    print("Corrupted JSON:")
    print(json.dumps(corrupted_3, indent=2))
    
    result_3 = await feedback_loop.process_document(corrupted_3, "demo_003")
    
    print("\nCorrected JSON:")
    print(json.dumps(result_3["corrected_data"], indent=2))
    print(f"\n✓ Corrections made with {result_3['confidence']:.2%} confidence (improved from learning)")
    
    # Summary
    print("\n6. Summary")
    print("-" * 40)
    print(f"Total corrections made: {feedback_loop.metrics['total_corrections']}")
    print(f"Accepted corrections: {feedback_loop.metrics['accepted_corrections']}")
    print(f"Current accuracy: {feedback_loop.metrics['accuracy']:.2%}")
    print("\n✓ Demo completed successfully!")


async def run_batch_test():
    """Run batch testing with multiple documents"""
    print("\n" + "=" * 80)
    print("BATCH TESTING")
    print("=" * 80)
    
    agent = AnomalyDetectorAgent()
    feedback_loop = FeedbackLoop(agent)
    
    # Generate test cases
    test_cases = [
        {
            "corrupted": {
                "fund_name": "2018-12-01",
                "date": "Carlyle Partners VI"
            },
            "ground_truth": {
                "fund_name": "Carlyle Partners VI",
                "date": "2018-12-01"
            }
        },
        {
            "corrupted": {
                "fund_name": "TPG Growth IV",
                "investment_amount": "$25,000,000",
                "irr": "60%",  # Wrong
                "multiple": "2.2x",
                "investment_date": "2019-01-01",
                "exit_date": "2023-01-01"
            },
            "ground_truth": {
                "fund_name": "TPG Growth IV",
                "investment_amount": "$25,000,000",
                "irr": "21.7%",
                "multiple": "2.2x",
                "investment_date": "2019-01-01",
                "exit_date": "2023-01-01"
            }
        }
    ]
    
    print(f"Processing {len(test_cases)} test documents...")
    
    for i, test_case in enumerate(test_cases):
        doc_id = f"batch_{i:03d}"
        
        # Process
        result = await feedback_loop.process_document(test_case["corrupted"], doc_id)
        
        # Validate
        await feedback_loop.receive_validation(doc_id, test_case["ground_truth"])
        
        print(f"✓ Document {doc_id}: {result['corrections_made']} corrections, "
              f"confidence: {result['confidence']:.2%}")
    
    print(f"\nFinal accuracy after batch: {feedback_loop.metrics['accuracy']:.2%}")


if __name__ == "__main__":
    # Run demos
    asyncio.run(run_demo())
    asyncio.run(run_batch_test())