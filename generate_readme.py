"""
Generate README with portfolio results
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")

def get_stock_display_name(ticker, stock_names_dict):
    """Get display name for stock (company name or cleaned ticker)"""
    return stock_names_dict.get(ticker, ticker.replace('.NS', ''))

def generate_readme():
    """Generate README_RESULTS.md with current portfolio status"""

    # Load data
    try:
        portfolio_df = pd.read_csv(DATA_DIR / "portfolio_value.csv")
        holdings_df = pd.read_csv(DATA_DIR / "current_holdings.csv")
        transactions_df = pd.read_csv(DATA_DIR / "transactions.csv")
        changes_df = pd.read_csv(DATA_DIR / "daily_changes.csv")

        # Load stock names mapping
        stock_names_file = DATA_DIR / "stock_names.csv"
        if stock_names_file.exists():
            names_df = pd.read_csv(stock_names_file)
            stock_names = dict(zip(names_df['Ticker'], names_df['Name']))
        else:
            stock_names = {}
    except FileNotFoundError:
        print("Data files not found. Run tracker.py first.")
        return

    # Get latest values
    if len(portfolio_df) == 0:
        print("No portfolio data yet.")
        return

    latest = portfolio_df.iloc[-1]
    first = portfolio_df.iloc[0]

    # Calculate statistics
    total_days = len(portfolio_df)
    current_value = latest['Portfolio_Value']
    invested = latest['Cash_Invested']
    returns = latest['Total_Return_Pct']
    nifty_value = latest['Nifty_Value']
    nifty_return = latest['Nifty_Return_Pct']
    alpha = latest['Alpha_Pct']

    # Count trades
    buys = len(transactions_df[transactions_df['Action'] == 'BUY'])
    sells = len(transactions_df[transactions_df['Action'] == 'SELL'])

    # Best and worst holdings
    if len(holdings_df) > 0:
        holdings_sorted = holdings_df.sort_values('Profit_Loss_Pct', ascending=False)
        best_stocks = holdings_sorted.head(5)
        worst_stocks = holdings_sorted.tail(5)
    else:
        best_stocks = pd.DataFrame()
        worst_stocks = pd.DataFrame()

    # Recent changes
    recent_changes = changes_df.tail(7) if len(changes_df) > 0 else pd.DataFrame()

    # Generate README content
    readme_content = f"""# 📊 Screener.in Portfolio Tracker

**Automated daily portfolio tracking based on [Market Scientist Screener](https://www.screener.in/screens/336269/market-scientist/)**

Last Updated: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}**

---

## 📈 Performance Summary

| Metric | Value |
|--------|-------|
| **Portfolio Value** | ₹{current_value:,.2f} |
| **Total Invested** | ₹{invested:,.2f} |
| **Returns** | **{returns:+.2f}%** |
| **Nifty 50 Closing** | {nifty_value:,.2f} |
| **Nifty 50 Returns** | {nifty_return:+.2f}% |
| **Alpha (Outperformance)** | **{alpha:+.2f}%** |
| **Current Holdings** | {len(holdings_df)} stocks |
| **Days Tracked** | {total_days} days |

---

## 💼 Current Holdings ({len(holdings_df)} stocks)

"""

    if len(holdings_df) > 0:
        readme_content += "| Stock | Shares | Buy Price | Current Price | Investment | Current Value | P/L % |\n"
        readme_content += "|-------|--------|-----------|---------------|------------|---------------|-------|\n"

        # Sort alphabetically by stock ticker
        holdings_sorted_alpha = holdings_df.sort_values('Stock')

        for _, holding in holdings_sorted_alpha.iterrows():
            stock_display = get_stock_display_name(holding['Stock'], stock_names)
            readme_content += f"| {stock_display} | {holding['Shares']:.2f} | ₹{holding['Avg_Buy_Price']:.2f} | ₹{holding['Last_Price']:.2f} | ₹{holding['Investment']:,.0f} | ₹{holding['Current_Value']:,.0f} | {holding['Profit_Loss_Pct']:+.2f}% |\n"
    else:
        readme_content += "*No holdings yet*\n"

    readme_content += f"""

---

## 🏆 Top 5 Performers

"""

    if len(best_stocks) > 0:
        readme_content += "| Rank | Stock | P/L % |\n"
        readme_content += "|------|-------|-------|\n"
        for idx, (_, stock) in enumerate(best_stocks.iterrows(), 1):
            stock_display = get_stock_display_name(stock['Stock'], stock_names)
            readme_content += f"| {idx} | {stock_display} | **{stock['Profit_Loss_Pct']:+.2f}%** |\n"
    else:
        readme_content += "*No data yet*\n"

    readme_content += f"""

## 📉 Bottom 5 Performers

"""

    if len(worst_stocks) > 0:
        readme_content += "| Rank | Stock | P/L % |\n"
        readme_content += "|------|-------|-------|\n"
        for idx, (_, stock) in enumerate(worst_stocks.iterrows(), 1):
            stock_display = get_stock_display_name(stock['Stock'], stock_names)
            readme_content += f"| {idx} | {stock_display} | {stock['Profit_Loss_Pct']:+.2f}% |\n"
    else:
        readme_content += "*No data yet*\n"

    readme_content += f"""

---

## 📅 Recent Activity (Last 7 Days)

"""

    if len(recent_changes) > 0:
        readme_content += "| Date | Added | Removed | Total Holdings | Cash Deployed |\n"
        readme_content += "|------|-------|---------|----------------|---------------|\n"
        for _, change in recent_changes.iterrows():
            added = change['Stocks_Added'] if change['Stocks_Added'] != 'None' else '-'
            removed = change['Stocks_Removed'] if change['Stocks_Removed'] != 'None' else '-'
            readme_content += f"| {change['Date']} | {added} | {removed} | {int(change['Total_Holdings'])} | ₹{change['Cash_Deployed']:,.0f} |\n"
    else:
        readme_content += "*No activity yet*\n"

    readme_content += f"""

---

## 📊 Trade Statistics

- **Total Buys:** {buys}
- **Total Sells:** {sells}
- **Net Trades:** {buys + sells}

---

## 🎯 Strategy Details

**Screening Criteria:**
- Stock price >50% above 52-week low
- ROE >15%
- Trading <25% below 52-week high
- Market cap >₹1,000 crores
- Promoter ownership >50%
- Debt-to-equity <0.5
- Interest coverage >3
- Positive operating cash flow
- Pledged shares <10%
- Operating profit margin >12%

**Portfolio Rules:**
- ₹10,000 allocation per stock
- Equal weight portfolio
- Daily rebalancing based on screener
- All transactions at opening price
- 0.05% fee on buy and sell

**Benchmark:** Nifty 50

---

## 📁 Data Files

- [`portfolio_value.csv`](data/portfolio_value.csv) - Daily portfolio value history
- [`current_holdings.csv`](data/current_holdings.csv) - Current stock holdings
- [`transactions.csv`](data/transactions.csv) - All buy/sell transactions
- [`daily_changes.csv`](data/daily_changes.csv) - Daily portfolio changes
- [`screener_history.csv`](data/screener_history.csv) - Historical screener results

---

*This portfolio is tracked automatically. Data updates daily at 4:00 PM IST.*

*⚠️ This is a simulation for educational purposes only. Not financial advice.*
"""

    # Write README
    with open('README_RESULTS.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("✓ README_RESULTS.md generated successfully")

if __name__ == "__main__":
    generate_readme()
