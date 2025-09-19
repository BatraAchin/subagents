import pytest
import json
import os
from datetime import datetime
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from state_manager import StateManager

class TestStateManager:
    
    def test_initialization(self, temp_dir):
        """Test StateManager initialization"""
        state_manager = StateManager(temp_dir)
        
        assert os.path.exists(temp_dir)
        assert state_manager.last_run_file == os.path.join(temp_dir, 'last_run.json')
        assert state_manager.processed_file == os.path.join(temp_dir, 'processed_articles.json')
    
    def test_get_last_run_time_empty(self, temp_dir):
        """Test getting last run time when no file exists"""
        state_manager = StateManager(temp_dir)
        last_run = state_manager.get_last_run_time()
        assert last_run is None
    
    def test_update_last_run_time(self, temp_dir):
        """Test updating last run time"""
        state_manager = StateManager(temp_dir)
        state_manager.update_last_run_time()
        
        last_run = state_manager.get_last_run_time()
        assert last_run is not None
        
        # Check that the timestamp is recent
        run_time = datetime.fromisoformat(last_run)
        now = datetime.now()
        time_diff = (now - run_time).total_seconds()
        assert time_diff < 5  # Should be within 5 seconds
    
    def test_get_processed_articles_empty(self, temp_dir):
        """Test getting processed articles when no file exists"""
        state_manager = StateManager(temp_dir)
        processed = state_manager.get_processed_articles()
        assert processed == set()
    
    def test_add_processed_articles(self, temp_dir):
        """Test adding processed articles"""
        state_manager = StateManager(temp_dir)
        
        articles = ['article1.md', 'article2.md', 'article3.md']
        state_manager.add_processed_articles(articles)
        
        processed = state_manager.get_processed_articles()
        assert processed == set(articles)
    
    def test_add_failed_articles(self, temp_dir):
        """Test adding failed articles"""
        state_manager = StateManager(temp_dir)
        
        failed_articles = ['failed1.md', 'failed2.md']
        state_manager.add_failed_articles(failed_articles)
        
        failed = state_manager.get_failed_articles()
        assert failed == set(failed_articles)
    
    def test_clear_failed_articles(self, temp_dir):
        """Test clearing failed articles"""
        state_manager = StateManager(temp_dir)
        
        # Add some failed articles
        failed_articles = ['failed1.md', 'failed2.md', 'failed3.md']
        state_manager.add_failed_articles(failed_articles)
        
        # Clear some of them
        state_manager.clear_failed_articles(['failed1.md'])
        
        failed = state_manager.get_failed_articles()
        assert failed == {'failed2.md', 'failed3.md'}
    
    def test_get_articles_to_process(self, temp_dir):
        """Test getting articles that need processing"""
        state_manager = StateManager(temp_dir)
        
        # Add some processed articles
        processed = ['processed1.md', 'processed2.md']
        state_manager.add_processed_articles(processed)
        
        # Add some failed articles
        failed = ['failed1.md', 'failed2.md']
        state_manager.add_failed_articles(failed)
        
        # All articles
        all_articles = [
            '/path/to/processed1.md',
            '/path/to/processed2.md',
            '/path/to/failed1.md',
            '/path/to/failed2.md',
            '/path/to/new1.md',
            '/path/to/new2.md'
        ]
        
        to_process = state_manager.get_articles_to_process(all_articles)
        
        # Should include failed articles and new articles, but not processed ones
        expected = {'failed1.md', 'failed2.md', 'new1.md', 'new2.md'}
        actual = {os.path.basename(f) for f in to_process}
        assert actual == expected
    
    def test_get_digest_info_no_digest(self, temp_dir):
        """Test getting digest info when no digest exists"""
        state_manager = StateManager(temp_dir)
        digest_info = state_manager.get_digest_info()
        
        assert digest_info['exists'] is False
    
    def test_get_digest_info_with_digest(self, temp_dir):
        """Test getting digest info when digest exists"""
        state_manager = StateManager(temp_dir)
        
        # Create a mock digest file
        digests_dir = os.path.join(os.path.dirname(temp_dir), 'digests')
        os.makedirs(digests_dir, exist_ok=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        digest_file = os.path.join(digests_dir, f'{today}-daily-digest.md')
        
        with open(digest_file, 'w') as f:
            f.write("# Daily Digest\nTest content")
        
        digest_info = state_manager.get_digest_info()
        
        assert digest_info['exists'] is True
        assert digest_info['date'] == today
        assert os.path.exists(digest_info['path'])
        
        # Cleanup
        os.remove(digest_file)
        os.rmdir(digests_dir)
