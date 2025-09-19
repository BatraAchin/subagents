import pytest
import os
import tempfile
import sys
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from state_manager import StateManager
from summarizer import GeminiSummarizer
from digest_builder import DigestBuilder

class TestFullWorkflow:
    
    @patch('summarizer.genai')
    @patch('requests.get')
    @patch('feedparser.parse')
    def test_complete_workflow(self, mock_feedparser, mock_requests, mock_genai, temp_dir):
        """Test the complete workflow from fetching to digest creation"""
        
        # Setup mock feedparser
        mock_feed = Mock()
        mock_feed.entries = [
            Mock(
                title="Test Article 1",
                link="https://example.com/article1",
                published_parsed=(2025, 9, 19, 10, 0, 0, 0, 0, 0)
            ),
            Mock(
                title="Test Article 2", 
                link="https://example.com/article2",
                published_parsed=(2025, 9, 19, 11, 0, 0, 0, 0, 0)
            )
        ]
        mock_feedparser.return_value = mock_feed
        
        # Setup mock requests
        mock_response = Mock()
        mock_response.content = b'<html><body><div class="post-content">Test article content about AI and machine learning.</div></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Setup mock Gemini
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "• Key insight about AI\n• Important development\n• Practical implications"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create test configuration
        config_dir = os.path.join(temp_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        import yaml
        
        # Substack config
        substacks_config = {
            'substacks': [
                {
                    'name': 'Test Substack',
                    'slug': 'test-substack',
                    'rss_url': 'https://test.substack.com/feed',
                    'base_url': 'https://test.substack.com'
                }
            ],
            'settings': {
                'max_articles_per_source': 3,
                'output_format': 'markdown',
                'include_metadata': True
            }
        }
        
        with open(os.path.join(config_dir, 'substacks.yaml'), 'w') as f:
            yaml.dump(substacks_config, f)
        
        # Gemini config
        gemini_config = {
            'gemini': {
                'api_key': 'test-api-key',
                'model': 'gemini-1.5-flash',
                'max_tokens': 8192,
                'temperature': 0.3
            },
            'summarization': {
                'max_article_length': 50000,
                'summary_style': 'bullet_points',
                'include_links': True,
                'digest_format': 'chronological'
            }
        }
        
        with open(os.path.join(config_dir, 'gemini.yaml'), 'w') as f:
            yaml.dump(gemini_config, f)
        
        # Initialize components
        state_manager = StateManager(os.path.join(temp_dir, '.state'))
        summarizer = GeminiSummarizer(os.path.join(config_dir, 'gemini.yaml'), state_manager)
        digest_builder = DigestBuilder(gemini_config['summarization'], state_manager)
        
        # Test article processing workflow
        articles_dir = os.path.join(temp_dir, 'articles')
        os.makedirs(articles_dir, exist_ok=True)
        
        # Simulate article files
        article_files = []
        for i in range(2):
            article_file = os.path.join(articles_dir, f'test-article-{i}.md')
            with open(article_file, 'w') as f:
                f.write(f"""# Test Article {i}

**Source:** Test Substack  
**Date:** 2025-09-19 10:00  
**URL:** https://example.com/article{i}  

---

This is test article {i} about AI and machine learning.
""")
            article_files.append(article_file)
        
        # Test summarization
        summaries = summarizer.summarize_articles(article_files)
        
        assert len(summaries) == 2
        assert all('Key insight about AI' in s['summary'] for s in summaries)
        
        # Test digest creation
        digests_dir = os.path.join(temp_dir, 'digests')
        digest_path = digest_builder.build_daily_digest(summaries, digests_dir)
        
        assert digest_path is not None
        assert os.path.exists(digest_path)
        
        # Verify digest content
        with open(digest_path, 'r') as f:
            content = f.read()
        
        assert 'Daily Tech News Digest' in content
        assert 'Test Article 0' in content
        assert 'Test Article 1' in content
        assert 'Test Substack' in content
        
        # Test state tracking
        processed = state_manager.get_processed_articles()
        assert len(processed) == 2
        assert 'test-article-0.md' in processed
        assert 'test-article-1.md' in processed
    
    def test_incremental_processing(self, temp_dir):
        """Test incremental processing - only new articles"""
        
        # Create test configuration
        config_dir = os.path.join(temp_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        import yaml
        
        gemini_config = {
            'gemini': {
                'api_key': 'test-api-key',
                'model': 'gemini-1.5-flash',
                'max_tokens': 8192,
                'temperature': 0.3
            },
            'summarization': {
                'max_article_length': 50000,
                'summary_style': 'bullet_points',
                'include_links': True,
                'digest_format': 'chronological'
            }
        }
        
        with open(os.path.join(config_dir, 'gemini.yaml'), 'w') as f:
            yaml.dump(gemini_config, f)
        
        # Initialize state manager
        state_manager = StateManager(os.path.join(temp_dir, '.state'))
        
        # Simulate some already processed articles
        state_manager.add_processed_articles(['old-article-1.md', 'old-article-2.md'])
        
        # Create test article files (mix of old and new)
        articles_dir = os.path.join(temp_dir, 'articles')
        os.makedirs(articles_dir, exist_ok=True)
        
        all_articles = [
            os.path.join(articles_dir, 'old-article-1.md'),
            os.path.join(articles_dir, 'old-article-2.md'),
            os.path.join(articles_dir, 'new-article-1.md'),
            os.path.join(articles_dir, 'new-article-2.md')
        ]
        
        for article_file in all_articles:
            with open(article_file, 'w') as f:
                f.write(f"""# {os.path.basename(article_file)}

**Source:** Test Source  
**Date:** 2025-09-19 10:00  
**URL:** https://example.com/{os.path.basename(article_file)}  

---

Test content for {os.path.basename(article_file)}.
""")
        
        # Test getting articles to process
        articles_to_process = state_manager.get_articles_to_process(all_articles)
        
        # Should only include new articles
        assert len(articles_to_process) == 2
        assert 'new-article-1.md' in [os.path.basename(f) for f in articles_to_process]
        assert 'new-article-2.md' in [os.path.basename(f) for f in articles_to_process]
        assert 'old-article-1.md' not in [os.path.basename(f) for f in articles_to_process]
        assert 'old-article-2.md' not in [os.path.basename(f) for f in articles_to_process]
    
    def test_retry_failed_articles(self, temp_dir):
        """Test retry logic for failed articles"""
        
        # Initialize state manager
        state_manager = StateManager(os.path.join(temp_dir, '.state'))
        
        # Add some failed articles
        state_manager.add_failed_articles(['failed-article-1.md', 'failed-article-2.md'])
        
        # Create test article files
        articles_dir = os.path.join(temp_dir, 'articles')
        os.makedirs(articles_dir, exist_ok=True)
        
        all_articles = [
            os.path.join(articles_dir, 'failed-article-1.md'),
            os.path.join(articles_dir, 'failed-article-2.md'),
            os.path.join(articles_dir, 'new-article-1.md')
        ]
        
        for article_file in all_articles:
            with open(article_file, 'w') as f:
                f.write(f"""# {os.path.basename(article_file)}

**Source:** Test Source  
**Date:** 2025-09-19 10:00  
**URL:** https://example.com/{os.path.basename(article_file)}  

---

Test content for {os.path.basename(article_file)}.
""")
        
        # Test getting articles to process
        articles_to_process = state_manager.get_articles_to_process(all_articles)
        
        # Should include both failed articles and new articles
        assert len(articles_to_process) == 3
        filenames = [os.path.basename(f) for f in articles_to_process]
        assert 'failed-article-1.md' in filenames
        assert 'failed-article-2.md' in filenames
        assert 'new-article-1.md' in filenames
