"""Test with different thresholds to find optimal value"""
import sqlite3
from product_matcher import filter_products

def get_all_products():
    """Fetch all products from database"""
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    all_products = []
    
    cursor.execute("SELECT product_name as name, price, rating, review_count, url FROM amazon")
    for row in cursor.fetchall():
        all_products.append({
            'product_name': row['name'],
            'source': 'Amazon',
            'price': row['price'],
            'rating': row['rating'],
            'reviews': row['review_count'],
            'url': row['url']
        })
    
    cursor.execute("SELECT product_name as name, price, rating, review_count, url FROM flipkart")
    for row in cursor.fetchall():
        all_products.append({
            'product_name': row['name'],
            'source': 'Flipkart',
            'price': row['price'],
            'rating': row['rating'],
            'reviews': row['review_count'],
            'url': row['url']
        })
    
    conn.close()
    return all_products

searches = {
    'iPhone 15 Pro': 0.70,
    'iPhone 17 Pro': 0.70,  # Doesn't exist - should return nothing
    'iPhone 15': 0.70,
    'Samsung Galaxy': 0.65,  # Try lower threshold
}

all_products = get_all_products()

print("\n" + "="*75)
print("PRODUCT MATCHER - THRESHOLD ANALYSIS")
print("="*75)
print(f"Total products in database: {len(all_products)}\n")

for search, threshold in searches.items():
    print(f"Query: '{search}' (threshold: {threshold})")
    print("-"*75)
    results = filter_products(search, all_products, similarity_threshold=threshold)
    if results:
        for r in results:
            print(f"  [MATCH] {r['product_name']} ({r['source']}) - Rs{int(r['price']):,} - Score: {r['similarity_score']:.3f}")
    else:
        print(f"  [NO MATCH] No products found with threshold {threshold}")
    print()

print("="*75)
print("\nNOTE:")
print("  - 'iPhone 17 Pro' doesn't exist in DB (database has iPhone 14 & 15 only)")
print("  - 'Samsung Galaxy' matches with lower threshold (0.65)")
print("  - This is expected behavior - the model only matches products that exist!")
print("="*75 + "\n")
