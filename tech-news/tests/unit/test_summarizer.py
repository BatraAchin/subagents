import pytest
import os
import tempfile
import sys
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from summarizer import GeminiSummarizer

class TestGeminiSummarizer:
    
    @patch('summarizer.genai')
    def test_initialization(self, mock_genai, temp_dir, mock_gemini_config):
        """Test GeminiSummarizer initialization"""
        config_file = os.path.join(temp_dir, 'config.yaml')
        
        # Write mock config
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(mock_gemini_config, f)
        
        summarizer = GeminiSummarizer(config_file)
        
        assert summarizer.config == mock_gemini_config
        assert summarizer.summary_config == mock_gemini_config['summarization']
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once()
    
    def test_extract_article_metadata(self, temp_dir, sample_article_content):
        """Test extracting metadata from article file"""
        # Create a mock state manager
        from state_manager import StateManager
        state_manager = StateManager(temp_dir)
        
        # Create mock config
        config_file = os.path.join(temp_dir, 'config.yaml')
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump({'gemini': {'api_key': 'test', 'model': 'test'}, 'summarization': {}}, f)
        
        summarizer = GeminiSummarizer(config_file, state_manager)
        
        # Create test article file
        article_file = os.path.join(temp_dir, 'test-article.md')
        with open(article_file, 'w') as f:
            f.write(sample_article_content)
        
        metadata = summarizer.extract_article_metadata(article_file)
        
        assert metadata is not None
        assert metadata['title'] == 'Test Article Title'
        assert metadata['source'] == 'Test Source'
        assert metadata['date'] == '2025-09-19 10:00'
        assert metadata['url'] == 'https://example.com/test-article'
        assert 'This is a test article about AI' in metadata['content']
        assert metadata['filename'] == 'test-article.md'
    
    def test_extract_article_metadata_invalid_file(self, temp_dir):
        """Test extracting metadata from invalid file"""
        from state_manager import StateManager
        state_manager = StateManager(temp_dir)
        
        config_file = os.path.join(temp_dir, 'config.yaml')
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump({'gemini': {'api_key': 'test', 'model': 'test'}, 'summarization': {}}, f)
        
        summarizer = GeminiSummarizer(config_file, state_manager)
        
        # Test with non-existent file
        metadata = summarizer.extract_article_metadata('/non/existent/file.md')
        assert metadata is None
    
    def test_truncate_content(self, temp_dir):
        """Test content truncation"""
        from state_manager import StateManager
        state_manager = StateManager(temp_dir)
        
        config_file = os.path.join(temp_dir, 'config.yaml')
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump({'gemini': {'api_key': 'test', 'model': 'test'}, 'summarization': {}}, f)
        
        summarizer = GeminiSummarizer(config_file, state_manager)
        
        # Test short content (should not be truncated)
        short_content = "This is short content."
        result = summarizer.truncate_content(short_content, 1000)
        assert result == short_content
        
        # Test long content (should be truncated)
        long_content = "This is a very long article. " * 1000  # Much longer than 100 chars
        result = summarizer.truncate_content(long_content, 100)
        assert len(result) <= 100 + 50  # Allow some buffer for truncation message
        assert "[Content truncated...]" in result
    
    @patch('summarizer.genai')
    def test_summarize_article(self, mock_genai, temp_dir, sample_article_metadata):
        """Test summarizing a single article"""
        from state_manager import StateManager
        state_manager = StateManager(temp_dir)
        
        # Mock the model response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "• Key insight about AI\n• Important development\n• Practical implications"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        config_file = os.path.join(temp_dir, 'config.yaml')
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump({
                'gemini': {'api_key': 'test', 'model': 'test'},
                'summarization': {'max_article_length': 50000}
            }, f)
        
        summarizer = GeminiSummarizer(config_file, state_manager)
        
        result = summarizer.summarize_article(sample_article_metadata)
        
        assert result is not None
        assert result['title'] == sample_article_metadata['title']
        assert result['source'] == sample_article_metadata['source']
        assert result['date'] == sample_article_metadata['date']
        assert result['url'] == sample_article_metadata['url']
        assert 'Key insight about AI' in result['summary']
        assert result['filename'] == sample_article_metadata['filename']
        
        # Verify the model was called
        mock_model.generate_content.assert_called_once()
    
    @patch('summarizer.genai')
    def test_summarize_articles(self, mock_genai, temp_dir, sample_article_content):
        """Test summarizing multiple articles"""
        from state_manager import StateManager
        state_manager = StateManager(temp_dir)
        
        # Mock the model response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "• Test summary point 1\n• Test summary point 2"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        config_file = os.path.join(temp_dir, 'config.yaml')
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump({
                'gemini': {'api_key': 'test', 'model': 'test'},
                'summarization': {'max_article_length': 50000}
            }, f)
        
        summarizer = GeminiSummarizer(config_file, state_manager)
        
        # Create test article files
        article_files = []
        for i in range(3):
            article_file = os.path.join(temp_dir, f'test-article-{i}.md')
            with open(article_file, 'w') as f:
                f.write(sample_article_content.replace('Test Article Title', f'Test Article {i}'))
            article_files.append(article_file)
        
        summaries = summarizer.summarize_articles(article_files)
        
        assert len(summaries) == 3
        for i, summary in enumerate(summaries):
            assert summary['title'] == f'Test Article {i}'
            assert 'Test summary point 1' in summary['summary']
        
        # Verify state was updated
        processed = state_manager.get_processed_articles()
        assert len(processed) == 3
        assert 'test-article-0.md' in processed
        assert 'test-article-1.md' in processed
        assert 'test-article-2.md' in processed
