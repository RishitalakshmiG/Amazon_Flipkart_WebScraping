"""
Unit tests and validation for the SBERT product matcher.

Run this file to verify the product matcher works correctly:
    python test_product_matcher.py
"""

import logging
import sys
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import product matcher
try:
    from product_matcher import (
        filter_products,
        cosine_similarity,
        get_embedding,
        is_excluded_product,
        enhance_scraper_results,
        batch_embeddings
    )
except ImportError as e:
    logger.error(f"Failed to import product_matcher: {e}")
    sys.exit(1)


# ============================================================================
# TEST DATA
# ============================================================================

TEST_PRODUCTS_IPHONE = [
    {'product_name': 'Apple iPhone 14 Pro Max', 'price': 139999, 'rating': 4.5},
    {'product_name': 'iPhone 14 Pro', 'price': 99999, 'rating': 4.4},
    {'product_name': 'iPhone 14', 'price': 79999, 'rating': 4.3},
    {'product_name': 'iPhone 14 Pro Case', 'price': 1999, 'rating': 4.0},
    {'product_name': 'iPhone 14 Tempered Glass Screen Protector', 'price': 299, 'rating': 3.9},
    {'product_name': 'Samsung Galaxy S23 Ultra', 'price': 124999, 'rating': 4.6},
    {'product_name': 'Refurbished iPhone 14 Pro Max', 'price': 119999, 'rating': 4.2},
]

TEST_PRODUCTS_HEADPHONES = [
    {'product_name': 'Sony WH-1000XM5 Wireless Headphones', 'price': 29999, 'rating': 4.8},
    {'product_name': 'Sony WH-1000XM4 Noise Cancelling', 'price': 24999, 'rating': 4.7},
    {'product_name': 'Sony WH-CH720N Headphones', 'price': 9999, 'rating': 4.5},
    {'product_name': 'Sony WH-1000XM5 Case', 'price': 1999, 'rating': 4.0},
    {'product_name': 'Beats Studio Pro Headphones', 'price': 39999, 'rating': 4.6},
    {'product_name': 'Audio Technica ATH-M50x Professional', 'price': 18999, 'rating': 4.5},
]

TEST_PRODUCTS_MISC = [
    {'product_name': 'Samsung Galaxy S23', 'price': 79999, 'rating': 4.5},
    {'product_name': 'OnePlus 11 Pro', 'price': 69999, 'rating': 4.4},
    {'product_name': 'Google Pixel 8 Pro', 'price': 84999, 'rating': 4.3},
    {'product_name': 'iPad Pro 12.9', 'price': 129999, 'rating': 4.6},
    {'product_name': 'MacBook Pro 14', 'price': 199999, 'rating': 4.7},
]


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_exclusion_keywords():
    """Test that accessories and refurbished items are excluded"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Exclusion Keywords")
    logger.info("="*70)
    
    test_cases = {
        'iPhone 14 Case': True,  # Should exclude
        'iPhone 14': False,  # Should not exclude
        'Refurbished iPhone 14': True,  # Should exclude
        'iPhone 14 Screen Protector': True,  # Should exclude
        'iPhone 14 USB-C Cable': True,  # Should exclude
        'iPhone Charger': True,  # Should exclude
        'iPhone 14 Bundle Pack': True,  # Should exclude
        'iPhone 14 Warranty Plan': True,  # Should exclude
    }
    
    passed = 0
    for product, should_exclude in test_cases.items():
        result = is_excluded_product(product)
        status = "✓ PASS" if result == should_exclude else "✗ FAIL"
        logger.info(f"{status}: '{product}' → excluded={result} (expected={should_exclude})")
        if result == should_exclude:
            passed += 1
    
    logger.info(f"\nResult: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_basic_filtering():
    """Test basic filtering with simple query"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Basic Filtering (iPhone)")
    logger.info("="*70)
    
    matched = filter_products(
        "iPhone 14",
        TEST_PRODUCTS_IPHONE,
        similarity_threshold=0.80
    )
    
    logger.info(f"Input: {len(TEST_PRODUCTS_IPHONE)} products")
    logger.info(f"Output: {len(matched)} matches (threshold=0.80)")
    logger.info("\nMatched products:")
    
    for product in matched:
        logger.info(
            f"  ✓ {product['product_name']:<40} "
            f"(score: {product['similarity_score']:.4f})"
        )
    
    # Verify no accessories were returned
    accessories_returned = any(
        is_excluded_product(p['product_name']) for p in matched
    )
    
    if not accessories_returned:
        logger.info("\n✓ PASS: No accessories returned")
        return True
    else:
        logger.info("\n✗ FAIL: Accessories were not filtered out")
        return False


