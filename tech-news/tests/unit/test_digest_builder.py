import pytest
import os
import tempfile
import sys
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from digest_builder import DigestBuilder

class TestDigestBuilder:
    
    def test_initialization(self, mock_gemini_config):
        """Test DigestBuilder initialization"""
        builder = DigestBuilder(mock_gemini_config['summarization'])
        
        assert builder.config == mock_gemini_config['summarization']
        assert builder.state_manager is None
    
    def test_sort_articles_chronologically(self, mock_gemini_config):
        """Test sorting articles by date"""
        builder = DigestBuilder(mock_gemini_config['summarization'])
        
        summaries = [
            {'date': '2025-09-19 10:00', 'title': 'Article 1'},
            {'date': '2025-09-18 15:30', 'title': 'Article 2'},
            {'date': '2025-09-20 08:00', 'title': 'Article 3'},
            {'date': '2025-09-19 14:00', 'title': 'Article 4'}
        ]
        
        sorted_summaries = builder.sort_articles_chronologically(summaries)
        
        # Should be sorted newest first
        assert sorted_summaries[0]['title'] == 'Article 3'  # 2025-09-20
        assert sorted_summaries[1]['title'] == 'Article 1'  # 2025-09-19 10:00 (same day, earlier time)
        assert sorted_summaries[2]['title'] == 'Article 4'  # 2025-09-19 14:00 (same day, later time)
        assert sorted_summaries[3]['title'] == 'Article 2'  # 2025-09-18
    
    def test_format_article_summary(self, mock_gemini_config, sample_summary):
        """Test formatting article summary"""
        builder = DigestBuilder(mock_gemini_config['summarization'])
        
        formatted = builder.format_article_summary(sample_summary)
        
        # Check that it contains the title as a link
        assert f"[{sample_summary['title']}]({sample_summary['url']})" in formatted
        
        # Check that it contains source and date
        assert sample_summary['source'] in formatted
        assert sample_summary['date'] in formatted
        
        # Check that it contains the summary content (with proper indentation)
        summary_lines = sample_summary['summary'].split('\n')
        for line in summary_lines:
            if line.strip():  # Skip empty lines
                assert line.strip() in formatted
        
        # Check that it has proper markdown formatting
        assert formatted.startswith('### [')
        assert '---' in formatted
    
    def test_create_new_digest(self, mock_gemini_config, temp_dir, sample_summary):
        """Test creating a new daily digest"""
        builder = DigestBuilder(mock_gemini_config['summarization'])
        
        summaries = [sample_summary]
        filepath = os.path.join(temp_dir, 'test-digest.md')
        
        result = builder.create_new_digest(filepath, summaries)
        
        assert result == filepath
        assert os.path.exists(filepath)
        
        # Read and check content
        with open(filepath, 'r') as f:
            content = f.read()
        
        assert '# Daily Tech News Digest' in content
        assert sample_summary['title'] in content
        assert sample_summary['source'] in content
        assert 'Today\'s digest contains 1 articles' in content
    
    def test_update_existing_digest(self, mock_gemini_config, temp_dir, sample_summary):
        """Test updating existing digest with new articles"""
        builder = DigestBuilder(mock_gemini_config['summarization'])
        
        # Create initial digest
        filepath = os.path.join(temp_dir, 'test-digest.md')
        initial_summaries = [sample_summary]
        builder.create_new_digest(filepath, initial_summaries)
        
        # Create new article with different URL
        new_summary = sample_summary.copy()
        new_summary['url'] = 'https://example.com/new-article'
        new_summary['title'] = 'New Article Title'
        
        # Update digest
        result = builder.update_existing_digest(filepath, [new_summary])
        
        assert result == filepath
        
        # Read and check content
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Should contain both articles
        assert sample_summary['title'] in content
        assert new_summary['title'] in content
        
        # Should have updated article count
        assert 'Today\'s digest contains 2 articles' in content
    
    def test_update_existing_digest_no_new_articles(self, mock_gemini_config, temp_dir, sample_summary):
        """Test updating digest when no new articles"""
        builder = DigestBuilder(mock_gemini_config['summarization'])
        
        # Create initial digest
        filepath = os.path.join(temp_dir, 'test-digest.md')
        initial_summaries = [sample_summary]
        builder.create_new_digest(filepath, initial_summaries)
        
        # Try to update with same article (same URL)
        result = builder.update_existing_digest(filepath, [sample_summary])
        
        assert result == filepath
        
        # Read and check content - should still have only 1 article
        with open(filepath, 'r') as f:
            content = f.read()
        
        assert 'Today\'s digest contains 1 articles' in content
    
    def test_build_daily_digest_new(self, mock_gemini_config, temp_dir, sample_summary):
        """Test building new daily digest"""
        builder = DigestBuilder(mock_gemini_config['summarization'])
        
        summaries = [sample_summary]
        output_dir = temp_dir
        
        result = builder.build_daily_digest(summaries, output_dir, is_update=False)
        
        assert result is not None
        assert os.path.exists(result)
        
        # Check filename format
        filename = os.path.basename(result)
        assert filename.startswith(datetime.now().strftime('%Y-%m-%d'))
        assert filename.endswith('-daily-digest.md')
    
    def test_build_daily_digest_update(self, mock_gemini_config, temp_dir, sample_summary):
        """Test updating existing daily digest"""
        builder = DigestBuilder(mock_gemini_config['summarization'])
        
        # Create initial digest
        output_dir = temp_dir
        initial_result = builder.build_daily_digest([sample_summary], output_dir, is_update=False)
        
        # Update with new article
        new_summary = sample_summary.copy()
        new_summary['url'] = 'https://example.com/new-article'
        new_summary['title'] = 'New Article Title'
        
        update_result = builder.build_daily_digest([new_summary], output_dir, is_update=True)
        
        assert update_result == initial_result
        assert os.path.exists(update_result)
        
        # Check that both articles are in the digest
        with open(update_result, 'r') as f:
            content = f.read()
        
        assert sample_summary['title'] in content
        assert new_summary['title'] in content
