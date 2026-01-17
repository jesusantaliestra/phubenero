-- ================================================
-- MIGRATION 008: Update constraints for 30 exam types
-- Date: 2026-01-14
-- ================================================

-- This migration updates CHECK constraints to support all 30 exam types:
-- TIER 1 - Core Exams (17):
-- - 1 TOEFL iBT
-- - 2 IELTS variants
-- - 2 PTE variants  
-- - 12 OET professions
--
-- TIER 2 - Additional (13):
-- - 1 TOEIC
-- - 1 CELPIP
-- - 5 Cambridge levels (A2-C2)
-- - 2 Linguaskill
-- - 1 TOEFL ITP
-- - 1 Trinity ISE
-- - 1 Oxford Test
-- - 1 APTIS

-- Drop old constraints
ALTER TABLE student_licenses DROP CONSTRAINT IF EXISTS valid_exam_type;
ALTER TABLE exam_usage DROP CONSTRAINT IF EXISTS valid_usage_exam_type;
ALTER TABLE exam_dashboards DROP CONSTRAINT IF EXISTS valid_dashboard_exam_type;

-- Add new constraints with 30 exam types
ALTER TABLE student_licenses ADD CONSTRAINT valid_exam_type CHECK (exam_type IN (
    -- TOEFL (2)
    'toefl_ibt', 'toefl_itp',
    
    -- IELTS (2)
    'ielts_academic', 'ielts_general',
    
    -- PTE (2)
    'pte_academic', 'pte_core',
    
    -- OET (12 professions)
    'oet_nursing', 'oet_medicine', 'oet_dentistry', 'oet_pharmacy',
    'oet_physiotherapy', 'oet_veterinary', 'oet_occupational_therapy',
    'oet_podiatry', 'oet_radiography', 'oet_optometry',
    'oet_speech_pathology', 'oet_dietetics',
    
    -- TOEIC (1)
    'toeic',
    
    -- CELPIP (1)
    'celpip',
    
    -- Cambridge (5 levels)
    'cambridge_a2_key', 'cambridge_b1_preliminary', 'cambridge_b2_first',
    'cambridge_c1_advanced', 'cambridge_c2_proficiency',
    
    -- Linguaskill (2)
    'linguaskill', 'linguaskill_business',
    
    -- Other specialized (3)
    'trinity_ise', 'oxford_test', 'aptis'
));

ALTER TABLE exam_usage ADD CONSTRAINT valid_usage_exam_type CHECK (exam_type IN (
    'toefl_ibt', 'toefl_itp',
    'ielts_academic', 'ielts_general',
    'pte_academic', 'pte_core',
    'oet_nursing', 'oet_medicine', 'oet_dentistry', 'oet_pharmacy',
    'oet_physiotherapy', 'oet_veterinary', 'oet_occupational_therapy',
    'oet_podiatry', 'oet_radiography', 'oet_optometry',
    'oet_speech_pathology', 'oet_dietetics',
    'toeic', 'celpip',
    'cambridge_a2_key', 'cambridge_b1_preliminary', 'cambridge_b2_first',
    'cambridge_c1_advanced', 'cambridge_c2_proficiency',
    'linguaskill', 'linguaskill_business',
    'trinity_ise', 'oxford_test', 'aptis'
));

ALTER TABLE exam_dashboards ADD CONSTRAINT valid_dashboard_exam_type CHECK (exam_type IN (
    'toefl_ibt', 'toefl_itp',
    'ielts_academic', 'ielts_general',
    'pte_academic', 'pte_core',
    'oet_nursing', 'oet_medicine', 'oet_dentistry', 'oet_pharmacy',
    'oet_physiotherapy', 'oet_veterinary', 'oet_occupational_therapy',
    'oet_podiatry', 'oet_radiography', 'oet_optometry',
    'oet_speech_pathology', 'oet_dietetics',
    'toeic', 'celpip',
    'cambridge_a2_key', 'cambridge_b1_preliminary', 'cambridge_b2_first',
    'cambridge_c1_advanced', 'cambridge_c2_proficiency',
    'linguaskill', 'linguaskill_business',
    'trinity_ise', 'oxford_test', 'aptis'
));

-- Update exam_types_meta table with ALL 30 exam types
INSERT INTO exam_types_meta (exam_type, display_name, description, sections, avg_duration_minutes) VALUES
-- TOEFL (2)
('toefl_ibt', 'TOEFL iBT', 'Internet-based test for academic English, primarily for US/Canada universities', '["reading", "listening", "speaking", "writing"]', 180),
('toefl_itp', 'TOEFL ITP', 'Institutional paper-based test for placement and progress monitoring', '["reading", "listening", "speaking", "writing"]', 150),

-- IELTS (2)
('ielts_academic', 'IELTS Academic', 'For university admission and professional registration', '["reading", "listening", "speaking", "writing"]', 165),
('ielts_general', 'IELTS General Training', 'For immigration, work experience and training programs', '["reading", "listening", "speaking", "writing"]', 165),

