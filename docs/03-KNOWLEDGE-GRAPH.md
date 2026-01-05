# 📊 Knowledge Graph

> **Who is this for?** Data engineers and developers working with the data layer.

---

## Overview

The knowledge graph stores university data as a **network of connected entities**.

**Technology**: NetworkX (Python graph library) + JSON data file

**Location**: 
- Schema: `src/knowledge_graph.py`
- Data: `data/university_kg.json`

---

## Entity Types (Nodes)

### Department
```json
{
    "id": "dept_cs",
    "name": "Computer Science",
    "code": "CS",
    "faculty_head": "prof_smith"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Full department name |
| `code` | string | Short code (CS, MATH, etc.) |
| `faculty_head` | string | ID of department head |

### Faculty
```json
{
    "id": "prof_smith",
    "name": "Dr. Alice Smith",
    "title": "Professor",
    "department": "dept_cs",
    "email": "alice.smith@university.edu",
    "research_areas": ["Machine Learning", "AI", "Data Mining"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Full name with title |
| `title` | string | Academic title |
| `department` | string | Department ID |
| `email` | string | Contact email |
| `research_areas` | array | Research specializations |

### Course
```json
{
    "id": "cs401",
    "code": "CS401",
    "name": "Machine Learning",
    "department": "dept_cs",
    "credits": 4,
    "level": "graduate",
    "description": "Introduction to machine learning techniques",
    "taught_by": ["prof_smith", "prof_garcia"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `code` | string | Course code (CS401) |
| `name` | string | Course title |
| `department` | string | Department ID |
| `credits` | integer | Credit hours |
| `level` | string | "undergraduate" or "graduate" |
| `description` | string | Course description |
| `taught_by` | array | Faculty IDs |

---

## Relationship Types (Edges)

```
┌──────────────┐    belongs_to    ┌────────────────┐
│   Faculty    │─────────────────▶│   Department   │
└──────────────┘                  └────────────────┘
       │                                 ▲
       │ teaches                         │ belongs_to
       ▼                                 │
┌──────────────┐                  ┌──────┴─────────┐
│   Course     │──────────────────│   Course       │
└──────────────┘   prerequisite   └────────────────┘
```

| Relationship | From | To | Meaning |
|--------------|------|----|---------||`belongs_to` | Faculty | Department | Employment |
| `belongs_to` | Course | Department | Course offering |
| `teaches` | Faculty | Course | Instruction assignment |
| `prerequisite` | Course | Course | Dependency (A→B means B requires A) |
| `heads` | Faculty | Department | Leadership role |

---

## Data Statistics

| Entity | Count |
|--------|-------|
| Departments | 4 |
| Faculty | 7 |
| Courses | 18 |
| Prerequisites | 24 |
| **Total Edges** | ~70 |

---

## Prerequisite Chains

```
Level 100 (No prereqs):
  CS101, MATH101

Level 200:
  CS201 ← CS101
  MATH201 ← MATH101
  MATH102 ← MATH101

Level 300:
  CS301 ← [CS201, MATH301]
  CS350 ← CS201
  MATH301 ← MATH101

Level 400 (Most prereqs):
  CS401 ← [CS301, MATH201, MATH401]  (8 transitive prereqs!)
  CS402 ← CS401                       (9 transitive prereqs!)
```

---

## KnowledgeGraph Class API

```python
class KnowledgeGraph:
    def __init__(self, data_path: str)
    
    # Entity Lookups
    def get_course_by_code(self, code: str) -> Optional[dict]
    def get_faculty_by_name(self, name: str) -> Optional[dict]
    def get_department_by_code(self, code: str) -> Optional[dict]
    
    # Relationship Queries
    def get_prerequisites(self, course_id: str) -> List[dict]
    def get_all_prerequisites(self, course_id: str) -> List[dict]
    def get_courses_taught_by(self, faculty_id: str) -> List[dict]
    def get_courses_by_department(self, dept_id: str) -> List[dict]
    def get_faculty_by_department(self, dept_id: str) -> List[dict]
    
    # Search & Filter
    def search_courses(self, query: str) -> List[dict]
    def get_courses_by_level(self, level: str) -> List[dict]
    def get_faculty_by_research_area(self, area: str) -> List[dict]
```

---

## Adding New Data

Edit `data/university_kg.json`:

```json
{
    "courses": [
        // Add new course
        {
            "id": "cs501",
            "code": "CS501", 
            "name": "Deep Learning",
            "department": "dept_cs",
            "credits": 4,
            "level": "graduate",
            "taught_by": ["prof_smith"]
        }
    ],
    "prerequisites": [
        // Add prerequisite relationship
        {"course": "cs501", "requires": "cs401"}
    ]
}
```

---

## Next Steps

- 🤖 [LLM Integration](./04-LLM-INTEGRATION.md) - Query parsing
- 🔮 [Symbolic Reasoning](./05-SYMBOLIC-REASONING.md) - Query execution
