import os
from datetime import datetime
import re

class DigestBuilder:
    def __init__(self, config, state_manager=None):
        self.config = config
        self.state_manager = state_manager
    
    def sort_articles_chronologically(self, summaries):
        """Sort articles by date (newest first)"""
        def parse_date(date_str):
            try:
                # Try to parse various date formats
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    return datetime.strptime(date_str.split()[0], '%Y-%m-%d')
            except:
                return datetime.min  # Put unparseable dates at the end
        
        return sorted(summaries, key=lambda x: parse_date(x['date']), reverse=True)
    
    def format_article_summary(self, article):
        """Format a single article summary"""
        # Clean up the title for display
        title = article['title']
        if len(title) > 80:
            title = title[:77] + "..."
        
        # Format the summary with proper structure
        summary_lines = article['summary'].split('\n')
        formatted_summary = []
        
        for line in summary_lines:
            line = line.strip()
            if line:
                # Handle different types of formatting
                if line.startswith('##'):
                    # Section headers - make them bold
                    formatted_summary.append(f"\n**{line[2:].strip()}**")
                elif line.startswith('###'):
                    # Subsection headers - make them italic
                    formatted_summary.append(f"\n*{line[3:].strip()}*")
                elif line.startswith('- ') or line.startswith('• '):
                    # Bullet points - keep as is
                    formatted_summary.append(f"  {line}")
                elif line.startswith('  - ') or line.startswith('  • '):
                    # Sub-bullet points - keep as is
                    formatted_summary.append(f"    {line[2:]}")
                else:
                    # Regular text - add bullet point
                    formatted_summary.append(f"  • {line}")
        
        summary_text = '\n'.join(formatted_summary)
        
        # Create the formatted entry
        entry = f"""### [{title}]({article['url']})
**{article['source']}** • {article['date']}

{summary_text}

---"""
        
        return entry
    
    def build_daily_digest(self, summaries, output_dir, is_update=False):
        """Build or update the daily digest"""
        if not summaries:
            return None
        
        # Sort articles chronologically
        sorted_summaries = self.sort_articles_chronologically(summaries)
        
        # Get today's date for filename
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if digest already exists
        filename = f"{today}-daily-digest.md"
        filepath = os.path.join(output_dir, filename)
        
        if is_update and os.path.exists(filepath):
            # Update existing digest
            return self.update_existing_digest(filepath, sorted_summaries)
        else:
            # Create new digest
            return self.create_new_digest(filepath, sorted_summaries)
    
    def create_new_digest(self, filepath, sorted_summaries):
        """Create a new daily digest"""
        digest_content = f"""# Daily Tech News Digest - {datetime.now().strftime('%Y-%m-%d')}

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Summary
Today's digest contains {len(sorted_summaries)} articles from {len(set(s['source'] for s in sorted_summaries))} sources, covering the latest developments in AI, technology, and software development.

## Articles

"""
        
        # Add each article
        for article in sorted_summaries:
            digest_content += self.format_article_summary(article) + "\n\n"
        
        # Add footer
        digest_content += f"""
## Sources
{', '.join(sorted(set(s['source'] for s in sorted_summaries)))}

---
*This digest was automatically generated from Substack feeds.*
"""
        
        # Save digest
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        return filepath
    
    def update_existing_digest(self, filepath, new_summaries):
        """Update existing digest with new articles"""
        try:
            # Read existing digest
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Extract existing article URLs to avoid duplicates
            existing_urls = set()
            url_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(url_pattern, existing_content):
                existing_urls.add(match.group(2))
            
            # Filter out articles that already exist
            new_articles = [article for article in new_summaries 
                          if article['url'] not in existing_urls]
            
            if not new_articles:
                print("  No new articles to add to existing digest")
                return filepath
            
            # Find insertion point (before the Sources section)
            sources_pattern = r'\n## Sources\n'
            match = re.search(sources_pattern, existing_content)
            
            if match:
                # Insert new articles before Sources section
                insertion_point = match.start()
                new_articles_text = ""
                for article in new_articles:
                    new_articles_text += self.format_article_summary(article) + "\n\n"
                
                updated_content = (existing_content[:insertion_point] + 
                                 new_articles_text + 
                                 existing_content[insertion_point:])
                
                # Update the summary count
                total_articles = len(re.findall(r'### \[', updated_content))
                summary_pattern = r"Today's digest contains \d+ articles"
                updated_content = re.sub(summary_pattern, 
                                       f"Today's digest contains {total_articles} articles", 
                                       updated_content)
                
                # Update generation time
                time_pattern = r'\*Generated on \d{4}-\d{2}-\d{2} \d{2}:\d{2}\*'
                updated_content = re.sub(time_pattern, 
                                       f'*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}*', 
                                       updated_content)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"  ✅ Added {len(new_articles)} new articles to existing digest")
            else:
                # Fallback: append to end
                new_articles_text = "\n\n## New Articles\n\n"
                for article in new_articles:
                    new_articles_text += self.format_article_summary(article) + "\n\n"
                
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(new_articles_text)
                
                print(f"  ✅ Appended {len(new_articles)} new articles to digest")
            
            return filepath
            
        except Exception as e:
            print(f"  ❌ Error updating digest: {e}")
            # Fallback to creating new digest
            return self.create_new_digest(filepath, new_summaries)
