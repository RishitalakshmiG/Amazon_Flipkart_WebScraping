# 🏗️ Project Architecture & Structure

Complete overview of how the application is organized and how it works.

---

## Application Flow Diagram

```
USER INPUT (Search for "iPhone 15")
         ↓
    main.py (PriceComparator)
    ├─ Check database first
    │  └─ If found: Return cached results
    │
    ├─ NOT in database?
    │  ├─ amazon_scraper.py (AmazonScraper)
    │  │  ├─ Make HTTP request to Amazon.in
    │  │  ├─ Parse HTML with BeautifulSoup
    │  │  ├─ Extract: name, price, rating, reviews, URL
    │  │  └─ Filter by keywords (quality control)
    │  │
    │  └─ flipkart_scraper.py (FlipkartScraper)
    │     ├─ Make HTTP request to Flipkart.com
    │     ├─ Parse HTML with BeautifulSoup
    │     ├─ Extract: name, price, rating, reviews, URL
    │     └─ Filter by keywords (quality control)
    │
    ├─ Extracted data goes to:
    │  └─ database.py (Database)
    │     ├─ Store in SQLite database
    │     ├─ amazon_products table
    │     └─ flipkart_products table
    │
    ├─ Match products with:
    │  └─ utils.py (find_best_matching_pair)
    │     ├─ Extract: color, storage, size
    │     ├─ Score each potential pair
    │     ├─ Require storage match (for phones/laptops)
    │     └─ Return best match
    │
    ├─ Compare with:
    │  └─ utils.py (compare_products)
    │     ├─ Calculate price difference
    │     ├─ Compare ratings
    │     ├─ Compare review counts
    │     └─ Generate recommendation
    │
    └─ Generate report:
       └─ excel_reporter.py (ExcelReporter)
          ├─ Create/Update Excel file
          ├─ Add product data
          ├─ Apply formatting
          └─ Save to output/product_comparison.xlsx

DISPLAY RESULTS TO USER
```

---

## File Structure

```
amazon_flipkart/
│
├── 📜 Core Application Files
│   ├── main.py                  # Entry point, main CLI menu
│   ├── database.py              # SQLite database operations
│   ├── amazon_scraper.py        # Amazon web scraper
│   ├── flipkart_scraper.py      # Flipkart web scraper
│   ├── excel_reporter.py        # Excel report generation
│   ├── utils.py                 # Utility & helper functions
│   └── config.py                # Configuration & settings
│
├── 📚 Documentation Files
│   ├── README.md                # Complete documentation
│   ├── README_FIRST.md          # Welcome & overview (START HERE)
│   ├── QUICKSTART.md            # 5-minute setup guide
│   ├── INSTALLATION.md          # Detailed setup & troubleshooting
│   ├── PROJECT_STRUCTURE.md     # This file (architecture)
│   ├── INDEX.md                 # Complete navigation guide
│   ├── VISUAL_GUIDES.md         # Diagrams and visuals
│   ├── FILE_GENERATION.md       # File management info
│   └── START_HERE.md            # Project summary
│
├── 🔧 Configuration & Dependencies
│   ├── requirements.txt          # Python package dependencies
│   └── .gitignore               # Git ignore file
│
├── 📁 Data Directories
│   ├── database/                # Database storage
│   │   └── price_comparison.db  # SQLite database file
│   ├── output/                  # Generated Excel reports
│   │   └── product_comparison.xlsx
│   └── logs/                    # Application logs
│       └── app.log
│
└── 🎯 Additional Files (Optional)
    └── examples.py              # 7 working code examples
```

---

## Core Modules Explained

### 1. **main.py** - Application Entry Point

**Purpose:** Main CLI application, handles user interaction

**Key Classes:**
```python
class PriceComparator:
    def __init__(self)              # Initialize scrapers & database
    def search_and_compare(product) # Main search workflow
    def display_comparison(result)  # Show results to user
```

**Key Functions:**
```python
def find_best_matching_pair(amazon_results, flipkart_results)
    # Intelligent matching algorithm
    # Returns: (amazon_product, flipkart_product)
```

