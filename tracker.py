"""
Automated Screener.in Portfolio Tracker
Tracks a portfolio based on Market Scientist screener with daily rebalancing

PRICING: Uses CMP (Current Market Price) from screener.in
- During market hours: live price
- After 4 PM: closing price
- Works for both NSE and BSE stocks
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import os
import json
from pathlib import Path

# Configuration
SCREENER_URL = "https://www.screener.in/screens/336269/market-scientist/"
ALLOCATION_PER_STOCK = 10000  # ₹10,000 per stock
BUY_FEE = 0.0005  # 0.05% fee on buying
SELL_FEE = 0.0005  # 0.05% fee on selling
DATA_DIR = Path("data")

class ScreenerPortfolioTracker:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(exist_ok=True)

        # File paths
        self.portfolio_file = self.data_dir / "portfolio_value.csv"
        self.holdings_file = self.data_dir / "current_holdings.csv"
        self.transactions_file = self.data_dir / "transactions.csv"
        self.changes_file = self.data_dir / "daily_changes.csv"
        self.screener_history_file = self.data_dir / "screener_history.csv"

        # Initialize or load data
        self.load_data()

    def load_data(self):
        """Load existing data or create new DataFrames"""
        # Portfolio value history
        if self.portfolio_file.exists():
            self.portfolio_df = pd.read_csv(self.portfolio_file)
        else:
            self.portfolio_df = pd.DataFrame(columns=[
                'Date', 'Portfolio_Value', 'Cash_Invested', 'Total_Return_Pct',
                'Nifty_Value', 'Nifty_Return_Pct', 'Alpha_Pct'
            ])

        # Current holdings
        if self.holdings_file.exists():
            self.holdings_df = pd.read_csv(self.holdings_file)
        else:
            self.holdings_df = pd.DataFrame(columns=[
                'Stock', 'Shares', 'Avg_Buy_Price', 'Last_Price',
                'Investment', 'Current_Value', 'Profit_Loss_Pct'
            ])

        # Transaction history
        if self.transactions_file.exists():
            self.transactions_df = pd.read_csv(self.transactions_file)
        else:
            self.transactions_df = pd.DataFrame(columns=[
                'Date', 'Stock', 'Action', 'Shares', 'Price',
                'Gross_Amount', 'Fee', 'Net_Amount'
            ])

        # Daily changes log
        if self.changes_file.exists():
            self.changes_df = pd.read_csv(self.changes_file)
        else:
            self.changes_df = pd.DataFrame(columns=[
                'Date', 'Stocks_Added', 'Stocks_Removed',
                'Total_Holdings', 'Cash_Deployed'
            ])

        # Screener history
        if self.screener_history_file.exists():
            self.screener_history_df = pd.read_csv(self.screener_history_file)
        else:
            self.screener_history_df = pd.DataFrame(columns=['Date', 'Stocks'])

    def scrape_screener(self):
        """Scrape current stocks and prices from screener.in"""
        print(f"Scraping screener: {SCREENER_URL}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.screener.in/',
        }

        stock_data = {}  # {ticker: price}

        # Scrape both pages
        for page in [1, 2]:
            url = f"{SCREENER_URL}?page={page}" if page > 1 else SCREENER_URL

            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find the data table
                table = soup.find('table', {'class': 'data-table'})

                if table:
                    rows = table.find_all('tr')[1:]  # Skip header

                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 3:  # Need at least: S.No, Name, Price
                            # Column 1 (index 1): Name with link
                            name_cell = cols[1]
                            link = name_cell.find('a')

                            # Column 2 (index 2): CMP Rs. (Current Market Price)
                            price_cell = cols[2]

                            if link and 'href' in link.attrs:
                                href = link['href']
                                parts = href.strip('/').split('/')
                                if len(parts) >= 2 and parts[0] == 'company':
                                    ticker = parts[1]

                                    # Extract price from the cell
                                    try:
                                        price_text = price_cell.get_text(strip=True)
                                        # Remove commas and convert to float
                                        price = float(price_text.replace(',', ''))

                                        if ticker and ticker not in stock_data:
                                            stock_data[ticker] = price

                                    except (ValueError, AttributeError) as e:
                                        print(f"  ⚠️  Could not parse price for {ticker}: {price_text}")

                print(f"  Page {page}: Found {len(stock_data)} stocks with prices so far")

            except Exception as e:
                print(f"  Error scraping page {page}: {e}")

        # If scraping failed, return empty dict
        if not stock_data:
            print("  ⚠️  Scraping failed - no stocks found")
            print("  This might be due to:")
            print("    - JavaScript-rendered content")
            print("    - Website blocking automated access")
            print("    - Changed page structure")
            return {}

        # Add .NS suffix for NSE (Yahoo Finance format)
        nse_stock_data = {f"{ticker}.NS": price for ticker, price in stock_data.items()}

        print(f"Total stocks scraped: {len(nse_stock_data)}")
        return nse_stock_data

    def get_nifty_price(self, date=None):
        """Get Nifty 50 current price using Yahoo Finance"""
        if date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)
        else:
            end_date = date + timedelta(days=1)
            start_date = date - timedelta(days=5)

        try:
            data = yf.download('^NSEI', start=start_date, end=end_date, progress=False)

            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    return float(data['Close'].iloc[-1, 0])
                else:
                    return float(data['Close'].iloc[-1])
        except Exception as e:
            print(f"  ⚠️  Error fetching Nifty: {e}")

        return None


    def execute_trades(self, stocks_to_add, stocks_to_remove, current_prices):
        """Execute buy and sell trades"""
        today = datetime.now().strftime('%Y-%m-%d')
        cash_deployed = 0

        # SELL removed stocks
        for stock in stocks_to_remove:
            if stock in self.holdings_df['Stock'].values:
                holding = self.holdings_df[self.holdings_df['Stock'] == stock].iloc[0]
                shares = holding['Shares']
                price = current_prices.get(stock)

                if price:
                    gross_amount = shares * price
                    fee = gross_amount * SELL_FEE
                    net_amount = gross_amount - fee  # Money received after fee

                    # Record transaction
                    transaction = {
                        'Date': today,
                        'Stock': stock,
                        'Action': 'SELL',
                        'Shares': shares,
                        'Price': price,
                        'Gross_Amount': gross_amount,
                        'Fee': fee,
                        'Net_Amount': net_amount
                    }
                    self.transactions_df = pd.concat([
                        self.transactions_df,
                        pd.DataFrame([transaction])
                    ], ignore_index=True)

                    # Remove from holdings
                    self.holdings_df = self.holdings_df[self.holdings_df['Stock'] != stock]

                    print(f"  SOLD: {stock} - {shares:.2f} shares @ ₹{price:.2f} = ₹{net_amount:.2f} (after fee)")

        # BUY new stocks
        for stock in stocks_to_add:
            price = current_prices.get(stock)

            if price:
                # Allocate ₹10,000, but fee is deducted
                net_investment = ALLOCATION_PER_STOCK * (1 - BUY_FEE)
                shares = net_investment / price
                fee = ALLOCATION_PER_STOCK * BUY_FEE

                # Record transaction
                transaction = {
                    'Date': today,
                    'Stock': stock,
                    'Action': 'BUY',
                    'Shares': shares,
                    'Price': price,
                    'Gross_Amount': ALLOCATION_PER_STOCK,
                    'Fee': fee,
                    'Net_Amount': net_investment
                }
                self.transactions_df = pd.concat([
                    self.transactions_df,
                    pd.DataFrame([transaction])
                ], ignore_index=True)

                # Add to holdings
                new_holding = {
                    'Stock': stock,
                    'Shares': shares,
                    'Avg_Buy_Price': price,
                    'Last_Price': price,
                    'Investment': net_investment,
                    'Current_Value': net_investment,
                    'Profit_Loss_Pct': 0.0
                }
                self.holdings_df = pd.concat([
                    self.holdings_df,
                    pd.DataFrame([new_holding])
                ], ignore_index=True)

                cash_deployed += ALLOCATION_PER_STOCK

                print(f"  BOUGHT: {stock} - {shares:.2f} shares @ ₹{price:.2f} = ₹{net_investment:.2f} (fee: ₹{fee:.2f})")

        return cash_deployed

    def update_portfolio_value(self, current_prices):
        """Update portfolio value based on current prices"""
        total_value = 0
        total_investment = 0

        for idx, holding in self.holdings_df.iterrows():
            stock = holding['Stock']
            shares = holding['Shares']
            price = current_prices.get(stock, holding['Last_Price'])

            current_value = shares * price
            investment = holding['Investment']
            profit_loss_pct = ((current_value - investment) / investment) * 100

            # Update holding
            self.holdings_df.at[idx, 'Last_Price'] = price
            self.holdings_df.at[idx, 'Current_Value'] = current_value
            self.holdings_df.at[idx, 'Profit_Loss_Pct'] = profit_loss_pct

            total_value += current_value
            total_investment += investment

        return total_value, total_investment

    def run_daily_update(self):
        """Main function to run daily update"""
        print("="*60)
        print(f"Running daily update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        today = datetime.now().strftime('%Y-%m-%d')

        # Step 1: Scrape current screener stocks with prices
        print("\n1. Scraping screener...")
        screener_data = self.scrape_screener()  # Returns {ticker: price}

        if not screener_data:
            print("⚠️  No stocks found in screener. Aborting.")
            return

        # Extract tickers and prices
        current_stocks = list(screener_data.keys())
        current_prices = screener_data  # Use scraped prices directly

        # Save screener history
        screener_record = {
            'Date': today,
            'Stocks': json.dumps(current_stocks)
        }
        self.screener_history_df = pd.concat([
            self.screener_history_df,
            pd.DataFrame([screener_record])
        ], ignore_index=True)

        # Step 2: Compare with current holdings
        print("\n2. Comparing with current holdings...")
        current_holdings = set(self.holdings_df['Stock'].values)
        new_stocks_set = set(current_stocks)

        stocks_to_add = list(new_stocks_set - current_holdings)
        stocks_to_remove = list(current_holdings - new_stocks_set)

        print(f"   Current holdings: {len(current_holdings)}")
        print(f"   Screener stocks: {len(new_stocks_set)}")
        print(f"   To ADD: {len(stocks_to_add)}")
        print(f"   To REMOVE: {len(stocks_to_remove)}")

        if stocks_to_add:
            print(f"   Adding: {stocks_to_add[:5]}{'...' if len(stocks_to_add) > 5 else ''}")
        if stocks_to_remove:
            print(f"   Removing: {stocks_to_remove[:5]}{'...' if len(stocks_to_remove) > 5 else ''}")

        # Step 3: Use scraped prices (already have them!)
        print("\n3. Using prices from screener...")
        print(f"   Got prices for {len(current_prices)} stocks from screener")

        # Step 4: Execute trades
        print("\n4. Executing trades...")
        cash_deployed = self.execute_trades(stocks_to_add, stocks_to_remove, current_prices)

        # Step 5: Update portfolio value
        print("\n5. Updating portfolio value...")
        portfolio_value, total_investment = self.update_portfolio_value(current_prices)

        # Step 6: Get Nifty value
        print("\n6. Fetching Nifty 50...")
        nifty_value = self.get_nifty_price()

        # Calculate returns
        if len(self.portfolio_df) > 0:
            initial_nifty = self.portfolio_df.iloc[0]['Nifty_Value']
            nifty_return = ((nifty_value - initial_nifty) / initial_nifty * 100) if nifty_value and initial_nifty else 0
        else:
            initial_nifty = nifty_value
            nifty_return = 0

        portfolio_return = ((portfolio_value - total_investment) / total_investment * 100) if total_investment > 0 else 0
        alpha = portfolio_return - nifty_return

        # Step 7: Record portfolio value
        portfolio_record = {
            'Date': today,
            'Portfolio_Value': portfolio_value,
            'Cash_Invested': total_investment,
            'Total_Return_Pct': portfolio_return,
            'Nifty_Value': nifty_value,
            'Nifty_Return_Pct': nifty_return,
            'Alpha_Pct': alpha
        }
        self.portfolio_df = pd.concat([
            self.portfolio_df,
            pd.DataFrame([portfolio_record])
        ], ignore_index=True)

        # Step 8: Record daily changes
        changes_record = {
            'Date': today,
            'Stocks_Added': ', '.join(stocks_to_add) if stocks_to_add else 'None',
            'Stocks_Removed': ', '.join(stocks_to_remove) if stocks_to_remove else 'None',
            'Total_Holdings': len(self.holdings_df),
            'Cash_Deployed': cash_deployed
        }
        self.changes_df = pd.concat([
            self.changes_df,
            pd.DataFrame([changes_record])
        ], ignore_index=True)

        # Step 9: Save all data
        print("\n7. Saving data...")
        self.save_data()

        # Step 10: Print summary
        print("\n" + "="*60)
        print("DAILY SUMMARY")
        print("="*60)
        print(f"Portfolio Value: ₹{portfolio_value:,.2f}")
        print(f"Total Invested: ₹{total_investment:,.2f}")
        print(f"Return: {portfolio_return:+.2f}%")
        print(f"Nifty Return: {nifty_return:+.2f}%")
        print(f"Alpha: {alpha:+.2f}%")
        print(f"Holdings: {len(self.holdings_df)} stocks")
        print("="*60)

    def save_data(self):
        """Save all dataframes to CSV"""
        self.portfolio_df.to_csv(self.portfolio_file, index=False)
        self.holdings_df.to_csv(self.holdings_file, index=False)
        self.transactions_df.to_csv(self.transactions_file, index=False)
        self.changes_df.to_csv(self.changes_file, index=False)
        self.screener_history_df.to_csv(self.screener_history_file, index=False)
        print("   ✓ All data saved")

if __name__ == "__main__":
    tracker = ScreenerPortfolioTracker()
    tracker.run_daily_update()

    # Generate README
    print("\n8. Generating README...")
    try:
        from generate_readme import generate_readme
        generate_readme()
    except Exception as e:
        print(f"   ⚠️  Could not generate README: {e}")
