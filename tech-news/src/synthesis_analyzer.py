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
You are a technology analyst writing an original analysis piece based on recent developments in AI and technology. 

Below are {len(articles)} recent articles from top tech newsletters and blogs that you've been following. Your task is to write an original analysis piece that:

1. **Identifies the 3-5 most significant cross-cutting themes** you've observed across the tech landscape
2. **Analyzes the most important technical developments** you're seeing emerge
3. **Examines patterns in industry trends** and market dynamics you've noticed
4. **Identifies emerging opportunities and challenges** you believe are worth highlighting
5. **Provides your original insights and analysis** for developers, engineers, and tech leaders

Write this as YOUR original analysis and commentary. Use the articles as reference material to support your points, but present this as your own insights and observations about the current state of technology. Structure it with clear sections, reference specific developments to support your analysis, and provide concrete takeaways based on your expertise.

Here are the recent articles you've been following:

{combined_text}

Write a comprehensive analysis piece that showcases your insights and analysis of the current technology landscape.
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
        header = f"""# Tech Analysis: {datetime.now().strftime('%B %d, %Y')}

*Published on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

*My analysis of the current technology landscape, based on recent developments across AI, software development, and emerging tech trends.*

---

"""
        
        full_content = header + synthesis_text
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return filepath