**Workflow:**
1. User searches for product
2. Check if in database (cached)
3. If not found, scrape both websites
4. Match products intelligently
5. Compare and generate recommendation
6. Save to database and Excel
7. Display to user

---

### 2. **amazon_scraper.py** - Amazon Web Scraper

**Purpose:** Scrape Amazon.in for products

**Key Classes:**
```python
class AmazonScraper:
    def __init__(self)              # Initialize with config
    def search(product_name)        # Search and return products
    def parse_products(soup)        # Extract data from HTML
    def fetch_page(url)             # Make HTTP request
```

**Data Extracted:**
- Product name (from title or link text)
- Price (with currency conversion)
- Rating (0-5 stars)
- Review count (number of reviews)
- Product URL (direct link)

**Quality Control:**
- Filters by search keywords
- Removes duplicates
- Validates data
- Handles errors gracefully

**Example:**
```python
scraper = AmazonScraper()
results = scraper.search("iPhone 15")
# Returns: [
#   {'product_name': 'Apple iPhone 15', 'price': 52990, ...},
#   {'product_name': 'Apple iPhone 15 Pro', 'price': 99990, ...},
#   ...
# ]
```

---

### 3. **flipkart_scraper.py** - Flipkart Web Scraper

**Purpose:** Scrape Flipkart.com for products

**Key Classes:**
```python
class FlipkartScraper:
    def __init__(self)              # Initialize with config
    def search(product_name)        # Search and return products
    def parse_products(soup)        # Extract data from HTML
    def fetch_page(url)             # Make HTTP request
```

**Features:**
- Same interface as Amazon scraper
- Compatible data format
- Similar quality control
- Handles Flipkart's HTML structure

**Note:** Both scrapers return data in the same format for easy comparison.

---

### 4. **database.py** - Database Management

**Purpose:** SQLite database for storing and retrieving products

**Key Classes:**
```python
class Database:
    def __init__(self)              # Initialize & create tables
    def insert_product(platform, data)  # Store product
    def find_product(name)          # Search stored products
    def get_all_products()          # List all products
    def clear_database()            # Delete all data
```

**Database Schema:**

**amazon_products table:**
```sql
id (Primary Key)
product_name (TEXT)
price (REAL)
rating (REAL)
review_count (INTEGER)
url (TEXT, UNIQUE)
search_query (TEXT)
last_updated (DATETIME)
```

**flipkart_products table:**
```sql
id (Primary Key)
product_name (TEXT)
price (REAL)
rating (REAL)
review_count (INTEGER)
url (TEXT, UNIQUE)
search_query (TEXT)
last_updated (DATETIME)
```

**Benefits:**
- Fast lookups (cached products)
- Avoids repeated scraping
- Track search history
- Easy data analysis

---

### 5. **excel_reporter.py** - Excel Report Generation

**Purpose:** Create professional Excel reports

**Key Classes:**
```python
class ExcelReporter:
    def __init__(self)              # Initialize workbook
    def create_workbook()           # Set up Excel file
    def add_product_comparison()    # Add product row
    def generate_from_results()     # Create report from data
    def update_from_database()      # Update from database
```

**Excel Features:**
- Professional formatting
- Color-coded columns
- Auto-adjusted column widths
- Alternating row colors
- Bold headers
- Centered alignment
- Product links

**Columns:**
1. Product Name
2. Amazon Price
3. Flipkart Price
4. Amazon Rating
5. Flipkart Rating
6. Amazon Reviews
7. Flipkart Reviews
8. Better Deal (recommendation)
9. Cheaper By % (savings)
10. Amazon URL
11. Flipkart URL

---

### 6. **utils.py** - Utility Functions

**Purpose:** Helper functions for the application

**Key Functions:**

**Product Extraction:**
```python
def extract_product_details(product_name)
    # Returns: (base_name, color, storage, size)
    # Example: "iPhone 15 128GB Black" → 
    #          ("iPhone 15", "Black", "128", "")
```

