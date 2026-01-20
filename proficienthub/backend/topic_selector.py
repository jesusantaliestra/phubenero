"""
ProficientHub - Topic Selector System
Handles intelligent topic selection for 30 exam types
Based on official academic sources and CEFR levels
"""

import random
import json
import threading
import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
from collections import OrderedDict
from functools import lru_cache


class LRUCache:
    """Thread-safe LRU cache for topic history to prevent memory leaks."""

    def __init__(self, max_size: int = 10000):
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            return default

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self._max_size:
                    self._cache.popitem(last=False)
            self._cache[key] = value

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._cache


class TopicHistory:
    """
    Thread-safe topic history tracker with proper ordering.
    Uses a deque-like structure to maintain insertion order.
    """

    def __init__(self, max_items: int = 5):
        self._items: List[str] = []
        self._max_items = max_items
        self._lock = threading.Lock()

    def add(self, item: str) -> None:
        with self._lock:
            if item in self._items:
                self._items.remove(item)
            self._items.append(item)
            if len(self._items) > self._max_items:
                self._items.pop(0)

    def __contains__(self, item: str) -> bool:
        with self._lock:
            return item in self._items

    def to_set(self) -> Set[str]:
        with self._lock:
            return set(self._items)


class TopicSelector:
    """
    Intelligent topic selection for mock exams
    Ensures academic quality and variety
    """
    
    # Valid topic file names (whitelist for security)
    VALID_TOPIC_FILES = frozenset([
        'cambridge_topics_official.json',
        'topics_c1_c2_complete.json',
        'topics_linguaskill_others.json'
    ])

    # Configuration constants
    MIN_CATEGORIES = 3
    MIN_TOPICS_PER_CATEGORY = 5
    MAX_HISTORY_ITEMS = 5
    MAX_CACHE_SIZE = 10000

    def __init__(self, topics_dir: Optional[str] = None):
        """
        Initialize topic selector with all exam topics

        Args:
            topics_dir: Directory containing topic JSON files (must be relative or validated)
        """
        # Validate and sanitize topics_dir to prevent path traversal
        if topics_dir is None:
            topics_dir = '../exam_topics_research'

        self.topics_dir = self._validate_topics_dir(topics_dir)
        self.topics: Dict[str, Any] = {}
        self._load_lock = threading.Lock()
        self._topics_loaded = False

        # Use LRU cache to prevent memory leaks
        self._topic_history_cache = LRUCache(max_size=self.MAX_CACHE_SIZE)

        # Lazy load topics
        self._ensure_topics_loaded()

    def _validate_topics_dir(self, topics_dir: str) -> Path:
        """
        Validate topics directory to prevent path traversal attacks.

        Args:
            topics_dir: Directory path to validate

        Returns:
            Validated Path object

        Raises:
            ValueError: If path is invalid or attempts path traversal
        """
        # Check for path traversal patterns
        if re.search(r'\.\.[/\\]', topics_dir) and not topics_dir.startswith('..'):
            raise ValueError("Invalid topics directory: path traversal detected")

        path = Path(topics_dir)

        # If relative path, resolve against current file's directory
        if not path.is_absolute():
            base_dir = Path(__file__).parent
            path = (base_dir / path).resolve()

        # Ensure the resolved path doesn't escape the project directory
        project_root = Path(__file__).parent.parent.resolve()
        try:
            path.resolve().relative_to(project_root)
        except ValueError:
            # Allow parent directory for exam_topics_research
            if 'exam_topics_research' not in str(path):
                raise ValueError(f"Invalid topics directory: {topics_dir}")

        return path

    def _ensure_topics_loaded(self) -> None:
        """Thread-safe lazy loading of topics."""
        if self._topics_loaded:
            return

        with self._load_lock:
            if not self._topics_loaded:
                self.topics = self._load_all_topics()
                self._topics_loaded = True
        
    def _load_all_topics(self) -> Dict[str, Any]:
        """
        Load all topic data from JSON files with proper error handling.

        Returns:
            Dictionary with all exam topics

        Raises:
            RuntimeError: If no topic files could be loaded
        """
        all_topics: Dict[str, Any] = {}
        errors: List[str] = []

        for filename in self.VALID_TOPIC_FILES:
            filepath = self.topics_dir / filename

            if not filepath.exists():
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    if not isinstance(data, dict):
                        errors.append(f"{filename}: Expected dict, got {type(data).__name__}")
                        continue

                    all_topics.update(data)

            except json.JSONDecodeError as e:
                errors.append(f"{filename}: Invalid JSON - {e}")
            except PermissionError:
                errors.append(f"{filename}: Permission denied")
            except OSError as e:
                errors.append(f"{filename}: OS error - {e}")

        if errors:
            import logging
            logger = logging.getLogger(__name__)
            for error in errors:
                logger.warning(f"Topic loading warning: {error}")

        if not all_topics:
            raise RuntimeError(
                f"No topics could be loaded from {self.topics_dir}. "
                f"Errors: {errors if errors else 'No valid files found'}"
            )

        return all_topics
    
    def get_exam_info(self, exam_type: str) -> Optional[Dict]:
        """
        Get complete information about an exam type
        
        Args:
            exam_type: e.g. 'cambridge_b2_first'
            
        Returns:
            Dict with exam info or None if not found
        """
        return self.topics.get(exam_type)
    
    def get_random_topic(
        self, 
        exam_type: str, 
        skill: str,
        user_id: Optional[str] = None,
        avoid_recent: bool = True
    ) -> Optional[str]:
        """
        Get random topic for specific exam type and skill
        
        Args:
            exam_type: e.g. 'cambridge_b2_first'
            skill: 'reading', 'listening', 'speaking', 'writing'
            user_id: Optional user ID to track history
            avoid_recent: Avoid recently used topics
            
        Returns:
            str: Random topic from appropriate category
        """
        if exam_type not in self.topics:
            return None
        
        exam_data = self.topics[exam_type]
        
        # Get topic pool
        topic_pool = self._get_topic_pool(exam_data, skill)
        if not topic_pool:
            return None
        
        # Filter out recent topics if requested
        if avoid_recent and user_id:
            topic_pool = self._filter_recent_topics(
                topic_pool, 
                user_id, 
                exam_type, 
                skill
            )
        
        if not topic_pool:
            # If all topics were filtered, use full pool
            topic_pool = self._get_topic_pool(exam_data, skill)
        
        # Select random topic
        selected_topic = random.choice(topic_pool)
        
        # Track selection
        if user_id:
            self._track_topic_usage(user_id, exam_type, skill, selected_topic)
        
        return selected_topic
    
    def _get_topic_pool(self, exam_data: Dict, skill: str) -> List[str]:
        """
        Get pool of available topics for a skill
        
        Args:
            exam_data: Exam configuration data
            skill: The skill to get topics for
            
        Returns:
            List of topic strings
        """
        topic_pool = []
        
        # Get from topic_categories (general topics)
        categories = exam_data.get('topic_categories', {})
        for category, topics_list in categories.items():
            topic_pool.extend(topics_list)
        
        # Get skill-specific topics if available
        skill_key = f'{skill}_topics'
        if skill_key in exam_data:
            skill_topics = exam_data[skill_key]
            if isinstance(skill_topics, list):
                topic_pool.extend(skill_topics)
        
        # Get skill-specific scenarios
        if skill == 'listening':
            scenarios_key = f'{skill}_scenarios'
            if scenarios_key in exam_data:
                topic_pool.extend(exam_data[scenarios_key])
        
        if skill == 'speaking':
            prompts_key = f'{skill}_prompts'
            if prompts_key in exam_data:
                topic_pool.extend(exam_data[prompts_key])
        
        if skill == 'writing':
            tasks_key = f'{skill}_tasks'
            if tasks_key in exam_data:
                topic_pool.extend(exam_data[tasks_key])
        
        return list(set(topic_pool))  # Remove duplicates
    
    def _filter_recent_topics(
        self,
        topic_pool: List[str],
        user_id: str,
        exam_type: str,
        skill: str
    ) -> List[str]:
        """
        Filter out recently used topics.

        Args:
            topic_pool: Available topics
            user_id: User identifier
            exam_type: Exam type
            skill: Skill type

        Returns:
            Filtered topic list (never empty - returns original if all filtered)
        """
        key = f"{user_id}_{exam_type}_{skill}"
        history = self._topic_history_cache.get(key)

        if history is None:
            return topic_pool

        recent_topics = history.to_set()
        filtered = [t for t in topic_pool if t not in recent_topics]

        return filtered if filtered else topic_pool

    def _track_topic_usage(
        self,
        user_id: str,
        exam_type: str,
        skill: str,
        topic: str
    ) -> None:
        """
        Track topic usage to avoid repetition.
        Uses thread-safe TopicHistory with proper ordering.

        Args:
            user_id: User identifier
            exam_type: Exam type
            skill: Skill type
            topic: Selected topic
        """
        key = f"{user_id}_{exam_type}_{skill}"

        history = self._topic_history_cache.get(key)
        if history is None:
            history = TopicHistory(max_items=self.MAX_HISTORY_ITEMS)
            self._topic_history_cache.set(key, history)

        history.add(topic)
    
    def get_topic_categories(self, exam_type: str) -> List[str]:
        """
        Get all topic categories for an exam type
        
        Args:
            exam_type: Exam type identifier
            
        Returns:
            List of category names
        """
        if exam_type not in self.topics:
            return []
        
        categories = self.topics[exam_type].get('topic_categories', {})
        return list(categories.keys())
    
    def get_topics_by_category(
        self, 
        exam_type: str, 
        category: str
    ) -> List[str]:
        """
        Get all topics in a specific category
        
        Args:
            exam_type: Exam type identifier
            category: Category name
            
        Returns:
            List of topics in that category
        """
        if exam_type not in self.topics:
            return []
        
        categories = self.topics[exam_type].get('topic_categories', {})
        return categories.get(category, [])
    
    def get_topic_stats(self, exam_type: str) -> Dict:
        """
        Get statistics about topics for an exam type
        
        Args:
            exam_type: Exam type identifier
            
        Returns:
            Dict with topic statistics
        """
        if exam_type not in self.topics:
            return {}
        
        exam_data = self.topics[exam_type]
        categories = exam_data.get('topic_categories', {})
        
        total_topics = sum(len(topics) for topics in categories.values())
        
        return {
            'exam_type': exam_type,
            'total_categories': len(categories),
            'total_topics': total_topics,
            'categories': {
                cat: len(topics) for cat, topics in categories.items()
            },
            'cefr_level': exam_data.get('cefr_level', 'N/A'),
            'vocabulary_size': exam_data.get('vocabulary_size', 'N/A')
        }
    
    def validate_topic_coverage(self, exam_type: str) -> Dict:
        """
        Validate that exam has adequate topic coverage
        
        Args:
            exam_type: Exam type identifier
            
        Returns:
            Dict with validation results
        """
        if exam_type not in self.topics:
            return {
                'valid': False,
                'error': f'Exam type {exam_type} not found'
            }
        
        exam_data = self.topics[exam_type]
        categories = exam_data.get('topic_categories', {})

        issues = []

        if len(categories) < self.MIN_CATEGORIES:
            issues.append(
                f'Only {len(categories)} categories (minimum {self.MIN_CATEGORIES})'
            )

        for cat, topics in categories.items():
            if len(topics) < self.MIN_TOPICS_PER_CATEGORY:
                issues.append(
                    f'Category "{cat}" has only {len(topics)} topics '
                    f'(minimum {self.MIN_TOPICS_PER_CATEGORY})'
                )
        
        return {
            'valid': len(issues) == 0,
            'exam_type': exam_type,
            'issues': issues,
            'category_count': len(categories),
            'total_topics': sum(len(t) for t in categories.values())
        }
    
    def generate_mock_exam_topics(
        self, 
        exam_type: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Generate topics for a complete mock exam
        
        Args:
            exam_type: Exam type identifier
            user_id: Optional user ID for history tracking
            
        Returns:
            Dict with topics for all sections
        """
        if exam_type not in self.topics:
            return {
                'error': f'Exam type {exam_type} not found',
                'available_types': list(self.topics.keys())
            }
        
        exam_data = self.topics[exam_type]
        
        mock_exam = {
            'exam_type': exam_type,
            'display_name': exam_data.get('display_name', exam_type),
            'cefr_level': exam_data.get('cefr_level', 'N/A'),
            'generated_at': datetime.utcnow().isoformat(),
            'sections': {}
        }
        
        # Generate topics for each skill
        for skill in ['reading', 'listening', 'speaking', 'writing']:
            topic = self.get_random_topic(exam_type, skill, user_id)
            
            mock_exam['sections'][skill] = {
                'topic': topic,
                'skill': skill
            }
        
        return mock_exam
    
    def get_all_exam_types(self) -> List[str]:
        """Get list of all available exam types"""
        return list(self.topics.keys())
    
    def search_topics(
        self, 
        exam_type: str, 
        search_term: str
    ) -> List[Dict]:
        """
        Search for topics containing a term
        
        Args:
            exam_type: Exam type identifier
            search_term: Term to search for
            
        Returns:
            List of matching topics with categories
        """
        if exam_type not in self.topics:
            return []
        
        search_term = search_term.lower()
        results = []
        
        categories = self.topics[exam_type].get('topic_categories', {})
        
        for category, topics in categories.items():
            for topic in topics:
                if search_term in topic.lower():
                    results.append({
                        'category': category,
                        'topic': topic
                    })
        
        return results


# Thread-safe singleton implementation
_topic_selector: Optional[TopicSelector] = None
_singleton_lock = threading.Lock()


def get_topic_selector() -> TopicSelector:
    """
    Get or create singleton TopicSelector instance.
    Thread-safe implementation using double-checked locking.

    Returns:
        TopicSelector singleton instance
    """
    global _topic_selector

    if _topic_selector is None:
        with _singleton_lock:
            # Double-check after acquiring lock
            if _topic_selector is None:
                _topic_selector = TopicSelector()

    return _topic_selector


def reset_topic_selector() -> None:
    """
    Reset the singleton instance. Useful for testing.
    """
    global _topic_selector
    with _singleton_lock:
        _topic_selector = None


# Example usage
if __name__ == '__main__':
    selector = TopicSelector()
    
    # Test with Cambridge B2 First
    exam_type = 'cambridge_b2_first'
    
    print(f"Testing Topic Selector for {exam_type}\n")
    
    # Get exam info
    info = selector.get_exam_info(exam_type)
    print(f"Exam: {info.get('display_name')}")
    print(f"CEFR: {info.get('cefr_level')}")
    print(f"Vocabulary: {info.get('vocabulary_size')}\n")
    
    # Get random topics
    print("Random Topics:")
    for skill in ['reading', 'listening', 'speaking', 'writing']:
        topic = selector.get_random_topic(exam_type, skill)
        print(f"  {skill.capitalize()}: {topic}")
    
    # Get statistics
    print("\nTopic Statistics:")
    stats = selector.get_topic_stats(exam_type)
    print(f"  Categories: {stats['total_categories']}")
    print(f"  Total Topics: {stats['total_topics']}")
    
    # Validate coverage
    print("\nValidation:")
    validation = selector.validate_topic_coverage(exam_type)
    print(f"  Valid: {validation['valid']}")
    if validation['issues']:
        print(f"  Issues: {validation['issues']}")
    
    # Generate mock exam
    print("\nGenerated Mock Exam:")
    mock = selector.generate_mock_exam_topics(exam_type, user_id='test_user')
    for skill, data in mock['sections'].items():
        print(f"  {skill.capitalize()}: {data['topic']}")
