# Tech News System Test Suite

This directory contains comprehensive tests for the tech news fetching and summarization system.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_state_manager.py
│   ├── test_summarizer.py
│   └── test_digest_builder.py
├── integration/             # Integration tests for full workflows
│   └── test_full_workflow.py
├── fixtures/                # Test data and fixtures
│   └── sample_articles.py
├── conftest.py             # Pytest configuration and shared fixtures
└── README.md               # This file
```

## Running Tests

### Quick Test Run
```bash
# From the tech-news directory
python3 run_tests.py
```

### Manual Test Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only

# Run specific test files
pytest tests/unit/test_state_manager.py -v
pytest tests/integration/test_full_workflow.py -v
```

## Test Coverage

### Unit Tests (24 tests)

#### StateManager Tests
- ✅ Initialization and directory creation
- ✅ Last run time tracking (empty and populated)
- ✅ Processed articles tracking
- ✅ Failed articles tracking and retry logic
- ✅ Article filtering (new vs processed)
- ✅ Digest info detection

#### GeminiSummarizer Tests
- ✅ Initialization with configuration
- ✅ Article metadata extraction
- ✅ Content truncation for long articles
- ✅ Article summarization with mocked Gemini API
- ✅ Batch article processing with state tracking
- ✅ Error handling for invalid files

#### DigestBuilder Tests
- ✅ Initialization
- ✅ Chronological article sorting
- ✅ Article summary formatting
- ✅ New digest creation
- ✅ Existing digest updates
- ✅ Duplicate article handling
- ✅ Digest file management

### Integration Tests (3 tests)

#### Full Workflow Tests
- ✅ Complete end-to-end workflow (fetch → summarize → digest)
- ✅ Incremental processing (only new articles)
- ✅ Failed article retry logic

## Test Features

### Mocking
- **Gemini API**: All external API calls are mocked to avoid costs and dependencies
- **HTTP Requests**: Web scraping requests are mocked for reliable testing
- **RSS Feeds**: Feed parsing is mocked with sample data
- **File System**: Tests use temporary directories for isolation

### Fixtures
- **Sample Articles**: Realistic article content for testing
- **Configuration**: Mock configuration files for different scenarios
- **Temporary Directories**: Isolated test environments
- **State Data**: Pre-configured state for testing various scenarios

### Error Scenarios
- Invalid file paths
- Network timeouts
- API failures
- Malformed content
- Missing configuration

## Test Data

The `fixtures/sample_articles.py` file contains:
- Sample article content in markdown format
- RSS feed XML data
- HTML content for web scraping tests
- Various article metadata examples

## Configuration

Tests use `pytest.ini` for configuration:
- Verbose output (`-v`)
- Short traceback format (`--tb=short`)
- Strict marker enforcement
- Disabled warnings for cleaner output

## Dependencies

Test dependencies are included in `requirements.txt`:
- `pytest==7.4.3` - Test framework
- `pytest-mock==3.12.0` - Mocking utilities

## Test Results

All 27 tests pass successfully:
- ✅ 24 unit tests
- ✅ 3 integration tests
- ✅ 0 failures
- ⚠️ 1 warning (SSL library version - not critical)

## Adding New Tests

When adding new functionality:

1. **Unit Tests**: Add to appropriate `test_*.py` file in `unit/`
2. **Integration Tests**: Add to `test_full_workflow.py` in `integration/`
3. **Fixtures**: Add sample data to `fixtures/` if needed
4. **Mocking**: Use `@patch` decorators for external dependencies
5. **Naming**: Follow `test_*` naming convention

## Test Best Practices

- Use descriptive test names
- Test both success and failure scenarios
- Mock external dependencies
- Use fixtures for common test data
- Keep tests isolated and independent
- Test edge cases and error conditions
