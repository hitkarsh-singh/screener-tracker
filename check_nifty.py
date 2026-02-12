import yfinance as yf
import pandas as pd

# Check Nifty 50 data for the backtest period
start_date = '2023-02-01'
end_date = '2024-02-01'

print("Checking Nifty 50 benchmark data...")
print(f"Period: {start_date} to {end_date}\n")

nifty = yf.download('^NSEI', start=start_date, end=end_date, progress=False)

print("First 5 rows:")
print(nifty.head())
print("\nLast 5 rows:")
print(nifty.tail())

if not nifty.empty:
    print(f"\nData points: {len(nifty)}")
    print(f"\nColumn structure: {nifty.columns}")

    # Check what columns exist
    if isinstance(nifty.columns, pd.MultiIndex):
        print("MultiIndex columns detected")
        print(nifty.columns.tolist())
        close_col = nifty.iloc[:, 3]  # Close is usually 4th column
    else:
        close_col = nifty['Close'] if 'Close' in nifty.columns else nifty['Adj Close']

    start_price = close_col.iloc[0]
    end_price = close_col.iloc[-1]

    returns = ((end_price / start_price) - 1) * 100

    print(f"\nStart Price: {start_price:.2f}")
    print(f"End Price: {end_price:.2f}")
    print(f"Total Return: {returns:.2f}%")
