# Subagents

A collection of autonomous agents for specialized tasks. Currently featuring a tech news aggregation and summarization system.

## 🚀 Features

### Tech News Agent (`tech-news/`)
- **Automated Article Fetching**: Pulls latest articles from top AI/tech Substacks
- **AI-Powered Summarization**: Uses Gemini AI to create intelligent summaries
- **Incremental Processing**: Only processes new articles, avoiding duplicates
- **Daily Digest Generation**: Creates beautiful, organized daily summaries
- **Retry Logic**: Automatically retries failed articles on subsequent runs

## 📋 Supported Sources

- **Latent Space** - AI engineering insights and deep dives
- **The Sequence** - Concise AI research breakdowns
- **Exponential View** - Systems-level tech analysis
- **MLOps Roundup** - Production ML operations and tools

## 🛠️ Quick Start

### Prerequisites
- Python 3.9+
- Google AI API key (for summarization)

### Installation

#### Option 1: Global Command Installation (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/BatraAchin/subagents.git
   cd subagents
   ```

2. **Install globally**
   ```bash
   ./install.sh
   ```

3. **Configure API key**
   ```bash
   # Edit the config file
   nano tech-news/config/gemini.yaml
   ```

4. **Use from anywhere**
   ```bash
   # Fetch articles only
   fetch-tech-news
   
   # Fetch and create daily digest
   fetch-tech-news --summarize
   ```

#### Option 2: Local Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/BatraAchin/subagents.git
   cd subagents
   ./setup.sh
   ```

2. **Run locally**
   ```bash
   # From the subagents directory
   ./fetch-tech-news --summarize
   ```

#### Uninstallation

To remove the global command:
```bash
cd subagents
./uninstall.sh
```

## 📁 Project Structure

```
subagents/
├── tech-news/                 # Tech news aggregation agent
│   ├── src/                   # Source code
│   │   ├── main.py           # CLI entry point
│   │   ├── fetcher.py        # Article fetching logic
│   │   ├── summarizer.py     # AI summarization
│   │   ├── digest_builder.py # Digest generation
│   │   └── state_manager.py  # State tracking
│   ├── config/               # Configuration files
│   │   ├── substacks.yaml   # Substack sources
│   │   └── gemini.yaml      # AI API configuration
│   ├── articles/             # Downloaded articles
│   ├── digests/              # Generated daily digests
│   ├── .state/               # Processing state
│   ├── tests/                # Comprehensive test suite
│   └── requirements.txt      # Python dependencies
└── README.md                 # This file
```

## 🔧 Configuration

### Adding New Sources
Edit `tech-news/config/substacks.yaml`:
```yaml
substacks:
  - name: "Your Source"
    slug: "your-source"
    rss_url: "https://yoursource.com/feed"
    base_url: "https://yoursource.com"
```

### Customizing Summarization
Edit `tech-news/config/gemini.yaml`:
```yaml
gemini:
  api_key: "your-api-key"
  model: "gemini-1.5-flash"
  temperature: 0.3

summarization:
  max_article_length: 50000
  summary_style: "bullet_points"
  digest_format: "chronological"
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
cd tech-news
python3 run_tests.py
```

**Test Coverage:**
- ✅ 27 tests (24 unit + 3 integration)
- ✅ 100% component coverage
- ✅ Mocked external dependencies
- ✅ Error scenario testing

## 📊 Usage Examples

### Daily Workflow
```bash
# Morning: Fetch and summarize latest articles
./fetch-tech-news --summarize

# Afternoon: Check for new articles (incremental)
./fetch-tech-news --summarize
```

### Output
The system generates:
- **Individual Articles**: `articles/source-date-title.md`
- **Daily Digest**: `digests/YYYY-MM-DD-daily-digest.md`

## 🔄 Incremental Processing

The system intelligently handles:
- **New Articles**: Only processes articles since last run
- **Failed Articles**: Automatically retries on next run
- **Duplicate Prevention**: Never re-processes completed articles
- **Digest Updates**: Appends new articles to existing daily digest

## 🎯 Key Features

### Smart State Management
- Tracks processed articles to avoid duplicates
- Maintains retry queue for failed articles
- Preserves processing state across runs

### AI-Powered Summarization
- Uses Gemini AI for high-quality summaries
- Focuses on technical insights and practical implications
- Generates bullet-point summaries with source links

### Flexible Configuration
- Easy to add new Substack sources
- Customizable summarization parameters
- Configurable article limits and formats

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Substack** for providing RSS feeds
- **Google AI** for Gemini API
- **Open source community** for the amazing tools and libraries

## 📈 Roadmap

- [ ] Add more news sources
- [ ] Email digest delivery
- [ ] Web interface for digest viewing
- [ ] Custom summarization prompts
- [ ] Article categorization and tagging
- [ ] Analytics and usage tracking

---

**Built with ❤️ for the developer community**
