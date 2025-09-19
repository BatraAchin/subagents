"""
Sample article fixtures for testing
"""

SAMPLE_ARTICLE_1 = """# The Future of AI in Software Development

**Source:** Tech Weekly  
**Date:** 2025-09-19 10:00  
**URL:** https://techweekly.com/ai-software-development  

---

Artificial intelligence is revolutionizing how we write, test, and deploy software. From GitHub Copilot to automated testing frameworks, AI tools are becoming indispensable for modern developers.

Key developments include:
- Code generation and completion tools
- Automated testing and debugging
- Intelligent code review systems
- AI-powered deployment optimization

The article explores how these tools are changing the development workflow and what developers need to know to stay competitive in the AI era.
"""

SAMPLE_ARTICLE_2 = """# Machine Learning Operations Best Practices

**Source:** MLOps Today  
**Date:** 2025-09-19 14:30  
**URL:** https://mlops.today/best-practices  

---

MLOps is becoming critical as machine learning models move from research to production. This comprehensive guide covers the essential practices for managing ML workflows at scale.

Topics covered:
- Model versioning and tracking
- Automated model deployment
- Monitoring and observability
- Data pipeline management
- Model performance optimization

The article provides practical insights from industry leaders and real-world case studies of successful ML operations implementations.
"""

SAMPLE_ARTICLE_3 = """# The Rise of Edge Computing in AI

**Source:** Edge AI Insights  
**Date:** 2025-09-18 16:45  
**URL:** https://edgeai.insights/rise-edge-computing  

---

Edge computing is transforming how AI models are deployed and used in real-world applications. This article examines the latest trends and technologies in edge AI.

Key points:
- Reduced latency and improved performance
- Privacy and data sovereignty benefits
- Hardware acceleration for edge devices
- Challenges in model optimization
- Future outlook for edge AI adoption

The piece includes interviews with leading researchers and practitioners in the edge computing space.
"""

SAMPLE_RSS_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Tech News Feed</title>
    <link>https://example.com</link>
    <description>Latest technology news and insights</description>
    <item>
      <title>The Future of AI in Software Development</title>
      <link>https://techweekly.com/ai-software-development</link>
      <description>Artificial intelligence is revolutionizing software development...</description>
      <pubDate>Thu, 19 Sep 2025 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Machine Learning Operations Best Practices</title>
      <link>https://mlops.today/best-practices</link>
      <description>MLOps is becoming critical as ML models move to production...</description>
      <pubDate>Thu, 19 Sep 2025 14:30:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

SAMPLE_HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
    <title>Sample Article</title>
</head>
<body>
    <article>
        <header>
            <h1>The Future of AI in Software Development</h1>
            <div class="meta">
                <span class="author">Tech Writer</span>
                <span class="date">September 19, 2025</span>
            </div>
        </header>
        <div class="post-content">
            <p>Artificial intelligence is revolutionizing how we write, test, and deploy software.</p>
            <p>From GitHub Copilot to automated testing frameworks, AI tools are becoming indispensable for modern developers.</p>
            <h2>Key Developments</h2>
            <ul>
                <li>Code generation and completion tools</li>
                <li>Automated testing and debugging</li>
                <li>Intelligent code review systems</li>
                <li>AI-powered deployment optimization</li>
            </ul>
            <p>The article explores how these tools are changing the development workflow.</p>
        </div>
    </article>
</body>
</html>"""
