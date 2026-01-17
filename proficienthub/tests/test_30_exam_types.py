#!/usr/bin/env python3
"""
Comprehensive tests for 30 exam types system
"""

import sys
sys.path.append('/home/claude/proficienthub/backend')

from exam_types_config_30 import *

def test_exam_count():
    """Test that we have exactly 30 exam types"""
    assert len(EXAM_TYPES) == 30, f"Expected 30 exam types, got {len(EXAM_TYPES)}"
    print("✅ Test 1: Exam count is correct (30)")

def test_all_families():
    """Test that all exam families are present"""
    expected_families = [
        'toefl', 'ielts', 'pte', 'oet', 'toeic', 
        'celpip', 'cambridge', 'linguaskill', 'trinity', 'oxford', 'aptis'
    ]
    assert set(EXAM_FAMILIES.keys()) == set(expected_families)
    print(f"✅ Test 2: All {len(expected_families)} exam families present")

def test_family_counts():
    """Test exam counts per family"""
    expected_counts = {
        'toefl': 2, 'ielts': 2, 'pte': 2, 'oet': 12,
        'toeic': 1, 'celpip': 1, 'cambridge': 5, 'linguaskill': 2,
        'trinity': 1, 'oxford': 1, 'aptis': 1,
    }
    
    for family, expected_count in expected_counts.items():
        actual_count = len(EXAM_FAMILIES[family])
        assert actual_count == expected_count
    
    print("✅ Test 3: All family counts correct")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 RUNNING TESTS FOR 30 EXAM TYPES")
    print("="*60 + "\n")
    
    test_exam_count()
    test_all_families()
    test_family_counts()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)

if __name__ == '__main__':
    run_all_tests()
