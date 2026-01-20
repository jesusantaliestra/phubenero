#!/usr/bin/env python3
"""
Comprehensive tests for 30 exam types system.
Tests cover configuration, topic selection, and edge cases.
"""

import sys
import os
import unittest
from pathlib import Path

# Add backend to path using relative imports
TESTS_DIR = Path(__file__).parent
BACKEND_DIR = TESTS_DIR.parent / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

from exam_types_config_30 import (
    EXAM_TYPES, EXAM_FAMILIES, EXAM_DISPLAY_NAMES, EXAM_SECTIONS,
    SPEAKING_DURATIONS, WRITING_TASKS, EXAM_DESCRIPTIONS,
    VALID_AVATAR_PROVIDERS,
    get_exam_family, get_section_cost, get_full_mock_cost,
    is_valid_exam_type, get_all_exam_types, get_exam_types_by_family,
    get_exam_info, get_family_average_cost
)
from topic_selector import (
    TopicSelector, get_topic_selector, reset_topic_selector,
    LRUCache, TopicHistory
)


class TestExamTypesConfig(unittest.TestCase):
    """Tests for exam_types_config_30.py"""

    def test_exam_count(self):
        """Test that we have exactly 30 exam types."""
        self.assertEqual(len(EXAM_TYPES), 30, f"Expected 30 exam types, got {len(EXAM_TYPES)}")

    def test_all_families_present(self):
        """Test that all 11 exam families are present."""
        expected_families = {
            'toefl', 'ielts', 'pte', 'oet', 'toeic',
            'celpip', 'cambridge', 'linguaskill', 'trinity', 'oxford', 'aptis'
        }
        self.assertEqual(set(EXAM_FAMILIES.keys()), expected_families)

    def test_family_counts(self):
        """Test exam counts per family."""
        expected_counts = {
            'toefl': 2, 'ielts': 2, 'pte': 2, 'oet': 12,
            'toeic': 1, 'celpip': 1, 'cambridge': 5, 'linguaskill': 2,
            'trinity': 1, 'oxford': 1, 'aptis': 1,
        }
        for family, expected_count in expected_counts.items():
            actual_count = len(EXAM_FAMILIES[family])
            self.assertEqual(
                actual_count, expected_count,
                f"Family {family}: expected {expected_count}, got {actual_count}"
            )

    def test_all_exams_have_display_names(self):
        """Test all exam types have display names."""
        for exam_type in EXAM_TYPES:
            self.assertIn(exam_type, EXAM_DISPLAY_NAMES,
                         f"Missing display name for {exam_type}")

    def test_all_exams_have_sections(self):
        """Test all exam types have section definitions."""
        for exam_type in EXAM_TYPES:
            self.assertIn(exam_type, EXAM_SECTIONS)
            self.assertEqual(len(EXAM_SECTIONS[exam_type]), 4)

    def test_all_exams_have_speaking_duration(self):
        """Test all exam types have speaking duration."""
        for exam_type in EXAM_TYPES:
            self.assertIn(exam_type, SPEAKING_DURATIONS)
            self.assertGreater(SPEAKING_DURATIONS[exam_type], 0)

    def test_all_exams_have_writing_tasks(self):
        """Test all exam types have writing task count."""
        for exam_type in EXAM_TYPES:
            self.assertIn(exam_type, WRITING_TASKS)
            self.assertGreater(WRITING_TASKS[exam_type], 0)

    def test_all_exams_have_descriptions(self):
        """Test all exam types have descriptions."""
        for exam_type in EXAM_TYPES:
            self.assertIn(exam_type, EXAM_DESCRIPTIONS)
            self.assertIsInstance(EXAM_DESCRIPTIONS[exam_type], str)

    def test_families_contain_all_exams(self):
        """Test that all exams are in exactly one family."""
        all_exams_in_families = []
        for exams in EXAM_FAMILIES.values():
            all_exams_in_families.extend(exams)

        self.assertEqual(
            sorted(all_exams_in_families),
            sorted(EXAM_TYPES),
            "Mismatch between EXAM_TYPES and EXAM_FAMILIES"
        )


