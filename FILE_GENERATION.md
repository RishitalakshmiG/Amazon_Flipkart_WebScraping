# 📁 File Generation & Management Guide

What files are created and where they're stored.

---

## File Creation Timeline

```
WHEN: python main.py
├─ T+0.1s: Application starts
│
├─ T+0.2s: Load configuration
│   └─ Read config.py
│
├─ T+0.3s: Check databases directory
│   ├─ If not exists: Create ./database/
│   └─ If exists: Use existing
│
├─ T+0.4s: Check/Create database file
│   ├─ If not exists: Create database/price_comparison.db
│   └─ If exists: Connect to existing
│
├─ T+0.5s: Check output directory
│   ├─ If not exists: Create ./output/
│   └─ If exists: Use existing
│
├─ T+0.6s: Check logs directory
│   ├─ If not exists: Create ./logs/
│   └─ If exists: Use existing
│
├─ T+0.7s: Initialize logging
│   ├─ If not exists: Create logs/app.log
│   └─ If exists: Append to existing
│
└─ T+1.0s: Application ready for use
   └─ Show main menu
```

---

## Directory Structure Created

When you first run `python main.py`, these directories are created:

```
amazon_flipkart/
│
├─ database/                    ← CREATED (if not exists)
│  └─ price_comparison.db       ← CREATED (if not exists)
│
├─ output/                      ← CREATED (if not exists)
│  └─ product_comparison.xlsx   ← CREATED on first search
│
└─ logs/                        ← CREATED (if not exists)
   └─ app.log                   ← CREATED automatically
```

---

## File Descriptions

### Database Files

#### database/price_comparison.db
- **What:** SQLite database file
- **Size:** Starts ~100 KB, grows with data
- **Created:** Automatically on first run
- **Contains:** Two tables (amazon_products, flipkart_products)
- **Format:** Binary (not human-readable)
- **Backup:** Can copy to backup location

**Table 1: amazon_products**
```
id              | product_name        | price | rating | review_count | url | search_query | last_updated
────────────────────────────────────────────────────────────────────────────────────────────────────────
1               | Apple iPhone 15     | 52990 | 4.5    | 5000         | ... | iPhone 15    | 2025-12-13...
2               | Samsung Galaxy S23  | 45000 | 4.3    | 3000         | ... | Samsung S23  | 2025-12-13...
```

**Table 2: flipkart_products**
```
id              | product_name        | price | rating | review_count | url | search_query | last_updated
────────────────────────────────────────────────────────────────────────────────────────────────────────
1               | Apple iPhone 15     | 51000 | 4.0    | 2000         | ... | iPhone 15    | 2025-12-13...
2               | Samsung Galaxy S23  | 43000 | 4.5    | 4000         | ... | Samsung S23  | 2025-12-13...
```

### Excel Files

#### output/product_comparison.xlsx
- **What:** Excel spreadsheet with comparisons
- **Size:** Starts ~10 KB, grows with data
- **Created:** On first product search
- **Format:** Excel 2007+ (.xlsx)
- **Updated:** Every search
- **Can be opened in:**
  - Microsoft Excel
  - Google Sheets
  - OpenOffice Calc
  - LibreOffice

**Excel Structure:**
```
Row 1: Headers (Blue background)
Row 2: First product comparison
Row 3: Second product comparison
...
```

**Columns:**
1. Product Name
2. Amazon Price
3. Flipkart Price
4. Amazon Rating
5. Flipkart Rating
6. Amazon Reviews
7. Flipkart Reviews
8. Better Deal (recommendation)
9. Cheaper By % (savings percentage)
10. Amazon URL (clickable link)
11. Flipkart URL (clickable link)

### Log Files

#### logs/app.log
- **What:** Application activity log
- **Size:** Grows with usage (typically 1-5 MB)
- **Created:** Automatically on first run
- **Format:** Plain text
- **Contains:**
  - All searches performed
  - Database operations
  - Web scraping activities
  - Errors and warnings
  - Timestamps

**Log Example:**
```
2025-12-13 13:50:03,461 - amazon_scraper - INFO - Searching Amazon for: iPhone 15
2025-12-13 13:50:05,406 - main - INFO - Best match score: 10
2025-12-13 13:50:05,421 - database - INFO - Inserted Amazon product
2025-12-13 13:50:05,426 - database - INFO - Inserted Flipkart product
```

---

## File Sizes

### Initial Installation
```
Source code:          ~50 KB
Documentation:        ~200 KB
Total before first run: ~250 KB
```

### After First Search
```
database/price_comparison.db: ~150 KB
output/product_comparison.xlsx: ~20 KB
logs/app.log: ~5 KB
Total: ~175 KB
```

