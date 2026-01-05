# 🤖 LLM Integration

> **Who is this for?** ML engineers and developers working on query understanding.

---

## Overview

The LLM Interface serves two purposes:
1. **Parse** natural language questions into structured queries
2. **Generate** human-readable answers from reasoning results

---

## Provider Architecture

```python
# Abstract base class
class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

# Implementations
class OpenAIProvider(BaseLLMProvider): ...
class GeminiProvider(BaseLLMProvider): ...
class MockLLMProvider(BaseLLMProvider): ...  # Pattern-based
```

### Switching Providers

```bash
# Environment variable
LLM_PROVIDER=openai python -m src.main
LLM_PROVIDER=gemini python -m src.main
LLM_PROVIDER=mock python -m src.main  # Default
```

Or programmatically:
```python
from src.llm_interface import LLMInterface, OpenAIProvider

llm = LLMInterface(provider=OpenAIProvider(api_key="sk-xxx"))
```

---

## Query Parsing

### Input/Output

```
Input:  "What prerequisites do I need for Machine Learning?"

Output: ParsedQuery(
    original_question="...",
    query_type=QueryType.GET_ALL_PREREQUISITES,
    parameters={"course_code": "CS401"},
    confidence=0.85
)
```

### Real LLM Approach (OpenAI/Gemini)

**Prompt Template**:
```
You are a query parser for a university knowledge base.

Available query types:
- GET_COURSE_INFO: Get details about a specific course
- GET_PREREQUISITES: Get direct prerequisites
- GET_ALL_PREREQUISITES: Get ALL prerequisites (transitive)
...

Question: "{user_question}"

Respond with JSON:
{
    "query_type": "<TYPE>",
    "parameters": {...},
    "confidence": 0.0-1.0
}
```

### Mock LLM Approach (Pattern Matching)

For cost-free testing, the mock provider uses regex patterns:

```python
patterns = [
    # "all prerequisites for X"
    (r"all\s+prerequisite[s]?\s+for\s+(\w+\d+)", 
     "GET_ALL_PREREQUISITES",
     lambda m: {"course_code": m.group(1).upper()}),
    
    # "prerequisites for X"
    (r"prerequisite[s]?\s+for\s+(\w+\d+)",
     "GET_PREREQUISITES", 
     lambda m: {"course_code": m.group(1).upper()}),
    
    # "who teaches X"
    (r"who\s+teaches?\s+(\w+\d+)",
     "GET_COURSE_INSTRUCTORS",
     lambda m: {"course_code": m.group(1).upper()}),
    
    # ... 30+ patterns
]
```

**Pattern Priority**: More specific patterns are checked first (e.g., "all prerequisites" before "prerequisites").

---

## Course Name Resolution

The mock LLM maps informal course names to codes:

```python
COURSE_NAME_MAP = {
    "machine learning": "CS401",
    "algorithms": "CS301",
    "data structures": "CS201",
    "nlp": "CS402",
    "calculus": "MATH101",
    # ...
}
```

**Example**:
```
Input:  "Prerequisites for Machine Learning"
Maps:   "Machine Learning" → "CS401"
Output: {course_code: "CS401"}
```

---

## Department Name Normalization

```python
dept_map = {
    "computer science": "CS",
    "cs": "CS",
    "comp": "CS",
    "mathematics": "MATH",
    "math": "MATH",
    # ...
}
```

---

## Answer Generation

After the reasoner executes, we format the result:

```python
def generate_answer(self, question: str, result: ReasoningResult) -> str:
    if result.query_type == QueryType.GET_PREREQUISITES:
        return self._format_prerequisites(result.answer)
    
    elif result.query_type == QueryType.GET_COURSE_INFO:
        return self._format_course_info(result.answer)
    
    # ... type-specific formatting
```

**Example Formats**:

```markdown
# Course Info
**CS401 - Machine Learning**
- Credits: 4
- Level: Graduate
- Prerequisites: CS301, MATH201, MATH401

# Prerequisites List
Direct prerequisites:
- CS301: Algorithms
- MATH201: Linear Algebra
- MATH401: Probability and Statistics

# Comparison Table
| Aspect | CS301 | CS401 |
|--------|-------|-------|
| Credits | 4 | 4 |
| Level | Undergraduate | Graduate |
```

---

## Confidence Scores

| Score | Meaning |
|-------|---------|
| 0.85+ | High confidence, clear match |
| 0.50-0.84 | Medium confidence, possible ambiguity |
| < 0.50 | Low confidence, fallback to search |

---

## Error Handling

```python
try:
    parsed = json.loads(llm_response)
except JSONDecodeError:
    # Fallback to search
    return ParsedQuery(
        query_type=QueryType.SEARCH_COURSES,
        parameters={"query": question},
        confidence=0.3
    )
```

---

## Next Steps

- 🔮 [Symbolic Reasoning](./05-SYMBOLIC-REASONING.md) - How queries are executed
- 📋 [API Reference](./06-API-REFERENCE.md) - Full class documentation