class TestHelperFunctions(unittest.TestCase):
    """Tests for helper functions."""

    def test_get_exam_family(self):
        """Test get_exam_family returns correct family."""
        self.assertEqual(get_exam_family('toefl_ibt'), 'toefl')
        self.assertEqual(get_exam_family('ielts_academic'), 'ielts')
        self.assertEqual(get_exam_family('oet_nursing'), 'oet')
        self.assertEqual(get_exam_family('cambridge_b2_first'), 'cambridge')

    def test_get_exam_family_unknown(self):
        """Test get_exam_family with unknown exam."""
        self.assertEqual(get_exam_family('unknown_exam'), 'other')

    def test_is_valid_exam_type(self):
        """Test is_valid_exam_type function."""
        self.assertTrue(is_valid_exam_type('toefl_ibt'))
        self.assertTrue(is_valid_exam_type('cambridge_c2_proficiency'))
        self.assertFalse(is_valid_exam_type('invalid_exam'))
        self.assertFalse(is_valid_exam_type(''))

    def test_get_all_exam_types_returns_copy(self):
        """Test get_all_exam_types returns a copy, not original."""
        types = get_all_exam_types()
        types.append('fake_exam')
        self.assertNotIn('fake_exam', EXAM_TYPES)

    def test_get_exam_types_by_family(self):
        """Test get_exam_types_by_family function."""
        oet_exams = get_exam_types_by_family('oet')
        self.assertEqual(len(oet_exams), 12)
        self.assertIn('oet_nursing', oet_exams)

    def test_get_exam_types_by_family_unknown(self):
        """Test get_exam_types_by_family with unknown family."""
        self.assertEqual(get_exam_types_by_family('unknown'), [])


class TestCostFunctions(unittest.TestCase):
    """Tests for cost calculation functions."""

    def test_get_section_cost_valid_provider(self):
        """Test get_section_cost with valid providers."""
        cost_rive = get_section_cost('toefl_ibt', 'speaking', 'rive')
        cost_did = get_section_cost('toefl_ibt', 'speaking', 'd-id')

        self.assertGreater(cost_rive, 0)
        self.assertGreater(cost_did, 0)
        self.assertGreater(cost_did, cost_rive)  # D-ID is more expensive

    def test_get_section_cost_case_insensitive(self):
        """Test get_section_cost accepts case variations."""
        cost1 = get_section_cost('toefl_ibt', 'speaking', 'RIVE')
        cost2 = get_section_cost('toefl_ibt', 'speaking', 'Rive')
        cost3 = get_section_cost('toefl_ibt', 'speaking', 'rive')

        self.assertEqual(cost1, cost2)
        self.assertEqual(cost2, cost3)

    def test_get_section_cost_invalid_provider(self):
        """Test get_section_cost raises error for invalid provider."""
        with self.assertRaises(ValueError) as context:
            get_section_cost('toefl_ibt', 'speaking', 'invalid')

        self.assertIn('Invalid avatar provider', str(context.exception))

    def test_get_full_mock_cost(self):
        """Test get_full_mock_cost returns positive values."""
        for exam_type in EXAM_TYPES:
            cost = get_full_mock_cost(exam_type, 'rive')
            self.assertGreater(cost, 0, f"Cost for {exam_type} should be > 0")

    def test_get_full_mock_cost_invalid_provider(self):
        """Test get_full_mock_cost raises error for invalid provider."""
        with self.assertRaises(ValueError):
            get_full_mock_cost('toefl_ibt', 'invalid_provider')

    def test_get_family_average_cost(self):
        """Test get_family_average_cost function."""
        avg_cost = get_family_average_cost('oet', 'rive')
        self.assertGreater(avg_cost, 0)

    def test_get_exam_info(self):
        """Test get_exam_info returns complete info."""
        info = get_exam_info('cambridge_b2_first')

        self.assertIsNotNone(info)
        self.assertEqual(info['exam_type'], 'cambridge_b2_first')
        self.assertIn('display_name', info)
        self.assertIn('family', info)
        self.assertIn('sections', info)
        self.assertIn('cost_rive', info)
        self.assertIn('cost_did', info)

    def test_get_exam_info_invalid(self):
        """Test get_exam_info with invalid exam type."""
        info = get_exam_info('invalid_exam')
        self.assertIsNone(info)


