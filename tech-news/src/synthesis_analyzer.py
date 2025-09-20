import os
import yaml
import google.generativeai as genai
from datetime import datetime
import json

class SynthesisAnalyzer:
    def __init__(self, config_path, state_manager):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Configure Gemini
        genai.configure(api_key=self.config['gemini']['api_key'])
        self.model = genai.GenerativeModel(self.config['gemini']['model'])
        self.state_manager = state_manager
    
    def analyze_all_articles(self):
        """Read all articles and analyze for common themes"""
        articles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'articles')
        
        if not os.path.exists(articles_dir):
            print("No articles directory found")
            return None
        
        articles = []
        for filename in os.listdir(articles_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(articles_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    articles.append({
                        'filename': filename,
                        'content': content
                    })
        
        print(f"Found {len(articles)} articles to analyze")
        return articles
    
    def synthesize_insights(self, articles):
        """Use Gemini to analyze articles and synthesize insights"""
        
        # Prepare article summaries for analysis
        article_texts = []
        for article in articles:
            # Extract title and first 2000 characters of content
            lines = article['content'].split('\n')
            title = lines[0].replace('# ', '') if lines else article['filename']
            content_preview = article['content'][:2000] + "..." if len(article['content']) > 2000 else article['content']
            
            article_texts.append(f"**{title}**\n{content_preview}\n---\n")
        
        combined_text = "\n".join(article_texts)
        
        prompt = f"""
You are a technology analyst tasked with synthesizing insights from multiple AI and technology articles. 

Below are {len(articles)} recent articles from top tech newsletters and blogs. Your job is to:

1. **Identify the 3-5 most significant cross-cutting themes** that appear across multiple articles
2. **Extract the most important technical developments** mentioned
3. **Find common patterns in industry trends** and market dynamics
4. **Identify emerging opportunities and challenges** that multiple sources are highlighting
5. **Synthesize actionable insights** for developers, engineers, and tech leaders

Write a comprehensive analysis that reads like a high-quality tech newsletter post. Structure it with clear sections, use specific examples from the articles, and provide concrete takeaways.

Here are the articles to analyze:

{combined_text}

Please provide a well-structured analysis that would be valuable for a technical audience interested in AI, software development, and technology trends.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating synthesis: {e}")
            return None
    
    def save_synthesis(self, synthesis_text):
        """Save the synthesized analysis to a file"""
        if not synthesis_text:
            return None
        
        # Create synthesis directory
        synthesis_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'synthesis')
        os.makedirs(synthesis_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        filename = f"synthesis_{timestamp}.md"
        filepath = os.path.join(synthesis_dir, filename)
        
        # Add header and metadata
        header = f"""# Tech News Synthesis - {datetime.now().strftime('%B %d, %Y')}

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

*This analysis synthesizes insights from multiple AI and technology sources to identify cross-cutting themes and emerging trends.*

---

"""
        
        full_content = header + synthesis_text
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return filepath
