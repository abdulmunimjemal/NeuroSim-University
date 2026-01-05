# 📋 API Reference

> **Who is this for?** All developers needing quick reference to classes and methods.

---

## Module: `knowledge_graph.py`

### Class: `KnowledgeGraph`

Graph-based storage for university data.

```python
from src.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph("data/university_kg.json")
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_course_by_code` | `code: str` | `dict \| None` | Find course by code (CS101) |
| `get_course_by_id` | `course_id: str` | `dict \| None` | Find course by internal ID |
| `get_faculty_by_name` | `name: str` | `dict \| None` | Find faculty (fuzzy match) |
| `get_faculty_by_id` | `faculty_id: str` | `dict \| None` | Find faculty by ID |
| `get_department_by_code` | `code: str` | `dict \| None` | Find dept (CS, MATH, etc.) |
| `get_prerequisites` | `course_id: str` | `List[dict]` | Direct prerequisites |
| `get_all_prerequisites` | `course_id: str` | `List[dict]` | All prerequisites (transitive) |
| `get_courses_taught_by` | `faculty_id: str` | `List[dict]` | Courses by instructor |
| `get_courses_by_department` | `dept_id: str` | `List[dict]` | Courses in department |
| `get_faculty_by_department` | `dept_id: str` | `List[dict]` | Faculty in department |
| `get_department_head` | `dept_id: str` | `dict \| None` | Department leader |
| `get_courses_requiring` | `course_id: str` | `List[dict]` | Courses that require this one |
| `search_courses` | `query: str` | `List[dict]` | Keyword search in names/descriptions |
| `get_courses_by_level` | `level: str` | `List[dict]` | Filter by "undergraduate"/"graduate" |
| `get_faculty_by_research_area` | `area: str` | `List[dict]` | Find by research interest |

---

## Module: `reasoner.py`

### Enum: `QueryType`

```python
from src.reasoner import QueryType

QueryType.GET_COURSE_INFO
QueryType.GET_ALL_PREREQUISITES
# ... 17 total types
```

### Dataclass: `ReasoningStep`

```python
@dataclass
class ReasoningStep:
    rule_name: str       # e.g., "RESOLVE_COURSE"
    description: str     # Human explanation
    inputs: dict
    outputs: Any
```

### Dataclass: `ReasoningResult`

```python
@dataclass
class ReasoningResult:
    query_type: QueryType
    answer: Any
    success: bool
    reasoning_chain: List[ReasoningStep]
    error_message: Optional[str] = None
```

### Class: `SymbolicReasoner`

```python
from src.reasoner import SymbolicReasoner
from src.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph("data/university_kg.json")
reasoner = SymbolicReasoner(kg)

result = reasoner.reason(QueryType.GET_PREREQUISITES, {"course_code": "CS401"})
```

#### Methods

| Method | Parameters | Returns |
|--------|------------|---------|
| `reason` | `query_type: QueryType, params: dict` | `ReasoningResult` |

---

## Module: `llm_interface.py`

### Dataclass: `ParsedQuery`

```python
@dataclass
class ParsedQuery:
    original_question: str
    query_type: QueryType
    parameters: dict
    confidence: float  # 0.0 to 1.0
```

### Class: `LLMInterface`

```python
from src.llm_interface import LLMInterface

llm = LLMInterface()  # Uses LLM_PROVIDER env var

# Parse question
parsed = llm.parse_question("Prerequisites for CS401?")
# parsed.query_type == QueryType.GET_PREREQUISITES
# parsed.parameters == {"course_code": "CS401"}

# Generate answer
answer = llm.generate_answer("Prerequisites?", reasoning_result)
# Returns formatted string
```

#### Methods

| Method | Parameters | Returns |
|--------|------------|---------|
| `parse_question` | `question: str` | `ParsedQuery` |
| `generate_answer` | `question: str, result: ReasoningResult` | `str` |

### Provider Classes

```python
from src.llm_interface import OpenAIProvider, GeminiProvider, MockLLMProvider

# Custom provider
llm = LLMInterface(provider=OpenAIProvider(api_key="sk-xxx"))
```

---

## Module: `main.py`

### Dataclass: `AgentResponse`

```python
@dataclass
class AgentResponse:
    parsed_query: ParsedQuery
    reasoning_result: ReasoningResult
    answer: str
    explanation: str
```

### Class: `UniversityQAAgent`

```python
from src.main import UniversityQAAgent

agent = UniversityQAAgent(llm_provider="mock")

response = agent.process_query("What is CS101?")
print(response.answer)
print(response.explanation)
```

#### Methods

| Method | Parameters | Returns |
|--------|------------|---------|
| `process_query` | `question: str` | `AgentResponse` |

---

## Quick Examples

### Get All Prerequisites
```python
from src.main import UniversityQAAgent

agent = UniversityQAAgent()
result = agent.process_query("All prerequisites for CS401?")
print(result.answer)
```

### Direct Knowledge Graph Query
```python
from src.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph("data/university_kg.json")
prereqs = kg.get_all_prerequisites("cs401")
for p in prereqs:
    print(f"{p['code']}: {p['name']}")
```

### Custom LLM Provider
```python
from src.llm_interface import LLMInterface
from src.reasoner import SymbolicReasoner
from src.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph("data/university_kg.json")
reasoner = SymbolicReasoner(kg)
llm = LLMInterface()  # or with custom provider

parsed = llm.parse_question("Who teaches CS401?")
result = reasoner.reason(parsed.query_type, parsed.parameters)
answer = llm.generate_answer("Who teaches CS401?", result)
```

---

## Next Steps

- 🧪 [Testing Guide](./07-TESTING.md) - How to test your changes
