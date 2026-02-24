# 👋 Welcome to Price Comparison System!

## What is this?

This is a smart shopping tool that **automatically compares prices** for the same products across **Amazon** and **Flipkart**, then tells you which one is cheaper and why.

### In 30 seconds:
1. You search for a product (e.g., "iPhone 15")
2. The system finds it on both Amazon and Flipkart
3. It compares prices, ratings, and reviews
4. It recommends the better deal
5. Results are saved to an Excel file

**That's it!** 🎉

---

## Quick Start (5 minutes)

### Step 1: Install
```bash
pip install -r requirements.txt
```

### Step 2: Run
```bash
python main.py
```

### Step 3: Search
```
Enter product name: iPhone 15
```

### Step 4: Get Results
```
Amazon:   ₹52,990
Flipkart: ₹51,000
Better Deal: Flipkart (3.7% cheaper)
```

**Done!** Check `output/product_comparison.xlsx` for the full report.

---

## Features at a Glance

✅ **Smart Matching**
- Finds the same product on both platforms
- Matches by brand, storage, color, and size
- Won't compare iPhone 128GB with 512GB

✅ **Price Comparison**
- Shows current prices from both platforms
- Calculates percentage savings
- Recommends cheaper option

✅ **Rating & Reviews**
- Compares customer ratings
- Shows number of reviews
- Helps you make informed decisions

✅ **Excel Reports**
- Automatically creates Excel file
- Professional formatting
- Easy to share

✅ **Database Storage**
- Saves products for quick lookup
- Second search is instant
- Build your shopping history

---

## What Can You Do?

### Search for Products
```
✓ Smartphones (iPhone, Samsung, OnePlus)
✓ Laptops (HP, Dell, Lenovo)
✓ Beauty Products (Moisturizers, Lipsticks)
✓ Clothing (T-shirts, Tank tops)
✓ Electronics (Headphones, Speakers)
✓ And much more!
```

### Get Recommendations
The system recommends based on:
- Price (most important)
- Customer Rating
- Number of Reviews

### Track Comparisons
All comparisons are saved to:
- `database/price_comparison.db` (SQLite)
- `output/product_comparison.xlsx` (Excel)

---

## Where to Go Next?

### Want to start immediately?
👉 Run: `python main.py`

### Want quick instructions?
👉 Read: `QUICKSTART.md` (5 minutes)

### Want full documentation?
👉 Read: `README.md` (30 minutes)

### Want to understand the code?
👉 Read: `PROJECT_STRUCTURE.md`

### Need help setting up?
👉 Read: `INSTALLATION.md`

### Want to see examples?
👉 Run: `python examples.py`

### Want a complete guide?
👉 Read: `INDEX.md`

---

## System Requirements

- **Python**: 3.7 or higher
- **Internet**: Required for web scraping
- **Storage**: ~10 MB for database and logs
- **Time**: 5-10 seconds per search (web scraping)

---

## How It Works (Technical Overview)

```
You Search for "iPhone 15"
        ↓
System scrapes Amazon.in
        ↓
System scrapes Flipkart.com
        ↓
Intelligently matches products
        ↓
Extracts prices, ratings, reviews
        ↓
Compares and recommends
        ↓
Saves to database
        ↓
Updates Excel file
        ↓
Shows results to you
```

---

## Common Questions

**Q: Is it free?**
A: Yes, completely free and open source!

**Q: Is it safe?**
A: Yes, it uses official public websites. No passwords needed.

**Q: Will it harm my computer?**
A: No, it's just a Python application that reads websites.

**Q: Can I modify it?**
A: Yes! All source code is yours. Customize as you wish.

**Q: Can I add more websites?**
A: Yes! Follow the PROJECT_STRUCTURE.md guide to add more platforms.

**Q: How often does it update prices?**
A: Prices are current at the time of your search.

---

## Troubleshooting

### Problem: "ModuleNotFoundError"
**Solution:** Run `pip install -r requirements.txt`

### Problem: "No products found"
**Solution:** Check spelling, or try a different product name

### Problem: Slow searches
**Solution:** First search is slow (web scraping). Repeat searches are instant!

### Problem: Excel file not updating
**Solution:** Close Excel if it's open, then try again

---

## Next Steps

### Right Now:
1. Open PowerShell or Terminal
2. Navigate to project folder
3. Run: `pip install -r requirements.txt`
4. Run: `python main.py`
5. Search for a product
6. Done! 🎉

### Next: 
Read `QUICKSTART.md` for more details

### After That:
Read `README.md` for complete documentation

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Run this to start |
| `README.md` | Complete documentation |
| `QUICKSTART.md` | 5-minute setup guide |
| `requirements.txt` | Install dependencies |
| `database/` | Your data storage |
| `output/` | Excel reports folder |
| `logs/` | Application logs |

---

## Important Note

This application scrapes public websites. It's designed for personal use. Always:
- Respect website terms of service
- Don't overload servers
- Use reasonable delays between searches
- Check website policies

---

## Support

If something doesn't work:
1. Check `logs/app.log` for errors
2. Read `INSTALLATION.md` for setup help
3. Read `README.md` for features help
4. Check `INDEX.md` for more documentation

---

## You're Ready!

Everything is installed and ready to use. Just run:

```bash
python main.py
```

**Happy shopping! 🛒**

---

**Created:** December 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
