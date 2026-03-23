#!/usr/bin/env python3
"""
Sample Python file to test LocalWise text-based file processing.

This file demonstrates the new text-based file processing capabilities
that have been added to LocalWise v1.0.0.

Features tested:
- Python source code processing
- Comment extraction
- Function definition recognition
- Multi-line string handling
"""

def greet_user(name: str) -> str:
    """
    Greets a user with their name.
    
    Args:
        name (str): The user's name
        
    Returns:
        str: A greeting message
    """
    return f"Hello, {name}! Welcome to LocalWise."

def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n (int): The position in the Fibonacci sequence
        
    Returns:
        int: The nth Fibonacci number
    """
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)

# Test data
test_data = {
    "name": "LocalWise User",
    "version": "1.0.0",
    "features": [
        "PDF processing",
        "CSV analysis", 
        "JSON parsing",
        "YAML configuration",
        "XML structure",
        "Text-based files",
        "Source code files",
        "Documentation files"
    ]
}

if __name__ == "__main__":
    print("LocalWise Text Processing Test File")
    print("=" * 40)
    
    # Test greeting function
    user_name = test_data["name"]
    greeting = greet_user(user_name)
    print(greeting)
    
    # Test fibonacci calculation
    fib_result = calculate_fibonacci(10)
    print(f"10th Fibonacci number: {fib_result}")
    
    # Display supported features
    print("\nSupported features:")
    for i, feature in enumerate(test_data["features"], 1):
        print(f"{i}. {feature}")