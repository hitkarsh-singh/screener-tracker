"""
Extract stock tickers from Screener.in screen
This script scrapes the screener page and extracts all stock tickers
"""

import requests
from bs4 import BeautifulSoup
import json

def extract_tickers_from_screener(url):
    """
    Extract stock tickers from a Screener.in screen URL

    Parameters:
    -----------
    url : str
        The screener.in URL

    Returns:
    --------
    list : List of tickers with .NS suffix for NSE
    """
    print(f"Fetching data from: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table with results
        table = soup.find('table', {'class': 'data-table'})

        if not table:
            print("❌ Could not find results table")
            return []

        tickers = []
        stock_names = []

        # Extract ticker symbols from the table
        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                # First column contains the company name and link
                name_cell = cols[0]
                link = name_cell.find('a')

                if link and 'href' in link.attrs:
                    # Extract company URL which contains the ticker
                    href = link['href']
                    # URL format: /company/TICKER/
                    parts = href.strip('/').split('/')
                    if len(parts) >= 2:
                        ticker = parts[-1]
                        company_name = link.text.strip()

                        # Add .NS for NSE (you can change to .BO for BSE)
                        ticker_with_suffix = f"{ticker}.NS"
                        tickers.append(ticker_with_suffix)
                        stock_names.append(company_name)

                        print(f"  ✓ {company_name} ({ticker_with_suffix})")

        print(f"\n✅ Extracted {len(tickers)} tickers")

        return tickers, stock_names

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return [], []


def save_tickers_to_file(tickers, stock_names, filename='tickers.txt'):
    """Save tickers to a file"""
    with open(filename, 'w') as f:
        f.write("# Tickers from Market Scientist Screener\n")
        f.write("# Format: TICKER.NS (NSE)\n\n")
        f.write("TICKERS = [\n")
        for ticker, name in zip(tickers, stock_names):
            f.write(f"    '{ticker}',  # {name}\n")
        f.write("]\n")

    print(f"\n💾 Saved to {filename}")


if __name__ == "__main__":
    screener_url = "https://www.screener.in/screens/336269/market-scientist/"

    print("="*60)
    print("📊 SCREENER.IN TICKER EXTRACTOR")
    print("="*60)
    print()

    tickers, names = extract_tickers_from_screener(screener_url)

    if tickers:
        save_tickers_to_file(tickers, names)

        print("\n" + "="*60)
        print(f"Total stocks found: {len(tickers)}")
        print("="*60)
        print("\nYou can now copy these tickers into screener_backtest.py")
    else:
        print("\n⚠️  No tickers found. The page structure might have changed.")
        print("Please manually copy ticker symbols from the screener page.")
