"""
Generate test data for the feedback loop
"""

import random
import json
from datetime import datetime, timedelta

def generate_ground_truth(n=100):
    """Generate n ground truth documents"""
    fund_names = [
        "Blackstone Capital Partners", "Apollo Global Management",
        "KKR Americas Fund", "Carlyle Partners", "TPG Growth",
        "Warburg Pincus Private Equity", "Silver Lake Partners",
        "Vista Equity Partners", "Thoma Bravo", "Bain Capital"
    ]
    
    documents = []
    
    for i in range(n):
        # Random dates
        investment_date = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 2000))
        exit_date = investment_date + timedelta(days=random.randint(365, 3650))
        
        # Calculate realistic IRR
        years = (exit_date - investment_date).days / 365.25
        multiple = random.uniform(1.5, 4.0)
        irr = (multiple ** (1/years) - 1) * 100
        
        # Investment amounts
        investment_amount = random.choice([10, 25, 50, 100, 250]) * 1_000_000
        exit_value = investment_amount * multiple
        
        doc = {
            "id": f"doc_{i:04d}",
            "fund_name": f"{random.choice(fund_names)} {random.choice(['VII', 'VIII', 'IX', 'X'])}",
            "investment_date": investment_date.strftime("%Y-%m-%d"),
            "exit_date": exit_date.strftime("%Y-%m-%d"),
            "irr": f"{irr:.1f}%",
            "multiple": f"{multiple:.1f}x",
            "investment_amount": investment_amount,
            "exit_value": int(exit_value)
        }
        
        documents.append(doc)
    
    return documents

def corrupt_document(doc):
    """Introduce common errors into document"""
    corrupted = doc.copy()
    error_types = []
    
    # Common error patterns
    if random.random() < 0.3:  # 30% chance of date/fund swap
        corrupted["fund_name"], corrupted["investment_date"] = corrupted["investment_date"], corrupted["fund_name"]
        error_types.append("date_fund_swap")
    
    if random.random() < 0.2:  # 20% chance of wrong IRR
        # Make IRR inconsistent with multiple and time period
        corrupted["irr"] = f"{random.uniform(30, 60):.1f}%"
        error_types.append("wrong_irr")
    
    if random.random() < 0.15:  # 15% chance of date format issue
        if "exit_date" in corrupted:
            # Change date format
            date = datetime.strptime(corrupted["exit_date"], "%Y-%m-%d")
            corrupted["exit_date"] = date.strftime("%m/%d/%Y")
        error_types.append("date_format")
    
    return corrupted, error_types

def generate_test_set():
    """Generate complete test set"""
    ground_truth_docs = generate_ground_truth(100)
    
    test_set = []
    for doc in ground_truth_docs:
        corrupted, errors = corrupt_document(doc)
        
        test_set.append({
            "ground_truth": doc,
            "corrupted": corrupted,
            "errors": errors
        })
    
    return test_set

def generate_all_test_cases():
    return [
        # 1. Cumulative/Total Consistency
        {
            'pattern_type': 'cumulative_total',
            'extracted': {
                'revenue_q1': 10000,
                'revenue_q2': 15000,
                'revenue_q3': 20000,
                'total_revenue': 40000  # should be 45000
            },
            'audited': {
                'revenue_q1': 10000,
                'revenue_q2': 15000,
                'revenue_q3': 20000,
                'total_revenue': 45000
            }
        },
        # 2. Date Sequence
        {
            'pattern_type': 'date_sequence',
            'extracted': {
                'reporting_period_start': '2023-01-01',
                'reporting_period_end': '2022-12-31'  # end before start
            },
            'audited': {
                'reporting_period_start': '2023-01-01',
                'reporting_period_end': '2023-12-31'
            }
        },
        # 3. Pattern Consistency (chronological order)
        {
            'pattern_type': 'chronological',
            'extracted': {
                'investment_date': '2021-05-01',
                'exit_date': '2020-05-01'  # exit before investment
            },
            'audited': {
                'investment_date': '2021-05-01',
                'exit_date': '2024-05-01'
            }
        },
        # 4. Type/Format Error
        {
            'pattern_type': 'type_error',
            'extracted': {
                'investment_amount': 'ten million',
                'exit_value': 20000000
            },
            'audited': {
                'investment_amount': 10000000,
                'exit_value': 20000000
            }
        },
        # 5. Swapped Fields
        {
            'pattern_type': 'swapped_fields',
            'extracted': {
                'fund_name': '2022-03-15',
                'investment_date': 'Blackstone Capital Partners VII'
            },
            'audited': {
                'fund_name': 'Blackstone Capital Partners VII',
                'investment_date': '2022-03-15'
            }
        },
        # 6. Accounting Equation
        {
            'pattern_type': 'accounting_equation',
            'extracted': {
                'assets': 100000,
                'liabilities': 40000,
                'equity': 30000  # should be 60000
            },
            'audited': {
                'assets': 100000,
                'liabilities': 40000,
                'equity': 60000
            }
        },
        # 7. Realistic multi-error case
        {
            'pattern_type': 'multi_error',
            'extracted': {
                'fund_name': '2018-01-01',
                'investment_date': 'Apollo Fund',
                'exit_date': '2017-12-31',  # exit before investment
                'investment_amount': 'five million',
                'exit_value': 8000000
            },
            'audited': {
                'fund_name': 'Apollo Fund',
                'investment_date': '2018-01-01',
                'exit_date': '2022-12-31',
                'investment_amount': 5000000,
                'exit_value': 8000000
            }
        }
    ]

if __name__ == "__main__":
    # Generate test data
    test_data = generate_test_set()
    
    # Save to file
    with open("test_data.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"Generated {len(test_data)} test documents")
    
    # Show statistics
    error_counts = {}
    for item in test_data:
        for error in item["errors"]:
            error_counts[error] = error_counts.get(error, 0) + 1
    
    print("\nError distribution:")
    for error_type, count in error_counts.items():
        print(f"  {error_type}: {count} ({count/len(test_data)*100:.1f}%)")


