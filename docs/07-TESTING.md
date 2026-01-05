# 🧪 Testing Guide

> **Who is this for?** QA engineers and developers writing/running tests.

---

## Test Suite Overview

| File | Type | Count | Purpose |
|------|------|-------|---------|
| `test_questions.py` | Integration | 50 | End-to-end QA tests |
| `test_knowledge_graph.py` | Unit | 20 | Knowledge graph methods |

---

## Running Tests

### Full QA Test Suite

```bash
python tests/test_questions.py
```

**Output**:
```
[1] ✅ PASS | SIMPLE       | Course info lookup
    Q: What is CS101?
    Expected: GET_COURSE_INFO, Got: get_course_info

...

======================================================================
TEST SUMMARY
======================================================================

Total: 50 | Passed: 48 | Failed: 2
Success Rate: 96.0%

By Category:
  SIMPLE         : 10/10 (100%)
  INTERMEDIATE   : 10/10 (100%)
  COMPLEX        : 10/10 (100%)
  TRICKY         : 8/10 (80%)
  MULTI-STEP     : 10/10 (100%)
======================================================================
```

### Run Specific Test

```bash
python tests/test_questions.py --test 11
```

### Quiet Mode (Summary Only)

```bash
python tests/test_questions.py --quiet
```

### Unit Tests (pytest)

```bash
# All unit tests
python -m pytest tests/test_knowledge_graph.py -v

# Specific test class
python -m pytest tests/test_knowledge_graph.py::TestCourseQueries -v
```

---

## Test Categories Explained

### Simple (10 tests)
**Focus**: Direct entity lookups

```python
{
    "question": "What is CS101?",
    "expected_type": "GET_COURSE_INFO"
}
```

**Examples**:
- Course info by code
- Faculty info by name
- Department info
- Count entities

### Intermediate (10 tests)
**Focus**: Single-hop relationship queries

```python
{
    "question": "What are the prerequisites for CS201?",
    "expected_type": "GET_PREREQUISITES"
}
```

**Examples**:
- Direct prerequisites
- Courses by department
- Faculty by department
- Courses taught by faculty

### Complex (10 tests)
**Focus**: Multi-step reasoning

```python
{
    "question": "What are ALL prerequisites for CS401 including transitive?",
    "expected_type": "GET_ALL_PREREQUISITES"
}
```

**Examples**:
- Transitive prerequisites
- Course comparisons
- Level filtering
- Research area search

### Tricky (10 tests)
**Focus**: Informal phrasing, edge cases

```python
{
    "question": "What do I need for ML?",
    "expected_type": "GET_ALL_PREREQUISITES",
    "alternative_types": ["GET_PREREQUISITES"]
}
```

**Examples**:
- Informal course names ("ML" → CS401)
- Possessive forms ("Dr. Smith's classes")
- Short queries ("Prereqs for Algorithms")

### Multi-step (10 tests)
**Focus**: Compound queries requiring multiple operations

```python
{
    "question": "List courses taught by the head of CS",
    "expected_type": "GET_COURSES_TAUGHT_BY"
}
```

**Examples**:
- Head of department → their courses
- Eligibility checks
- Count after lookup

---

## Test Structure

### QA Test Entry

```python
{
    "id": 1,
    "question": "What is CS101?",
    "category": "simple",
    "expected_type": "GET_COURSE_INFO",
    "alternative_types": [],  # Optional: other valid types
    "description": "Course info lookup"
}
```

### Pass Criteria

A test passes if:
1. `query_type` matches `expected_type` OR is in `alternative_types`
2. `reasoning_result.success` is `True`

---

## Adding New Tests

Edit `tests/test_questions.py`:

```python
TEST_QUESTIONS = [
    # ... existing tests
    
    {
        "id": 51,
        "question": "Your new question here",
        "category": "simple",  # or intermediate/complex/tricky/multi-step
        "expected_type": "GET_COURSE_INFO",
        "description": "Brief description"
    },
]
```

---

## Unit Test Structure

`test_knowledge_graph.py`:

```python
class TestCourseQueries:
    def test_get_course_by_code(self):
        course = kg.get_course_by_code("CS101")
        assert course is not None
        assert course['name'] == "Introduction to Programming"
    
    def test_get_prerequisites(self):
        prereqs = kg.get_prerequisites("cs201")
        assert len(prereqs) == 1
        assert prereqs[0]['code'] == "CS101"

class TestTransitiveQueries:
    def test_get_all_prerequisites(self):
        all_prereqs = kg.get_all_prerequisites("cs401")
        assert len(all_prereqs) >= 5  # Multiple levels
```

---

## Test Results History

| Version | Tests | Pass Rate | Notes |
|---------|-------|-----------|-------|
| v1.0 | 25 | 68% | Initial mock LLM |
| v1.1 | 25 | 88% | Pattern improvements |
| v1.2 | 25 | 96% | Course name resolution |
| v2.0 | 50 | 96% | Expanded test suite |

---

## Debugging Failed Tests

### 1. Run single test with output

```bash
python tests/test_questions.py --test 20
```

### 2. Check the reasoning trace

The output shows:
- Expected vs. actual query type
- The answer generated (or error message)

### 3. Test the pattern directly

```python
from src.llm_interface import MockLLMProvider

provider = MockLLMProvider()
result = provider.generate('Question: "Your question here"')
print(result)
```

### 4. Test knowledge graph directly

```python
from src.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph("data/university_kg.json")
print(kg.get_course_by_code("CS401"))
print(kg.get_all_prerequisites("cs401"))
```

---

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| QA Tests | >90% | 96% |
| Unit Tests | 100% | 100% |
| Edge Cases | >80% | 80% |

---

## Back to Docs

- 📚 [Documentation Index](./README.md)
- 📖 [Main README](../README.md)
