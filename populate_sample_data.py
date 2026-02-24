"""
Populate database with sample product data for testing
"""
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample products for testing
AMAZON_PRODUCTS = [
    ("iPhone 15 Pro Max", 139999, 4.5, 1250, "https://amazon.in/iPhone-15-Pro-Max", "Latest Apple flagship"),
    ("iPhone 15 Pro", 99999, 4.4, 980, "https://amazon.in/iPhone-15-Pro", "Apple Pro model"),
    ("iPhone 15", 79999, 4.3, 850, "https://amazon.in/iPhone-15", "Apple standard model"),
    ("iPhone 15 Plus", 89999, 4.3, 750, "https://amazon.in/iPhone-15-Plus", "Apple Plus model"),
    ("iPhone 14 Pro Max", 119999, 4.2, 500, "https://amazon.in/iPhone-14-Pro-Max", "Previous gen flagship"),
    ("iPhone 14 Pro", 89999, 4.1, 450, "https://amazon.in/iPhone-14-Pro", "Previous gen pro"),
    ("iPhone 14", 69999, 4.0, 400, "https://amazon.in/iPhone-14", "Previous gen standard"),
    ("iPhone SE", 49999, 3.9, 300, "https://amazon.in/iPhone-SE", "Budget iPhone"),
    ("Samsung Galaxy S24 Ultra", 149999, 4.6, 2100, "https://amazon.in/Samsung-S24-Ultra", "Samsung flagship"),
    ("Samsung Galaxy S24", 79999, 4.4, 1500, "https://amazon.in/Samsung-S24", "Samsung standard"),
    ("Google Pixel 8 Pro", 109999, 4.5, 980, "https://amazon.in/Pixel-8-Pro", "Google flagship"),
    ("Google Pixel 8", 74999, 4.4, 850, "https://amazon.in/Pixel-8", "Google standard"),
    ("iPhone 15 Screen Protector", 499, 4.2, 2500, "https://amazon.in/iPhone-15-Screen", "Tempered glass"),
    ("iPhone 15 Case", 599, 4.3, 3000, "https://amazon.in/iPhone-15-Case", "Protective case"),
    ("iPhone 15 Charger", 1299, 4.1, 1500, "https://amazon.in/iPhone-15-Charger", "Fast charger"),
]

FLIPKART_PRODUCTS = [
    ("Apple iPhone 15 Pro Max", 139999, 4.5, 980, "https://flipkart.com/iPhone-15-Pro-Max", "Latest Apple flagship"),
    ("Apple iPhone 15 Pro", 99999, 4.4, 750, "https://flipkart.com/iPhone-15-Pro", "Apple Pro model"),
    ("Apple iPhone 15", 79999, 4.3, 650, "https://flipkart.com/iPhone-15", "Apple standard model"),
    ("Apple iPhone 15 Plus", 89999, 4.3, 600, "https://flipkart.com/iPhone-15-Plus", "Apple Plus model"),
    ("Apple iPhone 14 Pro Max", 119999, 4.2, 400, "https://flipkart.com/iPhone-14-Pro-Max", "Previous gen flagship"),
    ("Apple iPhone 14 Pro", 89999, 4.1, 350, "https://flipkart.com/iPhone-14-Pro", "Previous gen pro"),
    ("Apple iPhone 14", 69999, 4.0, 300, "https://flipkart.com/iPhone-14", "Previous gen standard"),
    ("Samsung Galaxy S24 Ultra", 149999, 4.6, 1800, "https://flipkart.com/Samsung-S24-Ultra", "Samsung flagship"),
    ("Samsung Galaxy S24", 79999, 4.4, 1200, "https://flipkart.com/Samsung-S24", "Samsung standard"),
    ("Google Pixel 8 Pro", 109999, 4.5, 750, "https://flipkart.com/Pixel-8-Pro", "Google flagship"),
    ("Google Pixel 8", 74999, 4.4, 650, "https://flipkart.com/Pixel-8", "Google standard"),
    ("OnePlus 12", 64999, 4.3, 1000, "https://flipkart.com/OnePlus-12", "OnePlus flagship"),
    ("Xiaomi 14 Ultra", 59999, 4.2, 900, "https://flipkart.com/Xiaomi-14-Ultra", "Xiaomi flagship"),
]

def populate_database():
    """Populate database with sample data"""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS amazon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL,
            rating REAL,
            review_count INTEGER,
            url TEXT UNIQUE,
            description TEXT,
            last_updated TEXT,
            UNIQUE(url)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flipkart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL,
            rating REAL,
            review_count INTEGER,
            url TEXT UNIQUE,
            description TEXT,
            last_updated TEXT,
            UNIQUE(url)
        )
    """)
    
    # Insert Amazon products
    logger.info("Inserting Amazon products...")
    for name, price, rating, count, url, desc in AMAZON_PRODUCTS:
        try:
            cursor.execute("""
                INSERT INTO amazon (product_name, price, rating, review_count, url, description, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, price, rating, count, url, desc, timestamp))
        except sqlite3.IntegrityError:
            logger.debug(f"Duplicate URL: {url}")
    
    # Insert Flipkart products
    logger.info("Inserting Flipkart products...")
    for name, price, rating, count, url, desc in FLIPKART_PRODUCTS:
        try:
            cursor.execute("""
                INSERT INTO flipkart (product_name, price, rating, review_count, url, description, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, price, rating, count, url, desc, timestamp))
        except sqlite3.IntegrityError:
            logger.debug(f"Duplicate URL: {url}")
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM amazon")
    amazon_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM flipkart")
    flipkart_count = cursor.fetchone()[0]
    
    conn.close()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✓ Database populated successfully!")
    logger.info(f"{'='*60}")
    logger.info(f"Amazon products: {amazon_count}")
    logger.info(f"Flipkart products: {flipkart_count}")
    logger.info(f"Total products: {amazon_count + flipkart_count}")
    logger.info(f"{'='*60}\n")

if __name__ == "__main__":
    populate_database()
