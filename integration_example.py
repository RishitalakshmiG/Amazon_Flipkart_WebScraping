"""
Integration guide and examples for using the SBERT product matcher.

This file demonstrates how to integrate product_matcher.py into your
existing scraper pipeline with minimal changes.
"""

import logging
from typing import List, Dict, Optional

# Import your existing modules
from amazon_scraper import AmazonScraper
from flipkart_scraper import FlipkartScraper
from database import Database

# Import the new product matcher
from product_matcher import filter_products, enhance_scraper_results

logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: Basic Usage - Filter products from a single platform
# ============================================================================

def search_amazon_with_matching(product_name: str, threshold: float = 0.80):
    """
    Search Amazon and filter results using semantic matching.
    
    Before (keyword-based, matches "iPhone 14 Case"):
        >>> scraped = scraper.search("iPhone 14")
        >>> # Returns: iPhone 14, iPhone 14 Case, iPhone 14 Pro, etc.
    
    After (semantic matching, filters out case):
        >>> matched = search_amazon_with_matching("iPhone 14")
        >>> # Returns: iPhone 14, iPhone 14 Pro (case excluded by filter_products)
    """
    scraper = AmazonScraper()
    
    # Step 1: Scrape products using keyword-based search
    logger.info(f"Scraping Amazon for: {product_name}")
    soup = scraper.fetch_page(product_name)
    
    if not soup:
        logger.error("Failed to fetch Amazon page")
        return []
    
    scraped_products = scraper.parse_products(soup)
    logger.info(f"Found {len(scraped_products)} products on Amazon")
    
    # Step 2: Filter using semantic matching (NEW!)
    matched_products = filter_products(
        user_product_name=product_name,
        scraped_products=scraped_products,
        similarity_threshold=threshold,
        exclude_accessories=True,
        max_results=5
    )
    
    logger.info(f"After semantic filtering: {len(matched_products)} matches")
    
    return matched_products


# ============================================================================
# EXAMPLE 2: Compare both platforms with semantic matching
# ============================================================================

def search_both_platforms_with_matching(
    product_name: str,
    similarity_threshold: float = 0.80,
    max_results_per_platform: int = 5
) -> Dict[str, List[Dict]]:
    """
    Search both Amazon and Flipkart, then apply semantic matching to both.
    
    This is the recommended approach for your main workflow.
    
    Usage in main.py:
    ----
    results = search_both_platforms_with_matching("iPhone 14 Pro")
    
    print("AMAZON MATCHES:")
    for product in results['amazon']:
        print(f"  {product['product_name']}")
        print(f"    Similarity: {product['similarity_score']:.2%}")
        print(f"    Price: ₹{product.get('price', 'N/A')}\n")
    
    print("FLIPKART MATCHES:")
    for product in results['flipkart']:
        print(f"  {product['product_name']}")
        print(f"    Similarity: {product['similarity_score']:.2%}")
        print(f"    Price: ₹{product.get('price', 'N/A')}\n")
    ----
    """
    amazon_scraper = AmazonScraper()
    flipkart_scraper = FlipkartScraper()
    
    logger.info(f"Searching for: {product_name}")
    
    # Step 1: Scrape from both platforms
    logger.info("Scraping Amazon...")
    amazon_soup = amazon_scraper.fetch_page(product_name)
    amazon_products = (
        amazon_scraper.parse_products(amazon_soup)
        if amazon_soup else []
    )
    logger.info(f"Found {len(amazon_products)} products on Amazon")
    
    logger.info("Scraping Flipkart...")
    flipkart_soup = flipkart_scraper.fetch_page(product_name)
    flipkart_products = (
        flipkart_scraper.parse_products(flipkart_soup)
        if flipkart_soup else []
    )
    logger.info(f"Found {len(flipkart_products)} products on Flipkart")
    
    # Step 2: Apply semantic filtering to both platforms (NEW!)
    results = enhance_scraper_results(
        user_query=product_name,
        amazon_products=amazon_products,
        flipkart_products=flipkart_products,
        similarity_threshold=similarity_threshold,
        max_per_platform=max_results_per_platform
    )
    
    return results


# ============================================================================
# EXAMPLE 3: Integration with existing database workflow
# ============================================================================

def search_and_store_matched_products(product_name: str):
    """
    Complete workflow: scrape, match, and store only matched products.
    
    This maintains backward compatibility while adding semantic matching.
    Matched products have a 'similarity_score' field.
    """
    db = Database()
    
    # Get semantically matched products
    results = search_both_platforms_with_matching(
        product_name,
        similarity_threshold=0.80,
        max_results_per_platform=5
    )
    
    # Store matched products in database
    logger.info("Storing matched products in database...")
    
    # Amazon products
    for product in results['amazon']:
        db.insert_amazon_product(
            product_name=product['product_name'],
            price=product.get('price'),
            rating=product.get('rating'),
            review_count=product.get('review_count'),
            url=product.get('url', ''),
            description=f"Semantic match score: {product.get('similarity_score', 0):.2%}"
        )
    
    # Flipkart products
    for product in results['flipkart']:
        db.insert_flipkart_product(
            product_name=product['product_name'],
            price=product.get('price'),
            rating=product.get('rating'),
            review_count=product.get('review_count'),
            url=product.get('url', ''),
            description=f"Semantic match score: {product.get('similarity_score', 0):.2%}"
        )
    
    logger.info("Products stored successfully")
    return results