def test_similarity_threshold():
    """Test that similarity threshold works correctly"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Similarity Threshold Effect")
    logger.info("="*70)
    
    thresholds = [0.60, 0.75, 0.85, 0.95]
    results = {}
    
    for threshold in thresholds:
        matched = filter_products(
            "iPhone 14",
            TEST_PRODUCTS_IPHONE,
            similarity_threshold=threshold,
            exclude_accessories=False  # Include all for threshold testing
        )
        results[threshold] = len(matched)
        logger.info(f"Threshold {threshold:.2f}: {len(matched)} matches")
    
    # Verify monotonic decrease
    values = list(results.values())
    is_monotonic = all(values[i] >= values[i+1] for i in range(len(values)-1))
    
    if is_monotonic:
        logger.info("\n✓ PASS: Results decrease with higher threshold")
        return True
    else:
        logger.info("\n✗ FAIL: Results not monotonic")
        return False


def test_different_product_types():
    """Test filtering works for different product types"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Different Product Types")
    logger.info("="*70)
    
    test_cases = [
        ("Sony WH-1000XM5", TEST_PRODUCTS_HEADPHONES),
        ("Samsung Galaxy S23", TEST_PRODUCTS_MISC),
        ("iPad Pro", TEST_PRODUCTS_MISC),
    ]
    
    all_passed = True
    
    for query, products in test_cases:
        matched = filter_products(query, products, similarity_threshold=0.75)
        logger.info(f"\nQuery: '{query}'")
        logger.info(f"  Matches: {len(matched)}")
        
        if len(matched) > 0:
            best_match = matched[0]
            logger.info(
                f"  Best: {best_match['product_name'][:50]} "
                f"(score: {best_match['similarity_score']:.4f})"
            )
        else:
            logger.warning(f"  No matches found!")
            all_passed = False
    
    if all_passed:
        logger.info("\n✓ PASS: All product types matched correctly")
    else:
        logger.info("\n✗ FAIL: Some product types didn't match")
    
    return all_passed


def test_embedding_generation():
    """Test that embeddings are generated correctly"""
    logger.info("\n" + "="*70)
    logger.info("TEST 5: Embedding Generation")
    logger.info("="*70)
    
    try:
        # Test single embedding
        embedding = get_embedding("iPhone 14")
        logger.info(f"✓ Generated embedding with shape: {len(embedding)}")
        
        if len(embedding) == 384:
            logger.info("✓ PASS: Embedding dimension is correct (384)")
            
            # Test batch embeddings
            texts = ["iPhone 14", "iPhone 14 Pro", "Samsung Galaxy"]
            embeddings = batch_embeddings(texts)
            logger.info(f"✓ Generated {len(embeddings)} batch embeddings")
            
            return True
        else:
            logger.error(f"✗ FAIL: Expected dimension 384, got {len(embedding)}")
            return False
    
    except Exception as e:
        logger.error(f"✗ FAIL: {e}")
        return False


def test_cosine_similarity_math():
    """Test cosine similarity calculations"""
    logger.info("\n" + "="*70)
    logger.info("TEST 6: Cosine Similarity Calculations")
    logger.info("="*70)
    
    try:
        # Test similar texts
        emb1 = get_embedding("iPhone 14 Pro Max")
        emb2 = get_embedding("Apple iPhone 14 Pro Max")
        similarity = cosine_similarity(emb1, emb2)
        
        logger.info(f"Similarity('iPhone 14 Pro Max', 'Apple iPhone 14 Pro Max'): {similarity:.4f}")
        
        if similarity > 0.90:
            logger.info("✓ PASS: Very similar texts have high similarity")
            
            # Test different texts
            emb3 = get_embedding("Samsung Galaxy S23")
            similarity2 = cosine_similarity(emb1, emb3)
            logger.info(f"Similarity('iPhone 14', 'Samsung Galaxy S23'): {similarity2:.4f}")
            
            if similarity2 < similarity:
                logger.info("✓ PASS: Different texts have lower similarity")
                return True
            else:
                logger.error("✗ FAIL: Different texts should have lower similarity")
                return False
        else:
            logger.error(f"✗ FAIL: Similar texts should have similarity > 0.90, got {similarity}")
            return False
    
    except Exception as e:
        logger.error(f"✗ FAIL: {e}")
        return False