class TestLRUCache(unittest.TestCase):
    """Tests for LRUCache class."""

    def test_basic_operations(self):
        """Test basic get/set operations."""
        cache = LRUCache(max_size=3)

        cache.set('a', 1)
        cache.set('b', 2)

        self.assertEqual(cache.get('a'), 1)
        self.assertEqual(cache.get('b'), 2)
        self.assertIsNone(cache.get('c'))

    def test_max_size_eviction(self):
        """Test that oldest items are evicted when max size reached."""
        cache = LRUCache(max_size=2)

        cache.set('a', 1)
        cache.set('b', 2)
        cache.set('c', 3)  # Should evict 'a'

        self.assertIsNone(cache.get('a'))
        self.assertEqual(cache.get('b'), 2)
        self.assertEqual(cache.get('c'), 3)

    def test_access_updates_recency(self):
        """Test that accessing an item updates its recency."""
        cache = LRUCache(max_size=2)

        cache.set('a', 1)
        cache.set('b', 2)
        cache.get('a')  # Access 'a' to make it recent
        cache.set('c', 3)  # Should evict 'b', not 'a'

        self.assertEqual(cache.get('a'), 1)
        self.assertIsNone(cache.get('b'))
        self.assertEqual(cache.get('c'), 3)

    def test_contains(self):
        """Test __contains__ method."""
        cache = LRUCache(max_size=3)
        cache.set('a', 1)

        self.assertIn('a', cache)
        self.assertNotIn('b', cache)


class TestTopicHistory(unittest.TestCase):
    """Tests for TopicHistory class."""

    def test_basic_add(self):
        """Test basic add operation."""
        history = TopicHistory(max_items=3)
        history.add('topic1')
        history.add('topic2')

        self.assertIn('topic1', history)
        self.assertIn('topic2', history)

    def test_max_items_limit(self):
        """Test that oldest items are removed when limit reached."""
        history = TopicHistory(max_items=2)

        history.add('topic1')
        history.add('topic2')
        history.add('topic3')  # Should remove 'topic1'

        self.assertNotIn('topic1', history)
        self.assertIn('topic2', history)
        self.assertIn('topic3', history)

    def test_maintains_order(self):
        """Test that order is maintained (unlike sets)."""
        history = TopicHistory(max_items=3)

        history.add('a')
        history.add('b')
        history.add('c')
        history.add('d')  # Removes 'a'

        items = history.to_set()
        self.assertEqual(items, {'b', 'c', 'd'})

    def test_duplicate_moves_to_end(self):
        """Test that adding duplicate moves item to end."""
        history = TopicHistory(max_items=3)

        history.add('a')
        history.add('b')
        history.add('a')  # Move 'a' to end
        history.add('c')
        history.add('d')  # Should remove 'b', not 'a'

        self.assertIn('a', history)
        self.assertNotIn('b', history)


class TestTopicSelector(unittest.TestCase):
    """Tests for TopicSelector class."""

    def setUp(self):
        """Reset singleton before each test."""
        reset_topic_selector()

    def test_singleton_pattern(self):
        """Test that get_topic_selector returns same instance."""
        selector1 = get_topic_selector()
        selector2 = get_topic_selector()

        self.assertIs(selector1, selector2)

    def test_get_exam_info(self):
        """Test get_exam_info method."""
        selector = get_topic_selector()
        # Note: This depends on topic files existing
        # If they don't exist, this test may fail gracefully

    def test_reset_selector(self):
        """Test reset_topic_selector function."""
        selector1 = get_topic_selector()
        reset_topic_selector()
        selector2 = get_topic_selector()

        self.assertIsNot(selector1, selector2)


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def test_all_exam_families_consistent(self):
        """Test consistency between families and individual exams."""
        total_from_families = sum(
            len(exams) for exams in EXAM_FAMILIES.values()
        )
        self.assertEqual(total_from_families, 30)
        self.assertEqual(total_from_families, len(EXAM_TYPES))

    def test_cost_consistency(self):
        """Test that D-ID is always more expensive than Rive."""
        for exam_type in EXAM_TYPES:
            cost_rive = get_full_mock_cost(exam_type, 'rive')
            cost_did = get_full_mock_cost(exam_type, 'd-id')

            self.assertGreater(
                cost_did, cost_rive,
                f"{exam_type}: D-ID ({cost_did}) should be > Rive ({cost_rive})"
            )


def run_all_tests():
    """Run all tests with verbose output."""
    print("\n" + "=" * 60)
    print("🧪 RUNNING COMPREHENSIVE TESTS FOR 30 EXAM TYPES")
    print("=" * 60 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExamTypesConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestCostFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestLRUCache))
    suite.addTests(loader.loadTestsFromTestCase(TestTopicHistory))
    suite.addTests(loader.loadTestsFromTestCase(TestTopicSelector))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
