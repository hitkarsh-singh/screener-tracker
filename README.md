# 🤖 Automated Screener.in Portfolio Tracker

Fully automated portfolio tracking system that follows the [Market Scientist Screener](https://www.screener.in/screens/336269/market-scientist/) with daily rebalancing.

## 🎯 What This Does

- **Scrapes** the screener daily at 4 PM IST
- **Automatically buys** new stocks that enter the screener (₹10,000 per stock)
- **Automatically sells** stocks that drop out of the screener
- **Tracks** performance vs Nifty 50 benchmark
- **Records** all transactions with proper fee accounting
- **Generates** daily reports with detailed analytics

All transactions use **opening prices** and include **0.05% fees** on both buy and sell.

---

## 🚀 Quick Start

### 1. Fork This Repository

Click the "Fork" button on GitHub to create your own copy.

### 2. Enable GitHub Actions

1. Go to your forked repo
2. Click **"Actions"** tab
3. Click **"I understand my workflows, go ahead and enable them"**

### 3. Give Write Permissions

1. Go to **Settings** → **Actions** → **General**
2. Scroll to **"Workflow permissions"**
3. Select **"Read and write permissions"**
4. Click **Save**

### 4. Run Manually First Time

1. Go to **Actions** tab
2. Click **"Daily Portfolio Tracker"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 2-3 minutes for completion

### 5. Check Results

View your portfolio performance in [`README_RESULTS.md`](README_RESULTS.md)

---

## 📊 What Gets Tracked

The system creates and updates these files daily:

| File | Description |
|------|-------------|
| `data/portfolio_value.csv` | Daily portfolio value and returns |
| `data/current_holdings.csv` | Current stock positions |
| `data/transactions.csv` | All buy/sell transactions |
| `data/daily_changes.csv` | Daily portfolio changes |
| `data/screener_history.csv` | Historical screener results |
| `README_RESULTS.md` | Auto-generated performance report |

---

## 🎯 Portfolio Strategy

### Screening Criteria (from Screener.in)

- Stock price >50% above 52-week low
- Return on Equity (ROE) >15%
- Trading <25% below 52-week high
- Market cap >₹1,000 crores
- Promoter ownership >50%
- Debt-to-equity ratio <0.5
- Interest coverage ratio >3
- Positive operating cash flow
- Pledged shares <10%
- Operating profit margin >12%

### Portfolio Rules

- **₹10,000** allocated per stock (equal weight)
- **Daily rebalancing** - buy new stocks, sell removed stocks
- **CMP from screener.in** used for all transactions (live/closing price)
- **0.05% fee** on buys and sells (total 0.1% round-trip)
- **Unlimited capital** - always have ₹10k for new stocks
- **Works with NSE & BSE** stocks

### Transaction Logic

**Pricing:** Uses CMP (Current Market Price) from screener.in
- During market hours: Live current price
- After 4 PM: Closing price of the day
- Works for both NSE and BSE stocks

**When a stock is ADDED to screener:**
```
Allocation: ₹10,000
Fee (0.05%): ₹5
Net Investment: ₹9,995
Shares Bought: ₹9,995 / CMP
```

**When a stock is REMOVED from screener:**
```
Sale Value: shares × CMP
Fee (0.05%): sale_value × 0.0005
Net Proceeds: sale_value - fee
```

---

## 📅 Automation Schedule

- **Runs:** Every day at **4:00 PM IST** (10:30 AM UTC)
- **Scrapes:** Screener.in for current stocks
- **Executes:** Trades based on changes
- **Updates:** All CSV files and README
- **Commits:** Changes to GitHub automatically

You can also run manually anytime from GitHub Actions tab.

---

## 🧪 Running Locally

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tracker

```bash
python tracker.py
```

### Generate README

```bash
python generate_readme.py
```

---

## 📈 Viewing Results

### Latest Performance

Check [`README_RESULTS.md`](README_RESULTS.md) for:
- Current portfolio value
- Returns vs Nifty 50
- Top/bottom performing stocks
- Recent activity
- Complete holdings list

### Historical Data

Download CSV files from `data/` folder for analysis:
- Import into Excel/Google Sheets
- Create charts and graphs
- Perform custom analysis

### Example Analysis

```python
import pandas as pd

# Load portfolio history
df = pd.read_csv('data/portfolio_value.csv')

# Plot returns
df.plot(x='Date', y=['Total_Return_Pct', 'Nifty_Return_Pct'])
```

---

## ⚙️ Configuration

Edit `tracker.py` to customize:

```python
# Change allocation per stock
ALLOCATION_PER_STOCK = 10000  # ₹10,000 per stock

# Change fees
BUY_FEE = 0.0005   # 0.05%
SELL_FEE = 0.0005  # 0.05%

# Change screener URL
SCREENER_URL = "https://www.screener.in/screens/YOUR_SCREEN_ID/"
```

---

## 🔧 Troubleshooting

### "No stocks found in screener"

The scraper might have failed. Check if screener.in is accessible or if page structure changed.

### "Error fetching prices"

Yahoo Finance might be rate-limiting. The script will retry next day.

### "GitHub Actions not running"

1. Check Actions tab is enabled
2. Verify workflow permissions are set to "Read and write"
3. Check if cron schedule is correct for your timezone

---

## 🤝 Contributing

Feel free to:
- Report bugs via Issues
- Suggest improvements
- Submit pull requests
- Share your results

---

## ⚠️ Disclaimer

**This is a simulation for educational purposes only.**

- This tracks a **hypothetical portfolio**, not real money
- No actual trades are executed
- Past performance doesn't guarantee future results
- Not financial advice - do your own research
- The screener criteria may not be suitable for everyone

---

## 📄 License

MIT License - feel free to use and modify.

---

## 🙏 Credits

- Screener: [Screener.in](https://www.screener.in)
- Data: [Yahoo Finance](https://finance.yahoo.com)
- Automation: [GitHub Actions](https://github.com/features/actions)

---

**Star ⭐ this repo if you find it useful!**

---

## 📬 Contact

Have questions? Open an issue or discussion on GitHub.

---

*Last updated: Automated daily*
