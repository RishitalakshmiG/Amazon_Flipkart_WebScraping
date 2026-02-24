"""
Amazon product scraper
"""
import requests
from bs4 import BeautifulSoup
import logging
from config import AMAZON_BASE_URL, USER_AGENT, REQUEST_TIMEOUT, MAX_RETRIES
from utils import clean_price, clean_rating, clean_reviews

logger = logging.getLogger(__name__)

class AmazonScraper:
    """Scrape product data from Amazon"""
    
    def __init__(self):
        """Initialize Amazon scraper"""
        self.base_url = AMAZON_BASE_URL
        self.headers = {
            'User-Agent': USER_AGENT
        }
        self.timeout = REQUEST_TIMEOUT
        self.max_retries = MAX_RETRIES
    
    def fetch_page(self, product_query):
        """
        Fetch Amazon search page
        Args:
            product_query: Product to search
        Returns:
            BeautifulSoup object or None
        """
        try:
            params = {
                'k': product_query
            }
            
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        self.base_url,
                        headers=self.headers,
                        params=params,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    return BeautifulSoup(response.content, 'html.parser')
                except requests.RequestException as e:
                    if attempt == self.max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error fetching Amazon page: {e}")
            return None
    
    def parse_products(self, soup):
        """
        Parse products from soup
        Args:
            soup: BeautifulSoup object
        Returns:
            list: List of product dictionaries
        """
        products = []
        
        try:
            # Try multiple container selectors for flexibility
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            # If no results, try alternative selectors
            if not product_containers:
                product_containers = soup.find_all('div', {'class': lambda x: x and 's-result-item' in x})
            
            if not product_containers:
                product_containers = soup.find_all('div', {'class': lambda x: x and 'sg-col-inner' in x})
            
            for container in product_containers[:5]:  # Limit to 5 products
                try:
                    # Extract product name - be more aggressive about finding it
                    product_name = "N/A"
                    
                    # Try h2 first
                    name_elem = container.find('h2')
                    if name_elem:
                        product_name = name_elem.get_text(strip=True)
                    
                    # If still generic, try to get from span with more context
                    if product_name == "N/A" or len(product_name) < 10:
                        name_elem = container.find('a', {'class': lambda x: x and 's-underline' in x})
                        if name_elem:
                            product_name = name_elem.get_text(strip=True)
                    
                    # If still short, find the longest text element
                    if len(product_name) < 10:
                        spans = container.find_all('span')
                        longest = max(spans, key=lambda s: len(s.get_text(strip=True)), default=None)
                        if longest:
                            text = longest.get_text(strip=True)
                            if len(text) > 10 and len(text) < 300:
                                product_name = text
                    
                    # Remove extra text from product name
                    if len(product_name) > 200:
                        product_name = product_name[:200]
                    
                    # Extract price - get the first price element with actual value
                    price = None
                    price_elements = container.find_all('span', {'class': lambda x: x and 'a-price-whole' in x})
                    if price_elements:
                        # Take the first price element (usually the main price)
                        for price_elem in price_elements[:1]:
                            price_text = price_elem.get_text(strip=True)
                            cleaned_price = clean_price(price_text)
                            if cleaned_price:
                                price = cleaned_price
                                break
                    
                    # If still no price, try finding any price span
                    if not price:
                        price_elem = container.find('span', {'class': lambda x: x and 'a-price' in x})
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price = clean_price(price_text)
                    
                    # Extract rating - try multiple selectors
                    rating_elem = container.find('span', {'class': lambda x: x and 'a-icon-star' in x})
                    if rating_elem:
                        rating = clean_rating(rating_elem.get_text(strip=True))
                    else:
                        rating = None
                    
                    # Extract review count
                    review_elem = container.find('span', {'class': lambda x: x and 'a-size-base' in x})
                    review_count = 0
                    if review_elem:
                        review_count = clean_reviews(review_elem.get_text(strip=True))
                    
                    # Extract URL
                    url_elem = container.find('a', {'class': lambda x: x and 'a-link' in x})
                    if url_elem and url_elem.get('href'):
                        href = url_elem['href']
                        if href.startswith('/dp/'):
                            url = "https://www.amazon.in" + href
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = "https://www.amazon.in" + href
                    else:
                        url = "N/A"
                    
                    # Extract description
                    desc_elem = container.find('span', {'class': lambda x: x and 'a-size-body' in x})
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Only add if we have at least name and either price or rating
                    if product_name != "N/A" and (price or rating):
                        products.append({
                            'product_name': product_name,
                            'price': price,
                            'rating': rating,
                            'review_count': review_count,
                            'url': url,
                            'description': description
                        })
                except Exception as e:
                    logger.debug(f"Error parsing individual Amazon product: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(products)} products from Amazon")
            return products
        except Exception as e:
            logger.error(f"Error parsing Amazon products: {e}")
            return []
    
    def search(self, product_query):
        """
        Search for products on Amazon
        Args:
            product_query: Product to search
        Returns:
            list: List of product dictionaries
        """
        logger.info(f"Searching Amazon for: {product_query}")
        
        soup = self.fetch_page(product_query)
        if not soup:
            return []
        
        products = self.parse_products(soup)
        
        # Filter products to ensure they match the search query - EXTREMELY STRICT
        # Split query into keywords (exclude common words)
        query_keywords = []
        common_words = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        for word in product_query.lower().split():
            if word not in common_words and len(word) > 2:
                query_keywords.append(word)
        
        logger.info(f"Amazon search keywords required: {query_keywords}")
        
        # Log all parsed products for debugging
        logger.info(f"Parsed {len(products)} Amazon products:")
        for product in products:
            logger.info(f"  - {product['product_name'][:70]}")
        
        # Score products based on keyword matches
        # Accept ANY product that contains at least one keyword
        scored_products = []
        
        for product in products:
            product_name_lower = product['product_name'].lower()
            match_count = sum(1 for keyword in query_keywords if keyword in product_name_lower)
            
            if match_count > 0:
                # Has at least one matching keyword
                scored_products.append((product, match_count))
                logger.info(f"[AMAZON MATCH] {product['product_name'][:60]} ({match_count}/{len(query_keywords)} keywords)")
        
        # Sort by match count (highest first)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        filtered_products = [p[0] for p in scored_products]
        
        # Return all products that match at least one keyword
        if not filtered_products:
            logger.warning(f"Amazon: No products matched any keywords: {query_keywords}")
            logger.warning(f"Query keywords: {query_keywords} | Parsed {len(products)} products")
            return []
        
        if filtered_products:
            logger.info(f"Filtered Amazon results: {len(filtered_products)} products matched")
            return filtered_products
        
        return []