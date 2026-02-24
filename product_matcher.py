"""
AI-powered product matching using Sentence-BERT (SBERT) embeddings.

This module provides semantic similarity-based product matching to filter out
incorrect products, accessories, refurbished items, and unrelated variants.

Key Features:
    - Load pretrained SentenceTransformer model (all-MiniLM-L6-v2)
    - Convert product names to embeddings
    - Compute cosine similarity between user input and scraped products
    - Filter products using configurable similarity threshold
    - Exclude accessories, refurbished items, and unrelated variants
    - Production-ready with caching and error handling
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
import pickle
import os

logger = logging.getLogger(__name__)

# Lazy import to avoid dependency issues if sentence-transformers not installed
_model = None
_base_model_name = "all-MiniLM-L6-v2"
_finetuned_model_path = "./models/finetuned_sbert"


def get_model():
    """
    Load and cache the SentenceTransformer model.
    Prefers fine-tuned model if available, otherwise uses base model.
    
    Returns:
        SentenceTransformer: The model (fine-tuned or base)
        
    Raises:
        ImportError: If sentence-transformers is not installed
        RuntimeError: If model loading fails
    """
    global _model
    
    if _model is not None:
        return _model
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Check for fine-tuned model first
        if os.path.exists(_finetuned_model_path):
            logger.info(f"Found fine-tuned model at: {_finetuned_model_path}")
            logger.info("Loading fine-tuned SentenceTransformer model...")
            _model = SentenceTransformer(_finetuned_model_path)
            logger.info("✓ Fine-tuned model loaded successfully")
            return _model
        else:
            # Fall back to base model
            logger.info(f"Fine-tuned model not found. Using base model: {_base_model_name}")
            logger.info(f"(To use fine-tuned model, run: python finetune_sbert.py)")
            logger.info(f"Loading SentenceTransformer model: {_base_model_name}")
            _model = SentenceTransformer(_base_model_name)
            logger.info("✓ Base model loaded successfully")
            return _model
    except ImportError:
        logger.error(
            "sentence-transformers not installed. "
            "Install with: pip install sentence-transformers"
        )
        raise
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Model loading failed: {e}") from e


def get_embedding(text: str) -> np.ndarray:
    """
    Convert text to embedding vector using SBERT.
    
    Args:
        text (str): Input text to convert
        
    Returns:
        np.ndarray: Embedding vector (shape: 384 for all-MiniLM-L6-v2)
        
    Raises:
        ValueError: If text is None or empty
        RuntimeError: If model loading fails
    """
    if not text or not isinstance(text, str):
        raise ValueError("Text must be a non-empty string")
    
    # Normalize text: lowercase and strip whitespace
    text = text.strip().lower()
    
    try:
        model = get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding for '{text}': {e}")
        raise


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Formula: similarity = (A · B) / (||A|| * ||B||)
    
    Args:
        vec1 (np.ndarray): First vector
        vec2 (np.ndarray): Second vector
        
    Returns:
        float: Similarity score between -1 and 1 (typically 0 to 1)
        
    Raises:
        ValueError: If vectors are invalid or have different shapes
    """
    if vec1 is None or vec2 is None:
        raise ValueError("Vectors cannot be None")
    
    if len(vec1) != len(vec2):
        raise ValueError(f"Vector dimension mismatch: {len(vec1)} vs {len(vec2)}")
    
    # Normalize vectors to unit length
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        logger.warning("Zero-norm vector encountered")
        return 0.0
    
    # Compute cosine similarity
    similarity = np.dot(vec1, vec2) / (norm1 * norm2)
    
    # Clamp to [-1, 1] to handle floating point errors
    return float(np.clip(similarity, -1.0, 1.0))


