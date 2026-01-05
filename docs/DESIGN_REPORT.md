# Design Report: Neuro-Symbolic University QA Agent

## 1. Introduction

### 1.1 Project Objective
Build a question-answering agent that combines Large Language Models (LLMs) with symbolic reasoning for answering university-related queries about courses, faculty, departments, and prerequisites.

### 1.2 Scope
- Create a knowledge graph representing university entities and relationships
- Implement symbolic reasoning rules for query execution
- Integrate an LLM for natural language understanding
- Provide transparent explanations for all answers

---

## 2. System Architecture

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface (CLI)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    UniversityQAAgent                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  LLM Interface  │→ │ Symbolic Reasoner│→ │Answer Generator│ │
│  │  (NL → Query)   │  │ (Query Execution)│  │(Result → NL)   │ │
│  └─────────────────┘  └──────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Graph (NetworkX)                    │
│  Nodes: Departments, Faculty, Courses                           │
│  Edges: belongs_to, teaches, prerequisite, heads                │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Breakdown

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| `KnowledgeGraph` | Store and query university data | NetworkX, JSON |
| `SymbolicReasoner` | Execute structured queries, track reasoning | Python rules |
| `LLMInterface` | NL→Query translation, answer generation | OpenAI/Gemini/Mock |
| `UniversityQAAgent` | Orchestrate pipeline, combine results | Python |

---

## 3. Knowledge Graph Design

### 3.1 Schema Design Decisions

**Choice: JSON + NetworkX over RDF/OWL**

*Rationale:*
- Simpler development and debugging
- No external dependencies (no triple store needed)
- Sufficient for the ~30 entity scale
- Fast in-memory operations for demos

**Entity Types:**
1. **Department** - Organizational units (CS, MATH, PHYS, EE)
2. **Faculty** - Professors with research areas
3. **Course** - Academic courses with levels and credits

**Relationship Types:**
1. `belongs_to` - Faculty/Course membership in Department
2. `teaches` - Faculty instructing a Course
3. `prerequisite` - Course dependency chains
4. `heads` - Department leadership

### 3.2 Sample Data Statistics
- 4 Departments
- 7 Faculty members
- 18 Courses
- 24 Prerequisite relationships
- 70 total edges in the graph

---

## 4. Symbolic Reasoning Approach

### 4.1 Query Type Taxonomy

We defined **17 distinct query types** organized by complexity:

**Simple (Direct Lookups):**
- `GET_COURSE_INFO`, `GET_FACULTY_INFO`, `GET_DEPARTMENT_INFO`

**Relationship Queries:**
- `GET_PREREQUISITES`, `GET_COURSES_BY_DEPARTMENT`, `GET_COURSES_TAUGHT_BY`
- `GET_COURSE_INSTRUCTORS`, `GET_FACULTY_BY_DEPARTMENT`, `GET_DEPARTMENT_HEAD`

**Complex Reasoning:**
- `GET_ALL_PREREQUISITES` - Transitive closure computation
- `CAN_TAKE_COURSE` - Prerequisite satisfaction checking
- `GET_COURSES_REQUIRING` - Reverse dependency lookup
- `COMPARE_COURSES` - Multi-attribute comparison

**Search & Aggregation:**
- `SEARCH_COURSES`, `GET_FACULTY_BY_RESEARCH`
- `COUNT_ENTITIES`, `GET_COURSES_BY_LEVEL`

### 4.2 Reasoning Chain Implementation

Each query execution produces a `ReasoningResult` containing:
```python
@dataclass
class ReasoningResult:
    query_type: QueryType
    answer: Any
    success: bool
    reasoning_chain: list[ReasoningStep]  # Explainability!
    error_message: Optional[str]
```

Each step in the chain captures:
- **Rule name** (e.g., "RESOLVE_COURSE", "COMPUTE_TRANSITIVE_CLOSURE")
- **Description** of what the step does
- **Inputs and Outputs** for full transparency

### 4.3 Example Reasoning Trace

**Query:** "What are all prerequisites for CS401?"

```
Reasoning Trace:
  1. [RESOLVE_COURSE] Resolved course code CS401 to Machine Learning
  2. [QUERY_DIRECT_PREREQUISITES] Found 3 direct prerequisite(s): [CS301, MATH201, MATH401]
  3. [COMPUTE_TRANSITIVE_CLOSURE] Computed transitive closure: 7 total prerequisite(s)
```

---

## 5. LLM Integration

### 5.1 Multi-Provider Architecture

We implemented a pluggable provider system:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str: ...