def test_max_results_limit():
    """Test that max_results parameter works"""
    logger.info("\n" + "="*70)
    logger.info("TEST 7: Max Results Limit")
    logger.info("="*70)
    
    # Get all matches
    all_matches = filter_products(
        "iPhone",
        TEST_PRODUCTS_IPHONE,
        similarity_threshold=0.50,
        exclude_accessories=False,
        max_results=None
    )
    
    # Get limited matches
    limited_matches = filter_products(
        "iPhone",
        TEST_PRODUCTS_IPHONE,
        similarity_threshold=0.50,
        exclude_accessories=False,
        max_results=2
    )
    
    logger.info(f"All matches: {len(all_matches)}")
    logger.info(f"Limited matches (max=2): {len(limited_matches)}")
    
    if len(limited_matches) == 2 and len(limited_matches) <= len(all_matches):
        logger.info("✓ PASS: max_results limit works correctly")
        return True
    else:
        logger.error("✗ FAIL: max_results limit not working")
        return False


def test_edge_cases():
    """Test edge cases and error handling"""
    logger.info("\n" + "="*70)
    logger.info("TEST 8: Edge Cases & Error Handling")
    logger.info("="*70)
    
    passed = 0
    total = 0
    
    # Test 1: Empty product list
    total += 1
    try:
        result = filter_products("iPhone", [])
        if result == []:
            logger.info("✓ PASS: Empty product list handled")
            passed += 1
        else:
            logger.error("✗ FAIL: Empty list should return empty result")
    except Exception as e:
        logger.error(f"✗ FAIL: Empty list raised exception: {e}")
    
    # Test 2: Invalid threshold (should raise error)
    total += 1
    try:
        result = filter_products("iPhone", TEST_PRODUCTS_IPHONE, similarity_threshold=1.5)
        logger.error("✗ FAIL: Should reject threshold > 1.0")
    except ValueError:
        logger.info("✓ PASS: Rejected invalid threshold (> 1.0)")
        passed += 1
    except Exception as e:
        logger.error(f"✗ FAIL: Wrong exception type: {e}")
    
    # Test 3: Missing product_name field (should handle gracefully)
    total += 1
    try:
        products = [{'price': 999}]  # No product_name
        result = filter_products("iPhone", products)
        logger.info("✓ PASS: Missing product_name field handled gracefully")
        passed += 1
    except Exception as e:
        logger.error(f"✗ FAIL: Should handle missing fields: {e}")
    
    logger.info(f"\nResult: {passed}/{total} edge cases handled correctly")
    return passed == total


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and report results"""
    logger.info("\n" + "="*70)
    logger.info("SBERT PRODUCT MATCHER - COMPREHENSIVE TEST SUITE")
    logger.info("="*70)
    
    tests = [
        ("Exclusion Keywords", test_exclusion_keywords),
        ("Basic Filtering", test_basic_filtering),
        ("Similarity Threshold", test_similarity_threshold),
        ("Different Product Types", test_different_product_types),
        ("Embedding Generation", test_embedding_generation),
        ("Cosine Similarity", test_cosine_similarity_math),
        ("Max Results Limit", test_max_results_limit),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"\n✗ EXCEPTION in {test_name}: {e}")
            results[test_name] = False
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info("="*70 + "\n")
    
    return passed == total


# ============================================================================
# PERFORMANCE BENCHMARK
# ============================================================================

def benchmark_performance():
    """Benchmark performance of product matching"""
    logger.info("\n" + "="*70)
    logger.info("PERFORMANCE BENCHMARK")
    logger.info("="*70)
    
    import time
    
    # Create larger test set
    large_product_list = []
    for i in range(100):
        large_product_list.append({
            'product_name': f'Product {i}',
            'price': 1000 + i,
            'rating': 4.0
        })
    
    # Add some actual product names for variety
    for product in TEST_PRODUCTS_IPHONE:
        large_product_list.append(product)
    for product in TEST_PRODUCTS_HEADPHONES:
        large_product_list.append(product)
    
    logger.info(f"\nTest set size: {len(large_product_list)} products")
    
    # Benchmark
    start = time.time()
    matched = filter_products(
        "iPhone 14",
        large_product_list,
        similarity_threshold=0.75
    )
    elapsed = time.time() - start
    
    logger.info(f"Execution time: {elapsed:.2f} seconds")
    logger.info(f"Products per second: {len(large_product_list) / elapsed:.0f}")
    logger.info(f"Time per product: {(elapsed / len(large_product_list)) * 1000:.1f}ms")
    logger.info(f"Matches found: {len(matched)}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        # Run tests
        all_passed = run_all_tests()
        
        # Run benchmark
        try:
            benchmark_performance()
        except Exception as e:
            logger.warning(f"Benchmark failed: {e}")
        
        # Exit code
        sys.exit(0 if all_passed else 1)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
