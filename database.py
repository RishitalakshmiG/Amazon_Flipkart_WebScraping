"""
Database module for storing Amazon and Flipkart product data
"""
import sqlite3
import logging
from config import DB_PATH, AMAZON_TABLE, FLIPKART_TABLE
from utils import get_timestamp

logger = logging.getLogger(__name__)

class Database:
    """Handle all database operations"""
    
    def __init__(self, db_path=DB_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Create Amazon table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {AMAZON_TABLE} (
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
        
        # Create Flipkart table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {FLIPKART_TABLE} (
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
        
        conn.commit()
        conn.close()
        logger.info("Database tables initialized successfully")
    
    def insert_amazon_product(self, product_name, price, rating, review_count, url, description=""):
        """Insert or update Amazon product"""
        conn = self.get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                INSERT OR REPLACE INTO {AMAZON_TABLE} 
                (product_name, price, rating, review_count, url, description, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_name, price, rating, review_count, url, description, get_timestamp()))
            conn.commit()
            logger.info(f"Inserted Amazon product: {product_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting Amazon product: {e}")
            return False
        finally:
            conn.close()
    
    def insert_flipkart_product(self, product_name, price, rating, review_count, url, description=""):
        """Insert or update Flipkart product"""
        conn = self.get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                INSERT OR REPLACE INTO {FLIPKART_TABLE}
                (product_name, price, rating, review_count, url, description, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_name, price, rating, review_count, url, description, get_timestamp()))
            conn.commit()
            logger.info(f"Inserted Flipkart product: {product_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting Flipkart product: {e}")
            return False
        finally:
            conn.close()
    
    def search_product(self, product_name):
        """
        Search for product in both tables
        Returns:
            dict: Product data from both platforms
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        try:
            # Search Amazon
            cursor.execute(f"""
                SELECT * FROM {AMAZON_TABLE} 
                WHERE product_name LIKE ? LIMIT 1
            """, (f"%{product_name}%",))
            amazon_data = cursor.fetchone()
            
            # Search Flipkart
            cursor.execute(f"""
                SELECT * FROM {FLIPKART_TABLE}
                WHERE product_name LIKE ? LIMIT 1
            """, (f"%{product_name}%",))
            flipkart_data = cursor.fetchone()
            
            return {
                'amazon': dict(amazon_data) if amazon_data else None,
                'flipkart': dict(flipkart_data) if flipkart_data else None
            }
        except sqlite3.Error as e:
            logger.error(f"Error searching for product: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_products(self):
        """Get all products from both tables"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM {AMAZON_TABLE}")
            amazon_products = cursor.fetchall()
            
            cursor.execute(f"SELECT * FROM {FLIPKART_TABLE}")
            flipkart_products = cursor.fetchall()
            
            return {
                'amazon': [dict(row) for row in amazon_products],
                'flipkart': [dict(row) for row in flipkart_products]
            }
        except sqlite3.Error as e:
            logger.error(f"Error fetching products: {e}")
            return None
        finally:
            conn.close()
    
    def clear_table(self, table_name):
        """Clear all data from a table"""
        conn = self.get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            cursor.execute(f"DELETE FROM {table_name}")
            conn.commit()
            logger.info(f"Cleared table: {table_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error clearing table: {e}")
            return False
        finally:
            conn.close()
    
    def delete_product(self, table_name, product_id):
        """Delete a specific product"""
        conn = self.get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (product_id,))
            conn.commit()
            logger.info(f"Deleted product with id: {product_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting product: {e}")
            return False
        finally:
            conn.close()
#13-12-25
