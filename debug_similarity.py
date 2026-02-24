"""Debug pipeline - check similarity scores"""
import logging
from sentence_transformers import SentenceTransformer
from amazon_scraper import AmazonScraper
from flipkart_scraper import FlipkartScraper
from utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Load model
model = SentenceTransformer("./models/finetuned_sbert")

# Scrape
amazon = AmazonScraper()
flipkart = FlipkartScraper()

query = "iphone 15"
amazon_products = amazon.search(query)
flipkart_products = flipkart.search(query)

all_products = amazon_products + flipkart_products

logger.info(f"\n\nDEBUG: Found {len(all_products)} products\n")

# Get query embedding
query_embedding = model.encode(query)

# Check similarities
from scipy.spatial.distance import cosine

for product in all_products:
    product_name = product.get('title') or product.get('name', 'Unknown')
    try:
        product_emb = model.encode(product_name)
        similarity = 1 - cosine(query_embedding, product_emb)
        logger.info(f"\nProduct: {product_name}")
        logger.info(f"Similarity: {similarity:.4f}")
    except Exception as e:
        logger.error(f"Error: {e}")
