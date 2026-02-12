"""
Screener.in Strategy Backtester
Backtests the "Market Scientist" screening strategy from Screener.in
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

class ScreenerBacktest:
    def __init__(self, tickers, start_date, end_date, initial_capital=100000):
        """
        Initialize the backtester

        Parameters:
        -----------
        tickers : list
            List of stock tickers (NSE symbols with .NS suffix)
        start_date : str
            Start date in 'YYYY-MM-DD' format
        end_date : str
            End date in 'YYYY-MM-DD' format
        initial_capital : float
            Initial investment amount in INR
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.data = None
        self.portfolio_value = None

    def fetch_data(self):
        """Fetch historical price data for all tickers"""
        print(f"Fetching data for {len(self.tickers)} stocks...")

        all_data = {}
        failed_tickers = []

        for ticker in self.tickers:
            try:
                print(f"Downloading {ticker}...")
                stock = yf.download(ticker, start=self.start_date, end=self.end_date, progress=False)

                if not stock.empty and len(stock) > 10:
                    # Try to get Adj Close, fall back to Close if not available
                    if isinstance(stock.columns, pd.MultiIndex):
                        # Handle MultiIndex columns
                        if ('Adj Close', ticker) in stock.columns:
                            all_data[ticker] = stock[('Adj Close', ticker)]
                        elif ('Close', ticker) in stock.columns:
                            all_data[ticker] = stock[('Close', ticker)]
                    else:
                        # Handle regular columns
                        if 'Adj Close' in stock.columns:
                            all_data[ticker] = stock['Adj Close']
                        elif 'Close' in stock.columns:
                            all_data[ticker] = stock['Close']
                        else:
                            print(f"  ⚠️  No price data for {ticker}")
                            failed_tickers.append(ticker)
                            continue
                    print(f"  ✓ Success")
                else:
                    print(f"  ⚠️  Insufficient data for {ticker}")
                    failed_tickers.append(ticker)
            except Exception as e:
                print(f"  ❌ Failed to download {ticker}: {str(e)}")
                failed_tickers.append(ticker)

        if failed_tickers:
            print(f"\n⚠️  Could not fetch data for {len(failed_tickers)} stocks")

        self.data = pd.DataFrame(all_data)
        print(f"\n✓ Successfully loaded data for {len(all_data)} stocks")
        return self.data

    def equal_weight_backtest(self):
        """
        Backtest with equal weight allocation
        Buy all stocks at start date, hold until end date
        """
        if self.data is None or self.data.empty:
            raise ValueError("No data available. Run fetch_data() first.")

        # Remove stocks with missing data on first day
        first_day_data = self.data.iloc[0]
        valid_stocks = first_day_data.dropna().index.tolist()

        print(f"\n📊 Starting backtest with {len(valid_stocks)} stocks")
        print(f"Initial Capital: ₹{self.initial_capital:,.2f}")

        # Equal weight allocation
        weight_per_stock = self.initial_capital / len(valid_stocks)

        # Calculate number of shares for each stock
        first_prices = self.data[valid_stocks].iloc[0]
        shares = weight_per_stock / first_prices

        # Calculate portfolio value over time
        portfolio_values = (self.data[valid_stocks] * shares).sum(axis=1)

        self.portfolio_value = portfolio_values

        return portfolio_values

    def calculate_metrics(self, benchmark_ticker='^NSEI'):
        """
        Calculate performance metrics

        Parameters:
        -----------
        benchmark_ticker : str
            Benchmark index ticker (default: Nifty 50)
        """
        if self.portfolio_value is None:
            raise ValueError("Run backtest first using equal_weight_backtest()")

        # Portfolio metrics
        total_return = (self.portfolio_value.iloc[-1] / self.initial_capital - 1) * 100

        # Calculate daily returns
        daily_returns = self.portfolio_value.pct_change().dropna()

        # Annualized metrics
        days = (pd.to_datetime(self.end_date) - pd.to_datetime(self.start_date)).days
        years = days / 365.25
        cagr = (((self.portfolio_value.iloc[-1] / self.initial_capital) ** (1/years)) - 1) * 100

        volatility = daily_returns.std() * np.sqrt(252) * 100
        sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))

        # Max drawdown
        cumulative = self.portfolio_value / self.portfolio_value.cummax()
        max_drawdown = ((cumulative.min() - 1) * 100)

        # Benchmark comparison
        try:
            print(f"\nFetching benchmark data ({benchmark_ticker})...")
            benchmark = yf.download(benchmark_ticker, start=self.start_date, end=self.end_date, progress=False)

            if not benchmark.empty:
                # Get Close column - handle both single and multi-index
                if isinstance(benchmark.columns, pd.MultiIndex):
                    # For MultiIndex, extract just the 'Close' prices
                    bench_prices = benchmark['Close'].iloc[:, 0]
                else:
                    bench_prices = benchmark['Close'] if 'Close' in benchmark.columns else benchmark['Adj Close']

                start_price = bench_prices.iloc[0]
                end_price = bench_prices.iloc[-1]

                print(f"  Benchmark Start: {start_price:.2f}, End: {end_price:.2f}")

                benchmark_return = ((end_price / start_price) - 1) * 100
                benchmark_cagr = (((end_price / start_price) ** (1/years)) - 1) * 100
                alpha = cagr - benchmark_cagr
            else:
                benchmark_return = None
                benchmark_cagr = None
                alpha = None
        except Exception as e:
            print(f"  ⚠️  Benchmark error: {e}")
            benchmark_return = None
            benchmark_cagr = None
            alpha = None

        # Print results
        print("\n" + "="*60)
        print("📈 BACKTEST RESULTS")
        print("="*60)
        print(f"\n💰 PORTFOLIO PERFORMANCE")
        print(f"  Initial Capital:        ₹{self.initial_capital:,.2f}")
        print(f"  Final Value:            ₹{self.portfolio_value.iloc[-1]:,.2f}")
        print(f"  Total Return:           {total_return:,.2f}%")
        print(f"  CAGR:                   {cagr:.2f}%")
        print(f"  Volatility (Annual):    {volatility:.2f}%")
        print(f"  Sharpe Ratio:           {sharpe_ratio:.2f}")
        print(f"  Max Drawdown:           {max_drawdown:.2f}%")

        if benchmark_return is not None:
            print(f"\n📊 BENCHMARK COMPARISON ({benchmark_ticker})")
            print(f"  Benchmark Return:       {benchmark_return:.2f}%")
            print(f"  Benchmark CAGR:         {benchmark_cagr:.2f}%")
            print(f"  Alpha:                  {alpha:+.2f}%")
            print(f"  Outperformance:         {total_return - benchmark_return:+.2f}%")

        print("\n" + "="*60)

        # Return metrics as dict
        metrics = {
            'initial_capital': self.initial_capital,
            'final_value': self.portfolio_value.iloc[-1],
            'total_return_pct': total_return,
            'cagr_pct': cagr,
            'volatility_pct': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            'benchmark_return_pct': benchmark_return,
            'benchmark_cagr_pct': benchmark_cagr,
            'alpha_pct': alpha
        }

        return metrics

    def get_top_bottom_performers(self, n=10):
        """Get top and bottom performing stocks"""
        if self.data is None:
            raise ValueError("No data available. Run fetch_data() first.")

        returns = ((self.data.iloc[-1] / self.data.iloc[0]) - 1) * 100
        returns = returns.dropna().sort_values(ascending=False)

        print(f"\n🏆 TOP {n} PERFORMERS")
        print("-" * 50)
        for i, (ticker, ret) in enumerate(returns.head(n).items(), 1):
            print(f"  {i:2d}. {ticker:20s} {ret:+8.2f}%")

        print(f"\n📉 BOTTOM {n} PERFORMERS")
        print("-" * 50)
        for i, (ticker, ret) in enumerate(returns.tail(n).items(), 1):
            print(f"  {i:2d}. {ticker:20s} {ret:+8.2f}%")

        return returns

    def save_results(self, filename='backtest_results.csv'):
        """Save portfolio value over time to CSV"""
        if self.portfolio_value is None:
            raise ValueError("Run backtest first")

        results_df = pd.DataFrame({
            'Date': self.portfolio_value.index,
            'Portfolio_Value': self.portfolio_value.values
        })
        results_df.to_csv(filename, index=False)
        print(f"\n💾 Results saved to {filename}")


