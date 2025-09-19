#!/usr/bin/env python3
"""
Test runner for the tech-news system
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with pytest"""
    
    # Change to the tech-news directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Install test dependencies
    print("Installing test dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    
    # Run tests
    print("\nRunning tests...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'tests/', 
        '-v', 
        '--tb=short',
        '--color=yes'
    ])
    
    return result.returncode

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
