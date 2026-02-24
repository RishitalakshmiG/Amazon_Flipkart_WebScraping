"""
Complete Price Comparison Pipeline
User Input → Normalize → Scrape → Embed → Score → Filter → Compare → Store
"""

import logging
import os
import json
from datetime import datetime
from database import Database
from amazon_scraper import AmazonScraper
from flipkart_scraper import FlipkartScraper
from product_matcher import filter_products
from utils import setup_logging, compare_products
from sentence_transformers import SentenceTransformer

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class PriceComparisonPipeline:
    """Complete pipeline for price comparison"""
    
    def __init__(self):
        """Initialize pipeline components"""
        self.db = Database()
        self.amazon = AmazonScraper()
        self.flipkart = FlipkartScraper()
        
        # Load fine-tuned SBERT model
        model_path = "./models/finetuned_sbert"
        if os.path.exists(model_path):
            logger.info("✓ Loading fine-tuned SBERT model...")
            self.model = SentenceTransformer(model_path)
            logger.info(f"✓ Fine-tuned model loaded from {model_path}")
        else:
            logger.warning(f"⚠️ Fine-tuned model not found at {model_path}")
            logger.info("✓ Loading base SBERT model...")
            self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    def normalize_input(self, user_input):
        """
        Step 1: Normalize user input
        - Clean text
        - Remove extra spaces
        - Convert to lowercase
        """
        logger.info(f"\n{'='*80}")
        logger.info("STEP 1: NORMALIZE INPUT")
        logger.info(f"{'='*80}")
        
        normalized = user_input.strip().lower()
        logger.info(f"Original input:   {user_input}")
        logger.info(f"Normalized:       {normalized}\n")
        
        return normalized
    
    def scrape_products(self, query):
        """
        Step 2: Scrape Amazon & Flipkart
        - Get all matching products from both platforms
        """
        logger.info(f"{'='*80}")
        logger.info("STEP 2: SCRAPE PRODUCTS")
        logger.info(f"{'='*80}")
        logger.info(f"Query: {query}\n")
        
        # Scrape Amazon
        logger.info("🔍 Scraping Amazon...")
        amazon_products = []
        try:
            amazon_products = self.amazon.search(query)
            logger.info(f"✓ Found {len(amazon_products)} products on Amazon\n")
        except Exception as e:
            logger.warning(f"⚠️ Amazon scraping failed: {e}\n")
        
        # Scrape Flipkart
        logger.info("🔍 Scraping Flipkart...")
        flipkart_products = []
        try:
            flipkart_products = self.flipkart.search(query)
            logger.info(f"✓ Found {len(flipkart_products)} products on Flipkart\n")
        except Exception as e:
            logger.warning(f"⚠️ Flipkart scraping failed: {e}\n")
        
        all_products = {
            'amazon': amazon_products,
            'flipkart': flipkart_products,
            'total': len(amazon_products) + len(flipkart_products)
        }
        
        logger.info(f"Total products scraped: {all_products['total']}\n")
        return all_products
    
    def generate_embeddings(self, products):
        """
        Step 3: Generate embeddings using fine-tuned SBERT
        - Create embeddings for query
        - Create embeddings for each product
        """
        logger.info(f"{'='*80}")
        logger.info("STEP 3: GENERATE EMBEDDINGS (SBERT)")
        logger.info(f"{'='*80}\n")
        
        # Add embeddings to products
        for platform in ['amazon', 'flipkart']:
            for product in products[platform]:
                try:
                    # Generate embedding for product name/title
                    product_name = product.get('product_name') or product.get('title') or product.get('name') or 'Unknown'
                    embedding = self.model.encode(product_name)
                    product['embedding'] = embedding.tolist()
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate embedding: {e}")
                    product['embedding'] = None
        
        logger.info(f"✓ Generated embeddings for {products['total']} products\n")
        return products
    
    def score_similarity(self, query, products):
        """
        Step 4: Compute similarity scores
        - Score each product against query using fine-tuned SBERT
        """
        logger.info(f"{'='*80}")
        logger.info("STEP 4: SIMILARITY SCORING")
        logger.info(f"{'='*80}\n")
        
        # Generate query embedding
        query_embedding = self.model.encode(query)
        
        # Score all products
        for platform in ['amazon', 'flipkart']:
            for product in products[platform]:
                if product.get('embedding'):
                    # Compute cosine similarity
                    from scipy.spatial.distance import cosine
                    similarity = 1 - cosine(query_embedding, product['embedding'])
                    product['similarity'] = float(similarity)
                else:
                    product['similarity'] = 0.0
        
        logger.info(f"✓ Similarity scores computed\n")
        return products
    
    def filter_best_matches(self, products, query, threshold=0.25):
        """
        Step 5: Filter only best-matching products
        - Keep only products with similarity > threshold
        - Prefer exact model matches (e.g., iPhone 15 over iPhone 15 Pro)
        """
        logger.info(f"{'='*80}")
        logger.info("STEP 5: FILTER BEST MATCHES")
        logger.info(f"{'='*80}")
        logger.info(f"Threshold: {threshold}\n")
        
        filtered = {'amazon': [], 'flipkart': []}
        
        # Check if user asked for specific variants
        query_lower = query.lower()
        user_wants_pro = "pro" in query_lower or "max" in query_lower or "plus" in query_lower
        
        for platform in ['amazon', 'flipkart']:
            original_count = len(products[platform])
            # Sort by similarity and filter
            products[platform].sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            filtered_products = []
            for p in products[platform]:
                product_name_lower = (p.get('product_name') or p.get('title') or p.get('name') or 'Unknown').lower()
                similarity = p.get('similarity', 0)
                
                # Apply stricter threshold for variants user didn't ask for
                if not user_wants_pro and ("pro" in product_name_lower or "max" in product_name_lower):
                    # Require higher similarity for Pro models when user searched for base model
                    if similarity < threshold + 0.15:  # Higher threshold for unwanted variants
                        logger.debug(f"Excluding {product_name_lower[:60]} (Pro variant not requested, low similarity)")
                        continue
                
                # Check standard threshold
                if similarity < threshold:
                    continue
                
                filtered_products.append(p)
            
            filtered[platform] = filtered_products
            
            logger.info(f"{platform.upper()}:")
            logger.info(f"  Original: {original_count} products")
            logger.info(f"  Filtered: {len(filtered[platform])} products (threshold: {threshold})")
            
            # Show top matches
            for i, product in enumerate(filtered[platform][:3], 1):
                product_name = product.get('product_name') or product.get('title') or product.get('name') or 'Unknown'
                logger.info(f"    {i}. {product_name[:80]}... (similarity: {product['similarity']:.3f})")
        
        logger.info('')
        return filtered
    
    def compare_prices(self, filtered_products):
        """
        Step 6: Compare prices & details, store in database
        - Extract price, rating, availability
        - Store in database
        """
        logger.info(f"{'='*80}")
        logger.info("STEP 6: COMPARE PRICES & STORE IN DATABASE")
        logger.info(f"{'='*80}\n")
        
        results = {'amazon': [], 'flipkart': []}
        comparison_data = []
        
        for platform in ['amazon', 'flipkart']:
            for product in filtered_products[platform]:
                try:
                    # Extract price
                    price = product.get('price', 'N/A')
                    if isinstance(price, str):
                        price_num = float(''.join(filter(str.isdigit, price.split('.')[0])) or 0) / 100
                    else:
                        price_num = price
                    
                    # Create result entry
                    result = {
                        'platform': platform,
                        'name': product.get('product_name') or product.get('title') or product.get('name', 'Unknown'),
                        'price': price,
                        'price_numeric': price_num,
                        'url': product.get('url', 'N/A'),
                        'rating': product.get('rating', 'N/A'),
                        'availability': product.get('availability', 'Unknown'),
                        'similarity': product.get('similarity', 0)
                    }
                    
                    results[platform].append(result)
                    comparison_data.append(result)
                    
                    # Store in database
                    try:
                        self.db.insert_comparison({
                            'timestamp': datetime.now().isoformat(),
                            'query': query,
                            'platform': platform,
                            'product_name': result['name'],
                            'price': str(result['price']),
                            'url': result['url'],
                            'rating': str(result['rating']),
                            'similarity_score': result['similarity']
                        })
                    except Exception as db_err:
                        logger.warning(f"⚠️ Database store failed: {db_err}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process {platform} product: {e}")
        
        logger.info(f"✓ Stored {len(comparison_data)} products in database\n")
        
        # Display comparison
        if comparison_data:
            logger.info(f"{'='*80}")
            logger.info("📊 PRICE COMPARISON RESULTS (Sorted by Price)")
            logger.info(f"{'='*80}\n")
            
            # Sort by price
            comparison_data.sort(key=lambda x: x['price_numeric'])
            
            for i, item in enumerate(comparison_data, 1):
                logger.info(f"{i}. {item['name'][:100]}")
                logger.info(f"   Platform:   {item['platform'].upper()}")
                logger.info(f"   Price:      ₹{item['price']}")
                logger.info(f"   Rating:     {item['rating']}")
                logger.info(f"   Similarity: {item['similarity']:.3f}")
                logger.info(f"   URL:        {item['url'][:100]}...")
                logger.info('')
        else:
            logger.info(f"\n⚠️ No products found matching your search.")
            logger.info(f"Try a more general search term.\n")
        
        return results
    
    def run(self, user_input, threshold=0.65):
        """
        Run complete pipeline
        """
        logger.info(f"\n\n{'='*80}")
        logger.info("PRICE COMPARISON PIPELINE")
        logger.info(f"{'='*80}\n")
        
        try:
            # Step 1: Normalize input
            normalized_query = self.normalize_input(user_input)
            
            # Step 2: Scrape products
            products = self.scrape_products(normalized_query)
            
            if products['total'] == 0:
                logger.warning("❌ No products found. Please try a different search.")
                return None
            
            # Step 3: Generate embeddings
            products = self.generate_embeddings(products)
            
            # Step 4: Score similarity
            products = self.score_similarity(normalized_query, products)
            
            # Step 5: Filter best matches
            filtered = self.filter_best_matches(products, normalized_query, threshold=threshold)
            
            # Step 6: Compare prices & store
            results = self.compare_prices(filtered)
            
            logger.info(f"{'='*80}")
            logger.info("PIPELINE COMPLETE ✓")
            logger.info(f"{'='*80}\n")
            
            return results
        
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}", exc_info=True)
            return None


def main():
    """Main entry point"""
    import sys
    
    # Get search query from command line or user input
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("\n🔍 Enter product to search: ").strip()
    
    if not query:
        logger.error("❌ No search query provided")
        return
    
    # Run pipeline
    pipeline = PriceComparisonPipeline()
    results = pipeline.run(query, threshold=0.25)
if __name__ == "__main__":
    main()
