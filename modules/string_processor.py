"""
MEGAN Auto-Generated Module: string_processor
Description: Utility for analyzing string properties
Created: 2026-05-09T21:03:06.532361
"""

import re

def calculate_complexity_score(text: str) -> dict:
    """
    Calculates a basic complexity score for a given string.
    Score includes: length, unique character count, and average ASCII value.
    """
    if not text:
        return {"error": "Input string cannot be empty."}

    length = len(text)
    unique_chars = len(set(text))
    
    # Calculate average ASCII value
    ascii_sum = sum(ord(char) for char in text)
    average_ascii = ascii_sum / length if length > 0 else 0

    return {
        "length": length,
        "unique_chars": unique_chars,
        "average_ascii": round(average_ascii, 2)
    }

# Example test call (This part is internal for module registration)
# print(calculate_complexity_score("MEGAN"))