# ============================================================================
# EXAMPLE 4: Advanced - Customizing similarity threshold
# ============================================================================

def search_with_custom_threshold(
    product_name: str,
    similarity_threshold: Optional[float] = None
) -> Dict[str, List[Dict]]:
    """
    Search with different thresholds based on product specificity.
    
    General products (e.g., "headphones"): Lower threshold (0.70)
    Specific models (e.g., "Sony WH-1000XM5"): Higher threshold (0.85)
    
    This helps balance between:
    - High precision: 0.85+ (only very similar products)
    - Balanced: 0.75-0.85 (good mix of precision & recall)
    - High recall: 0.65-0.75 (captures variations)
    """
    # Auto-detect threshold based on product specificity
    if similarity_threshold is None:
        word_count = len(product_name.split())
        
        if word_count >= 4:
            # Specific model name (e.g., "Sony WH-1000XM5 Black")
            similarity_threshold = 0.85
            logger.info("Detected specific model name - using threshold: 0.85")
        
        elif word_count >= 2:
            # Generic product with brand (e.g., "Sony headphones")
            similarity_threshold = 0.75
            logger.info("Detected generic product - using threshold: 0.75")
        
        else:
            # Very generic (e.g., "headphones")
            similarity_threshold = 0.65
            logger.info("Detected very generic product - using threshold: 0.65")
    
    return search_both_platforms_with_matching(
        product_name,
        similarity_threshold=similarity_threshold,
        max_results_per_platform=5
    )


# ============================================================================
# EXAMPLE 5: Comparative analysis - with/without semantic matching
# ============================================================================

def compare_keyword_vs_semantic_matching(product_name: str):
    """
    Demonstrate the difference between keyword-based and semantic matching.
    
    Useful for testing and validation.
    """
    amazon_scraper = AmazonScraper()
    
    # Get scraped products (keyword-based)
    soup = amazon_scraper.fetch_page(product_name)
    keyword_results = amazon_scraper.parse_products(soup) if soup else []
    
    print("\n" + "="*80)
    print("KEYWORD-BASED SEARCH (Before Semantic Matching)")
    print("="*80)
    for i, product in enumerate(keyword_results[:10], 1):
        print(f"{i}. {product['product_name'][:70]}")
        print(f"   Price: ₹{product.get('price', 'N/A')}\n")
    
    # Apply semantic matching
    semantic_results = filter_products(
        product_name,
        keyword_results,
        similarity_threshold=0.80,
        exclude_accessories=True,
        max_results=10
    )
    
    print("\n" + "="*80)
    print("SEMANTIC-BASED SEARCH (After Semantic Matching)")
    print("="*80)
    for i, product in enumerate(semantic_results, 1):
        score = product.get('similarity_score', 0)
        print(f"{i}. {product['product_name'][:70]}")
        print(f"   Similarity: {score:.2%}")
        print(f"   Price: ₹{product.get('price', 'N/A')}\n")
    
    print("\n" + "="*80)
    print("FILTERING IMPACT")
    print("="*80)
    print(f"Keyword results: {len(keyword_results)} products")
    print(f"Semantic results: {len(semantic_results)} products")
    print(f"Filtered out: {len(keyword_results) - len(semantic_results)} products")
    print("="*80 + "\n")


# ============================================================================
# How to integrate into your existing main.py
# ============================================================================

"""
INTEGRATION STEPS:

1. Add import at top of main.py:
   ----
   from product_matcher import filter_products, enhance_scraper_results
   ----

2. In PriceComparator.search_and_compare() method, modify the section
   that parses products:
   
   OLD CODE:
   ----
   soup = self.amazon_scraper.fetch_page(product_name)
   amazon_products = self.amazon_scraper.parse_products(soup)
   
   soup = self.flipkart_scraper.fetch_page(product_name)
   flipkart_products = self.flipkart_scraper.parse_products(soup)
   ----
   
   NEW CODE:
   ----
   soup = self.amazon_scraper.fetch_page(product_name)
   amazon_raw = self.amazon_scraper.parse_products(soup)
   amazon_products = filter_products(
       product_name,
       amazon_raw,
       similarity_threshold=0.80
   )
   
   soup = self.flipkart_scraper.fetch_page(product_name)
   flipkart_raw = self.flipkart_scraper.parse_products(soup)
   flipkart_products = filter_products(
       product_name,
       flipkart_raw,
       similarity_threshold=0.80
   )
   ----

3. (Optional) Display similarity scores in results:
   ----
   for product in amazon_products:
       score = product.get('similarity_score', 0)
       print(f"{product['product_name']} ({score:.2%} match)")
   ----

4. Update requirements.txt (already done):
   pip install -r requirements.txt

That's it! Your existing code will now filter out accessories and
unrelated variants automatically.
"""

if __name__ == "__main__":
    import sys
    from utils import setup_logging
    
    setup_logging()
    
    # Example usage
    if len(sys.argv) > 1:
        product = " ".join(sys.argv[1:])
        print(f"\nSearching for: {product}\n")
        compare_keyword_vs_semantic_matching(product)
    else:
        print("Usage: python integration_example.py <product_name>")
        print("Example: python integration_example.py iPhone 14 Pro")
