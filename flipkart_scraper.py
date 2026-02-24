"""
Flipkart product scraper
"""
import requests
from bs4 import BeautifulSoup
import logging
from config import FLIPKART_BASE_URL, USER_AGENT, REQUEST_TIMEOUT, MAX_RETRIES
from utils import clean_price, clean_rating, clean_reviews

logger = logging.getLogger(__name__)

class FlipkartScraper:
    """Scrape product data from Flipkart"""
    
    def __init__(self):
        """Initialize Flipkart scraper"""
        self.base_url = FLIPKART_BASE_URL
        self.headers = {
            'User-Agent': USER_AGENT
        }
        self.timeout = REQUEST_TIMEOUT
        self.max_retries = MAX_RETRIES
    
    def fetch_page(self, product_query):
        """
        Fetch Flipkart search page
        Args:
            product_query: Product to search
        Returns:
            BeautifulSoup object or None
        """
        try:
            params = {
                'q': product_query
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
            logger.error(f"Error fetching Flipkart page: {e}")
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
            import re
            
            products_found = {}  # Use dict to avoid duplicates
            
            # Strategy: Look for all links that point to product pages (contain /p/)
            product_links = soup.find_all('a', href=re.compile(r'/p/'))
            
            if not product_links:
                # Fallback: Find all divs with prices and extract product info
                all_divs = soup.find_all('div')
                
                for div in all_divs:
                    try:
                        text = div.get_text(strip=True)
                        
                        # Skip empty or very long divs
                        if not text or len(text) > 2000:
                            continue
                        
                        # Look for price pattern ₹XXXXX
                        price_match = re.search(r'₹[\d,]+', text)
                        if not price_match:
                            continue
                        
                        price_str = price_match.group()
                        price = clean_price(price_str)
                        
                        if not price:
                            continue
                        
                        # Extract product name from closest product link
                        product_name = "N/A"
                        url = "N/A"
                        
                        # Search for product links in this div and parent divs
                        search_element = div
                        for _ in range(5):
                            if search_element:
                                prod_link = search_element.find('a', href=re.compile(r'/p/'))
                                if prod_link:
                                    product_name = prod_link.get_text(strip=True)
                                    url = prod_link['href']
                                    break
                                search_element = search_element.parent
                        
                        # If still no product name found, look for any meaningful link text
                        if product_name == "N/A":
                            search_element = div
                            for _ in range(3):
                                if search_element:
                                    link = search_element.find('a', href=True)
                                    if link:
                                        link_text = link.get_text(strip=True)
                                        # Filter out category names
                                        category_keywords = ['electronics', 'mobiles', 'accessories', 'home', 'fashion', 'categories', 'filters']
                                        if (link_text and len(link_text) > 5 and len(link_text) < 300 and
                                            not any(cat in link_text.lower() for cat in category_keywords)):
                                            product_name = link_text
                                            url = link['href']
                                            break
                                    search_element = search_element.parent
                        
                        # Format URL
                        if url != "N/A":
                            if url.startswith('/p/'):
                                url = "https://www.flipkart.com" + url
                            elif not url.startswith('http'):
                                url = "https://www.flipkart.com" + url
                        
                        # Look for rating
                        rating = None
                        rating_match = re.search(r'(\d+\.?\d*)\s*(★|⭐|out of)', text)
                        if rating_match:
                            rating = clean_rating(rating_match.group(1))
                        
                        # Create unique key to avoid duplicates
                        product_key = f"{product_name}_{price}".lower()
                        
                        # Only add valid products
                        if (product_name != "N/A" and 
                            product_key not in products_found and 
                            len(products_found) < 5):
                            
                            products_found[product_key] = {
                                'product_name': product_name[:250],
                                'price': price,
                                'rating': rating,
                                'review_count': 0,
                                'url': url,
                                'description': ""
                            }
                            
                    except Exception as e:
                        logger.debug(f"Error processing div: {e}")
                        continue
            else:
                # Process product links directly
                for link in product_links:
                    try:
                        # PRIORITY: Get product name from title attribute (not truncated)
                        # Fall back to link text if title not available
                        product_name = link.get('title', '')
                        if not product_name:
                            product_name = link.get_text(strip=True)
                        
                        url = link.get('href', 'N/A')
                        
                        if not product_name or len(product_name) < 3:
                            continue
                        
                        # SKIP PRICE LINKS: If visible text contains price info (e.g., "₹1,345₹3,50061% off"),
                        # it's not a product name, it's a price link on the product page
                        visible_text = link.get_text(strip=True)
                        if re.search(r'₹[\d,]+.*(?:off|%)', visible_text):
                            # This is a price link, not a product name, skip it
                            continue
                        
                        # Also get parent div text to capture size info that might be separate
                        parent_text = link.parent.get_text(strip=True) if link.parent else ""
                        
                        # Combine product name with parent text if parent has size info
                        # Example: parent might contain "150 g" or "14 oz" separately
                        if parent_text and len(parent_text) > len(product_name):
                            # Check if parent text contains size info that's not in product_name
                            size_patterns = [r'\d+\s*(?:oz|ounces|g|ml|kg|lb|lbs)', r'\d+\.?\d*\s*(?:oz|ounces)']
                            for pattern in size_patterns:
                                if re.search(pattern, parent_text, re.IGNORECASE) and not re.search(pattern, product_name, re.IGNORECASE):
                                    # Extract size from parent and append to product name
                                    size_match = re.search(pattern, parent_text, re.IGNORECASE)
                                    if size_match:
                                        size_info = size_match.group()
                                        product_name = f"{product_name} {size_info}"
                                        break
                        
                        # Clean up product name - remove UI elements and metadata
                        # Remove common UI buttons and text
                        ui_elements = ['add to compare', 'add to', 'currently unavailable']
                        product_name_clean = product_name

                        
                        for ui in ui_elements:
                            product_name_clean = re.sub(ui, '', product_name_clean, flags=re.IGNORECASE)
                        
                        # Remove rating stars and ratings (e.g., "4.6★" or "4,20,676")
                        product_name_clean = re.sub(r'(\d+\.?\d*)\s*[★⭐]', '', product_name_clean)
                        product_name_clean = re.sub(r'\d{1,2}\.\s*$', '', product_name_clean)  # Remove trailing "4." etc
                        product_name_clean = re.sub(r'\d{1,3},\d{1,3},\d+\s*', '', product_name_clean)  # Remove review counts
                        
                        # Just take the text as is - it's the product name from the link
                        # The link text should be the product title, not cluttered with ratings
                        product_name = product_name_clean.strip()
                        
                        # Final cleanup - remove any trailing commas and dots (but keep size info like "7-oz" or "14 oz")
                        product_name = re.sub(r'[,\s]+$', '', product_name).strip()
                        
                        if not product_name or len(product_name) < 3:
                            continue
                        
                        # Find price in parent elements
                        price = None
                        current = link
                        for _ in range(10):
                            if current:
                                text = current.get_text(strip=True)
                                price_match = re.search(r'₹[\d,]+', text)
                                if price_match:
                                    price = clean_price(price_match.group())
                                    if price:
                                        break
                                current = current.parent
                        
                        if not price:
                            continue
                        
                        # Find rating if available
                        rating = None
                        current = link
                        for _ in range(10):
                            if current:
                                text = current.get_text(strip=True)
                                rating_match = re.search(r'(\d+\.?\d*)\s*(★|⭐)', text)
                                if rating_match:
                                    rating = clean_rating(rating_match.group(1))
                                    if rating:
                                        break
                                current = current.parent
                        
                        # Format URL
                        if url.startswith('/p/'):
                            url = "https://www.flipkart.com" + url
                        elif not url.startswith('http'):
                            url = "https://www.flipkart.com" + url
                        
                        # Avoid duplicates
                        product_key = f"{product_name}_{price}".lower()
                        
                        if product_key not in products_found and len(products_found) < 5:
                            products_found[product_key] = {
                                'product_name': product_name[:250],
                                'price': price,
                                'rating': rating,
                                'review_count': 0,
                                'url': url,
                                'description': ""
                            }
                    
                    except Exception as e:
                        logger.debug(f"Error processing product link: {e}")
                        continue
            
            # Convert dict to list
            products = list(products_found.values())
            
            logger.info(f"Successfully parsed {len(products)} products from Flipkart")
            return products
        except Exception as e:
            logger.error(f"Error parsing Flipkart products: {e}")
            return []
            
            # Convert dict to list
            products = list(products_found.values())
            
            logger.info(f"Successfully parsed {len(products)} products from Flipkart")
            return products
        except Exception as e:
            logger.error(f"Error parsing Flipkart products: {e}")
            return []
    
    def search(self, product_query):
        """
        Search for products on Flipkart
        Args:
            product_query: Product to search
        Returns:
            list: List of product dictionaries
        """
        logger.info(f"Searching Flipkart for: {product_query}")
        
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
        
        logger.info(f"Flipkart search keywords required: {query_keywords}")
        
        # Score products based on keyword matches
        # Try to find exact matches first, then fall back to partial matches
        scored_products = []
        partial_matches = []
        
        for product in products:
            product_name_lower = product['product_name'].lower()
            match_count = sum(1 for keyword in query_keywords if keyword in product_name_lower)
            match_percentage = (match_count / len(query_keywords)) * 100 if query_keywords else 0
            
            if match_count == len(query_keywords):
                # Exact match - all keywords present
                scored_products.append((product, match_count))
                logger.info(f"[FLIPKART MATCH] FLIPKART MATCH: {product['product_name'][:60]} (ALL {match_count}/{len(query_keywords)} keywords)")
            elif match_count >= max(1, len(query_keywords) - 1):
                # Partial match - missing 1 or fewer keywords (for fallback)
                missing_keywords = [kw for kw in query_keywords if kw not in product_name_lower]
                partial_matches.append((product, match_count))
                logger.debug(f"Partial match: {product['product_name'][:60]} (missing: {missing_keywords})")
            else:
                missing_keywords = [kw for kw in query_keywords if kw not in product_name_lower]
                logger.debug(f"Rejected: {product['product_name'][:60]} (missing too many: {missing_keywords})")
        
        # Sort by match count (highest first)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        partial_matches.sort(key=lambda x: x[1], reverse=True)
        
        filtered_products = [p[0] for p in scored_products]
        
        # If no exact matches found, use partial matches as fallback
        if not filtered_products:
            if partial_matches:
                logger.warning(f"Flipkart: No exact matches for ALL keywords, using partial matches ({len(partial_matches)} found)")
                filtered_products = [p[0] for p in partial_matches]
            else:
                logger.warning(f"Flipkart: No products matched keywords: {query_keywords}")
                return []
        
        if filtered_products:
            logger.info(f"Filtered Flipkart results: {len(filtered_products)} products matched")
            return filtered_products
        
        return []