def is_excluded_product(title: str) -> bool:
    """
    Check if a product should be excluded based on common keywords.
    
    Excludes:
        - Accessories (cases, covers, protectors, chargers, cables)
        - Refurbished items
        - Bulk/bundle packs
        - Warranties and insurance
        
    Args:
        title (str): Product title to check
        
    Returns:
        bool: True if product should be excluded, False otherwise
    """
    if not title:
        return False
    
    title_lower = title.lower()
    
    # Exclusion patterns
    exclusion_keywords = {
        # Accessories
        "case", "cover", "protector", "charger", "cable", "adapter",
        "stand", "holder", "mount", "screen protector", "glass",
        "tempered glass", "foil", "sticker", "pouch", "bag",
        "sleeve", "flip cover", "flip case", "leather case",
        
        # Refurbished/Used
        "refurbished", "used", "open box", "b grade", "c grade",
        "renewed", "reconditioned", "certified", "seller refurbished",
        
        # Bundles/Deals
        "bundle", "combo", "pack", "set", "kit", "pair",
        
        # Warranty/Insurance
        "warranty", "insurance", "protection plan", "extended warranty",
        "care plan", "accidental damage",
    }
    
    for keyword in exclusion_keywords:
        if keyword in title_lower:
            logger.debug(f"Excluded '{title}' (keyword: {keyword})")
            return True
    
    return False


def filter_products(
    user_product_name: str,
    scraped_products: List[Dict],
    similarity_threshold: float = 0.80,
    exclude_accessories: bool = True,
    max_results: Optional[int] = None
) -> List[Dict]:
    """
    Filter and rank products based on semantic similarity to user input.
    
    This is the main function that should be called in your scraper pipeline.
    It performs the following steps:
    
    1. Generate embedding for user input
    2. For each scraped product:
       a. Check if it should be excluded (accessories, refurbished, etc.)
       b. Generate embedding for product title
       c. Compute cosine similarity with user input
       d. Keep product if similarity >= threshold
    3. Sort by similarity score (highest first)
    4. Return top matches
    
    Args:
        user_product_name (str): User's input product name
        scraped_products (List[Dict]): List of product dictionaries from scrapers
            Each dict should have at minimum: {'product_name': str, ...}
        similarity_threshold (float): Minimum similarity score (0-1). Default 0.80
        exclude_accessories (bool): Whether to exclude accessories. Default True
        max_results (Optional[int]): Max number of results to return. Default None (all)
        
    Returns:
        List[Dict]: Filtered and ranked products with similarity scores
            Each product includes original data + 'similarity_score' field
            
    Raises:
        ValueError: If user_product_name is empty or invalid
        RuntimeError: If model loading fails
        
    Example:
        >>> scraped = [
        ...     {'product_name': 'iPhone 14 Pro Max', 'price': 999, 'url': '...'},
        ...     {'product_name': 'iPhone 14 Pro Max Case', 'price': 20, 'url': '...'},
        ... ]
        >>> matched = filter_products('iPhone 14', scraped, similarity_threshold=0.75)
        >>> # Returns only the phone, not the case
    """
    # Validate inputs
    if not user_product_name or not isinstance(user_product_name, str):
        raise ValueError("user_product_name must be a non-empty string")
    
    if not scraped_products:
        logger.warning("No products provided to filter")
        return []
    
    if not (0.0 <= similarity_threshold <= 1.0):
        raise ValueError("similarity_threshold must be between 0 and 1")
    
    try:
        # Step 1: Get embedding for user input
        logger.info(f"Processing user query: '{user_product_name}'")
        user_embedding = get_embedding(user_product_name)
        
        matched_products = []
        excluded_count = 0
        
        # Step 2-4: Process each scraped product
        for product in scraped_products:
            # Extract product name (handle different key names)
            product_name = product.get('product_name') or product.get('name') or ""
            
            if not product_name:
                logger.warning(f"Product missing name field: {product}")
                continue
            
            # Check exclusion rules
            if exclude_accessories and is_excluded_product(product_name):
                excluded_count += 1
                continue
            
            try:
                # Get embedding for product title
                product_embedding = get_embedding(product_name)
                
                # Compute similarity
                similarity = cosine_similarity(user_embedding, product_embedding)
                
                # Check threshold
                if similarity >= similarity_threshold:
                    # Create result with similarity score
                    result = product.copy()
                    result['similarity_score'] = round(similarity, 4)
                    matched_products.append(result)
                    logger.debug(
                        f"Match: '{product_name}' "
                        f"(similarity: {similarity:.4f})"
                    )
                else:
                    logger.debug(
                        f"Below threshold: '{product_name}' "
                        f"(similarity: {similarity:.4f})"
                    )
            
            except Exception as e:
                logger.warning(f"Error processing product '{product_name}': {e}")
                continue
        
        # Step 5: Sort by similarity (highest first)
        matched_products.sort(
            key=lambda x: x.get('similarity_score', 0),
            reverse=True
        )
        
        # Step 6: Apply max_results limit
        if max_results is not None and max_results > 0:
            matched_products = matched_products[:max_results]
        
        # Log summary
        logger.info(
            f"Filtering complete: {len(matched_products)} matches found "
            f"(threshold: {similarity_threshold}, excluded: {excluded_count})"
        )
        
        return matched_products
    
    except Exception as e:
        logger.error(f"Error in product filtering: {e}")
        raise


