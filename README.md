# Price Comparison System - Amazon vs Flipkart

A comprehensive Python application for comparing product prices, ratings, and reviews across Amazon and Flipkart e-commerce platforms.

## Features

✨ **Core Functionality:**
- 🔍 Search and compare products across Amazon and Flipkart
- 💰 Price comparison with percentage savings calculation
- ⭐ Rating and review comparison
- 💾 SQLite database for storing product data
- 📊 Automatic Excel report generation and updates
- 🤖 Intelligent recommendations based on multiple factors

## Project Structure

```
amazon_flipkart/
├── main.py                  # Main application entry point
├── config.py               # Configuration settings
├── utils.py                # Utility functions and helpers
├── database.py             # Database operations and schema
├── amazon_scraper.py       # Amazon web scraper
├── flipkart_scraper.py     # Flipkart web scraper
├── excel_reporter.py       # Excel report generation
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── database/              # Database storage directory
│   └── price_comparison.db
├── output/                # Excel output directory
│   └── product_comparison.xlsx
└── logs/                  # Application logs
    └── app.log
```

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Steps

1. **Clone or download the project**
```bash
cd amazon_flipkart
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create necessary directories**
```bash
mkdir database
mkdir output
mkdir logs
```

## Usage

### Running the Application

```bash
python main.py
```

### Menu Options

1. **Search & Compare Product**
   - Enter a product name
   - System checks database first
   - If not found, scrapes both Amazon and Flipkart
   - Displays comprehensive comparison
   - Updates Excel report automatically

2. **View All Products in Database**
   - Shows all stored Amazon products
   - Shows all stored Flipkart products
   - Useful for tracking available comparisons

3. **Clear Database**
   - Removes all stored product data
   - Useful for fresh start

4. **Exit**
   - Close application safely

## Modules Overview

### `main.py`
- **PriceComparator Class**: Main orchestrator
- Handles search workflow
- Manages comparison logic
- Provides user interface

### `amazon_scraper.py`
- **AmazonScraper Class**: Scrapes Amazon.in
- Extracts: Product name, price, rating, reviews, URL
- Includes retry logic for reliability
- User-Agent rotation for better success

### `flipkart_scraper.py`
- **FlipkartScraper Class**: Scrapes Flipkart.com
- Extracts: Product name, price, rating, reviews, URL
- Robust error handling
- Configurable timeout and retries

### `database.py`
- **Database Class**: SQLite operations
- Two tables: `amazon_products` and `flipkart_products`
- CRUD operations for products
- Search functionality with fuzzy matching

### `excel_reporter.py`
- **ExcelReporter Class**: Excel file generation
- Professional formatting with colors and borders
- Auto-updates existing reports
- Includes all comparison details

### `utils.py`
- Price/rating/review cleaning and parsing
- Product comparison algorithm
- Logging setup
- Helper functions

### `config.py`
- Centralized configuration
- Database paths
- Scraper settings
- Excel output paths

## Database Schema

### amazon_products table
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

### flipkart_products table
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

## Excel Report

The system automatically generates and updates `product_comparison.xlsx` with:

| Column | Description |
|--------|-------------|
| Product Name | Product being compared |
| Amazon Price | Current price on Amazon |
| Flipkart Price | Current price on Flipkart |
| Amazon Rating | Amazon product rating |
| Flipkart Rating | Flipkart product rating |
| Amazon Reviews | Number of reviews on Amazon |
| Flipkart Reviews | Number of reviews on Flipkart |
| Better Deal | Recommended platform |
| Cheaper By % | Percentage price difference |
| Amazon URL | Direct link to Amazon product |
| Flipkart URL | Direct link to Flipkart product |

## How the Comparison Algorithm Works

The system scores each platform based on:
1. **Price** (Weight: 2) - Lower price scores higher
2. **Rating** (Weight: 1) - Higher rating scores higher
3. **Review Count** (Weight: 1) - More reviews scores higher

Based on total scores, it recommends:
- **Amazon/Flipkart** - If one significantly scores higher
- **Both (Similar Quality)** - If scores are equal

## Logging

All activities are logged to `logs/app.log` including:
- Scraping operations
- Database operations
- Comparison results
- Errors and warnings

View logs:
```bash
tail -f logs/app.log
```

## Important Notes

⚠️ **Web Scraping Considerations:**
- Always respect website's `robots.txt`
- Don't overload servers with rapid requests
- Consider adding delays between requests
- Websites may change their HTML structure - inspect and update selectors
- Some websites may block automated scraping

🔧 **Customization:**
- Modify `config.py` for different settings
- Update CSS selectors in scrapers if website changes
- Add more platforms by creating new scraper modules
- Extend comparison algorithm in `utils.py`

## Troubleshooting

### Issue: "No products found"
- Website structure may have changed
- Update CSS selectors in scraper files
- Check internet connection

### Issue: "Database locked"
- Close other instances of the application
- Check for zombie processes

### Issue: "Excel file not updating"
- Ensure `output/` directory exists
- Check file permissions
- Verify openpyxl installation

## Dependencies

- **requests** - HTTP requests
- **beautifulsoup4** - HTML parsing
- **selenium** - Advanced web scraping (optional)
- **openpyxl** - Excel file creation
- **pandas** - Data manipulation
- **lxml** - XML parsing

## Future Enhancements

- [ ] Web UI with Flask/Django
- [ ] API endpoints for mobile app
- [ ] Price history tracking
- [ ] Email notifications for price drops
- [ ] More platforms (eBay, WalMart, etc.)
- [ ] Machine learning for better recommendations
- [ ] Real-time price updates with scheduling
- [ ] User accounts and wishlists
- [ ] Advanced filtering and sorting

## License

This project is provided as-is for educational and personal use.

## Support

For issues or suggestions:
1. Check the logs in `logs/app.log`
2. Verify all dependencies are installed
3. Ensure directories have proper permissions
4. Check internet connectivity

## Author

Price Comparison System
Created: December 2025
