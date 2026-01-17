# 📝 PROMPT TEMPLATES FOR MOCK EXAM GENERATION
## Professional Quality AI-Generated Mock Exams

**Version:** 1.0  
**Date:** 2026-01-14  
**Purpose:** Generate academically accurate mock exam questions using Claude/GPT

---

## 🎯 CORE PRINCIPLES

1. **Academic Accuracy:** Questions must match official exam format exactly
2. **CEFR Alignment:** Vocabulary and complexity must match target level
3. **Topic Authenticity:** Use topics from official sources
4. **Variety:** Avoid repetitive patterns
5. **Professional Quality:** Indistinguishable from official exams

---

## 📚 PROMPT TEMPLATES BY EXAM TYPE

### Cambridge B2 First (FCE) - Reading Part 1

```
Generate a Cambridge B2 First Reading Part 1 multiple-choice cloze exercise.

REQUIREMENTS:
- Text length: 150-170 words
- CEFR Level: B2
- Vocabulary: 3,500-4,000 word level
- Topic: [INSERT TOPIC FROM TOPIC SELECTOR]
- 8 gaps with 4 options each (A, B, C, D)

FORMAT:
- Focus on: vocabulary, collocations, fixed phrases, complementation
- Distractors must be plausible
- Text must be coherent and natural
- Topic should be interesting and engaging

EXAMPLE TOPIC: Technology and Innovation

Please generate the complete exercise with answer key.
```

### Cambridge B2 First (FCE) - Writing Part 1 (Essay)

```
Generate a Cambridge B2 First Writing Part 1 essay prompt.

REQUIREMENTS:
- Task: Argumentative essay
- CEFR Level: B2
- Word count: 140-190 words
- Topic: [INSERT TOPIC FROM TOPIC SELECTOR]
- Must include: two viewpoints and your opinion

FORMAT:
Essay title: "Some people think that... Other people believe that... 
Discuss both views and give your own opinion."

ASSESSMENT CRITERIA:
- Content: All points addressed
- Communicative Achievement: Holds target reader's attention
- Organisation: Clear structure with linking devices
- Language: Range and accuracy appropriate to B2

EXAMPLE TOPIC: Environment and Sustainability
Focus area: Renewable energy vs. traditional energy sources

Please generate the complete essay prompt with assessment criteria.
```

### Cambridge C1 Advanced (CAE) - Listening Part 1

```
Generate a Cambridge C1 Advanced Listening Part 1 transcript.

REQUIREMENTS:
- 3 short unrelated extracts
- Duration: ~30 seconds each
- CEFR Level: C1
- Vocabulary: 5,000-6,000 word level
- Topics: [INSERT 3 TOPICS FROM TOPIC SELECTOR]
- 2 multiple-choice questions per extract

FORMAT:
- Each extract: monologue or dialogue
- Questions focus on: attitude, opinion, purpose, feeling, main idea, gist
- Natural, conversational language
- Some idiomatic expressions
- Sophisticated vocabulary

EXAMPLE TOPICS:
1. Professional Development - Career advancement strategies
2. Arts & Culture - Contemporary art trends
3. Science & Technology - Artificial intelligence ethics

Please generate transcripts and questions with answer key.
```

### IELTS Academic - Reading Passage

```
Generate an IELTS Academic Reading passage with questions.

REQUIREMENTS:
- Passage length: 850-950 words
- CEFR Level: B2-C1
- Topic: [INSERT TOPIC FROM TOPIC SELECTOR]
- Academic style (journal article, research report, etc.)
- Question types: 
  * True/False/Not Given (4 questions)
  * Matching headings (5 questions)
  * Multiple choice (4 questions)

FORMAT:
- Introduction paragraph
- 4-5 body paragraphs with clear headings
- Academic vocabulary
- Complex sentence structures
- Cohesive devices
- Formal register

EXAMPLE TOPIC: Climate Change - Carbon capture technologies

Please generate the complete passage and all question types with answer key.
```

