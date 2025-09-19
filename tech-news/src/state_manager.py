import json
import os
from datetime import datetime
from typing import List, Dict, Set

class StateManager:
    def __init__(self, state_dir):
        self.state_dir = state_dir
        self.last_run_file = os.path.join(state_dir, 'last_run.json')
        self.processed_file = os.path.join(state_dir, 'processed_articles.json')
        
        # Ensure state directory exists
        os.makedirs(state_dir, exist_ok=True)
    
    def get_last_run_time(self):
        """Get the timestamp of the last successful run"""
        if not os.path.exists(self.last_run_file):
            return None
        
        try:
            with open(self.last_run_file, 'r') as f:
                data = json.load(f)
                return data.get('timestamp')
        except (json.JSONDecodeError, KeyError):
            return None
    
    def update_last_run_time(self):
        """Update the last run timestamp to now"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        with open(self.last_run_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_processed_articles(self) -> Set[str]:
        """Get set of already processed article filenames"""
        if not os.path.exists(self.processed_file):
            return set()
        
        try:
            with open(self.processed_file, 'r') as f:
                data = json.load(f)
                return set(data.get('processed_articles', []))
        except (json.JSONDecodeError, KeyError):
            return set()
    
    def add_processed_articles(self, article_filenames: List[str]):
        """Add article filenames to the processed list"""
        processed = self.get_processed_articles()
        processed.update(article_filenames)
        
        data = {
            'processed_articles': list(processed),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.processed_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_failed_articles(self) -> Set[str]:
        """Get set of articles that failed to process"""
        if not os.path.exists(self.processed_file):
            return set()
        
        try:
            with open(self.processed_file, 'r') as f:
                data = json.load(f)
                return set(data.get('failed_articles', []))
        except (json.JSONDecodeError, KeyError):
            return set()
    
    def add_failed_articles(self, article_filenames: List[str]):
        """Add article filenames to the failed list for retry"""
        processed_data = {}
        if os.path.exists(self.processed_file):
            try:
                with open(self.processed_file, 'r') as f:
                    processed_data = json.load(f)
            except (json.JSONDecodeError, KeyError):
                pass
        
        failed = set(processed_data.get('failed_articles', []))
        failed.update(article_filenames)
        
        processed_data['failed_articles'] = list(failed)
        processed_data['last_updated'] = datetime.now().isoformat()
        
        with open(self.processed_file, 'w') as f:
            json.dump(processed_data, f, indent=2)
    
    def clear_failed_articles(self, article_filenames: List[str]):
        """Remove successfully processed articles from failed list"""
        if not os.path.exists(self.processed_file):
            return
        
        try:
            with open(self.processed_file, 'r') as f:
                data = json.load(f)
            
            failed = set(data.get('failed_articles', []))
            failed -= set(article_filenames)
            
            data['failed_articles'] = list(failed)
            data['last_updated'] = datetime.now().isoformat()
            
            with open(self.processed_file, 'w') as f:
                json.dump(data, f, indent=2)
        except (json.JSONDecodeError, KeyError):
            pass
    
    def get_articles_to_process(self, all_article_files: List[str]) -> List[str]:
        """Get list of articles that need processing (new + failed retries)"""
        processed = self.get_processed_articles()
        failed = self.get_failed_articles()
        
        # Include new articles and previously failed articles
        to_process = []
        for filepath in all_article_files:
            filename = os.path.basename(filepath)
            if filename not in processed or filename in failed:
                to_process.append(filepath)
        
        return to_process
    
    def get_digest_info(self) -> Dict:
        """Get information about existing digests"""
        digests_dir = os.path.join(os.path.dirname(self.state_dir), 'digests')
        if not os.path.exists(digests_dir):
            return {'exists': False}
        
        # Find today's digest
        today = datetime.now().strftime('%Y-%m-%d')
        today_digest = os.path.join(digests_dir, f'{today}-daily-digest.md')
        
        if os.path.exists(today_digest):
            return {
                'exists': True,
                'path': today_digest,
                'date': today
            }
        
        return {'exists': False}
