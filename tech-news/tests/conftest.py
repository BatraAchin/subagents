import pytest
import tempfile
import os
import shutil
from datetime import datetime

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_article_content():
    """Sample article content for testing"""
    return """# Test Article Title

**Source:** Test Source
**Date:** 2025-09-19 10:00
**URL:** https://example.com/test-article

---

This is a test article about AI and machine learning. It contains some technical content that would be useful for developers and engineers working in the field.

Key points:
- Machine learning is transforming industries
- AI tools are becoming more accessible
- Developers need to stay updated with latest trends

The article discusses various frameworks and methodologies that are relevant to modern software development.
"""

@pytest.fixture
def sample_article_metadata():
    """Sample article metadata for testing"""
    return {
        'title': 'Test Article Title',
        'source': 'Test Source',
        'date': '2025-09-19 10:00',
        'url': 'https://example.com/test-article',
        'content': 'This is a test article about AI and machine learning...',
        'filename': 'test-article-2025-09-19.md'
    }

@pytest.fixture
def sample_summary():
    """Sample article summary for testing"""
    return {
        'title': 'Test Article Title',
        'source': 'Test Source',
        'date': '2025-09-19 10:00',
        'url': 'https://example.com/test-article',
        'summary': '• Key insight about AI development\n• Important framework mentioned\n• Practical implications for developers',
        'filename': 'test-article-2025-09-19.md'
    }

@pytest.fixture
def mock_gemini_config():
    """Mock Gemini configuration for testing"""
    return {
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