### IELTS Academic - Writing Task 2

```
Generate an IELTS Academic Writing Task 2 prompt.

REQUIREMENTS:
- CEFR Level: B2-C1
- Word count: 250+ words
- Topic: [INSERT TOPIC FROM TOPIC SELECTOR]
- Essay type: [Opinion/Discussion/Problem-Solution/Two-part]

FORMAT:
"[Topic statement with context]

To what extent do you agree or disagree?

Give reasons for your answer and include any relevant examples from your 
own knowledge or experience."

ASSESSMENT CRITERIA:
- Task Response
- Coherence and Cohesion
- Lexical Resource
- Grammatical Range and Accuracy

EXAMPLE TOPIC: Education - University education vs. vocational training

Please generate the complete task with band descriptors.
```

### TOEFL iBT - Reading Passage

```
Generate a TOEFL iBT Reading passage with questions.

REQUIREMENTS:
- Passage length: 700 words
- CEFR Level: B2-C1
- Topic: [INSERT TOPIC FROM TOPIC SELECTOR]
- Academic context (university textbook style)
- Question types:
  * Factual information (3 questions)
  * Negative factual (1 question)
  * Inference (2 questions)
  * Vocabulary (2 questions)
  * Sentence insertion (1 question)
  * Prose summary (1 question)

FORMAT:
- University-level academic text
- 4-6 paragraphs
- Topic sentences clearly stated
- Supporting details and examples
- Academic vocabulary in context

EXAMPLE TOPIC: Biology - Photosynthesis in extreme environments

Please generate passage and all question types with answer key and explanations.
```

### PTE Academic - Read Aloud

```
Generate PTE Academic Read Aloud texts.

REQUIREMENTS:
- 6-8 texts
- Length: 60 words each
- CEFR Level: B2-C1
- Topics: [INSERT TOPICS FROM TOPIC SELECTOR]
- Complexity: Academic style with some complex sentences

FORMAT:
- Natural reading flow
- Appropriate punctuation
- No tongue-twisters
- Academic vocabulary
- Varied sentence structures

SCORING CRITERIA:
- Content: All words pronounced
- Oral fluency: Smooth, natural pace
- Pronunciation: Clear and accurate

EXAMPLE TOPICS:
1. Technology - Quantum computing basics
2. Environment - Ocean acidification
3. Business - Global supply chains

Please generate 6 texts suitable for read-aloud assessment.
```

### OET Medicine - Reading Part A

```
Generate OET Medicine Reading Part A text and questions.

REQUIREMENTS:
- Text type: Summary completion (case notes)
- Word count: 350-400 words
- Topic: [INSERT MEDICAL TOPIC]
- Questions: 15-20 gap-fill items
- Medical terminology appropriate for healthcare professionals

FORMAT:
- Patient case presentation
- Clinical history
- Examination findings
- Treatment plan
- Follow-up information

ASSESSMENT FOCUS:
- Medical vocabulary
- Clinical comprehension
- Detail extraction
- Professional register

EXAMPLE TOPIC: Cardiology - Acute coronary syndrome management

Please generate case notes with gap-fill questions and answer key.
```

### Linguaskill Business - Writing Part 1

```
Generate a Linguaskill Business Writing Part 1 task.

REQUIREMENTS:
- Task type: Email
- CEFR Level: [A2/B1/B2/C1] - ADAPTIVE
- Word count: 50+ words (for B1+)
- Topic: [INSERT BUSINESS TOPIC]
- Scenario: Professional workplace communication

FORMAT:
- Situation described
- 3 bullet points to address
- Professional context
- Clear purpose

SCORING CRITERIA:
- Content: All points covered
- Communicative Quality: Appropriate register
- Organisation: Logical structure
- Language: Accuracy and range

EXAMPLE TOPIC: Business Operations - Vendor management issue

Scenario: You need to email a supplier about a delivery delay.

Write an email to the supplier. In your email, you should:
• explain the problem
• ask about the new delivery date
• request compensation for the inconvenience

Please generate the complete task prompt.
```

