# Screener.in Strategy Backtester

Backtest the "Market Scientist" screening strategy from Screener.in

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Extract Tickers from Screener

```bash
python extract_tickers.py
```

This will scrape the screener page and save all 48 stock tickers to `tickers.txt`

### 3. Update the Backtest Script

Open `tickers.txt` and copy the ticker list into `screener_backtest.py` (replace the SAMPLE_TICKERS list)

### 4. Run Backtest

```bash
python screener_backtest.py
```

## Configuration

Edit the following parameters in `screener_backtest.py`:

```python
start_date = '2023-02-01'      # Start date
end_date = '2024-02-01'        # End date
initial_capital = 100000       # Initial investment (INR)
benchmark_ticker = '^NSEI'     # Nifty 50 (change to ^BSESN for Sensex)
```

## Output

The script will show:

- **Portfolio Performance**: Total return, CAGR, Sharpe ratio, max drawdown
- **Benchmark Comparison**: Returns vs Nifty 50
- **Top/Bottom Performers**: Best and worst stocks
- **CSV Export**: Daily portfolio values saved to `backtest_results.csv`

## Screener Criteria

The "Market Scientist" screen filters for:

- ✅ Price up >50% from 52-week low
- ✅ ROE >15%
- ✅ Trading <25% below 52-week high
- ✅ Market cap >₹1,000 crores
- ✅ Promoter holding >50%
- ✅ Debt-to-equity <0.5
- ✅ Interest coverage >3
- ✅ Positive operating cash flow
- ✅ Pledged shares <10%
- ✅ Operating profit margin >12%

## Notes

- Uses equal-weight allocation across all stocks
- Data from Yahoo Finance (free)
- NSE tickers (.NS suffix)
- Does not account for transaction costs or taxes
- Survivorship bias may exist (delisted stocks not included)

## Extending the Backtest

To add rebalancing or test different time periods, modify the `ScreenerBacktest` class methods.