### After 100 Searches
```
database/price_comparison.db: ~2 MB
output/product_comparison.xlsx: ~500 KB
logs/app.log: ~5 MB
Total: ~7.5 MB
```

---

## File Management

### Viewing Files

**Database (sqlite3 tool):**
```bash
# Windows
sqlite3 database/price_comparison.db

# Command inside sqlite3:
.tables
SELECT * FROM amazon_products;
.quit
```

**Excel:**
```bash
# Windows
start output/product_comparison.xlsx

# macOS
open output/product_comparison.xlsx

# Linux
libreoffice output/product_comparison.xlsx
```

**Logs:**
```bash
# View last 50 lines
tail -50 logs/app.log

# Search for errors
grep ERROR logs/app.log

# Search for specific product
grep "iPhone" logs/app.log
```

### Backing Up Files

**Backup Database:**
```bash
# Windows
copy database\price_comparison.db database\backup_price_comparison.db

# macOS/Linux
cp database/price_comparison.db database/backup_price_comparison.db
```

**Backup Everything:**
```bash
# Windows
Compress-Archive -Path database, output, logs -DestinationPath backup.zip

# macOS/Linux
tar -czf backup.tar.gz database/ output/ logs/
```

### Clearing Files

**Clear Logs:**
```bash
# Windows
del logs\app.log

# macOS/Linux
rm logs/app.log
```

**Clear Database Only:**
```bash
# Windows
del database\price_comparison.db

# macOS/Linux
rm database/price_comparison.db
```

**Full Reset:**
```bash
# Windows
rmdir /s database output logs

# macOS/Linux
rm -rf database/ output/ logs/
```

**Clear Excel Only:**
```bash
# Windows
del output\product_comparison.xlsx

# macOS/Linux
rm output/product_comparison.xlsx
```

---

## How Files Are Used

### Workflow

```
User Action → Database Check → Web Scrape → Database Save → Excel Update → Log Entry

1. User searches "iPhone"
   ↓
2. App checks database/price_comparison.db
   ├─ If found: Use cached data
   └─ If not found: Scrape websites
   ↓
3. Data saved to database/price_comparison.db
   ↓
4. Excel updated: output/product_comparison.xlsx
   ├─ Creates if doesn't exist
   └─ Adds row if exists
   ↓
5. Activity logged to logs/app.log
   └─ "Inserted Amazon product..."
   └─ "Updated Excel from database"
```

---

## File Relationships

```
                    User Input
                        │
                        ▼
                    main.py
                  (reads config.py)
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
    Database        Scrapers         Utils
    (SQLite)     (Get web data)   (Process data)
         │              │              │
         └──────────────┼──────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
    database/      logs/app.log    output/
    .db file       (activity)      .xlsx file
    (Storage)      (History)       (Report)
```

---

## File Permissions

### Required Permissions

```
database/                 → Read/Write (r/w)
database/price_comparison.db → Read/Write (r/w)
output/                   → Read/Write (r/w)
output/product_comparison.xlsx → Read/Write (r/w)
logs/                     → Read/Write (r/w)
logs/app.log              → Read/Write (r/w)
```

### Fixing Permission Issues

**Windows:**
```bash
# Take ownership
takeown /f database
takeown /f output
takeown /f logs

# Grant permissions
icacls database /grant %username%:F
icacls output /grant %username%:F
icacls logs /grant %username%:F
```

**macOS/Linux:**
```bash
# Make directories writable
chmod -R 755 database output logs

# Or more permissive
chmod -R 777 database output logs
```

---

## Database Structure Details

### amazon_products Table

```sql
CREATE TABLE amazon_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    price REAL,
    rating REAL,
    review_count INTEGER,
    url TEXT UNIQUE,
    description TEXT,
    last_updated TEXT
);
```

**Example Data:**
```
id | product_name              | price | rating | review_count | url | last_updated
─────────────────────────────────────────────────────────────────────────────────────
1  | Apple iPhone 15 128GB     | 52990 | 4.5    | 5000         | ... | 2025-12-13
2  | Aquaphor Healing Ointment | 2699  | NULL   | 200          | ... | 2025-12-13
3  | HP 14s Laptop             | 24999 | NULL   | 100          | ... | 2025-12-13
```

### flipkart_products Table

```sql
CREATE TABLE flipkart_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    price REAL,
    rating REAL,
    review_count INTEGER,
    url TEXT UNIQUE,
    description TEXT,
    last_updated TEXT
);
```

---

## Log File Format

### Log Levels

```
DEBUG    - Detailed information (disabled by default)
INFO     - General information
WARNING  - Warning messages
ERROR    - Error messages
CRITICAL - Critical errors
```

### Example Log Entries

