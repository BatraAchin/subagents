import feedparser
import requests
from bs4 import BeautifulSoup
import yaml
import os
from datetime import datetime
import re
from urllib.parse import urljoin
import time

class SubstackFetcher:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.substacks = self.config['substacks']
        self.settings = self.config['settings']
        
    def fetch_rss_feed(self, rss_url):
        """Fetch and parse RSS feed"""
        try:
            feed = feedparser.parse(rss_url)
            if feed.bozo:
                print(f"Warning: RSS feed may have issues: {rss_url}")
            return feed
        except Exception as e:
            print(f"Error fetching RSS feed {rss_url}: {e}")
            return None
    
    def extract_article_content(self, article_url):
        """Extract full article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(article_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find article content - Substack specific selectors
            content_selectors = [
                'div[data-testid="post-content"]',
                'div.post-content',
                'div.entry-content',
                'article',
                'div[class*="post"]'
            ]
            
            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if not content:
                # Fallback: try to get the main content area
                content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'post|content'))
            
            if content:
                # Clean up the content
                for script in content(["script", "style"]):
                    script.decompose()
                
                # Convert to markdown-like text
                text = content.get_text(separator='\n', strip=True)
                return text
            else:
                print(f"Could not extract content from: {article_url}")
                return None
                
        except Exception as e:
            print(f"Error extracting content from {article_url}: {e}")
            return None
    
    def sanitize_filename(self, title):
        """Create a safe filename from article title"""
        # Remove special characters and limit length
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        return safe_title[:50]  # Limit length
    
    def format_article_filename(self, substack_slug, title, pub_date):
        """Create formatted filename for article"""
        date_str = pub_date.strftime('%Y-%m-%d')
        safe_title = self.sanitize_filename(title)
        return f"{substack_slug}-{date_str}-{safe_title}.md"
    
    def save_article(self, article, substack, content):
        """Save article to markdown file"""
        try:
            # Parse publication date
            pub_date = datetime(*article.published_parsed[:6])
            
            # Create filename
            filename = self.format_article_filename(
                substack['slug'], 
                article.title, 
                pub_date
            )
            
            # Create articles directory if it doesn't exist
            articles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'articles')
            os.makedirs(articles_dir, exist_ok=True)
            
            filepath = os.path.join(articles_dir, filename)
            
            # Prepare markdown content
            markdown_content = f"""# {article.title}

**Source:** {substack['name']}  
**Date:** {pub_date.strftime('%Y-%m-%d %H:%M')}  
**URL:** {article.link}  

---

{content}
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return filepath
            
        except Exception as e:
            print(f"Error saving article: {e}")
            return None
    
    def fetch_latest_articles(self):
        """Fetch latest articles from all configured Substacks"""
        results = {
            'success': [],
            'failed': []
        }
        
        for substack in self.substacks:
            print(f"\nFetching from {substack['name']}...")
            
            # Fetch RSS feed
            feed = self.fetch_rss_feed(substack['rss_url'])
            if not feed or not feed.entries:
                print(f"No articles found for {substack['name']}")
                results['failed'].append(substack['name'])
                continue
            
            # Get latest articles (limit by config)
            max_articles = self.settings.get('max_articles_per_source', 3)
            articles = feed.entries[:max_articles]
            
            for i, article in enumerate(articles, 1):
                print(f"  Processing article {i}/{len(articles)}: {article.title[:60]}...")
                
                # Extract full content
                content = self.extract_article_content(article.link)
                if not content:
                    print(f"    Failed to extract content")
                    continue
                
                # Save article
                filepath = self.save_article(article, substack, content)
                if filepath:
                    print(f"    Saved: {os.path.basename(filepath)}")
                    results['success'].append({
                        'substack': substack['name'],
                        'title': article.title,
                        'file': filepath
                    })
                else:
                    print(f"    Failed to save article")
                
                # Be respectful to the server
                time.sleep(1)
        
        return results