**Product Matching:**
```python
def find_matching_product_list(product_list, target_color, target_storage)
    # Find best match in list by color/storage
    # Returns: matching product or None
```

**Price Cleaning:**
```python
def clean_price(price_string)
    # Convert "₹10,000" → 10000.0
    # Returns: float
```

**Review Cleaning:**
```python
def clean_reviews(review_string)
    # Convert "1,234" → 1234
    # Returns: int
```

**Comparison:**
```python
def compare_products(amazon_data, flipkart_data)
    # Compare and generate recommendation
    # Returns: {recommendation, cheaper_by_percentage, ...}
```

**Logging:**
```python
def setup_logging()
    # Configure logging system
    # Logs to: logs/app.log
```

---

### 7. **config.py** - Configuration Settings

**Purpose:** Centralized configuration

**Key Settings:**

```python
# Database
DB_NAME = "price_comparison.db"
DB_PATH = "./database/price_comparison.db"
AMAZON_TABLE = "amazon_products"
FLIPKART_TABLE = "flipkart_products"

# Websites
AMAZON_BASE_URL = "https://www.amazon.in/s"
FLIPKART_BASE_URL = "https://www.flipkart.com/search"

# Excel
EXCEL_FILE_NAME = "product_comparison.xlsx"
EXCEL_OUTPUT_PATH = "./output/product_comparison.xlsx"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/app.log"

# Scraping
REQUEST_TIMEOUT = 10        # seconds
MAX_RETRIES = 3            # retry attempts
USER_AGENT = "Mozilla/5.0 ..."  # Browser identification

# Features
COMMON_WORDS = {'the', 'a', 'an', 'and', ...}
```

---

## How Matching Works

The intelligent matching algorithm ensures you compare the exact same product.

### Step 1: Extract Details
```python
name, color, storage, size = extract_product_details(
    "Apple iPhone 15 (128 GB) - Black"
)
# Result: ("Apple iPhone 15", "Black", "128", "")
```

### Step 2: Score Each Pair
For each Amazon-Flipkart pair:
```python
match_score = 0

# Storage match (REQUIRED for phones/laptops)
if amazon_storage == flipkart_storage:
    match_score += 10

# Color match
if amazon_color == flipkart_color:
    match_score += 5

# Size match (for beauty products)
if abs(amazon_size - flipkart_size) < 0.5:
    match_score += 3

# Name similarity
if amazon_name in flipkart_name:
    match_score += 1
```

### Step 3: Select Best Match
```python
# Only return if storage matches (for phones/laptops)
if amazon_storage and flipkart_storage:
    if amazon_storage == flipkart_storage:
        return (amazon_product, flipkart_product)
    else:
        skip this pair
```

### Result
**Prevents:**
- iPhone 128GB matched with iPhone 512GB ❌
- Black phone matched with Gold phone ❌
- 14oz moisturizer matched with 25oz moisturizer ❌

**Allows:**
- Same exact product on both platforms ✅
- Even if names are slightly different ✅
- As long as specs match ✅

---

## Data Flow Example

```
User: "Search for iPhone 15"
        ↓
Check Database:
  ✗ Not found
        ↓
Amazon Scraper:
  1. GET https://www.amazon.in/s?k=iphone+15
  2. Parse HTML
  3. Extract: 5 products
  4. Filter by keywords: 4 products remain
  5. Clean data (prices, ratings, etc.)
  6. Result: [{name, price, rating, ...}, ...]
        ↓
Flipkart Scraper:
  1. GET https://www.flipkart.com/search?q=iphone+15
  2. Parse HTML
  3. Extract: 3 products
  4. Filter by keywords: 3 products remain
  5. Clean data (prices, ratings, etc.)
  6. Result: [{name, price, rating, ...}, ...]
        ↓
Database Storage:
  1. Insert 4 Amazon products
  2. Insert 3 Flipkart products
  3. Mark timestamp
        ↓
Matching Algorithm:
  1. Compare all 4×3=12 pairs
  2. Score each pair
  3. Find best match: (A2, F1) with score 10
  4. Return: (Amazon iPhone 15 128GB, Flipkart iPhone 15 128GB)
        ↓
Comparison:
  Amazon: ₹52,990
  Flipkart: ₹51,000
  Difference: ₹1,990 (3.75%)
  Recommendation: Buy from Flipkart
        ↓
Report Generation:
  1. Create/Update Excel file
  2. Add row with all details
  3. Add hyperlinks
  4. Apply formatting
  5. Save file
        ↓
Display Results:
  Show to user in terminal
  "Better Deal: Flipkart"
```

