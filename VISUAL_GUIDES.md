# 📊 Visual Guides & Diagrams

Visual representations of how the system works.

---

## Application Flow Diagram

```
┌────────────────────────────────────────────────────────┐
│                    USER STARTS APP                     │
│                   python main.py                       │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   SHOW MAIN MENU            │
        │ 1. Search & Compare         │
        │ 2. View All Products        │
        │ 3. Clear Database           │
        │ 4. Exit                     │
        └─────────────┬───────────────┘
                      │
        ┌─────────────┴──────────────────────┐
        │                                    │
        ▼                                    ▼
    USER CHOICE 1                      OTHER OPTIONS
    SEARCH PRODUCT                     (View/Clear/Exit)
        │                                    │
        ├─ Check Database                   │
        │  (Is product cached?)              │
        │                                    │
        ├─ NO? Scrape both websites:        │
        │  ├─ Amazon Scraper                │
        │  │  └─ Parse 5 products           │
        │  └─ Flipkart Scraper              │
        │     └─ Parse 5 products           │
        │                                   │
        ├─ Save to Database                 │
        │                                   │
        ├─ Match products intelligently     │
        │  └─ Compare storage/color/size    │
        │                                   │
        ├─ Compare & recommend              │
        │  └─ Calculate price difference    │
        │                                   │
        ├─ Generate Excel report            │
        │                                   │
        └─ Display results to user          │
             │                              │
             └─ BACK TO MENU ──────────────┘
```

---

## Product Matching Algorithm

```
SEARCH FOR: "iPhone 15 128GB"
│
├─ EXTRACT: "iPhone 15" (name), "128" (storage), "" (color)
│
├─ AMAZON RESULTS:
│  ├─ iPhone 15 128GB Black
│  ├─ iPhone 15 256GB Blue
│  └─ iPhone 15 512GB Gold
│
├─ FLIPKART RESULTS:
│  ├─ iPhone 15 128GB Black
│  └─ iPhone 15 256GB Green
│
├─ SCORE ALL COMBINATIONS (3 × 2 = 6 pairs):
│
│  Pair 1: Amazon 128GB Black + Flipkart 128GB Black
│  ├─ Storage match? YES ✓ (+10 points)
│  ├─ Color match? YES ✓ (+5 points)
│  ├─ Name match? YES ✓ (+1 point)
│  └─ TOTAL SCORE: 16 ⭐⭐⭐⭐⭐
│
│  Pair 2: Amazon 128GB Black + Flipkart 256GB Green
│  ├─ Storage match? NO ✗ (Skip this pair)
│  └─ TOTAL SCORE: Invalid
│
│  Pair 3: Amazon 256GB Blue + Flipkart 128GB Black
│  ├─ Storage match? NO ✗ (Skip this pair)
│  └─ TOTAL SCORE: Invalid
│
│  (Continue for all pairs...)
│
├─ SELECT: Pair 1 (highest score)
│
└─ RETURN: (Amazon 128GB Black, Flipkart 128GB Black)
```

---

## Data Flow Diagram

```
                    ┌─────────────┐
                    │   USER      │
                    │ (Searching) │
                    └──────┬──────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  main.py     │
                    │ (Orchestrate)│
                    └──────┬───────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
                ▼          ▼          ▼
          ┌────────┐  ┌───────────┐  ┌──────────┐
          │Database│  │  Scrapers │  │  Utils   │
          │ SQLite │  │ Amazon &  │  │ Matching │
          │        │  │ Flipkart  │  │ Compare  │
          └────────┘  └───────────┘  └──────────┘
                │          │              │
                └──────────┼──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │Excel Reporter│
                    │(Generate .xlsx)│
                    └────────┬─────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │RESULTS DISPLAYED │
                    │  & SAVED TO:     │
                    │  • database/     │
                    │  • output/       │
                    │  • logs/         │
                    └──────────────────┘
```

---

## Database Structure

```
PRICE COMPARISON DATABASE
│
├─ amazon_products TABLE
│  │
│  ├─ id (Primary Key)
│  ├─ product_name (TEXT)
│  ├─ price (REAL)
│  ├─ rating (REAL)
│  ├─ review_count (INTEGER)
│  ├─ url (TEXT, UNIQUE)
│  ├─ search_query (TEXT)
│  └─ last_updated (DATETIME)
│
└─ flipkart_products TABLE
   │
   ├─ id (Primary Key)
   ├─ product_name (TEXT)
   ├─ price (REAL)
   ├─ rating (REAL)
   ├─ review_count (INTEGER)
   ├─ url (TEXT, UNIQUE)
   ├─ search_query (TEXT)
   └─ last_updated (DATETIME)
```

---

## Comparison Algorithm

