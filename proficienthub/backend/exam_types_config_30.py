"""
ProficientHub - 30 Exam Types Configuration
Complete system with all major English proficiency exams
"""

from typing import List, Dict, Optional, Any

# ============================================================
# 30 EXAM TYPES - COMPLETE LIST
# ============================================================

EXAM_TYPES = [
    # TOEFL (1)
    'toefl_ibt',
    
    # IELTS (2)
    'ielts_academic',
    'ielts_general',
    
    # PTE (2)
    'pte_academic',
    'pte_core',
    
    # OET (12 professions)
    'oet_nursing',
    'oet_medicine',
    'oet_dentistry',
    'oet_pharmacy',
    'oet_physiotherapy',
    'oet_veterinary',
    'oet_occupational_therapy',
    'oet_podiatry',
    'oet_radiography',
    'oet_optometry',
    'oet_speech_pathology',
    'oet_dietetics',
    
    # TOEIC (1)
    'toeic',
    
    # CELPIP (1)
    'celpip',
    
    # Cambridge 5 levels (5)
    'cambridge_a2_key',
    'cambridge_b1_preliminary',
    'cambridge_b2_first',
    'cambridge_c1_advanced',
    'cambridge_c2_proficiency',
    
    # Linguaskill (2)
    'linguaskill',
    'linguaskill_business',
    
    # Other specialized (4)
    'trinity_ise',
    'oxford_test',
    'toefl_itp',
    'aptis',
]

# ============================================================
# EXAM DISPLAY NAMES
# ============================================================

EXAM_DISPLAY_NAMES = {
    # TOEFL
    'toefl_ibt': 'TOEFL iBT',
    
    # IELTS
    'ielts_academic': 'IELTS Academic',
    'ielts_general': 'IELTS General Training',
    
    # PTE
    'pte_academic': 'PTE Academic',
    'pte_core': 'PTE Core',
    
    # OET
    'oet_nursing': 'OET Nursing',
    'oet_medicine': 'OET Medicine',
    'oet_dentistry': 'OET Dentistry',
    'oet_pharmacy': 'OET Pharmacy',
    'oet_physiotherapy': 'OET Physiotherapy',
    'oet_veterinary': 'OET Veterinary Science',
    'oet_occupational_therapy': 'OET Occupational Therapy',
    'oet_podiatry': 'OET Podiatry',
    'oet_radiography': 'OET Radiography',
    'oet_optometry': 'OET Optometry',
    'oet_speech_pathology': 'OET Speech Pathology',
    'oet_dietetics': 'OET Dietetics',
    
    # TOEIC
    'toeic': 'TOEIC',
    
    # CELPIP
    'celpip': 'CELPIP',
    
    # Cambridge
    'cambridge_a2_key': 'Cambridge A2 Key (KET)',
    'cambridge_b1_preliminary': 'Cambridge B1 Preliminary (PET)',
    'cambridge_b2_first': 'Cambridge B2 First (FCE)',
    'cambridge_c1_advanced': 'Cambridge C1 Advanced (CAE)',
    'cambridge_c2_proficiency': 'Cambridge C2 Proficiency (CPE)',
    
    # Linguaskill
    'linguaskill': 'Linguaskill',
    'linguaskill_business': 'Linguaskill Business',
    
    # Other
    'trinity_ise': 'Trinity ISE',
    'oxford_test': 'Oxford Test of English',
    'toefl_itp': 'TOEFL ITP',
    'aptis': 'APTIS',
}

# ============================================================
# EXAM FAMILIES (for grouping)
# ============================================================

