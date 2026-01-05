# 🔮 Symbolic Reasoning

> **Who is this for?** Backend developers implementing or extending query logic.

---

## Overview

The Symbolic Reasoner executes structured queries using **explicit logical rules**.

**Key Principle**: Every answer is derived through traceable, deterministic steps.

---

## Query Types Taxonomy

### 17 Query Types Organized by Complexity

```
SIMPLE (Direct Lookups)
├── GET_COURSE_INFO
├── GET_FACULTY_INFO
└── GET_DEPARTMENT_INFO

RELATIONSHIPS (Single-Hop)
├── GET_PREREQUISITES
├── GET_COURSES_BY_DEPARTMENT
├── GET_FACULTY_BY_DEPARTMENT
├── GET_COURSES_TAUGHT_BY
├── GET_COURSE_INSTRUCTORS
├── GET_DEPARTMENT_HEAD
└── GET_COURSES_REQUIRING

COMPLEX (Multi-Step)
├── GET_ALL_PREREQUISITES (transitive closure)
├── CAN_TAKE_COURSE (eligibility check)
└── COMPARE_COURSES (multi-attribute)

SEARCH & AGGREGATION
├── SEARCH_COURSES
├── GET_FACULTY_BY_RESEARCH
├── GET_COURSES_BY_LEVEL
└── COUNT_ENTITIES
```

---

## Reasoning Chain

Every query execution produces a **ReasoningResult** with a trace:

```python
@dataclass
class ReasoningStep:
    rule_name: str       # e.g., "RESOLVE_COURSE"
    description: str     # Human-readable explanation
    inputs: dict         # What went into this step
    outputs: Any         # What came out

@dataclass
class ReasoningResult:
    query_type: QueryType
    answer: Any
    success: bool
    reasoning_chain: List[ReasoningStep]  # Full trace!
    error_message: Optional[str]
```

---

## Example: Transitive Prerequisites

**Query**: `GET_ALL_PREREQUISITES` for CS401

```
Step 1: [RESOLVE_COURSE]
  Input:  {course_code: "CS401"}
  Output: {id: "cs401", name: "Machine Learning", ...}
  
Step 2: [QUERY_DIRECT_PREREQUISITES]
  Input:  {course_id: "cs401"}
  Output: ["cs301", "math201", "math401"]
  
Step 3: [COMPUTE_TRANSITIVE_CLOSURE]
  Input:  {direct_prereqs: [...]}
  Process:
    - cs301 requires: [cs201, math301]
    - cs201 requires: [cs101]
    - math201 requires: [math101]
    - math401 requires: [math102, math201]
    - math301 requires: [math101]
    - math102 requires: [math101]
    - Collect all unique courses
  Output: [cs101, cs201, cs301, math101, math102, math201, math301, math401]
```

**Total: 8 prerequisites** (vs. 3 direct)

---

## Rule Implementation Pattern

Each query type has a corresponding rule method:

```python
class SymbolicReasoner:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        self._rules = {
            QueryType.GET_COURSE_INFO: self._rule_get_course_info,
            QueryType.GET_ALL_PREREQUISITES: self._rule_get_all_prerequisites,
            # ... all 17 types
        }
    
    def reason(self, query_type: QueryType, params: dict) -> ReasoningResult:
        rule_fn = self._rules.get(query_type)
        if not rule_fn:
            return ReasoningResult(success=False, error="Unknown query type")
        return rule_fn(params)
```

---

## Key Rule Implementations

### GET_ALL_PREREQUISITES (Transitive Closure)

