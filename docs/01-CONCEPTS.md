# 🧠 Core Concepts

> **Who is this for?** Everyone! No prior AI knowledge needed.

---

## What Problem Are We Solving?

You want to ask a computer:
> *"What courses do I need before I can take Machine Learning?"*

Sounds simple, but there are **two challenges**:

1. **The computer doesn't speak English** - It needs structured data
2. **The answer requires reasoning** - Not just looking up facts, but following chains of relationships

This project solves both using **Neuro-Symbolic AI**.

---

## 🤖 What is Neuro-Symbolic AI?

It's the combination of **two AI approaches**:

### Neural Networks (The "Neuro" Part)

Think of neural networks (like ChatGPT) as pattern recognition experts:
- They've read billions of sentences
- They understand language nuances, typos, and informal speech
- But they can make things up ("hallucinate")

### Symbolic AI (The "Symbolic" Part)

Think of symbolic AI as a calculator for logic:
- It follows precise rules
- It never makes things up
- But it can't understand "What do I need for ML?" (too informal)

### The Magic Combination ✨

```
┌─────────────────────────────────────────────────────────────┐
│  "What do I need for ML?"                                   │
└────────────────────────────────┬────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│  NEURAL (LLM)                                                │
│  "Ah, they mean: Get all prerequisites for CS401"           │
│  Output: {query: GET_ALL_PREREQUISITES, course: CS401}      │
└────────────────────────────────┬────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│  SYMBOLIC (Reasoner)                                         │
│  "CS401 needs CS301, MATH201, MATH401..."                   │
│  "CS301 needs CS201, MATH301..."                            │
│  *follows ALL chains precisely*                              │
│  Output: [CS101, CS201, CS301, MATH101, MATH102, ...]       │
└─────────────────────────────────────────────────────────────┘
```

**Result**: Flexible understanding + Guaranteed accuracy!

---

## 🗃️ What is a Knowledge Graph?

A **knowledge graph** is a way to store information as a network of connections.

### Traditional Database vs Knowledge Graph

**Traditional (Table-based):**
```
Courses Table:
| ID   | Name    | Prereq |
|------|---------|--------|
| CS301| Algorithms| CS201 |
```
*Problem*: What if a course has 3 prerequisites? Multiple prereqs for the prereqs?

**Knowledge Graph (Connection-based):**
```
    [CS101] ←─requires─ [CS201] ←─requires─ [CS301] ←─requires─ [CS401]
                           ↑                   ↑
                     [MATH301] ────────────────┘
```

*Advantage*: You can "walk" the connections to find ALL prerequisites!

### Our University Graph

```
ENTITIES (Nodes):
├── 4 Departments (CS, MATH, PHYS, EE)
├── 7 Faculty (Dr. Smith, Dr. Johnson, ...)
└── 18 Courses (CS101, MATH201, ...)

RELATIONSHIPS (Edges):
├── teaches: Faculty → Course
├── belongs_to: Course/Faculty → Department
├── prerequisite: Course → Course
└── heads: Faculty → Department
```

---

## 🔮 What is Symbolic Reasoning?

**Symbolic reasoning** means reaching conclusions by following explicit rules.

### Example: Transitive Prerequisites

**Rule**: *"To get ALL prerequisites, find direct prerequisites, then get THEIR prerequisites, and repeat until done."*

```python
# Pseudocode
def get_all_prerequisites(course):
    direct = get_direct_prerequisites(course)
    all_prereqs = set(direct)
    
    for prereq in direct:
        # RECURSION: get prerequisites of prerequisites
        all_prereqs.update(get_all_prerequisites(prereq))
    
    return all_prereqs
```

### Why This Matters

| Approach | "Prerequisites for CS401?" | Pros/Cons |
|----------|--------------------------|-----------|
| ChatGPT alone | "You need Algorithms and some math classes" | Vague, might be wrong |
| Our System | [CS101, CS201, CS301, MATH101, MATH102, MATH201, MATH301, MATH401] | Precise, complete, correct |

---

## 🔄 The Complete Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. USER                                                       │
│    "What courses does Dr. Smith teach?"                      │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. LLM INTERFACE                                              │
│    Understands natural language                               │
│    Converts to: {type: GET_COURSES_TAUGHT_BY, name: "Smith"} │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. SYMBOLIC REASONER                                          │
│    Rule: "Find faculty by name, then find courses they teach"│
│    Steps:                                                     │
│      1. Normalize "Smith" → "Alice Smith"                    │
│      2. Find faculty node in graph                           │
│      3. Follow "teaches" edges to course nodes               │
│    Result: [CS101, CS201, CS301, CS401]                      │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. ANSWER GENERATOR                                           │
│    Formats result for human reading                           │
│    "Dr. Smith teaches: CS101, CS201, CS301, CS401"           │
│    + Shows reasoning trace for transparency                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Takeaways

| Concept | One-Line Summary |
|---------|------------------|
| **Neuro-Symbolic AI** | LLMs for understanding + Rules for accuracy |
| **Knowledge Graph** | Data as a network of connected entities |
| **Symbolic Reasoning** | Following logical rules to reach conclusions |
| **Transparency** | Every answer includes HOW it was derived |

---

## Next Steps

- 🏗️ [Architecture](./02-ARCHITECTURE.md) - How the system is built
- 📊 [Knowledge Graph](./03-KNOWLEDGE-GRAPH.md) - Deep dive into the data