```
AMAZON PRODUCT          FLIPKART PRODUCT
│                       │
├─ Price: ₹52,990       ├─ Price: ₹51,000
├─ Rating: 4.5          ├─ Rating: 4.3
└─ Reviews: 5000        └─ Reviews: 3000

                ▼

         COMPARISON SCORES
         
    Price Score:      Flipkart wins (Lower) ← 2 points
    Rating Score:     Amazon wins (Higher)   ← 1 point
    Review Score:     Amazon wins (More)     ← 1 point
    
         Total: Flipkart = 2, Amazon = 2
         
         RESULT: Similar Quality
         
         BUT: Flipkart is ₹1,990 cheaper (3.75%)
         
         ▼
         
      RECOMMENDATION
      
         "Buy from Flipkart"
         
         Reasons:
         ✓ Cheaper by 3.75%
         ✓ Similar rating
         ✓ Fewer reviews (but acceptable)
```

---

## Menu Flow Chart

```
                    START
                      │
                      ▼
            ┌─────────────────────┐
            │   MAIN MENU         │
            │ 1. Search & Compare │
            │ 2. View Products    │
            │ 3. Clear Database   │
            │ 4. Exit             │
            └──────────┬──────────┘
                       │
        ┌──────┬───────┼───────┬──────┐
        │      │       │       │      │
        ▼      ▼       ▼       ▼      ▼
      (1)    (2)     (3)     (4)   Invalid
        │      │       │       │      │
        ▼      ▼       ▼       ▼      ▼
       Get    View   Clear   Exit   Error
      Input  Data   Data     │      Loop
        │      │      │       │      │
        ▼      ▼      ▼       ▼      │
     Search  Show   Delete  Close   │
      Web    All    All      App    │
       │      │      │               │
       └──────┴──────┴───────────────┘
              │
              ▼
        Back to Menu
```

---

## Web Scraping Process

```
SEARCH FOR: "iPhone 15"
│
├─ AMAZON SCRAPING:
│  │
│  ├─ 1. Create HTTP Request
│  │   └─ URL: https://www.amazon.in/s?k=iPhone+15
│  │
│  ├─ 2. Send Request with User-Agent
│  │   └─ "Mozilla/5.0..."
│  │
│  ├─ 3. Receive HTML Response
│  │   └─ 250KB+ of HTML
│  │
│  ├─ 4. Parse HTML with BeautifulSoup
│  │   └─ Find product containers
│  │
│  ├─ 5. Extract Data
│  │   ├─ Product Name (from title attribute)
│  │   ├─ Price (from price span)
│  │   ├─ Rating (from rating element)
│  │   ├─ Reviews (from review count)
│  │   └─ URL (from product link)
│  │
│  ├─ 6. Clean Data
│  │   ├─ Convert "₹10,000" → 10000.0
│  │   ├─ Convert "1.5K" → 1500
│  │   └─ Remove HTML entities
│  │
│  ├─ 7. Filter Results
│  │   └─ Keep only products matching "iPhone" AND "15"
│  │
│  └─ 8. Return: 5 products (best matches)
│
└─ FLIPKART SCRAPING: (Same process)
   └─ Return: 3-5 products
```

---

## File Generation Timeline

```
START: python main.py
│
├─ T+0.1s: Load config.py
│          Load database.py
│
├─ T+0.2s: Check if database exists
│          └─ If not: Create database/price_comparison.db
│
├─ T+0.5s: User enters search
│
├─ T+0.6s: Search database
│          └─ If found: Use cache (instant)
│          └─ If not found: Scrape websites (5-10 seconds)
│
├─ T+5-10s: Scraping complete
│           Data saved to database
│
├─ T+10.1s: Create/Update Excel
│           └─ output/product_comparison.xlsx
│
├─ T+10.2s: Create logs
│           └─ logs/app.log (if not exists)
│
└─ T+10.3s: Display results

FILES CREATED/MODIFIED:
├─ database/price_comparison.db      ✓ Created (once)
├─ output/product_comparison.xlsx    ✓ Created/Updated
├─ logs/app.log                      ✓ Created/Updated
└─ Various temp files                (Cleaned automatically)
```

---

## Comparison Result Breakdown

```
SEARCH RESULTS:
┌──────────────────────────────────┐
│   AMAZON PRODUCT DATA            │
├──────────────────────────────────┤
│ Name:  Apple iPhone 15 128GB     │
│ Price: ₹52,990                   │
│ Rating: 4.5 stars                │
│ Reviews: 5000                     │
│ URL: https://amazon.in/...       │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│  FLIPKART PRODUCT DATA           │
├──────────────────────────────────┤
│ Name:  Apple iPhone 15 128GB     │
│ Price: ₹51,000                   │
│ Rating: 4.3 stars                │
│ Reviews: 3000                     │
│ URL: https://flipkart.com/...    │
└──────────────────────────────────┘

ANALYSIS:
┌──────────────────────────────────┐
│   PRICE COMPARISON               │
├──────────────────────────────────┤
│ Amazon:   ₹52,990                │
│ Flipkart: ₹51,000                │
│ Difference: ₹1,990 (3.75%)        │
│ Better Deal: Flipkart ✓           │
└──────────────────────────────────┘

RECOMMENDATION:
┌──────────────────────────────────┐
│  SUGGESTED ACTION                │
├──────────────────────────────────┤
│ Buy from: FLIPKART               │
│ Save: ₹1,990                     │
│ Rating: Slightly lower (acceptable) │
│ Action: Click link below to buy  │
└──────────────────────────────────┘
```

