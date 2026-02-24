"""
Configuration settings for the Price Comparison Application
"""

# Database Configuration
DB_NAME = "price_comparison.db"
DB_PATH = "./database/price_comparison.db"

# Tables
AMAZON_TABLE = "amazon_products"
FLIPKART_TABLE = "flipkart_products"

# Scraper Configuration
AMAZON_BASE_URL = "https://www.amazon.in/s"
FLIPKART_BASE_URL = "https://www.flipkart.com/search"

# User Agent for web scraping
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Excel Configuration
EXCEL_FILE_NAME = "product_comparison.xlsx"
EXCEL_OUTPUT_PATH = "./output/product_comparison.xlsx"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/app.log"

# Request timeout (seconds)
REQUEST_TIMEOUT = 10

# Number of retries for failed requests
MAX_RETRIES = 3
#13-12-25