# Example usage and stock list
if __name__ == "__main__":
    # Sample tickers from the screener (add .NS for NSE or .BO for BSE)
    # You need to replace these with the actual tickers from the screener

    # ACTUAL Tickers from Market Scientist Screener (as of current date)
    # Extracted directly from https://www.screener.in/screens/336269/market-scientist/
    SAMPLE_TICKERS = [
        # Page 1
        'SAFEENTP.NS',      # Safe Enterprises
        'WAAREE.NS',        # Waaree Energies
        'GVTD.NS',          # GVT&D
        'ALPEXSOLAR.NS',    # Alpex Solar
        'PRUDENT.NS',       # Prudent Corporate
        'NATIONALUM.NS',    # National Aluminium
        'TANLA.NS',         # Tanla Platforms
        'HDFCAMC.NS',       # HDFC AMC
        'TANFAC.NS',        # Tanfac Industries
        'FRONTIERSPR.NS',   # Frontier Springs
        'NAM-INDIA.NS',     # Nam India
        'BEL.NS',           # Bharat Electronics
        'SOLARINDS.NS',     # Solar Industries
        'CUMMINSIND.NS',    # Cummins India
        'ABSLAMC.NS',       # Aditya Birla Sun Life AMC
        'WAAREERENEW.NS',   # Waaree Renewable Energy
        'SHREEJISPG.NS',    # Shree Jee Spinning Mills
        'BANCOINDIA.NS',    # Banco Products India
        'FOSECOIND.NS',     # Foseco India
        'ASTRAL.NS',        # Astral Ltd
        'KINGFA.NS',        # Kingfa Science & Technology
        'FORCEMOT.NS',      # Force Motors
        'POLYCAB.NS',       # Polycab India
        'SIKAINTER.NS',     # Sika Interplant Systems
        # Page 2
        'POKARNA.NS',       # Pokarna
        'ECLERX.NS',        # eClerx Services
        'AMIC.NS',          # Amic Forging
        'FIEMIND.NS',       # Fiem Industries
        'STYLAMIND.NS',     # Stylam Industries
        'GUJTHEMIS.NS',     # Gujarat Themis Biosyn
        'HINDCOPPER.NS',    # Hindustan Copper
        'GODAWRI.NS',       # Godawari Power
        'INDIANMETAL.NS',   # Indian Metals
        'EMCURE.NS',        # Emcure Pharma
        'ZFCVINDIA.NS',     # ZF Commercial Vehicle
        'GALLANTT.NS',      # Gallantt Ispat
        'HAPPYFORGE.NS',    # Happy Forgings
        'VISHNUCHEM.NS',    # Vishnu Chemicals
        'TEGA.NS',          # Tega Industries
        'NAVA.NS',          # Nava Bharat Ventures
    ]

    print("="*60)
    print("🔬 SCREENER.IN STRATEGY BACKTESTER")
    print("="*60)
    print("\n⚠️  NOTE: You need to update the SAMPLE_TICKERS list")
    print("   with the actual 48 stocks from the screener.\n")

    # Set backtest period
    start_date = '2023-02-01'  # 1 year ago
    end_date = '2024-02-01'
    initial_capital = 100000  # 1 Lakh INR

    # Initialize backtester
    bt = ScreenerBacktest(
        tickers=SAMPLE_TICKERS,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    # Fetch data
    bt.fetch_data()

    # Run backtest
    bt.equal_weight_backtest()

    # Calculate and display metrics
    metrics = bt.calculate_metrics(benchmark_ticker='^NSEI')  # Nifty 50

    # Show top/bottom performers
    bt.get_top_bottom_performers(n=5)

    # Save results
    bt.save_results('backtest_results.csv')
