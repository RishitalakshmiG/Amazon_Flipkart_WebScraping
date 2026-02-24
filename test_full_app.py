"""
Test the full application with a specific product search
"""
import sys
import os
import logging
sys.path.insert(0, 'c:\\Users\\grish\\Downloads\\amazon_flipkart')
os.chdir('c:\\Users\\grish\\Downloads\\amazon_flipkart')

# Suppress detailed logging for this test
logging.basicConfig(level=logging.WARNING)

from database import Database
from amazon_scraper import AmazonScraper
from flipkart_scraper import FlipkartScraper
from main import find_best_matching_pair
from utils import extract_product_details

print("="*100)
print("TESTING FULL APPLICATION WITH REAL SCRAPING")
print("="*100)

# Clear database first
db = Database()
db.clear_table('amazon_products')
db.clear_table('flipkart_products')
print("\n✓ Database cleared")

# Initialize scrapers
amazon = AmazonScraper()
flipkart = FlipkartScraper()

# Search for a specific product
search_query = "iPhone 17 Pro 256GB Cosmic Orange"
print(f"\nSearching for: '{search_query}'")
print("\nScrapers are working...")

# Get results
amazon_results = amazon.search(search_query)
flipkart_results = flipkart.search(search_query)

print(f"\nAmazon found {len(amazon_results)} products")
print(f"Flipkart found {len(flipkart_results)} products")

# Show extracted details for each
print("\n" + "="*100)
print("AMAZON PRODUCTS:")
print("="*100)
for i, prod in enumerate(amazon_results[:3], 1):
    base, color, storage, size, weight, dims, brand = extract_product_details(prod['product_name'])
    print(f"\n{i}. {prod['product_name'][:70]}...")
    print(f"   Color: '{color}' | Storage: {storage}GB | Price: ₹{prod['price']}")

print("\n" + "="*100)
print("FLIPKART PRODUCTS:")
print("="*100)
for i, prod in enumerate(flipkart_results[:3], 1):
    base, color, storage, size, weight, dims, brand = extract_product_details(prod['product_name'])
    print(f"\n{i}. {prod['product_name'][:70]}...")
    print(f"   Color: '{color}' | Storage: {storage}GB | Price: ₹{prod['price']}")

# Run matching algorithm
print("\n" + "="*100)
print("RUNNING MATCHING ALGORITHM:")
print("="*100)

amazon_match, flipkart_match, quality = find_best_matching_pair(amazon_results, flipkart_results, search_query)

if amazon_match and flipkart_match:
    a_base, a_color, a_storage, _, _, _, _ = extract_product_details(amazon_match['product_name'])
    f_base, f_color, f_storage, _, _, _, _ = extract_product_details(flipkart_match['product_name'])
    
    print(f"\n✓ MATCH FOUND (Quality: {quality})")
    print(f"\nAmazon:  {amazon_match['product_name'][:70]}...")
    print(f"  Color: '{a_color}' | Storage: {a_storage}GB | Price: ₹{amazon_match['price']}")
    print(f"\nFlipkart: {flipkart_match['product_name'][:70]}...")
    print(f"  Color: '{f_color}' | Storage: {f_storage}GB | Price: ₹{flipkart_match['price']}")
    print(f"\nColor Match: {a_color.lower() == f_color.lower()}")
    print(f"Storage Match: {a_storage == f_storage}")
else:
    print("\n✗ NO MATCH FOUND")

print("\n" + "="*100)