def batch_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    Efficiently generate embeddings for multiple texts at once.
    
    More efficient than calling get_embedding() repeatedly.
    
    Args:
        texts (List[str]): List of text strings
        
    Returns:
        List[np.ndarray]: List of embedding vectors
        
    Raises:
        ValueError: If texts list is empty or invalid
        RuntimeError: If model loading fails
    """
    if not texts:
        raise ValueError("texts list cannot be empty")
    
    # Filter out None and empty strings
    valid_texts = [t.strip().lower() for t in texts if t]
    
    if not valid_texts:
        raise ValueError("No valid texts to embed")
    
    try:
        model = get_model()
        embeddings = model.encode(valid_texts, convert_to_numpy=True)
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Error in batch embedding: {e}")
        raise


def cache_embeddings(
    products: List[Dict],
    cache_file: str = "embeddings_cache.pkl"
) -> Dict[str, np.ndarray]:
    """
    Cache product embeddings to disk for faster processing.
    
    Useful for large product lists that won't change frequently.
    
    Args:
        products (List[Dict]): List of products with 'product_name'
        cache_file (str): Path to cache file
        
    Returns:
        Dict[str, np.ndarray]: Dictionary mapping product names to embeddings
        
    Note:
        Embeddings are cached by product name. If a product name changes,
        the old embedding will remain cached.
    """
    try:
        cache = {}
        for product in products:
            name = product.get('product_name', '')
            if name and name not in cache:
                cache[name] = get_embedding(name)
        
        # Save to disk
        with open(cache_file, 'wb') as f:
            pickle.dump(cache, f)
        
        logger.info(f"Cached {len(cache)} embeddings to {cache_file}")
        return cache
    
    except Exception as e:
        logger.error(f"Error caching embeddings: {e}")
        raise


def load_embeddings_cache(cache_file: str = "embeddings_cache.pkl") -> Optional[Dict]:
    """
    Load cached embeddings from disk.
    
    Args:
        cache_file (str): Path to cache file
        
    Returns:
        Dict[str, np.ndarray]: Cached embeddings, or None if file doesn't exist
    """
    try:
        if not os.path.exists(cache_file):
            logger.info(f"Cache file not found: {cache_file}")
            return None
        
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)
        
        logger.info(f"Loaded {len(cache)} embeddings from cache")
        return cache
    
    except Exception as e:
        logger.warning(f"Error loading embeddings cache: {e}")
        return None


# ============================================================================
# Integration Helpers
# ============================================================================

def enhance_scraper_results(
    user_query: str,
    amazon_products: List[Dict],
    flipkart_products: List[Dict],
    similarity_threshold: float = 0.80,
    max_per_platform: int = 5
) -> Dict[str, List[Dict]]:
    """
    Convenience function to filter products from both platforms in one call.
    
    Perfect for integrating into your main.py after scraping.
    
    Args:
        user_query (str): User's product search query
        amazon_products (List[Dict]): Products from Amazon scraper
        flipkart_products (List[Dict]): Products from Flipkart scraper
        similarity_threshold (float): Minimum similarity score
        max_per_platform (int): Maximum results per platform
        
    Returns:
        Dict with 'amazon' and 'flipkart' keys, each containing filtered products
        
    Example:
        >>> results = enhance_scraper_results(
        ...     "iPhone 14",
        ...     amazon_products=[...],
        ...     flipkart_products=[...],
        ...     max_per_platform=3
        ... )
        >>> print(results['amazon'])  # Top 3 matching products from Amazon
        >>> print(results['flipkart'])  # Top 3 matching products from Flipkart
    """
    return {
        'amazon': filter_products(
            user_query,
            amazon_products,
            similarity_threshold=similarity_threshold,
            max_results=max_per_platform
        ),
        'flipkart': filter_products(
            user_query,
            flipkart_products,
            similarity_threshold=similarity_threshold,
            max_results=max_per_platform
        )
    }