class OpenAIProvider(BaseLLMProvider): ...
class GeminiProvider(BaseLLMProvider): ...
class MockLLMProvider(BaseLLMProvider): ...  # For testing
```

### 5.2 Query Parsing Strategy

**Prompt Engineering Approach:**
- Structured system prompt listing all query types
- Expected parameter formats with examples
- JSON output format specification

**Mock Provider Pattern Matching:**
For cost-free testing, we implemented regex-based pattern matching with:
- Course name → code mapping (e.g., "machine learning" → "CS401")
- Department name normalization (e.g., "computer science" → "CS")
- 30+ patterns covering most query formulations

### 5.3 Answer Generation

The LLM Interface generates human-readable answers by:
1. Checking the `ReasoningResult.query_type`
2. Applying type-specific formatting (tables, lists, markdown)
3. Including relevant context (credits, departments, etc.)

---

## 6. Test Results & Evaluation

### 6.1 Test Suite Design

**25 Questions across 5 categories:**

| Category | Questions | Focus |
|----------|-----------|-------|
| Simple | 5 | Direct lookups, basic info |
| Intermediate | 5 | Single-hop relationships |
| Complex | 5 | Multi-step reasoning, transitive |
| Tricky | 5 | Informal references, edge cases |
| Multi-step | 5 | Compound queries, aggregations |

### 6.2 Results with Mock LLM

| Category | Pass Rate | Notes |
|----------|-----------|-------|
| Simple | 4/5 (80%) | One "count" pattern missed |
| Intermediate | 5/5 (100%) | All relationship queries work |
| Complex | 4/5 (80%) | Transitive prereqs work well |
| Tricky | 3/5 (60%) | Informal references challenging |
| Multi-step | 1/5 (20%) | Requires real LLM reasoning |
| **Total** | **17/25 (68%)** | |

### 6.3 Analysis

**Strengths:**
- Excellent performance on structured queries
- Transitive prerequisite chains work perfectly
- Explanations are clear and detailed

**Limitations:**
- Mock LLM struggles with informal phrasing
- Multi-step queries (e.g., "courses taught by faculty in area X") need LLM composition
- Pattern matching is brittle for novel formulations

---

## 7. Limitations & Future Work

### 7.1 Current Limitations

1. **Static Knowledge Base** - No real-time updates
2. **Mock LLM Brittleness** - Pattern matching can miss edge cases
3. **No Learning** - System doesn't improve from user feedback
4. **Limited Multi-hop Reasoning** - Some compound queries unsupported

### 7.2 Future Enhancements

1. **Enhanced LLM Prompting** - Few-shot examples, chain-of-thought
2. **Query Decomposition** - Break complex queries into sub-queries
3. **Caching** - Store frequent query results
4. **Web Interface** - Beyond CLI for better UX
5. **Larger Knowledge Graph** - Real university data integration

---

## 8. Conclusion

This project successfully demonstrates a **neuro-symbolic approach** to question answering by:

1. Combining **LLM flexibility** (natural language understanding) with **symbolic precision** (rule-based reasoning)
2. Providing **full transparency** through reasoning chain explanations
3. Achieving **68% accuracy** on a diverse test suite with only pattern matching
4. Supporting **17 distinct query types** across the university domain

The architecture is modular and extensible, allowing easy integration of more sophisticated LLMs or larger knowledge bases in the future.

---

## Appendix A: Sample Queries and Responses

### Query 1: Simple Course Lookup
**Q:** "What is CS101?"
**A:** 
```
**CS101 - Introduction to Programming**
- Credits: 3
- Level: Undergraduate
- Description: Fundamentals of programming using Python
- Department: Computer Science
- Instructors: Dr. Alice Smith
- Prerequisites: None
```

### Query 2: Transitive Prerequisites
**Q:** "What are all the prerequisites for CS401?"
**A:**
```
All prerequisites (including transitive):
- MATH101: Calculus I
- CS101: Introduction to Programming
- CS201: Data Structures
- MATH201: Linear Algebra
- MATH301: Discrete Mathematics
- CS301: Algorithms
- MATH102: Calculus II
- MATH401: Probability and Statistics
```

### Query 3: Course Comparison
**Q:** "Compare CS301 and CS401"
**A:**
```
**Comparing CS301 and CS401:**

| Aspect | CS301 | CS401 |
|--------|-------|-------|
| Name | Algorithms | Machine Learning |
| Credits | 4 | 4 |
| Level | undergraduate | graduate |

- Same Department: Yes
- Same Level: No
- Common Prerequisites: 4
```

---

## Appendix B: Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.9+ |
| Graph Library | NetworkX | 3.0+ |
| LLM Client | OpenAI SDK | 1.0+ |
| LLM Client | Google GenAI | 0.3+ |
| Testing | pytest | 7.0+ |
| Environment | python-dotenv | 1.0+ |
