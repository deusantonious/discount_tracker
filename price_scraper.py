import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re
import time
from urllib.parse import urlparse

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False


class PriceScraper:
    """Web scraper to extract price and title from product pages."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })

    def scrape_product(self, url: str) -> Dict[str, Optional[str]]:
        """
        Scrape product information from URL.
        Returns dict with 'title' and 'price' keys.
        """
        try:
            # First request to get cookies
            domain = self.get_domain(url)
            base_url = f"https://{domain}"
            try:
                self.session.get(base_url, timeout=10)
                time.sleep(0.5)
            except requests.RequestException:
                pass  # Continue even if base URL fails

            response = self.session.get(url, timeout=15, allow_redirects=True)

            # If blocked, retry with cloudscraper
            if response.status_code == 403 and HAS_CLOUDSCRAPER:
                scraper = cloudscraper.create_scraper()
                response = scraper.get(url, timeout=15)

            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Try to extract title
            title = self._extract_title(soup)

            # Try to extract price
            price = self._extract_price(soup, response.text)

            return {
                'title': title,
                'price': price,
                'success': True
            }

        except requests.RequestException as e:
            return {
                'title': None,
                'price': None,
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'title': None,
                'price': None,
                'success': False,
                'error': f"Parsing error: {str(e)}"
            }

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title from page."""
        # Try common title selectors
        selectors = [
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'title'}),
            ('h1', {}),
            ('title', {})
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()

                if title:
                    return title[:200]  # Limit length

        return None

    def _extract_price(self, soup: BeautifulSoup, html: str) -> Optional[float]:
        """
        Extract the actual/discounted price from page.
        Prioritizes sale/discount price over original price.
        """
        # 1. Try sale/discount-specific selectors first (these are the actual price you pay)
        price = self._extract_sale_price(soup)
        if price:
            return price

        # 2. Try meta tags (usually contain the current/sale price)
        price = self._extract_price_from_meta(soup)
        if price:
            return price

        # 3. Try JSON-LD structured data (most reliable)
        price = self._extract_price_from_jsonld(html)
        if price:
            return price

        # 4. Try common CSS selectors, preferring lowest price
        price = self._extract_price_from_selectors(soup)
        if price:
            return price

        # 5. Try regex patterns as last resort
        price = self._extract_price_from_patterns(html)
        if price:
            return price

        return None

    def _extract_sale_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract sale/discount price — the actual price a customer pays."""
        # Sale price selectors (checked first — these are the discounted price)
        sale_selectors = [
            {'class': re.compile(r'sale.?price|special.?price|discount.?price|final.?price|offer.?price', re.I)},
            {'class': re.compile(r'price.?sale|price.?special|price.?discount|price.?final|price.?current', re.I)},
            {'class': re.compile(r'price.?new|new.?price|price.?now|now.?price', re.I)},
            {'class': re.compile(r'price--sale|price--current|price--special', re.I)},
            {'class': re.compile(r'promo.?price|actual.?price', re.I)},
            {'data-price-type': 'finalPrice'},
            {'data-price-type': 'salePrice'},
        ]

        for selector in sale_selectors:
            elements = soup.find_all(['span', 'div', 'p', 'ins', 'meta'], selector, limit=3)
            for element in elements:
                # Skip elements that are inside a "was"/"old" price container
                parent_classes = ' '.join(element.parent.get('class', [])) if element.parent else ''
                if re.search(r'old|original|was|before|compare|regular|list', parent_classes, re.I):
                    continue

                text = element.get('content', '') or element.get_text()
                price = self._parse_price(text)
                if price:
                    return price

        # WooCommerce / common pattern: <ins> inside price contains the sale price
        ins_elements = soup.find_all('ins')
        for ins in ins_elements:
            parent_classes = ' '.join(ins.parent.get('class', [])) if ins.parent else ''
            if re.search(r'price', parent_classes, re.I):
                price = self._parse_price(ins.get_text())
                if price:
                    return price

        return None

    def _extract_price_from_meta(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from meta tags."""
        # Sale price meta tags first
        meta_tags = [
            ('meta', {'property': 'product:sale_price:amount'}),
            ('meta', {'property': 'og:price:amount'}),
            ('meta', {'property': 'product:price:amount'}),
            ('meta', {'itemprop': 'price'}),
        ]

        for tag, attrs in meta_tags:
            element = soup.find(tag, attrs)
            if element:
                content = element.get('content', '')
                price = self._parse_price(content)
                if price:
                    return price

        return None

    def _extract_price_from_jsonld(self, html: str) -> Optional[float]:
        """Extract price from JSON-LD structured data (schema.org)."""
        import json

        # Find JSON-LD blocks
        jsonld_pattern = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.DOTALL | re.IGNORECASE
        )

        for block in jsonld_pattern:
            try:
                data = json.loads(block)
                price = self._find_price_in_jsonld(data)
                if price:
                    return price
            except (json.JSONDecodeError, ValueError):
                continue

        return None

    def _find_price_in_jsonld(self, data) -> Optional[float]:
        """Recursively find the best price in JSON-LD data."""
        if isinstance(data, list):
            for item in data:
                price = self._find_price_in_jsonld(item)
                if price:
                    return price
            return None

        if not isinstance(data, dict):
            return None

        # Check for Offer/AggregateOffer with price
        offers = data.get('offers', data)
        if isinstance(offers, list):
            prices = []
            for offer in offers:
                p = self._find_price_in_jsonld(offer)
                if p:
                    prices.append(p)
            # Return the lowest price (the sale/discounted price)
            return min(prices) if prices else None

        # Direct price fields — prefer lowPrice/sale price
        for key in ['lowPrice', 'price']:
            val = offers.get(key) if isinstance(offers, dict) else None
            if val is not None:
                price = self._parse_price(str(val))
                if price:
                    return price

        # Recurse into nested objects
        if isinstance(data, dict):
            for key in ['offers', 'mainEntity', '@graph']:
                if key in data:
                    price = self._find_price_in_jsonld(data[key])
                    if price:
                        return price

        return None

    def _extract_price_from_selectors(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price using common CSS selectors, preferring the lowest (sale) price."""
        selectors = [
            {'class': re.compile(r'price', re.I)},
            {'itemprop': 'price'},
            {'class': re.compile(r'cost', re.I)},
            {'id': re.compile(r'price', re.I)},
        ]

        all_prices = []
        for selector in selectors:
            elements = soup.find_all(['span', 'div', 'p', 'meta'], selector, limit=10)
            for element in elements:
                # Skip elements marked as old/original price
                classes = ' '.join(element.get('class', []))
                if re.search(r'old|original|was|before|compare|regular|list|crossed|line-?through', classes, re.I):
                    continue
                # Also check for line-through style (strikethrough = old price)
                style = element.get('style', '')
                if 'line-through' in style:
                    continue

                text = element.get('content', '') or element.get_text()
                price = self._parse_price(text)
                if price:
                    all_prices.append(price)

        # Return the lowest reasonable price (most likely the sale price)
        if all_prices:
            return min(all_prices)

        return None

    def _extract_price_from_patterns(self, html: str) -> Optional[float]:
        """Extract price using regex patterns."""
        # Look for JSON "salePrice" or "sale_price" first
        sale_patterns = [
            r'"(?:sale_?[Pp]rice|special_?[Pp]rice|final_?[Pp]rice|discount(?:ed)?_?[Pp]rice)"[:\s]*["\']?(\d+(?:\.\d{1,2})?)',
        ]

        for pattern in sale_patterns:
            matches = re.findall(pattern, html)
            for match in matches[:3]:
                price = self._parse_price(match)
                if price and 0.01 < price < 1000000:
                    return price

        # General price patterns
        patterns = [
            r'[\$€£₴]\s*(\d+(?:[.,]\d{3})*(?:[.,]\d{2}))',  # $1,234.56
            r'(\d+(?:[.,]\d{3})*(?:[.,]\d{2}))\s*[\$€£₴]',  # 1,234.56$
            r'"price["\s:]+(\d+(?:\.\d{2})?)"',              # "price": 123.45
        ]

        all_prices = []
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches[:5]:
                price = self._parse_price(match)
                if price and 0.01 < price < 1000000:
                    all_prices.append(price)

        # Return lowest (most likely the discounted price)
        if all_prices:
            return min(all_prices)

        return None

    def _parse_price(self, text: str) -> Optional[float]:
        """Parse price from text string."""
        if not text:
            return None

        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d.,]', '', str(text))

        if not cleaned:
            return None

        # Handle different decimal separators
        # If there are multiple commas/periods, the last one is likely decimal
        if ',' in cleaned and '.' in cleaned:
            # Determine which is decimal separator (usually the last one)
            if cleaned.rindex(',') > cleaned.rindex('.'):
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Check if comma is decimal separator (European format)
            if cleaned.count(',') == 1 and len(cleaned.split(',')[1]) == 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')

        try:
            price = float(cleaned)
            # Validate reasonable price range
            if 0.01 <= price <= 1000000:
                return round(price, 2)
        except ValueError:
            pass

        return None

    def get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "Unknown"
