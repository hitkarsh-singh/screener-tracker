"""
Explore nsepython capabilities for historical fundamental data
"""

from nsepython import *
import pandas as pd
from datetime import datetime, timedelta

print("="*60)
print("Exploring nsepython capabilities")
print("="*60)

# Test with a sample stock - Bharat Electronics (BEL)
symbol = "BEL"

print(f"\n1. Testing equity_history for {symbol}...")
try:
    # Get historical price data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    history = equity_history(symbol, "EQ", start_date.strftime("%d-%m-%Y"), end_date.strftime("%d-%m-%Y"))
    print(f"   ✓ Price history available")
    print(f"   Columns: {list(history.columns)}")
    print(f"   Data points: {len(history)}")
    print(history.head(3))
except Exception as e:
    print(f"   ✗ Error: {e}")

print(f"\n2. Testing nse_eq for fundamental data...")
try:
    # Get current stock info
    info = nse_eq(symbol)
    print(f"   ✓ Stock info available")
    print(f"   Keys available: {list(info.keys())[:20]}")  # Show first 20 keys
except Exception as e:
    print(f"   ✗ Error: {e}")

print(f"\n3. Testing nse_quote for quote data...")
try:
    quote = nse_quote(symbol)
    print(f"   ✓ Quote data available")
    if isinstance(quote, dict):
        print(f"   Keys: {list(quote.keys())[:15]}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print(f"\n4. Checking for corporate info...")
try:
    # Try to get corporate announcements or financial data
    corp_info = nse_eq(symbol)
    if 'metadata' in corp_info:
        print(f"   ✓ Metadata available")
        print(f"   Metadata keys: {list(corp_info['metadata'].keys())}")
    if 'securityInfo' in corp_info:
        print(f"   ✓ Security info available")
        print(f"   Security info keys: {list(corp_info['securityInfo'].keys())}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print(f"\n5. Testing if we can get financial ratios...")
try:
    # See if there's any financial ratio data
    data = nse_eq(symbol)

    # Look for financial metrics
    financial_keys = ['roe', 'ROE', 'debt', 'ratio', 'promoter', 'holding', 'margin', 'cash']
    found = []

    def search_dict(d, prefix=''):
        results = []
        if isinstance(d, dict):
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                # Check if key contains financial keywords
                if any(keyword in str(key).lower() for keyword in financial_keys):
                    results.append((full_key, type(value).__name__))
                # Recurse into nested dicts
                if isinstance(value, dict):
                    results.extend(search_dict(value, full_key))
        return results

    found = search_dict(data)

    if found:
        print(f"   ✓ Found {len(found)} potential financial metrics:")
        for key, vtype in found[:10]:
            print(f"     - {key} ({vtype})")
    else:
        print(f"   ✗ No obvious financial metrics found in NSE data")

except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)
print("Summary:")
print("="*60)
print("nsepython provides:")
print("  ✓ Historical price data (OHLCV)")
print("  ✓ Current stock quotes")
print("  ? Fundamental data - need to explore further")
print("\nFor screener criteria, we need:")
print("  - ROE (Return on Equity)")
print("  - Debt-to-equity ratio")
print("  - Interest coverage ratio")
print("  - Operating cash flow")
print("  - Promoter holding")
print("  - Pledged shares")
print("  - Operating profit margin")
print("  - Market cap")
print("\nLet's see what we can extract...")