```python
def _rule_get_all_prerequisites(self, params: dict) -> ReasoningResult:
    chain = []
    course = self.kg.get_course_by_code(params['course_code'])
    
    # Step 1: Resolve course
    chain.append(ReasoningStep(
        rule_name="RESOLVE_COURSE",
        description=f"Found course: {course['name']}",
        inputs=params,
        outputs=course
    ))
    
    # Step 2: Compute transitive closure (recursive)
    all_prereqs = set()
    visited = set()
    
    def collect_prereqs(course_id):
        if course_id in visited:
            return
        visited.add(course_id)
        direct = self.kg.get_prerequisites(course_id)
        for prereq in direct:
            all_prereqs.add(prereq['id'])
            collect_prereqs(prereq['id'])  # Recurse!
    
    collect_prereqs(course['id'])
    
    chain.append(ReasoningStep(
        rule_name="COMPUTE_TRANSITIVE_CLOSURE",
        description=f"Found {len(all_prereqs)} total prerequisites",
        inputs={'course_id': course['id']},
        outputs=list(all_prereqs)
    ))
    
    # Convert IDs to full course objects
    prereq_courses = [self.kg.get_course_by_id(pid) for pid in all_prereqs]
    
    return ReasoningResult(
        query_type=QueryType.GET_ALL_PREREQUISITES,
        answer=prereq_courses,
        success=True,
        reasoning_chain=chain
    )
```

### CAN_TAKE_COURSE (Eligibility Check)

```python
def _rule_can_take_course(self, params: dict) -> ReasoningResult:
    course_code = params['course_code']
    completed = set(params.get('completed_courses', []))
    
    # Get all prerequisites
    all_prereqs = self.kg.get_all_prerequisites(course_code)
    prereq_codes = {p['code'] for p in all_prereqs}
    
    # Check which are missing
    missing = prereq_codes - completed
    
    return ReasoningResult(
        answer={
            'can_take': len(missing) == 0,
            'missing_prerequisites': list(missing)
        },
        success=True,
        # ... reasoning chain
    )
```

---

## Name Resolution

The reasoner includes helper methods for fuzzy matching:

### Faculty Name Normalization
```python
def _normalize_faculty_name(self, name: str) -> str:
    """Strip titles like 'Dr.', 'Prof.' for matching."""
    return re.sub(r'^(dr\.?|prof(?:essor)?\.?)\s*', '', name, flags=re.I)

# "Dr. Smith" → "Smith"
# "Professor Johnson" → "Johnson"
```

### Course Name Resolution
```python
COURSE_NAME_MAP = {
    "machine learning": "CS401",
    "algorithms": "CS301",
    # ...
}

def _resolve_course_name(self, name: str) -> str:
    return self.COURSE_NAME_MAP.get(name.lower(), name)

# "Machine Learning" → "CS401"
```

### Department Head Resolution
```python
# "head of CS" → resolves to "Dr. Alice Smith"
if name.startswith('head of '):
    dept_code = name.replace('head of ', '')
    dept = self.kg.get_department_by_code(dept_code)
    head = self.kg.get_department_head(dept['id'])
    return head['name']
```

---

## Error Handling

```python
def _rule_get_course_info(self, params: dict) -> ReasoningResult:
    course = self.kg.get_course_by_code(params.get('course_code'))
    
    if not course:
        return ReasoningResult(
            query_type=QueryType.GET_COURSE_INFO,
            answer=None,
            success=False,
            error_message=f"Course not found: {params.get('course_code')}",
            reasoning_chain=[]
        )
    
    # ... success path
```

---

## Extending with New Rules

1. Add to `QueryType` enum:
```python
class QueryType(Enum):
    # ... existing types
    GET_COURSE_SCHEDULE = "get_course_schedule"
```

2. Implement rule method:
```python
def _rule_get_course_schedule(self, params: dict) -> ReasoningResult:
    # Your logic here
    pass
```

3. Register in `_rules`:
```python
self._rules[QueryType.GET_COURSE_SCHEDULE] = self._rule_get_course_schedule
```

4. Add pattern in `llm_interface.py`:
```python
(r"schedule\s+for\s+(\w+\d+)", "GET_COURSE_SCHEDULE", 
 lambda m: {"course_code": m.group(1).upper()})
```

---

## Next Steps

- 📋 [API Reference](./06-API-REFERENCE.md) - Complete class documentation
- 🧪 [Testing Guide](./07-TESTING.md) - How to test your changes
