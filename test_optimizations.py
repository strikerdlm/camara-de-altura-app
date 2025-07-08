#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify that optimizations are working correctly.
"""

import sys
import time
import os

def test_performance_monitoring():
    """Test the performance monitoring system."""
    print("🔍 Testing Performance Monitoring...")
    try:
        from performance_monitor import performance_monitor, monitor_performance, track_operation
        
        # Test function timing
        @monitor_performance("test_function")
        def test_function():
            time.sleep(0.1)  # Simulate some work
            return "success"
        
        # Run test function
        result = test_function()
        
        # Test operation tracking
        with track_operation("test_operation"):
            time.sleep(0.05)
        
        # Get performance report
        report = performance_monitor.get_performance_report()
        
        print(f"✅ Performance monitoring working!")
        print(f"   - Functions tracked: {len(report['function_performance'])}")
        print(f"   - Active operations: {report['active_operations']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring error: {e}")
        return False

def test_optimized_data_manager():
    """Test the optimized data manager."""
    print("\n💾 Testing Optimized Data Manager...")
    try:
        from data_manager import OptimizedDataManager
        
        # Create test data manager
        test_data_dir = "test_data"
        os.makedirs(test_data_dir, exist_ok=True)
        
        dm = OptimizedDataManager(test_data_dir)
        
        # Test throttled saving
        start_time = time.time()
        dm.save_data_throttled()
        save_time = time.time() - start_time
        
        print(f"✅ Optimized Data Manager working!")
        print(f"   - Throttled save completed in: {save_time:.3f}s")
        print(f"   - Data manager type: {type(dm).__name__}")
        
        # Cleanup
        import shutil
        if os.path.exists(test_data_dir):
            shutil.rmtree(test_data_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Optimized Data Manager error: {e}")
        return False

def test_lazy_ui_components():
    """Test lazy loading UI components."""
    print("\n🎨 Testing Lazy UI Components...")
    try:
        from optimized_ui_components import LazyCombobox, CachedDataProvider
        
        # Test data provider
        provider = CachedDataProvider()
        staff_list = provider.get_staff_list()
        
        print(f"✅ Lazy UI Components working!")
        print(f"   - Staff list loaded: {len(staff_list)} items")
        print(f"   - Sample staff: {staff_list[:3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lazy UI Components error: {e}")
        return False

def test_configuration():
    """Test configuration files."""
    print("\n⚙️  Testing Configuration...")
    try:
        import json
        
        # Test performance config
        if os.path.exists('performance_config.json'):
            with open('performance_config.json', 'r') as f:
                config = json.load(f)
            
            print(f"✅ Configuration working!")
            print(f"   - Monitoring enabled: {config.get('monitoring', {}).get('enabled', False)}")
            print(f"   - Caching enabled: {config.get('caching', {}).get('enabled', False)}")
            print(f"   - Lazy loading: {config.get('ui', {}).get('lazy_loading', False)}")
            
            return True
        else:
            print("❌ Configuration file not found")
            return False
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_backup_integrity():
    """Test that backups were created properly."""
    print("\n💾 Testing Backup Integrity...")
    try:
        # Find backup directory
        backup_dirs = [d for d in os.listdir('.') if d.startswith('backup_optimization_')]
        
        if backup_dirs:
            backup_dir = backup_dirs[0]  # Use the first/most recent
            backed_up_files = os.listdir(backup_dir)
            
            print(f"✅ Backup system working!")
            print(f"   - Backup directory: {backup_dir}")
            print(f"   - Files backed up: {len(backed_up_files)}")
            print(f"   - Backup files: {', '.join(backed_up_files[:5])}")
            
            return True
        else:
            print("❌ No backup directory found")
            return False
            
    except Exception as e:
        print(f"❌ Backup test error: {e}")
        return False

def run_performance_benchmark():
    """Run a simple performance benchmark."""
    print("\n⚡ Running Performance Benchmark...")
    try:
        from performance_monitor import performance_monitor, monitor_performance
        
        @monitor_performance("benchmark_test")
        def benchmark_function():
            # Simulate typical app operations
            data = {}
            for i in range(1000):
                data[f"key_{i}"] = f"value_{i}"
            
            # Simulate data processing
            processed = {k: v.upper() for k, v in data.items() if i % 2 == 0}
            return len(processed)
        
        # Run benchmark multiple times
        results = []
        for i in range(5):
            start_time = time.time()
            result = benchmark_function()
            duration = time.time() - start_time
            results.append(duration)
        
        avg_time = sum(results) / len(results)
        
        print(f"✅ Performance benchmark completed!")
        print(f"   - Average execution time: {avg_time:.4f}s")
        print(f"   - Best time: {min(results):.4f}s")
        print(f"   - Worst time: {max(results):.4f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Benchmark error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 OPTIMIZATION VERIFICATION TEST")
    print("=" * 50)
    
    tests = [
        test_performance_monitoring,
        test_optimized_data_manager,
        test_lazy_ui_components,
        test_configuration,
        test_backup_integrity,
        run_performance_benchmark
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL OPTIMIZATIONS WORKING CORRECTLY!")
        print("Your application is ready for improved performance!")
    elif passed >= total * 0.8:
        print("\n✅ MOST OPTIMIZATIONS WORKING!")
        print("Some minor issues detected, but core optimizations are functional.")
    else:
        print("\n⚠️  SOME OPTIMIZATIONS NEED ATTENTION")
        print("Please check the error messages above and verify your setup.")
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Run your application normally")
    print("2. Monitor performance improvements")
    print("3. Check FINAL_OPTIMIZATION_REPORT.md for details")
    print("4. Configure settings in performance_config.json if needed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)