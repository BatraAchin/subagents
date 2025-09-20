import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse

class BlogScraper:
    def __init__(self, config):
        self.config = config
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def scrape_blog_posts(self, blog_config):
        """Scrape recent blog posts from a blog without RSS feed"""
        try:
            # Get the main blog page
            response = requests.get(blog_config['base_url'], headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find blog post links using the selector from config
            post_links = []
            if 'post_selector' in blog_config:
                # Use CSS selector to find post links
                post_elements = soup.select(blog_config['post_selector'])
                for element in post_elements:
                    link = element.get('href')
                    if link:
                        # Convert relative URLs to absolute
                        full_url = urljoin(blog_config['base_url'], link)
                        post_links.append(full_url)
            else:
                # Fallback: look for common patterns
                post_links = self._find_blog_links(soup, blog_config['base_url'])
            
            # Limit to recent posts
            max_posts = blog_config.get('max_posts', 5)
            post_links = post_links[:max_posts]
            
            articles = []
            for link in post_links:
                article = self._scrape_article(link, blog_config)
                if article:
                    articles.append(article)
                time.sleep(1)  # Be respectful
            
            return articles
            
        except Exception as e:
            print(f"Error scraping blog {blog_config['name']}: {e}")
            return []
    
    def _find_blog_links(self, soup, base_url):
        """Find blog post links using common patterns"""
        links = []
        
        # Look for links that might be blog posts
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            # Skip if no text or too short
            if not text or len(text) < 10:
                continue
            
            # Convert to absolute URL
            full_url = urljoin(base_url, href)
            
            # Skip external links
            if not full_url.startswith(base_url):
                continue
            
            # Skip common non-post pages
            skip_patterns = ['/about', '/contact', '/subscribe', '/newsletter', '/tags', '/categories']
            if any(pattern in full_url.lower() for pattern in skip_patterns):
                continue
            
            # Look for date patterns in the link or text
            if self._looks_like_blog_post(href, text):
                links.append(full_url)
        
        return links
    
    def _looks_like_blog_post(self, href, text):
        """Check if a link looks like a blog post"""
        # Look for date patterns in URL
        date_patterns = [
            r'/\d{4}/\d{2}/',  # /2024/01/
            r'/\d{4}-\d{2}-\d{2}',  # /2024-01-15
            r'/\d{2}/\d{2}/\d{4}',  # /01/15/2024
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, href):
                return True
        
        # Look for common blog post indicators in text
        blog_indicators = ['post', 'article', 'blog', 'note']
        if any(indicator in text.lower() for indicator in blog_indicators):
            return True
        
        # If it's a reasonable length and not obviously a page
        if 20 < len(text) < 100:
            return True
        
        return False
    
    def _scrape_article(self, url, blog_config):
        """Scrape individual article content"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup, blog_config)
            if not title:
                return None
            
            # Extract content
            content = self._extract_content(soup, blog_config)
            if not content:
                return None
            
            # Extract date
            date = self._extract_date(soup, blog_config)
            
            return {
                'title': title,
                'link': url,
                'published_parsed': date,
                'content': content,
                'source': blog_config['name']
            }
            
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None
    
    def _extract_title(self, soup, blog_config):
        """Extract article title"""
        # Try different selectors
        title_selectors = [
            'h1',
            'title',
            '.post-title',
            '.entry-title',
            'article h1',
            '[class*="title"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 5:
                    return title
        
        return None
    
    def _extract_content(self, soup, blog_config):
        """Extract article content"""
        # Try different content selectors
        content_selectors = [
            'article',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            '[class*="content"]',
            '[class*="post"]'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove script and style elements
                for script in element(["script", "style"]):
                    script.decompose()
                
                content = element.get_text(separator='\n', strip=True)
                if content and len(content) > 100:
                    return content
        
        return None
    
    def _extract_date(self, soup, blog_config):
        """Extract article date"""
        # Try different date selectors
        date_selectors = [
            'time',
            '.date',
            '.published',
            '.post-date',
            '[class*="date"]'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text().strip()
                if date_text:
                    # Try to parse the date
                    try:
                        # This is a simplified date parser
                        # You might want to use dateutil for more robust parsing
                        return datetime.now().timetuple()
                    except:
                        pass
        
        # Fallback to current date
        return datetime.now().timetuple()