EXAM_FAMILIES = {
    'toefl': ['toefl_ibt', 'toefl_itp'],
    'ielts': ['ielts_academic', 'ielts_general'],
    'pte': ['pte_academic', 'pte_core'],
    'oet': [
        'oet_nursing', 'oet_medicine', 'oet_dentistry', 'oet_pharmacy',
        'oet_physiotherapy', 'oet_veterinary', 'oet_occupational_therapy',
        'oet_podiatry', 'oet_radiography', 'oet_optometry',
        'oet_speech_pathology', 'oet_dietetics'
    ],
    'toeic': ['toeic'],
    'celpip': ['celpip'],
    'cambridge': [
        'cambridge_a2_key', 'cambridge_b1_preliminary', 'cambridge_b2_first',
        'cambridge_c1_advanced', 'cambridge_c2_proficiency'
    ],
    'linguaskill': ['linguaskill', 'linguaskill_business'],
    'trinity': ['trinity_ise'],
    'oxford': ['oxford_test'],
    'aptis': ['aptis'],
}

# ============================================================
# EXAM SECTIONS (all have 4 sections)
# ============================================================

EXAM_SECTIONS = {
    exam_type: ['reading', 'listening', 'speaking', 'writing']
    for exam_type in EXAM_TYPES
}

# ============================================================
# SPEAKING DURATIONS (minutes)
# ============================================================

SPEAKING_DURATIONS = {
    # TOEFL
    'toefl_ibt': 17,
    'toefl_itp': 15,
    
    # IELTS
    'ielts_academic': 14,
    'ielts_general': 14,
    
    # PTE
    'pte_academic': 20,
    'pte_core': 18,
    
    # OET (all same)
    'oet_nursing': 18,
    'oet_medicine': 18,
    'oet_dentistry': 18,
    'oet_pharmacy': 18,
    'oet_physiotherapy': 18,
    'oet_veterinary': 18,
    'oet_occupational_therapy': 18,
    'oet_podiatry': 18,
    'oet_radiography': 18,
    'oet_optometry': 18,
    'oet_speech_pathology': 18,
    'oet_dietetics': 18,
    
    # TOEIC
    'toeic': 10,
    
    # CELPIP
    'celpip': 16,
    
    # Cambridge
    'cambridge_a2_key': 12,
    'cambridge_b1_preliminary': 13,
    'cambridge_b2_first': 14,
    'cambridge_c1_advanced': 15,
    'cambridge_c2_proficiency': 16,
    
    # Linguaskill
    'linguaskill': 15,
    'linguaskill_business': 15,
    
    # Other
    'trinity_ise': 14,
    'oxford_test': 13,
    'aptis': 12,
}

# ============================================================
# WRITING TASKS
# ============================================================

WRITING_TASKS = {
    # Most have 2 tasks
    'toefl_ibt': 2,
    'toefl_itp': 2,
    'ielts_academic': 2,
    'ielts_general': 2,
    'pte_academic': 2,
    'pte_core': 2,
    
    # OET has 1 task (letter)
    'oet_nursing': 1,
    'oet_medicine': 1,
    'oet_dentistry': 1,
    'oet_pharmacy': 1,
    'oet_physiotherapy': 1,
    'oet_veterinary': 1,
    'oet_occupational_therapy': 1,
    'oet_podiatry': 1,
    'oet_radiography': 1,
    'oet_optometry': 1,
    'oet_speech_pathology': 1,
    'oet_dietetics': 1,
    
    # TOEIC has 1 task
    'toeic': 1,
    
    # Rest have 2
    'celpip': 2,
    'cambridge_a2_key': 2,
    'cambridge_b1_preliminary': 2,
    'cambridge_b2_first': 2,
    'cambridge_c1_advanced': 2,
    'cambridge_c2_proficiency': 2,
    'linguaskill': 2,
    'linguaskill_business': 2,
    'trinity_ise': 2,
    'oxford_test': 2,
    'aptis': 2,
}

# ============================================================
# SECTION COSTS - RIVE (Basic Avatar)
# ============================================================

SECTION_COSTS_RIVE = {
    exam_type: {
        'reading': 0.12,  # Average GPT-4 cost
        'listening': 0.14,  # Average GPT-4 cost
        'speaking': SPEAKING_DURATIONS.get(exam_type, 15) * 0.013,  # $0.013/min with Rive
        'writing': WRITING_TASKS.get(exam_type, 2) * 0.012,  # $0.012 per task
    }
    for exam_type in EXAM_TYPES
}

# ============================================================
# SECTION COSTS - D-ID (Premium Avatar)
# ============================================================

