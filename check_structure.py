"""Check product structure"""
from amazon_scraper import AmazonScraper
from flipkart_scraper import FlipkartScraper
import json

amazon = AmazonScraper()
flipkart = FlipkartScraper()

query = "iphone 15"
print("\n=== AMAZON ===")
amazon_products = amazon.search(query)
if amazon_products:
    print(f"Found {len(amazon_products)} products")
    print("First product keys:", amazon_products[0].keys() if amazon_products else "None")
    print("First product:", json.dumps(amazon_products[0], indent=2, default=str))

print("\n=== FLIPKART ===")
flipkart_products = flipkart.search(query)
if flipkart_products:
    print(f"Found {len(flipkart_products)} products")
    print("First product keys:", flipkart_products[0].keys() if flipkart_products else "None")
    print("First product:", json.dumps(flipkart_products[0], indent=2, default=str))
