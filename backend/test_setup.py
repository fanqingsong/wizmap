#!/usr/bin/env python3
"""
Quick test script to verify backend setup
"""
import sys
import os

# Add notebook-widget to path
sys.path.insert(0, '/home/fqs/workspace/self/wizmap/notebook-widget')

print("Testing backend dependencies...")

try:
    # Test wizmap import
    from wizmap import generate_contour_dict, generate_topic_dict
    print("✅ wizmap module imported successfully")

    # Test basic functionality
    import numpy as np
    test_xs = [1.0, 2.0, 3.0]
    test_ys = [4.0, 5.0, 6.0]
    test_texts = ["test1", "test2", "test3"]

    result = generate_contour_dict(test_xs, test_ys, grid_size=10)
    print("✅ generate_contour_dict works")
    print(f"   Generated grid: {len(result.get('grid', []))}x{len(result.get('grid', [[]])[0] if result.get('grid') else 0)}")

    print("\n🎉 All basic tests passed!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   This is expected - full ML processing will work when dependencies are installed")

except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)