---

## 🔧 USAGE GUIDE

### Step 1: Select Topic

```python
from topic_selector import get_topic_selector

selector = get_topic_selector()
topic = selector.get_random_topic('cambridge_b2_first', 'reading', user_id='123')
```

### Step 2: Insert Topic into Template

Replace `[INSERT TOPIC FROM TOPIC SELECTOR]` with the selected topic.

### Step 3: Generate with AI

Send the complete prompt to Claude/GPT to generate the mock exam content.

### Step 4: Validate Quality

- Check CEFR alignment
- Verify topic authenticity
- Ensure format matches official exams
- Validate answer key accuracy

---

## 📊 QUALITY CHECKLIST

### For All Exam Types:

- [ ] CEFR level appropriate
- [ ] Vocabulary matches target level
- [ ] Topic from official sources
- [ ] Format matches official exam
- [ ] Instructions clear and complete
- [ ] Answer key provided
- [ ] Distractors plausible
- [ ] No grammatical errors
- [ ] Professional appearance
- [ ] Assessment criteria included

### Additional for Reading:

- [ ] Text length correct
- [ ] Passage coherent and engaging
- [ ] Questions test comprehension
- [ ] Question types appropriate
- [ ] Natural language flow

### Additional for Writing:

- [ ] Prompt clear and unambiguous
- [ ] Word count specified
- [ ] Assessment criteria defined
- [ ] Task achievable in time limit
- [ ] Sample answer available (optional)

### Additional for Listening:

- [ ] Transcript natural and conversational
- [ ] Timing appropriate
- [ ] Audio producible
- [ ] Questions test listening skills
- [ ] Accent diversity (where applicable)

### Additional for Speaking:

- [ ] Prompts elicit appropriate responses
- [ ] Time limits realistic
- [ ] Topics allow for elaboration
- [ ] Assessment rubric provided
- [ ] Sample responses available (optional)

---

## 🎓 BEST PRACTICES

### 1. Topic Selection

- Use topic selector for authenticity
- Avoid recent news events (dates quickly)
- Choose engaging, universal topics
- Ensure cultural neutrality

### 2. Language Level

- A2: ~1,500 common words
- B1: ~2,500 words, simple structures
- B2: ~3,500-4,000 words, complex structures
- C1: ~5,000-6,000 words, sophisticated language
- C2: ~8,000+ words, near-native fluency

### 3. Question Writing

- One clear correct answer
- Plausible distractors
- Test understanding, not trickery
- Avoid negatives in questions
- Use clear, simple language

### 4. Content Quality

- Error-free grammar
- Natural language
- Professional appearance
- Culturally appropriate
- Academically sound

---

## 🚀 AUTOMATION WORKFLOW

### Recommended Process:

```python
def generate_mock_exam(exam_type, avatar_provider='rive'):
    # 1. Initialize selector
    selector = get_topic_selector()
    
    # 2. Generate topics for all sections
    mock_topics = selector.generate_mock_exam_topics(exam_type, user_id='auto')
    
    # 3. For each section, generate questions
    for section, data in mock_topics['sections'].items():
        # Get appropriate prompt template
        template = get_prompt_template(exam_type, section)
        
        # Insert topic
        prompt = template.replace('[INSERT TOPIC]', data['topic'])
        
        # Generate with AI
        questions = generate_with_ai(prompt)
        
        # Validate quality
        if validate_questions(questions, exam_type, section):
            save_to_database(questions)
    
    return mock_exam_id
```

---

## 📚 REFERENCES

- Cambridge Assessment English Official Handbooks
- ETS TOEFL Official Guides
- IELTS Official Materials
- PTE Academic Official Guide
- OET Official Preparation Materials

---

**These templates ensure professional, academically accurate mock exams 
that match official exam quality standards.** ✨

*Last Updated: 2026-01-14*