-- PTE (2)
('pte_academic', 'PTE Academic', 'Computer-based test accepted by universities worldwide', '["reading", "listening", "speaking", "writing"]', 150),
('pte_core', 'PTE Core', 'For Canadian immigration (replaces CELPIP for some)', '["reading", "listening", "speaking", "writing"]', 140),

-- OET (12 professions)
('oet_nursing', 'OET Nursing', 'Healthcare English assessment for nurses', '["reading", "listening", "speaking", "writing"]', 175),
('oet_medicine', 'OET Medicine', 'Healthcare English assessment for doctors', '["reading", "listening", "speaking", "writing"]', 175),
('oet_dentistry', 'OET Dentistry', 'Healthcare English assessment for dentists', '["reading", "listening", "speaking", "writing"]', 175),
('oet_pharmacy', 'OET Pharmacy', 'Healthcare English assessment for pharmacists', '["reading", "listening", "speaking", "writing"]', 175),
('oet_physiotherapy', 'OET Physiotherapy', 'Healthcare English assessment for physiotherapists', '["reading", "listening", "speaking", "writing"]', 175),
('oet_veterinary', 'OET Veterinary Science', 'Healthcare English assessment for veterinarians', '["reading", "listening", "speaking", "writing"]', 175),
('oet_occupational_therapy', 'OET Occupational Therapy', 'Healthcare English assessment for occupational therapists', '["reading", "listening", "speaking", "writing"]', 175),
('oet_podiatry', 'OET Podiatry', 'Healthcare English assessment for podiatrists', '["reading", "listening", "speaking", "writing"]', 175),
('oet_radiography', 'OET Radiography', 'Healthcare English assessment for radiographers', '["reading", "listening", "speaking", "writing"]', 175),
('oet_optometry', 'OET Optometry', 'Healthcare English assessment for optometrists', '["reading", "listening", "speaking", "writing"]', 175),
('oet_speech_pathology', 'OET Speech Pathology', 'Healthcare English assessment for speech pathologists', '["reading", "listening", "speaking", "writing"]', 175),
('oet_dietetics', 'OET Dietetics', 'Healthcare English assessment for dietitians', '["reading", "listening", "speaking", "writing"]', 175),

-- TOEIC (1)
('toeic', 'TOEIC', 'Business English proficiency test for workplace contexts', '["reading", "listening", "speaking", "writing"]', 120),

-- CELPIP (1)
('celpip', 'CELPIP', 'Canadian English test for immigration and citizenship', '["reading", "listening", "speaking", "writing"]', 180),

-- Cambridge (5 levels)
('cambridge_a2_key', 'Cambridge A2 Key (KET)', 'Basic level English qualification (CEFR A2)', '["reading", "listening", "speaking", "writing"]', 140),
('cambridge_b1_preliminary', 'Cambridge B1 Preliminary (PET)', 'Intermediate English qualification (CEFR B1)', '["reading", "listening", "speaking", "writing"]', 140),
('cambridge_b2_first', 'Cambridge B2 First (FCE)', 'Upper-intermediate English qualification (CEFR B2)', '["reading", "listening", "speaking", "writing"]', 210),
('cambridge_c1_advanced', 'Cambridge C1 Advanced (CAE)', 'Advanced English qualification (CEFR C1)', '["reading", "listening", "speaking", "writing"]', 235),
('cambridge_c2_proficiency', 'Cambridge C2 Proficiency (CPE)', 'Proficient/native-level English (CEFR C2)', '["reading", "listening", "speaking", "writing"]', 240),

-- Linguaskill (2)
('linguaskill', 'Linguaskill', 'Fast, flexible online English test from Cambridge', '["reading", "listening", "speaking", "writing"]', 140),
('linguaskill_business', 'Linguaskill Business', 'Business English version of Linguaskill', '["reading", "listening", "speaking", "writing"]', 140),

-- Other specialized (3)
('trinity_ise', 'Trinity ISE', 'Integrated Skills in English from Trinity College London', '["reading", "listening", "speaking", "writing"]', 150),
('oxford_test', 'Oxford Test of English', 'Modular online test from Oxford University Press', '["reading", "listening", "speaking", "writing"]', 120),
('aptis', 'APTIS', 'Flexible English test from British Council', '["reading", "listening", "speaking", "writing"]', 130)
ON CONFLICT (exam_type) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    sections = EXCLUDED.sections,
    avg_duration_minutes = EXCLUDED.avg_duration_minutes;

-- Verify the migration
DO $$
DECLARE
    exam_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO exam_count FROM exam_types_meta;
    RAISE NOTICE 'Migration complete! Total exam types: %', exam_count;
    
    IF exam_count < 30 THEN
        RAISE EXCEPTION 'Expected 30 exam types, found %', exam_count;
    END IF;
END $$;
