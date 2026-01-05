# 🏗️ System Architecture

> **Who is this for?** Developers who want to understand how the system is built.

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface (CLI)                         │
│                         src/main.py                                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      UniversityQAAgent                               │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────┐   │
│  │  LLMInterface   │─▶│ SymbolicReasoner │─▶│ Answer Generator  │   │
│  │  (Parse Query)  │  │ (Execute Query)  │  │ (Format Result)   │   │
│  └─────────────────┘  └────────┬─────────┘  └───────────────────┘   │
│       src/llm_interface.py     │              src/llm_interface.py   │
│                                │                                     │
│                       src/reasoner.py                                │
└────────────────────────────────┼────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       KnowledgeGraph                                 │
│                       src/knowledge_graph.py                         │
│                                                                      │
│                   ┌──────────────────────┐                           │
│                   │   NetworkX Graph     │                           │
│                   │   + university_kg.json│                          │
│                   └──────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

### 1. `UniversityQAAgent` (Orchestrator)

**Location**: `src/main.py`

**Purpose**: Coordinates the entire question-answering pipeline.

```python
class UniversityQAAgent:
    def process_query(self, question: str) -> AgentResponse:
        # Step 1: Parse natural language to structured query
        parsed = self.llm.parse_question(question)
        
        # Step 2: Execute query using symbolic reasoning
        result = self.reasoner.reason(parsed.query_type, parsed.parameters)
        
        # Step 3: Generate human-readable answer
        answer = self.llm.generate_answer(question, result)
        
        return AgentResponse(parsed, result, answer, explanation)
```

### 2. `LLMInterface` (Language Understanding)

**Location**: `src/llm_interface.py`

**Purpose**: Translates natural language ↔ structured data.

**Two Key Methods**:
```python
# Question → Structured Query
def parse_question(question: str) -> ParsedQuery:
    # Uses LLM (or pattern matching) to understand intent
    # Returns: {query_type: "GET_PREREQUISITES", params: {course: "CS401"}}

# Reasoning Result → Natural Language
def generate_answer(question: str, result: ReasoningResult) -> str:
    # Formats the raw result into readable text
    # Returns: "CS401 requires: CS301, MATH201, MATH401"
```

### 3. `SymbolicReasoner` (Logic Engine)

**Location**: `src/reasoner.py`

**Purpose**: Executes structured queries using logical rules.

```python
class SymbolicReasoner:
    def reason(self, query_type: QueryType, params: dict) -> ReasoningResult:
        # Dispatch to appropriate rule
        rule_fn = self._rules[query_type]
        return rule_fn(params)
    
    def _rule_get_all_prerequisites(self, params) -> ReasoningResult:
        # Implements transitive prerequisite logic
        # Records each step in reasoning_chain for transparency
```

### 4. `KnowledgeGraph` (Data Layer)

**Location**: `src/knowledge_graph.py`

**Purpose**: Stores and queries university data.

```python
class KnowledgeGraph:
    def __init__(self, data_path: str):
        self.graph = nx.DiGraph()  # NetworkX directed graph
        self._load_data(data_path)
    
    def get_course_by_code(self, code: str) -> dict
    def get_prerequisites(self, course_id: str) -> list
    def get_faculty_by_name(self, name: str) -> dict
    # ... more query methods
```

---

## Data Flow Example

**Question**: *"What are all prerequisites for Machine Learning?"*

```
┌─ Step 1: Parse Question ─────────────────────────────────────────────┐
│                                                                       │
│  Input:  "What are all prerequisites for Machine Learning?"          │
│                                                                       │
│  LLMInterface.parse_question():                                       │
│    1. Recognizes "all prerequisites" → GET_ALL_PREREQUISITES         │
│    2. Maps "Machine Learning" → CS401                                │
│                                                                       │
│  Output: ParsedQuery(                                                 │
│            query_type=GET_ALL_PREREQUISITES,                         │
│            parameters={course_code: "CS401"},                        │
│            confidence=0.85                                           │
│          )                                                            │
└───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ Step 2: Execute Query ──────────────────────────────────────────────┐
│                                                                       │
│  SymbolicReasoner.reason(GET_ALL_PREREQUISITES, {course: CS401}):    │
│                                                                       │
│    1. [RESOLVE_COURSE] Find CS401 in graph                           │
│    2. [GET_DIRECT_PREREQS] CS401 → [CS301, MATH201, MATH401]        │
│    3. [RECURSIVE_LOOKUP] CS301 → [CS201, MATH301]                   │
│    4. [RECURSIVE_LOOKUP] CS201 → [CS101]                            │
│    5. [RECURSIVE_LOOKUP] MATH201 → [MATH101]                        │
│    6. [RECURSIVE_LOOKUP] MATH401 → [MATH102, MATH201]               │
│    7. [COLLECT_UNIQUE] Deduplicate all prerequisites                 │
│                                                                       │
│  Output: ReasoningResult(                                             │
│            answer=[CS101, CS201, CS301, MATH101, MATH102, ...],      │
│            reasoning_chain=[...7 steps above...],                    │
│            success=True                                              │
│          )                                                            │
└───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ Step 3: Generate Answer ────────────────────────────────────────────┐
│                                                                       │
│  LLMInterface.generate_answer():                                      │
│                                                                       │
│  Output:                                                              │
│    "All prerequisites (including transitive):                        │
│     - CS101: Introduction to Programming                             │
│     - CS201: Data Structures                                         │
│     - CS301: Algorithms                                              │
│     - MATH101: Calculus I                                            │
│     - MATH102: Calculus II                                           │
│     - MATH201: Linear Algebra                                        │
│     - MATH301: Discrete Mathematics                                  │
│     - MATH401: Probability and Statistics"                           │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Design Decisions

### Why NetworkX for the Graph?

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| NetworkX | Simple, Python-native, in-memory fast | Not for huge graphs | ✅ Chosen |
| Neo4j | Scalable, query language | External dependency | Not needed for demo |
| RDF/OWL | Semantic web standards | Complex, overkill | Not needed |

### Why Mock LLM for Testing?

```python
class MockLLMProvider:
    # Regex patterns to simulate LLM parsing
    patterns = [
        (r"prerequisites for (\w+)", "GET_PREREQUISITES"),
        (r"who teaches (\w+)", "GET_COURSE_INSTRUCTORS"),
        ...
    ]
```

**Benefits**:
- ✅ No API costs during development
- ✅ Deterministic tests
- ✅ Works offline
- ✅ Fast execution

---

## File Dependencies

```
main.py
├── imports: LLMInterface, SymbolicReasoner, KnowledgeGraph
├── uses: university_kg.json
│
llm_interface.py
├── imports: QueryType, ReasoningResult (from reasoner.py)
├── uses: OpenAI SDK, Google GenAI SDK (optional)
│
reasoner.py
├── imports: KnowledgeGraph
├── defines: QueryType (Enum), ReasoningStep, ReasoningResult
│
knowledge_graph.py
├── imports: networkx
├── uses: university_kg.json
```

---

## Next Steps

- 📊 [Knowledge Graph](./03-KNOWLEDGE-GRAPH.md) - Data schema details
- 🤖 [LLM Integration](./04-LLM-INTEGRATION.md) - How queries are parsed
