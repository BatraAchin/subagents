#!/usr/bin/env python3
"""
Tech News Fetcher - Fetch latest articles from AI/tech Substacks and create daily digest
"""

import os
import sys
import argparse
import glob
from fetcher import SubstackFetcher
from summarizer import GeminiSummarizer
from digest_builder import DigestBuilder
from state_manager import StateManager
from synthesis_analyzer import SynthesisAnalyzer

def main():
    parser = argparse.ArgumentParser(description='Fetch and summarize tech news from Substacks')
    parser.add_argument('--summarize', action='store_true', 
                       help='Create daily digest after fetching articles')
    parser.add_argument('--synthesize', action='store_true',
                       help='Analyze all articles and create synthesis post')
    args = parser.parse_args()
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    substacks_config = os.path.join(script_dir, '..', 'config', 'substacks.yaml')
    gemini_config = os.path.join(script_dir, '..', 'config', 'gemini.yaml')
    state_dir = os.path.join(script_dir, '..', '.state')
    
    # Check if config files exist
    if not os.path.exists(substacks_config):
        print(f"Error: Substack config file not found at {substacks_config}")
        sys.exit(1)
    
    if args.summarize and not os.path.exists(gemini_config):
        print(f"Error: Gemini config file not found at {gemini_config}")
        sys.exit(1)
    
    # Initialize state manager
    state_manager = StateManager(state_dir)
    
    print("🚀 Starting Tech News Fetcher...")
    print("=" * 50)
    
    try:
        # Only fetch articles if not doing synthesis only
        if not args.synthesize:
            # Initialize fetcher
            fetcher = SubstackFetcher(substacks_config)
            
            # Fetch articles
            results = fetcher.fetch_latest_articles()
        
        # Print fetch summary only if we fetched articles
        if not args.synthesize:
            print("\n" + "=" * 50)
            print("📊 FETCH SUMMARY")
            print("=" * 50)
            
            if results['success']:
                print(f"✅ Successfully fetched {len(results['success'])} articles:")
                for article in results['success']:
                    print(f"  • {article['substack']}: {article['title'][:60]}...")
            
            if results['failed']:
                print(f"\n❌ Failed to fetch from {len(results['failed'])} sources:")
                for source in results['failed']:
                    print(f"  • {source}")
            
            print(f"\n📁 Articles saved to: {os.path.join(script_dir, '..', 'articles')}")
        
        # Summarize if requested
        if args.summarize:
            print("\n" + "=" * 50)
            print("🤖 CREATING DAILY DIGEST")
            print("=" * 50)
            
            # Get all article files
            articles_dir = os.path.join(script_dir, '..', 'articles')
            all_article_files = glob.glob(os.path.join(articles_dir, '*.md'))
            
            if not all_article_files:
                print("No articles found to summarize")
                return
            
            # Get articles that need processing (new + failed retries)
            articles_to_process = state_manager.get_articles_to_process(all_article_files)
            
            if not articles_to_process:
                print("No new articles to process (all articles already summarized)")
                return
            
            print(f"Found {len(articles_to_process)} articles to process ({len(all_article_files)} total articles)")
            
            # Check if digest already exists for today
            digest_info = state_manager.get_digest_info()
            is_update = digest_info['exists']
            
            if is_update:
                print(f"📄 Updating existing digest: {digest_info['path']}")
            else:
                print("📄 Creating new daily digest")
            
            # Initialize summarizer with state manager
            summarizer = GeminiSummarizer(gemini_config, state_manager)
            
            # Summarize articles
            summaries = summarizer.summarize_articles(articles_to_process)
            
            if summaries:
                print(f"✅ Successfully summarized {len(summaries)} articles")
                
                # Build or update digest
                digest_builder = DigestBuilder(summarizer.summary_config, state_manager)
                digests_dir = os.path.join(script_dir, '..', 'digests')
                digest_path = digest_builder.build_daily_digest(summaries, digests_dir, is_update)
                
                if digest_path:
                    print(f"📄 Daily digest saved to: {digest_path}")
                    # Update last run time
                    state_manager.update_last_run_time()
                else:
                    print("❌ Failed to create daily digest")
            else:
                print("❌ No articles were successfully summarized")
        
        # Synthesis if requested
        if args.synthesize:
            print("\n" + "=" * 50)
            print("🧠 CREATING SYNTHESIS ANALYSIS")
            print("=" * 50)
            
            if not os.path.exists(gemini_config):
                print(f"Error: Gemini config file not found at {gemini_config}")
                return
            
            # Initialize synthesis analyzer
            analyzer = SynthesisAnalyzer(gemini_config, state_manager)
            
            # Analyze all articles
            articles = analyzer.analyze_all_articles()
            if not articles:
                print("No articles found to analyze")
                return
            
            print(f"Analyzing {len(articles)} articles for cross-cutting themes...")
            
            # Generate synthesis
            synthesis_text = analyzer.synthesize_insights(articles)
            if synthesis_text:
                # Save synthesis
                synthesis_path = analyzer.save_synthesis(synthesis_text)
                if synthesis_path:
                    print(f"📄 Synthesis analysis saved to: {synthesis_path}")
                else:
                    print("❌ Failed to save synthesis analysis")
            else:
                print("❌ Failed to generate synthesis analysis")
        
        print("\n✨ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
