"""
Simplified Anomaly Detection Agent that works without ML models
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class CorrectionDecision:
    field: str
    original_value: Any
    corrected_value: Any
    confidence: float
    reasoning: str
    pattern_id: str


class SimpleAnomalyAgent:
    """Simplified agent using rule-based detection"""
    
    def __init__(self):
        print("Initializing Simple Anomaly Agent...")
        self.correction_history = []
        
    def is_date_like(self, value: str) -> bool:
        """Check if value looks like a date"""
        try:
            # Check common date patterns
            date_patterns = [
                r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
                r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
                r'^\d{2}-\d{2}-\d{4}$',  # DD-MM-YYYY
            ]
            
            value_str = str(value).strip()
            for pattern in date_patterns:
                if re.match(pattern, value_str):
                    return True
            
            # Try parsing as date
            pd.to_datetime(value_str)
            return True
        except:
            return False
    
    def is_fund_name_like(self, value: str) -> bool:
        """Check if value looks like a fund name"""
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        
        # Fund name indicators
        indicators = [
            "fund", "capital", "partners", "lp", "llc", "inc", 
            "ventures", "management", "equity", "group", "holdings"
        ]
        
        # Check if contains any indicator
        has_indicator = any(ind in value_lower for ind in indicators)
        
        # Check if starts with capital letter and has multiple words
        has_capital = value and value[0].isupper()
        has_multiple_words = len(value.split()) > 1
        
        return has_indicator or (has_capital and has_multiple_words and len(value) > 10)
    
    def is_percentage_like(self, value: str) -> bool:
        """Check if value looks like a percentage"""
        try:
            value_str = str(value).strip()
            # Remove % sign if present
            value_clean = value_str.replace('%', '').strip()
            float_val = float(value_clean)
            return 0 <= float_val <= 100
        except:
            return False
    
    def is_multiple_like(self, value: str) -> bool:
        """Check if value looks like a multiple"""
        try:
            value_str = str(value).strip().lower()
            # Remove x if present
            value_clean = value_str.replace('x', '').strip()
            float_val = float(value_clean)
            return 0 < float_val < 20  # Reasonable range for multiples
        except:
            return False
    
    def detect_field_type(self, field_name: str) -> str:
        """Detect expected field type from field name"""
        field_lower = field_name.lower()
        
        # Date fields
        if any(d in field_lower for d in ["date", "dated", "dt"]):
            return "date"
        
        # Fund name fields
        if any(f in field_lower for f in ["fund", "name", "company", "portfolio"]):
            return "fund_name"
        
        # Percentage fields
        if any(p in field_lower for p in ["irr", "return", "percent", "rate"]):
            return "percentage"
        
        # Multiple fields
        if any(m in field_lower for m in ["multiple", "moic", "tvpi"]):
            return "multiple"
        
        # Amount fields
        if any(a in field_lower for a in ["amount", "value", "price"]):
            return "amount"
        
        return "unknown"
    
    def validate_field_value(self, field_name: str, value: Any) -> bool:
        """Check if value matches expected type for field"""
        expected_type = self.detect_field_type(field_name)
        
        if expected_type == "date":
            return self.is_date_like(str(value))
        elif expected_type == "fund_name":
            return self.is_fund_name_like(str(value))
        elif expected_type == "percentage":
            return self.is_percentage_like(str(value))
        elif expected_type == "multiple":
            return self.is_multiple_like(str(value))
        
        return True  # Unknown type, assume valid
    
    async def detect_and_correct(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[CorrectionDecision]]:
        """Main detection and correction method"""
        corrected = data.copy()
        corrections = []
        
        # Phase 1: Check for swapped fields
        for field1, value1 in data.items():
            if not self.validate_field_value(field1, value1):
                # Value doesn't match field type, look for swap
                for field2, value2 in data.items():
                    if field1 != field2:
                        # Check if swapping would fix both
                        if (self.validate_field_value(field1, value2) and 
                            self.validate_field_value(field2, value1)):
                            
                            # Found a swap!
                            corrections.append(CorrectionDecision(
                                field=field1,
                                original_value=value1,
                                corrected_value=value2,
                                confidence=0.95,
                                reasoning=f"Value appears to be swapped with {field2}",
                                pattern_id="field_swap"
                            ))
                            
                            corrections.append(CorrectionDecision(
                                field=field2,
                                original_value=value2,
                                corrected_value=value1,
                                confidence=0.95,
                                reasoning=f"Value appears to be swapped with {field1}",
                                pattern_id="field_swap"
                            ))
                            
                            corrected[field1] = value2
                            corrected[field2] = value1
                            break
        
        # Phase 2: IRR validation
        if all(k in corrected for k in ["investment_date", "exit_date", "multiple", "irr"]):
            try:
                inv_date = pd.to_datetime(corrected["investment_date"])
                exit_date = pd.to_datetime(corrected["exit_date"])
                years = (exit_date - inv_date).days / 365.25
                
                if years > 0:
                    multiple = float(str(corrected["multiple"]).replace("x", ""))
                    expected_irr = (multiple ** (1/years) - 1) * 100
                    actual_irr = float(str(corrected["irr"]).replace("%", ""))
                    
                    if abs(expected_irr - actual_irr) > 5:
                        corrections.append(CorrectionDecision(
                            field="irr",
                            original_value=corrected["irr"],
                            corrected_value=f"{expected_irr:.1f}%",
                            confidence=0.92,
                            reasoning=f"IRR inconsistent with {multiple}x over {years:.1f} years",
                            pattern_id="irr_calculation"
                        ))
                        corrected["irr"] = f"{expected_irr:.1f}%"
            except:
                pass
        
        return corrected, corrections


# Test function
async def test_simple_agent():
    """Test the simplified agent"""
    agent = SimpleAnomalyAgent()
    
    # Test case 1: Swapped fields
    print("\nTest 1: Swapped fields")
    data1 = {
        "fund_name": "2019-03-15",
        "investment_date": "Blackstone Capital Partners VII"
    }
    
    corrected1, corrections1 = await agent.detect_and_correct(data1)
    print(f"Original: {data1}")
    print(f"Corrected: {corrected1}")
    print(f"Corrections: {len(corrections1)}")
    
    # Test case 2: Wrong IRR
    print("\nTest 2: Wrong IRR")
    data2 = {
        "investment_date": "2020-01-01",
        "exit_date": "2024-01-01",
        "multiple": "2.0x",
        "irr": "50%"
    }
    
    corrected2, corrections2 = await agent.detect_and_correct(data2)
    print(f"Original IRR: {data2['irr']}")
    print(f"Corrected IRR: {corrected2['irr']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_simple_agent())