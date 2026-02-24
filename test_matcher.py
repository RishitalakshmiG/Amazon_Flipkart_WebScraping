"""Test the product matcher with sample data"""
import sqlite3
from product_matcher import filter_products

def get_all_products():
    """Fetch all products from database"""
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    all_products = []
    
    # Fetch Amazon products
    cursor.execute("SELECT product_name as name, price, rating, review_count, url, description FROM amazon")
    for row in cursor.fetchall():
        all_products.append({
            'product_name': row['name'],
            'name': row['name'],
            'source': 'Amazon',
            'price': row['price'],
            'rating': row['rating'],
            'reviews': row['review_count'],
            'url': row['url']
        })
    
    # Fetch Flipkart products
    cursor.execute("SELECT product_name as name, price, rating, review_count, url, description FROM flipkart")
    for row in cursor.fetchall():
        all_products.append({
            'product_name': row['name'],
            'name': row['name'],
            'source': 'Flipkart',
            'price': row['price'],
            'rating': row['rating'],
            'reviews': row['review_count'],
            'url': row['url']
        })
    
    conn.close()
    return all_products

searches = ['iPhone 15 Pro', 'iPhone 17 Pro', 'iPhone 15', 'iPhone 14', 'Samsung Galaxy']
all_products = get_all_products()

print("\n" + "="*70)
print("PRODUCT MATCHER TEST WITH TRAINED MODEL")
print("="*70)
print(f"Total products in database: {len(all_products)}\n")

for search in searches:
    print(f"Searching for: '{search}'")
    print("-"*70)
    results = filter_products(search, all_products, similarity_threshold=0.65)
    if results:
        for r in results:
            print(f"  ✓ {r['name']} ({r['source']}) - ₹{r['price']:,} - Score: {r['similarity_score']:.3f}")
    else:
        print("  ✗ No matching products found (threshold too high)")
    print()

print("="*70)