---

## Class Relationships

```
┌─────────────────────────────────────┐
│     main.py                         │
│  ┌─ PriceComparator                │
│  │  ├─ uses Amazon Scraper        │
│  │  ├─ uses Flipkart Scraper      │
│  │  ├─ uses Database              │
│  │  ├─ uses Excel Reporter        │
│  │  └─ uses utils functions       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  amazon_scraper.py                  │
│  ┌─ AmazonScraper                  │
│  │  ├─ imports config              │
│  │  ├─ uses utils functions        │
│  │  └─ uses logging                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  flipkart_scraper.py                │
│  ┌─ FlipkartScraper                │
│  │  ├─ imports config              │
│  │  ├─ uses utils functions        │
│  │  └─ uses logging                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  database.py                        │
│  ┌─ Database                       │
│  │  ├─ imports config              │
│  │  ├─ uses logging                │
│  │  └─ creates SQLite tables       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  excel_reporter.py                  │
│  ┌─ ExcelReporter                  │
│  │  ├─ imports config              │
│  │  ├─ uses logging                │
│  │  └─ uses openpyxl               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  utils.py                           │
│  ├─ extract_product_details()       │
│  ├─ find_best_matching_pair()       │
│  ├─ compare_products()              │
│  ├─ clean_price()                   │
│  ├─ clean_reviews()                 │
│  └─ setup_logging()                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  config.py                          │
│  ├─ Database paths                  │
│  ├─ Website URLs                    │
│  ├─ Output paths                    │
│  └─ Scraping settings               │
└─────────────────────────────────────┘
```

---

## How to Extend the Application

### Add a New Website (e.g., Myntra)

1. **Create scraper:**
```bash
cp flipkart_scraper.py myntra_scraper.py
```

2. **Update class name and logic:**
```python
class MyntraScraper:
    def __init__(self):
        self.base_url = "https://www.myntra.com/search"
        self.headers = {'User-Agent': USER_AGENT}
    
    def search(self, product_name):
        # Update URL and CSS selectors
        url = f"{self.base_url}?q={product_name}"
        # ... rest of implementation
```

3. **Add to main.py:**
```python
from myntra_scraper import MytraScraper

self.myntra_scraper = MytraScraper()
myntra_results = self.myntra_scraper.search(product_name)
```

4. **Update database.py:**
```python
# Add myntra_products table
CREATE TABLE myntra_products (...)
```

5. **Update matching:**
```python
# Update matching to include 3-way comparison
```

---

## Performance Optimization Tips

1. **Database Caching:** Repeat searches use cache (fast)
2. **Request Timeout:** Configured to 10 seconds
3. **Max Retries:** Automatic retry on failure (3 times)
4. **Selective Scraping:** Only scrape if not in database

---

## Error Handling Strategy

```python
def search(self, product_name):
    try:
        # Main logic
    except ConnectionError:
        # Handle network issues
    except TimeoutError:
        # Handle slow websites
    except Exception as e:
        # Handle any other error
        logger.error(f"Error: {e}")
    finally:
        # Cleanup code
```

---

## Summary

This architecture provides:
- **Modularity:** Each class has single responsibility
- **Reusability:** Easy to extend with new platforms
- **Maintainability:** Clear separation of concerns
- **Reliability:** Error handling throughout
- **Performance:** Database caching for speed
- **Professionalism:** Logging and reporting

---

**Next Steps:**
- Read `README.md` for full features
- Run `python examples.py` for code examples
- Review individual source files
- Customize for your needs

---

**Version:** 1.0  
**Status:** Production Ready ✅
