# ⚡ Quick Start Guide (5 Minutes)

Get up and running in 5 minutes!

---

## Step 1: Install Dependencies (2 minutes)

Open PowerShell/Terminal and run:

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - Download web pages
- `beautifulsoup4` - Parse HTML
- `openpyxl` - Create Excel files

**✓ Done!**

---

## Step 2: Run the Application (1 minute)

```bash
python main.py
```

You'll see the menu:
```
================================================================================
PRICE COMPARISON SYSTEM - AMAZON vs FLIPKART
================================================================================

MENU:
1. Search & Compare Product
2. View All Products in Database
3. Clear Database
4. Exit

Enter your choice (1-4):
```

**✓ Ready!**

---

## Step 3: Search for a Product (1 minute)

Type `1` and press Enter:
```
Enter your choice (1-4): 1
Enter product name to search: iPhone 15
```

**System will:**
1. Scrape Amazon.in
2. Scrape Flipkart.com
3. Find matching products
4. Compare prices
5. Show results
6. Save to Excel

---

## Step 4: View Results (1 minute)

You'll see something like:

```
================================================================================
PRODUCT COMPARISON RESULTS
================================================================================

AMAZON:
  Product:      Apple iPhone 15 (128 GB) - Black
  Price:        ₹52,990
  Rating:       4.5 stars
  Reviews:      5000
  URL:          https://www.amazon.in/...

FLIPKART:
  Product:      Apple iPhone 15 (128 GB) - Blue
  Price:        ₹51,000
  Rating:       4.3 stars
  Reviews:      3000
  URL:          https://www.flipkart.com/...

COMPARISON & RECOMMENDATION:
  Cheaper Deal: Flipkart
  Cheaper By:   3.75%
  Better Rating: Amazon
  More Reviews: Amazon

  RECOMMENDATION: Buy from Flipkart
```

**✓ You got your comparison!**

---

## Step 5: Check Excel File (Optional)

Go to: `output/product_comparison.xlsx`

Your Excel file automatically includes:
- Product names
- Amazon prices
- Flipkart prices
- Ratings
- Review counts
- Links to both products
- Recommendations

---

## Common Searches to Try

### Electronics
```
✓ iPhone 15
✓ HP Laptop
✓ Samsung Phone
✓ Wireless Earbuds
```

### Beauty/Personal Care
```
✓ Aquaphor Moisturizer
✓ Sunscreen SPF 50
✓ Lipstick
✓ Face Wash
```

### Clothing
```
✓ Tank Top
✓ Jeans
✓ T-Shirt
✓ Running Shoes
```

---

## Menu Options Explained

### 1. Search & Compare Product
- Enter any product name
- System finds it on both platforms
- Shows comparison
- Saves to Excel automatically

### 2. View All Products in Database
- Shows all products you've searched before
- Shows Amazon and Flipkart listings
- Shows when you last searched

### 3. Clear Database
- Deletes all stored products
- Useful for fresh start
- Warning: This removes all saved data!

### 4. Exit
- Closes application
- Saves everything automatically
- Database is persistent

---

## Tips for Better Results

✅ **Be specific**
```
GOOD:  "iPhone 15 128GB"
BAD:   "Phone"

GOOD:  "HP Pavilion 14 inch Laptop"
BAD:   "Laptop"
```

✅ **Include key details**
```
GOOD:  "Aquaphor 14 oz healing ointment"
BAD:   "Aquaphor"
```

✅ **Use common product names**
```
GOOD:  "Samsung Galaxy S23"
BAD:   "Latest Samsung phone"
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'requests'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No products found"
**Causes:**
- Typo in product name
- Product not available on both platforms
- Website structure changed

**Solution:**
- Check spelling
- Try a different product
- Wait a minute (site might be slow)

### Issue: Slow first search
**Reason:** Web scraping takes 5-10 seconds first time

**Solution:** 
- Be patient
- Second search of same product is instant (uses cache)

### Issue: "ConnectionError"
**Cause:** Internet connection issue

**Solution:**
- Check internet connection
- Verify website is accessible
- Try again in a moment

---

## What Gets Created

After your first search:

```
📁 database/
   └── price_comparison.db     (Your product database)

📁 output/
   └── product_comparison.xlsx (Your Excel report)

📁 logs/
   └── app.log                 (Application logs)
```

---

## Understanding Results

### Price Comparison
```
Amazon: ₹10,000
Flipkart: ₹9,500

Cheaper By: 5%
Recommendation: Buy from Flipkart
```

### Rating Comparison
```
Amazon: 4.5 stars (5000 reviews)
Flipkart: 4.3 stars (3000 reviews)

Better Rating: Amazon
More Reviews: Amazon
```

### Overall Recommendation
The system recommends based on:
1. **Price** (most important)
2. **Rating** (important)
3. **Review count** (helpful)

---

## Advanced: View Your Database

See all products you've searched:

```
1. Choose option 2: "View All Products in Database"
2. See all Amazon products
3. See all Flipkart products
```

---

## Advanced: Clear Everything

Start fresh:

```
1. Choose option 3: "Clear Database"
2. Confirm the deletion
3. Database is cleared
4. Excel file is reset
```

**⚠️ Warning:** This deletes all saved data!

---

## Next Steps

### After first search:
✓ Read `README.md` for full features
✓ Try more products
✓ Check Excel file

### To understand the code:
✓ Read `PROJECT_STRUCTURE.md`
✓ Read `examples.py`
✓ Explore source files

### To see working examples:
✓ Run: `python examples.py`

---

## Pro Tips

💡 **Tip 1:** Database caches products
- First search: 5-10 seconds (web scraping)
- Repeat search: <1 second (database)

💡 **Tip 2:** Search for exact products
- "iPhone 15 128GB Black" is better than "iPhone"
- More specific = better matches

💡 **Tip 3:** Check the Excel file
- Professional formatting
- Easy to share with friends
- Direct links to products

💡 **Tip 4:** Use for shopping decisions
- Compare before buying
- Check ratings
- See reviews
- Make informed choices

---

## You're All Set! 🎉

Everything is ready. Just run:

```bash
python main.py
```

Then:
1. Press `1` to search
2. Enter product name
3. Get comparison
4. Check Excel file

**Done!** That's all you need to know to get started.

---

## Need More Help?

- **Full Documentation:** Read `README.md`
- **Architecture Guide:** Read `PROJECT_STRUCTURE.md`
- **Setup Issues:** Read `INSTALLATION.md`
- **See Examples:** Run `python examples.py`
- **Complete Navigation:** Read `INDEX.md`

---

**Happy shopping! 🛒**

**Version:** 1.0  
**Status:** Ready to Use ✅
