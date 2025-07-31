#!/usr/bin/env python3
"""
Test runner for Drx.MediMate project
Run all tests with: python run_tests.py
"""

import os
import sys
import subprocess
import unittest

def run_tests():
    """Run all tests using unittest"""
    print("🧪 Running Drx.MediMate Tests...")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
        return 1

def run_with_pytest():
    """Alternative: Run tests with pytest if available"""
    try:
        subprocess.run([sys.executable, "-m", "pytest"], check=True)
        return 0
    except subprocess.CalledProcessError:
        return 1
    except FileNotFoundError:
        print("pytest not found, falling back to unittest")
        return run_tests()

if __name__ == "__main__":
    # Try pytest first, fallback to unittest
    if len(sys.argv) > 1 and sys.argv[1] == "--unittest":
        exit_code = run_tests()
    else:
        exit_code = run_with_pytest()
    
    sys.exit(exit_code)
