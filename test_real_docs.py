#!/usr/bin/env python3
"""
Test the agent with real-world-like documents that contain various errors
"""

import asyncio
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import AnomalyDetectorAgent, FeedbackLoop

async def test_document(doc_path, doc_name):
    """Test a single document with the agent"""
    print(f"\n{'='*50}")
    print(f"TESTING {doc_name}")
    print(f"{'='*50}")
    
    # Load the document
    with open(doc_path, 'r') as f:
        extracted_data = json.load(f)
    
    print("Original extracted data:")
    for key, value in extracted_data.items():
        print(f"  {key}: {value}")
    
    # Initialize agent and feedback loop
    agent = AnomalyDetectorAgent()
    feedback_loop = FeedbackLoop(agent)
    
    # Process document
    result = await feedback_loop.process_document(extracted_data, f"test_{doc_name}")
    
    print(f"\nAgent found {result['corrections_made']} corrections:")
    if result['corrections_made'] > 0:
        corrections = feedback_loop.pending_validations[f"test_{doc_name}"]["corrections"]
        for i, correction in enumerate(corrections, 1):
            print(f"  {i}. Field: {correction.field}")
            print(f"     Original: {correction.original_value}")
            print(f"     Corrected: {correction.corrected_value}")
            print(f"     Confidence: {correction.confidence:.2f}")
            print(f"     Reasoning: {correction.reasoning}")
            print()
        
        print("Final corrected data:")
        for key, value in result["corrected_data"].items():
            print(f"  {key}: {value}")
    else:
        print("  No corrections suggested - data appears correct to the agent")
    
    return result

async def main():
    """Test all three documents"""
    print("Testing Real Document Anomaly Detection Agent")
    print("=" * 60)
    
    # Test documents (with full paths)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_doc_dir = os.path.join(base_dir, "test_doc")
    docs = [
        (os.path.join(test_doc_dir, "test_real_doc1.json"), "KKR Capital Call (Swapped fields + text amounts)"),
        (os.path.join(test_doc_dir, "test_real_doc2.json"), "Vista Investment (Date logic + text amounts + totals)"),
        (os.path.join(test_doc_dir, "test_real_doc3.json"), "Blackstone Report (Date sequence + totals + accounting)")
    ]
    
    all_results = []
    
    for doc_path, doc_name in docs:
        try:
            result = await test_document(doc_path, doc_name)
            all_results.append((doc_name, result))
        except Exception as e:
            print(f"Error testing {doc_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    total_corrections = sum(result['corrections_made'] for _, result in all_results)
    print(f"Total corrections made across all documents: {total_corrections}")
    
    for doc_name, result in all_results:
        print(f"• {doc_name}: {result['corrections_made']} corrections")

if __name__ == "__main__":
    asyncio.run(main())