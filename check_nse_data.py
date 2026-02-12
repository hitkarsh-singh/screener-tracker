"""
Check what data NSE actually provides
"""

from nsepython import *
import json

symbol = "BEL"

print("="*60)
print(f"Full NSE data for {symbol}")
print("="*60)

try:
    data = nse_eq(symbol)

    # Print the full structure
    print(json.dumps(data, indent=2, default=str))

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("Checking if NSE provides corporate announcements or financials")
print("="*60)

# Try other nsepython functions
print("\nAvailable nsepython functions:")
import nsepython
functions = [func for func in dir(nsepython) if not func.startswith('_')]
print(functions[:30])  # Show first 30 functions
