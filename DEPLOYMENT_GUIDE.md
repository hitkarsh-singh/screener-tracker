# 🚀 Deployment Guide

## ✅ System Successfully Built!

Your automated portfolio tracker is ready to deploy. Here's what was created:

### 📁 Project Structure

```
screener_tracker/
├── tracker.py              # Main tracking script
├── generate_readme.py      # README generator
├── requirements.txt        # Python dependencies
├── README.md              # Setup instructions
├── DEPLOYMENT_GUIDE.md    # This file
├── .gitignore             # Git ignore rules
├── .github/
│   └── workflows/
│       └── daily_tracker.yml  # GitHub Actions workflow
└── data/                  # Auto-generated data (40 stocks initially)
    ├── portfolio_value.csv
    ├── current_holdings.csv
    ├── transactions.csv
    ├── daily_changes.csv
    └── screener_history.csv
```

### ✅ Test Results

**Initial Run Successful!**
- ✅ Scraped 48 stocks from screener (40 with valid data)
- ✅ Bought 40 stocks at ₹10,000 each
- ✅ Total portfolio value: **₹399,800**
- ✅ All CSV files created
- ✅ README generated successfully

---

## 📋 Deployment Steps

### Step 1: Create GitHub Repository

1. Go to GitHub.com
2. Click **"New Repository"**
3. Name it: `screener-portfolio-tracker`
4. Make it **Public** (required for free GitHub Actions)
5. **Don't** initialize with README (we have our own)
6. Click **"Create repository"**

### Step 2: Push Code to GitHub

```bash
cd /Users/hitkarsh/screener_tracker

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Automated screener portfolio tracker"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/screener-portfolio-tracker.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **"Actions"** tab
3. Click **"I understand my workflows, go ahead and enable them"**

### Step 4: Set Permissions

1. Go to **Settings** → **Actions** → **General**
2. Scroll to **"Workflow permissions"**
3. Select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

### Step 5: Run First Time Manually

1. Go to **Actions** tab
2. Click **"Daily Portfolio Tracker"** workflow
3. Click **"Run workflow"** dropdown
4. Click green **"Run workflow"** button
5. Wait 2-3 minutes
6. Check for green checkmark ✅

### Step 6: Verify Results

1. Go to repository home page
2. Click **"README_RESULTS.md"** to see portfolio
3. Check **"data/"** folder for CSV files

---

## 🎉 You're Done!

The system will now:
- ✅ Run automatically at **4:00 PM IST** every day
- ✅ Scrape the screener
- ✅ Buy new stocks / Sell removed stocks
- ✅ Update all CSV files
- ✅ Generate new README with results
- ✅ Commit changes to GitHub

---

## 📊 How to View Results

### Daily Portfolio Summary
Open [`README_RESULTS.md`](README_RESULTS.md) in your repo to see:
- Current portfolio value
- Returns vs Nifty 50
- Top/bottom performers
- Recent changes
- Complete holdings list

### Historical Data Analysis

**Download CSV files:**
1. Go to `data/` folder
2. Click any CSV file
3. Click **"Download"** or **"Raw"**
4. Import into Excel/Google Sheets

**Example: Plot returns over time**
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/portfolio_value.csv')
df.plot(x='Date', y=['Total_Return_Pct', 'Nifty_Return_Pct'])
plt.title('Portfolio vs Nifty 50')
plt.show()
```

---

## 🔧 Common Issues & Solutions

### Issue: Workflow doesn't run

**Solution:**
- Check Actions tab is enabled
- Verify workflow permissions are "Read and write"
- Check if repo is public (private repos have limited free Actions)

### Issue: "No stocks found in screener"

**Solution:**
- Screener.in might be blocking automated access
- Page structure might have changed
- Try running manually again later
- Check if screener URL is still valid

### Issue: Some stocks fail to fetch prices

**Solution:**
- Normal - some stocks might be newly listed or delisted
- System continues with stocks that have valid data
- Check `transactions.csv` to see which stocks were skipped

### Issue: Workflow runs but doesn't commit

**Solution:**
- Verify workflow permissions include write access
- Check if there were actual changes to commit
- Review workflow run logs in Actions tab

---

## 🎯 What Happens Next

### Daily (Automatic at 4 PM IST):
1. Scraper runs and gets current screener stocks
2. Compares with yesterday's holdings
3. Sells stocks that dropped from screener
4. Buys stocks newly added to screener
5. Updates portfolio value using opening prices
6. Records everything in CSV files
7. Generates updated README
8. Commits changes to GitHub

### You Can:
- Check README_RESULTS.md anytime for latest results
- Download CSV files for custom analysis
- Run workflow manually from Actions tab
- Modify settings in tracker.py if needed

---

## 📈 Expected Results

Based on backtest (Feb 2023 - Feb 2024):
- **Portfolio Return:** ~80%
- **Nifty 50 Return:** ~23%
- **Outperformance:** ~57%

*Note: Past performance doesn't guarantee future results*

---

## 🔄 Manual Updates

If you want to run the tracker manually on your computer:

```bash
cd screener_tracker

# Install dependencies (first time only)
pip install -r requirements.txt

# Run tracker
python tracker.py

# View results
cat README_RESULTS.md
```

---

## 🎊 Success Checklist

- [ ] Code pushed to GitHub
- [ ] GitHub Actions enabled
- [ ] Workflow permissions set to "Read and write"
- [ ] First manual run completed successfully
- [ ] README_RESULTS.md shows portfolio data
- [ ] CSV files created in data/ folder
- [ ] Workflow scheduled for daily 4 PM IST

---

## 📞 Support

If you encounter issues:
1. Check the workflow run logs in GitHub Actions
2. Review the error messages
3. Verify all permissions are set correctly
4. Try running manually first

---

## 🎯 Next Steps

1. **Monitor for a week** to ensure automation works
2. **Review results** to see portfolio changes
3. **Analyze data** in CSV files
4. **Compare** with Nifty 50 performance
5. **Share** your results if you'd like!

---

**Your automated portfolio tracker is live! 🎉**

*The system will now track the Market Scientist screener strategy automatically every day.*