SECTION_COSTS_DID = {
    exam_type: {
        'reading': 0.12,
        'listening': 0.14,
        'speaking': SPEAKING_DURATIONS.get(exam_type, 15) * 0.134,  # $0.134/min with D-ID
        'writing': WRITING_TASKS.get(exam_type, 2) * 0.012,
    }
    for exam_type in EXAM_TYPES
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_exam_family(exam_type: str) -> str:
    """Get the family name for an exam type"""
    for family, types in EXAM_FAMILIES.items():
        if exam_type in types:
            return family
    return 'other'

# Valid avatar providers
VALID_AVATAR_PROVIDERS = frozenset(['rive', 'd-id'])


def get_section_cost(exam_type: str, section: str, avatar_provider: str = 'rive') -> float:
    """
    Get cost for a specific section.

    Args:
        exam_type: The exam type identifier
        section: The section name (reading, listening, speaking, writing)
        avatar_provider: Avatar provider ('rive' or 'd-id')

    Returns:
        Cost as float

    Raises:
        ValueError: If avatar_provider is invalid
    """
    # Normalize and validate avatar provider
    avatar_provider = avatar_provider.lower().strip()

    if avatar_provider not in VALID_AVATAR_PROVIDERS:
        raise ValueError(
            f"Invalid avatar provider: '{avatar_provider}'. "
            f"Must be one of: {', '.join(sorted(VALID_AVATAR_PROVIDERS))}"
        )

    if avatar_provider == 'd-id':
        costs = SECTION_COSTS_DID.get(exam_type, {})
    else:
        costs = SECTION_COSTS_RIVE.get(exam_type, {})

    return costs.get(section, 0.0)

def get_full_mock_cost(exam_type: str, avatar_provider: str = 'rive') -> float:
    """
    Get total cost for a full mock exam.

    Args:
        exam_type: The exam type identifier
        avatar_provider: Avatar provider ('rive' or 'd-id')

    Returns:
        Total cost as float

    Raises:
        ValueError: If avatar_provider is invalid
    """
    avatar_provider = avatar_provider.lower().strip()

    if avatar_provider not in VALID_AVATAR_PROVIDERS:
        raise ValueError(
            f"Invalid avatar provider: '{avatar_provider}'. "
            f"Must be one of: {', '.join(sorted(VALID_AVATAR_PROVIDERS))}"
        )

    if avatar_provider == 'd-id':
        costs = SECTION_COSTS_DID.get(exam_type, {})
    else:
        costs = SECTION_COSTS_RIVE.get(exam_type, {})

    return sum(costs.values())

def is_valid_exam_type(exam_type: str) -> bool:
    """Check if exam type is valid."""
    return exam_type in EXAM_TYPES


def get_all_exam_types() -> List[str]:
    """Get list of all exam types."""
    return EXAM_TYPES.copy()

def get_exam_types_by_family(family: str) -> List[str]:
    """Get all exam types in a family."""
    return EXAM_FAMILIES.get(family, [])

def get_exam_info(exam_type: str) -> dict:
    """Get complete info for an exam type"""
    if not is_valid_exam_type(exam_type):
        return None
    
    return {
        'exam_type': exam_type,
        'display_name': EXAM_DISPLAY_NAMES.get(exam_type),
        'family': get_exam_family(exam_type),
        'sections': EXAM_SECTIONS.get(exam_type),
        'speaking_minutes': SPEAKING_DURATIONS.get(exam_type),
        'writing_tasks': WRITING_TASKS.get(exam_type),
        'cost_rive': get_full_mock_cost(exam_type, 'rive'),
        'cost_did': get_full_mock_cost(exam_type, 'd-id'),
    }

# ============================================================
# EXAM DESCRIPTIONS
# ============================================================

EXAM_DESCRIPTIONS = {
    'toefl_ibt': 'Internet-based test for academic English, primarily for US/Canada universities',
    'toefl_itp': 'Institutional paper-based test for placement and progress monitoring',
    'ielts_academic': 'For university admission and professional registration',
    'ielts_general': 'For immigration, work experience and training programs',
    'pte_academic': 'Computer-based test accepted by universities worldwide',
    'pte_core': 'For Canadian immigration (replaces CELPIP for some)',
    'oet_nursing': 'Healthcare English assessment for nurses',
    'oet_medicine': 'Healthcare English assessment for doctors',
    'oet_dentistry': 'Healthcare English assessment for dentists',
    'oet_pharmacy': 'Healthcare English assessment for pharmacists',
    'oet_physiotherapy': 'Healthcare English assessment for physiotherapists',
    'oet_veterinary': 'Healthcare English assessment for veterinarians',
    'oet_occupational_therapy': 'Healthcare English assessment for occupational therapists',
    'oet_podiatry': 'Healthcare English assessment for podiatrists',
    'oet_radiography': 'Healthcare English assessment for radiographers',
    'oet_optometry': 'Healthcare English assessment for optometrists',
    'oet_speech_pathology': 'Healthcare English assessment for speech pathologists',
    'oet_dietetics': 'Healthcare English assessment for dietitians',
    'toeic': 'Business English proficiency test for workplace contexts',
    'celpip': 'Canadian English test for immigration and citizenship',
    'cambridge_a2_key': 'Basic level English qualification (CEFR A2)',
    'cambridge_b1_preliminary': 'Intermediate English qualification (CEFR B1)',
    'cambridge_b2_first': 'Upper-intermediate English qualification (CEFR B2)',
    'cambridge_c1_advanced': 'Advanced English qualification (CEFR C1)',
    'cambridge_c2_proficiency': 'Proficient/native-level English (CEFR C2)',
    'linguaskill': 'Fast, flexible online English test from Cambridge',
    'linguaskill_business': 'Business English version of Linguaskill',
    'trinity_ise': 'Integrated Skills in English from Trinity College London',
    'oxford_test': 'Modular online test from Oxford University Press',
    'aptis': 'Flexible English test from British Council',
}

# ============================================================
# AVERAGE COSTS BY FAMILY (for quick reference)
# ============================================================

def get_family_average_cost(family: str, avatar_provider: str = 'rive') -> float:
    """Get average cost for all exams in a family"""
    exam_types = get_exam_types_by_family(family)
    if not exam_types:
        return 0.0
    
    costs = [get_full_mock_cost(et, avatar_provider) for et in exam_types]
    return sum(costs) / len(costs)

# ============================================================
# MARKET INFORMATION
# ============================================================

MARKET_INFO = {
    'toefl': {
        'annual_test_takers': 2_500_000,
        'primary_regions': ['North America', 'Asia', 'Middle East'],
        'cost_per_test': 195,
    },
    'ielts': {
        'annual_test_takers': 3_500_000,
        'primary_regions': ['UK', 'Australia', 'Europe', 'Asia'],
        'cost_per_test': 250,
    },
    'cambridge': {
        'annual_test_takers': 5_500_000,
        'primary_regions': ['Europe', 'Latin America', 'Asia'],
        'cost_per_test': 180,
    },
    'pte': {
        'annual_test_takers': 500_000,
        'primary_regions': ['Australia', 'UK', 'Canada'],
        'cost_per_test': 200,
    },
    'oet': {
        'annual_test_takers': 100_000,
        'primary_regions': ['Australia', 'UK', 'UAE', 'New Zealand'],
        'cost_per_test': 587,
    },
}

if __name__ == '__main__':
    # Test the configuration
    print(f"Total exam types: {len(EXAM_TYPES)}")
    print(f"\nExam families:")
    for family, types in EXAM_FAMILIES.items():
        print(f"  {family}: {len(types)} types")
    
    print(f"\nAverage costs (Rive):")
    for family in EXAM_FAMILIES.keys():
        avg = get_family_average_cost(family, 'rive')
        print(f"  {family}: ${avg:.3f}")
    
    print(f"\nSample exam info (cambridge_b2_first):")
    info = get_exam_info('cambridge_b2_first')
    for key, value in info.items():
        print(f"  {key}: {value}")
