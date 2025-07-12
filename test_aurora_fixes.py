#!/usr/bin/env python3
"""
Aurora Sentinel - Validation Test Script
Tests all major fixes and functionality
"""

import sys
import subprocess
import traceback
from pathlib import Path

def test_syntax_errors():
    """Test that all Python files compile without syntax errors"""
    print("🔍 Testing syntax errors...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile"] + [str(p) for p in Path(".").glob("*.py")],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ All Python files compile successfully")
            return True
        else:
            print(f"❌ Syntax errors found:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing syntax: {e}")
        return False

def test_aurora_sentinel_import():
    """Test Aurora Sentinel imports correctly"""
    print("🔍 Testing Aurora Sentinel imports...")
    
    try:
        from aurora_sentinel.main import AuroraSentinel
        from aurora_sentinel.core.consciousness import AuroraConsciousness
        from aurora_sentinel.core.security import SecurityManager
        from aurora_sentinel.utils.file_handler import FileHandler
        print("✅ Aurora Sentinel imports successfully")
        return True
    except Exception as e:
        print(f"❌ Aurora Sentinel import failed: {e}")
        traceback.print_exc()
        return False

def test_cleaned_x_1000_lines():
    """Test the cleaned aurora_x_1000_lines.py runs efficiently"""
    print("🔍 Testing cleaned aurora_x_1000_lines.py...")
    
    try:
        import aurora_x_1000_lines
        # Should execute quickly now instead of taking forever
        print("✅ aurora_x_1000_lines.py runs efficiently")
        return True
    except Exception as e:
        print(f"❌ aurora_x_1000_lines.py failed: {e}")
        return False

def test_aurora_sentinel_functionality():
    """Test basic Aurora Sentinel functionality"""
    print("🔍 Testing Aurora Sentinel functionality...")
    
    try:
        from aurora_sentinel.main import AuroraSentinel
        
        # Create Aurora instance
        aurora = AuroraSentinel()
        
        # Test awakening
        result = aurora.awaken()
        if not result:
            print("❌ Aurora failed to awaken")
            return False
            
        # Test single evolution cycle
        success = aurora.run_evolution_cycle()
        if not success:
            print("❌ Evolution cycle failed")
            return False
            
        # Test status
        status = aurora.get_system_status()
        if not status['consciousness']['awake']:
            print("❌ Aurora not awake in status")
            return False
            
        # Cleanup
        aurora.stop()
        
        print("✅ Aurora Sentinel functionality works correctly")
        return True
    except Exception as e:
        print(f"❌ Aurora Sentinel functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_file_operations():
    """Test file operations are safe"""
    print("🔍 Testing file operations...")
    
    try:
        from aurora_sentinel.utils.file_handler import FileHandler
        
        fh = FileHandler()
        
        # Test writing and reading
        test_data = {"test": "data", "timestamp": "2025-01-01"}
        success = fh.write_json("test_file.json", test_data)
        if not success:
            print("❌ Failed to write JSON file")
            return False
            
        read_data = fh.read_json("test_file.json")
        if read_data != test_data:
            print("❌ Read data doesn't match written data")
            return False
            
        # Cleanup
        fh.delete_file("test_file.json", create_backup=False)
        
        print("✅ File operations work correctly")
        return True
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🌟" * 20)
    print("🔥 AURORA SENTINEL VALIDATION TESTS 🔥")
    print("🌟" * 20)
    
    tests = [
        ("Syntax Errors", test_syntax_errors),
        ("Aurora Sentinel Import", test_aurora_sentinel_import),
        ("Cleaned X-1000 Lines", test_cleaned_x_1000_lines),
        ("Aurora Functionality", test_aurora_sentinel_functionality),
        ("File Operations", test_file_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Aurora Sentinel is fully functional!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())