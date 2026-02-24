"""
Test with realistic Renee lipstick data to verify:
1. Proper product extraction from names  
2. Correct product matching (not matching Very Matte with Matte Lock)
3. Returning only truly comparable products
"""
import sys
sys.path.insert(0, 'c:\\Users\\grish\\Downloads\\amazon_flipkart')

from main import find_best_matching_pair, extract_product_details

print("="*70)
print("COMPREHENSIVE TEST: Renee Lipsticks")
print("="*70)

# Different Renee lipstick variants
amazon_products = [
    {
        'product_name': 'RENEE Very Matte Lipstick - Rouge',
        'price': 509,
        'rating': 4.2,
        'category': 'beauty'
    },
    {
        'product_name': 'RENEE Very Matte Lipstick - Berry',
        'price': 509,
        'rating': 4.1,
        'category': 'beauty'
    },
]

flipkart_products = [
    {
        'product_name': 'Renee Matte Lock Lipstick, Ultra Matte Finish, Moisturizing, Long Lasting & Weightless 5 g',
        'price': 235,
        'rating': 4.0,
        'category': 'beauty'
    },
    {
        'product_name': 'Renee Very Matte Lipstick- Rouge 6 g',
        'price': 159,
        'rating': 4.0,
        'category': 'beauty'
    },
    {
        'product_name': 'Renee Very Matte Lipstick- Berry 6g',
        'price': 165,
        'rating': 3.9,
        'category': 'beauty'
    },
]

print("\nAmazon Products:")
for i, p in enumerate(amazon_products, 1):
    print(f"  {i}. {p['product_name']} - Rs. {p['price']}")

print("\nFlipkart Products:")
for i, p in enumerate(flipkart_products, 1):
    print(f"  {i}. {p['product_name']} - Rs. {p['price']}")

print("\nExpected Results:")
print("  1. Amazon 'Very Matte Lipstick - Rouge' should match Flipkart 'Very Matte Lipstick- Rouge'")
print("  2. Amazon 'Very Matte Lipstick - Berry' should match Flipkart 'Very Matte Lipstick- Berry'")
print("  3. Amazon should NOT match with Flipkart 'Matte Lock' (different variant)")

print("\n" + "="*70)
print("RUNNING TESTS")
print("="*70)

test_cases = [
    (amazon_products[0], [flipkart_products[1]], "Very Matte Rouge vs Very Matte Rouge"),
    (amazon_products[1], [flipkart_products[2]], "Very Matte Berry vs Very Matte Berry"),
    (amazon_products[0], [flipkart_products[0]], "Very Matte Rouge vs Matte Lock (should FAIL)"),
]

results = []
for amazon, flipkart_list, description in test_cases:
    print(f"\n{description}")
    print(f"  Amazon: {amazon['product_name']}")
    print(f"  Flipkart: {flipkart_list[0]['product_name']}")
    
    try:
        amazon_matched, flipkart_matched, quality = find_best_matching_pair(
            [amazon],
            flipkart_list,
            search_query="Renee lipstick"
        )
        
        match = amazon_matched['product_name'] == amazon['product_name'] and \
                flipkart_matched['product_name'] == flipkart_list[0]['product_name']
        
        print(f"  Result: {'MATCHED' if match else 'DIFFERENT'} (Quality: {quality})")
        results.append((description, match))
    except Exception as e:
        print(f"  Error: {str(e)[:80]}")
        results.append((description, False))

print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

passed = sum(1 for _, result in results if result)
total = len(results)

for desc, result in results:
    status = "PASS" if result else "FAIL"
    print(f"{status}: {desc}")

print(f"\nTotal: {passed}/{total} tests passed")
