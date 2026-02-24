"""Test the variant matching logic"""
import sys
sys.path.insert(0, 'c:\\Users\\grish\\Downloads\\amazon_flipkart')

from main import calculate_name_similarity

test_pairs = [
    ("Renee Very Matte Lipstick", "Renee Matte Lock Lipstick"),  # Should match but then variant check should reject
    ("Renee Very Matte Lipstick", "Renee Very Matte Lipstick"),  # Should match completely
    ("iPhone 14 Pro", "iPhone 14 Max"),  # Should be rejected (Pro vs Max)
    ("iPhone 14 Pro", "iPhone 14 Pro"),  # Should match
    ("Samsung S24 Ultra", "Samsung S24"),  # Different variants
]

print("="*70)
print("NAME SIMILARITY TESTS")
print("="*70)

for name1, name2 in test_pairs:
    is_identical, similarity = calculate_name_similarity(name1, name2)
    print(f"\n'{name1}'")
    print(f"vs '{name2}'")
    print(f"Similarity: {similarity:.0f}% - {'MATCH' if similarity >= 70 else 'REJECTED'}")