---

## Module Dependency Diagram

```
                    main.py
                   (Driver)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    amazon_scraper flipkart_scraper database.py
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────┼─────────────────┐
        │             │                 │
        ▼             ▼                 ▼
      config.py    utils.py        excel_reporter.py
        (Global)  (Helpers)         (Reports)
```

---

## Search Speed Comparison

```
FIRST SEARCH: "iPhone 15"
├─ Database Lookup: < 0.1 seconds
├─ Not found, start scraping
├─ Amazon Scraping: 3-5 seconds
├─ Flipkart Scraping: 2-4 seconds
├─ Matching Algorithm: < 0.1 seconds
├─ Database Save: 0.2 seconds
├─ Excel Generation: 0.5 seconds
└─ TOTAL: 5-10 seconds ⏱️

SECOND SEARCH: "iPhone 15" (same product)
├─ Database Lookup: < 0.1 seconds
├─ Found in cache! ✓
└─ TOTAL: < 0.5 seconds ⏱️ (20x faster!)

THIRD SEARCH: "Samsung S23" (different product)
├─ Database Lookup: < 0.1 seconds
├─ Not found, start scraping
├─ Scraping: 5-10 seconds
└─ TOTAL: 5-10 seconds ⏱️
```

---

## Error Handling Flow

```
OPERATION STARTS
│
├─ Try: Execute
│   └─ Success? → Continue
│
├─ Catch: ConnectionError
│   ├─ Log error to logs/app.log
│   ├─ Retry (up to 3 times)
│   ├─ Still failing? Show user message
│   └─ Return: Previous data or empty
│
├─ Catch: TimeoutError
│   ├─ Log to logs/app.log
│   ├─ Increase timeout
│   ├─ Retry
│   └─ Return: Available data
│
├─ Catch: Database Error
│   ├─ Log to logs/app.log
│   ├─ Try to recover
│   ├─ If fails: Clear database
│   └─ Return: Error message
│
└─ Finally: Clean up
   ├─ Close connections
   ├─ Release locks
   └─ Log completion
```

---

## Excel Report Structure

```
product_comparison.xlsx

┌─────────────────────────────────────────────────────────┐
│  HEADER ROW (Blue background, white text, bold)         │
├─────────────────────────────────────────────────────────┤
│Product│Amazon│Flipkart│Amazon│Flipkart│Amazon│Flipkart││
│ Name  │Price │ Price  │Rating│ Rating │ Rev  │  Rev   ││
├─────────────────────────────────────────────────────────┤
│ DATA ROWS (Alternating gray/white background)           │
├─────────────────────────────────────────────────────────┤
│iPhone15│₹52990│ ₹51000 │ 4.5  │  4.3   │ 5000 │ 3000   │
├─────────────────────────────────────────────────────────┤
│HP Laptop│₹24999│ ₹31740 │ 4.0  │  4.0   │ 100  │  20    │
├─────────────────────────────────────────────────────────┤
│Aquaphor│ ₹2699│ ₹2436  │ N/A  │  4.0   │ 200  │  0     │
└─────────────────────────────────────────────────────────┘

CONTINUATION (columns 8-11):
├─────────────────────────────────────────────────────────┐
│Better │Cheaper│Amazon URL│Flipkart URL│(Hyperlinks)    │
│ Deal  │  By % │ (Link)   │  (Link)     │                │
├─────────────────────────────────────────────────────────┤
│Flipkart│ 3.75% │ Link     │ Link        │ (Clickable)   │
├─────────────────────────────────────────────────────────┤
│ Amazon │ 21.24%│ Link     │ Link        │ (Clickable)   │
├─────────────────────────────────────────────────────────┤
│Flipkart│ 9.74% │ Link     │ Link        │ (Clickable)   │
└─────────────────────────────────────────────────────────┘
```

---

## System Architecture (High Level)

```
USER INTERFACE (CLI Menu)
         ↓
  BUSINESS LOGIC (main.py)
         ↓
  ┌──────┴──────┬──────────────┬────────────┐
  ↓             ↓              ↓            ↓
WEB SCRAPING  DATABASE    COMPARISON   REPORTING
(Scrapers)    (SQLite)     (Utils)      (Excel)
```

---

## Memory & Storage Usage

```
TYPICAL USAGE:

Application Size:
├─ Python files: 500 KB
├─ Dependencies: 50 MB
└─ Total: ~51 MB

Runtime Memory:
├─ Idle: 50 MB
├─ During scraping: 150 MB
├─ Peak: 200 MB
└─ Returns to idle after operation

Database Size:
├─ Initial: 100 KB
├─ After 10 products: 500 KB
├─ After 100 products: 2 MB
└─ Scales linearly

Excel File Size:
├─ Empty: 10 KB
├─ 10 products: 50 KB
├─ 100 products: 200 KB
└─ Professional formatting included
```

---

**Visual guides complete!** These diagrams help visualize:
- Application flow
- Data movement
- Matching algorithm
- File generation
- System architecture

---

**Version:** 1.0  
**Status:** Complete ✅