```
2025-12-13 13:50:03,461 - amazon_scraper - INFO - Searching Amazon for: iPhone 15
2025-12-13 13:50:05,406 - flipkart_scraper - INFO - Successfully parsed 5 products from Flipkart
2025-12-13 13:50:05,406 - __main__ - INFO - Matching 5 Amazon products with 3 Flipkart products
2025-12-13 13:50:05,406 - __main__ - INFO - Best match score: 10
2025-12-13 13:50:05,421 - database - INFO - Inserted Amazon product: Apple iPhone 15 128GB
2025-12-13 13:50:05,426 - database - INFO - Inserted Flipkart product: Apple iPhone 15 128GB
2025-12-13 13:50:05,435 - excel_reporter - INFO - Added product to Excel: Apple iPhone 15 128GB
```

### Reading Logs

**Find all errors:**
```bash
grep "ERROR\|WARNING" logs/app.log
```

**Find specific product:**
```bash
grep "iPhone" logs/app.log
```

**Find last 20 lines:**
```bash
tail -20 logs/app.log
```

**Find today's activity:**
```bash
grep "2025-12-13" logs/app.log
```

---

## Disk Space Management

### Monitor Disk Usage

```bash
# Windows
dir /s database output logs

# macOS/Linux
du -sh database output logs
```

### Large Files

**If database grows large:**
```bash
# 1. Back up database
cp database/price_comparison.db database/backup.db

# 2. Clear old data
rm database/price_comparison.db

# 3. App will create new database
python main.py
```

**If logs grow large:**
```bash
# 1. View last few lines
tail -100 logs/app.log > logs/recent_backup.log

# 2. Delete old logs
rm logs/app.log

# 3. App will create new log
python main.py
```

---

## Exporting Data

### Export Database to CSV

```bash
# Using sqlite3
sqlite3 -header -csv database/price_comparison.db \
  "SELECT * FROM amazon_products;" > amazon_products.csv

sqlite3 -header -csv database/price_comparison.db \
  "SELECT * FROM flipkart_products;" > flipkart_products.csv
```

### Export Excel Data

Excel file can be opened in:
- Microsoft Excel (native)
- Google Sheets (import)
- CSV (export from Excel)
- PDF (export from Excel)

---

## File Recovery

### If Database Corrupts

```bash
# Check database integrity
sqlite3 database/price_comparison.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp database/backup_price_comparison.db database/price_comparison.db
```

### If Excel File Corrupts

```bash
# Delete corrupted file
rm output/product_comparison.xlsx

# App will recreate on next search
python main.py
```

### If Logs Corrupt

```bash
# Delete logs
rm logs/app.log

# App will create new log on next run
python main.py
```

---

## File Access Patterns

### Read Operations (Fast)
- Check if product in database
- Read database contents
- Read log file
- Open Excel file

### Write Operations (Slower)
- Insert product to database
- Update Excel file
- Write to log file

### First-Time Operations (Slowest)
- Create new database: 0.5s
- Create new Excel: 1s
- Create new log: 0.1s

---

## Cleanup Strategies

### Daily Cleanup
```bash
# Remove old logs (keep last 100 lines)
tail -100 logs/app.log > logs/app_new.log && mv logs/app_new.log logs/app.log
```

### Weekly Cleanup
```bash
# Back up database
cp database/price_comparison.db database/backup_$(date +%Y%m%d).db

# Compress old logs
gzip logs/app.log
```

### Monthly Reset
```bash
# Archive everything
tar -czf archive_$(date +%Y%m).tar.gz database/ output/ logs/

# Start fresh
rm -rf database output logs
python main.py
```

---

## File Statistics

### Typical File Counts
```
Initial:    5 files (source code + docs)
After 1st search: 8 files (+ database, output, logs)
After 10 searches: 8 files (same count, different sizes)
After 100 searches: 8 files (same count)
```

### Typical Storage Growth
```
Start:      250 KB
After 10 searches: ~400 KB
After 100 searches: ~8 MB
After 1000 searches: ~80 MB
```

---

## File Security

### Sensitive Data
- **Stored:** Product data, prices, URLs, ratings
- **Not stored:** Passwords, personal information, user data
- **Privacy:** No tracking, all local storage

### Backup Important Data
```bash
# Back up everything
cp -r database output logs backups/
```

---

## Summary

| File | Type | Purpose | Auto-Created |
|------|------|---------|--------------|
| price_comparison.db | Binary | Data storage | ✓ |
| product_comparison.xlsx | Excel | Reports | ✓ |
| app.log | Text | Logging | ✓ |

All files are auto-created and managed by the application!

---

**Version:** 1.0  
**Status:** Complete ✅
#13-12-25