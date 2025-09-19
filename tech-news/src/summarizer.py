import google.generativeai as genai
import yaml
import os
from datetime import datetime
import re
from state_manager import StateManager

class GeminiSummarizer:
    def __init__(self, config_path, state_manager=None):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Configure Gemini
        genai.configure(api_key=self.config['gemini']['api_key'])
        self.model = genai.GenerativeModel(self.config['gemini']['model'])
        
        self.summary_config = self.config['summarization']
        self.state_manager = state_manager
    
    def extract_article_metadata(self, filepath):
        """Extract metadata from article markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title (first # heading)
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else "Unknown Title"
            
            # Extract source
            source_match = re.search(r'\*\*Source:\*\* (.+)', content)
            source = source_match.group(1) if source_match else "Unknown Source"
            
            # Extract date
            date_match = re.search(r'\*\*Date:\*\* (.+)', content)
            date = date_match.group(1) if date_match else "Unknown Date"
            
            # Extract URL
            url_match = re.search(r'\*\*URL:\*\* (.+)', content)
            url = url_match.group(1) if url_match else ""
            
            # Extract article content (after the --- separator)
            content_match = re.search(r'^---\s*\n(.*)$', content, re.DOTALL)
            article_content = content_match.group(1).strip() if content_match else content
            
            return {
                'title': title,
                'source': source,
                'date': date,
                'url': url,
                'content': article_content,
                'filename': os.path.basename(filepath)
            }
        except Exception as e:
            print(f"Error extracting metadata from {filepath}: {e}")
            return None
    
    def truncate_content(self, content, max_length):
        """Truncate content if too long"""
        if len(content) <= max_length:
            return content
        
        # Try to truncate at a sentence boundary
        truncated = content[:max_length]
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.8:  # If we can find a good break point
            return truncated[:last_period + 1] + "\n\n[Content truncated...]"
        else:
            return truncated + "\n\n[Content truncated...]"
    
    def summarize_article(self, article_metadata):
        """Summarize a single article using Gemini"""
        try:
            content = article_metadata['content']
            
            # Truncate if too long
            max_length = self.summary_config['max_article_length']
            content = self.truncate_content(content, max_length)
            
            # Create prompt for bullet point summary
            prompt = f"""Please provide a concise bullet-point summary of this AI/technology article. Focus on:

1. Key technical insights or findings
2. Important developments or announcements
3. Practical implications for developers/engineers
4. Notable tools, frameworks, or methodologies mentioned

Keep each bullet point to 1-2 sentences maximum. Be specific and technical.

Article Title: {article_metadata['title']}
Source: {article_metadata['source']}

Article Content:
{content}

Summary:"""

            # Generate summary
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            return {
                'title': article_metadata['title'],
                'source': article_metadata['source'],
                'date': article_metadata['date'],
                'url': article_metadata['url'],
                'summary': summary,
                'filename': article_metadata['filename']
            }
            
        except Exception as e:
            print(f"Error summarizing article {article_metadata['title']}: {e}")
            return None
    
    def summarize_articles(self, article_files):
        """Summarize multiple articles with retry logic"""
        summaries = []
        successful_files = []
        failed_files = []
        
        for filepath in article_files:
            filename = os.path.basename(filepath)
            print(f"  Summarizing: {filename}...")
            
            # Extract metadata
            metadata = self.extract_article_metadata(filepath)
            if not metadata:
                print(f"    Failed to extract metadata")
                failed_files.append(filename)
                continue
            
            # Summarize article
            summary = self.summarize_article(metadata)
            if summary:
                summaries.append(summary)
                successful_files.append(filename)
                print(f"    ✅ Success")
            else:
                print(f"    ❌ Failed to summarize")
                failed_files.append(filename)
        
        # Update state tracking
        if self.state_manager:
            if successful_files:
                self.state_manager.add_processed_articles(successful_files)
                self.state_manager.clear_failed_articles(successful_files)
            
            if failed_files:
                self.state_manager.add_failed_articles(failed_files)
        
        return summaries
