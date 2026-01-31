# 🎓 Neuro-Symbolic University QA Agent

> **A smart question-answering system that understands natural language and reasons like a human expert**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-96%25%20passing-green.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

---

## 📖 Table of Contents

1. [What is This Project?](#-what-is-this-project)
2. [Key Concepts Explained](#-key-concepts-explained)
3. [How It Works](#-how-it-works)
4. [Quick Start](#-quick-start)
5. [Project Structure](#-project-structure)
6. [Running Tests](#-running-tests)
7. [Supported Query Types](#-supported-query-types)
8. [For Developers](#-for-developers)
9. [Troubleshooting](#-troubleshooting)

---

## 🤔 What is This Project?

Imagine you could ask a computer questions like:

> *"What courses do I need to take before Machine Learning?"*
> 
> *"Who teaches CS401?"*
> 
> *"Can I take Algorithms if I've only completed CS101?"*

This project does exactly that! It's a **Question-Answering (QA) Agent** that:

1. **Understands** your question in plain English
2. **Reasons** through the university data to find the answer
3. **Explains** how it arrived at the answer (no black box!)

### Why is it called "Neuro-Symbolic"?

This system combines **two approaches to AI**:

| Approach | Strengths | How We Use It |
|----------|-----------|---------------|
| **Neural** (LLMs like ChatGPT) | Understands messy human language | Translates your question into a structured query |
| **Symbolic** (Rules & Logic) | Precise, explainable, 100% accurate | Executes the query and finds the exact answer |

**The best of both worlds**: Natural language understanding + Reliable logical reasoning!

---

## 📚 Key Concepts Explained

### 🧠 What is a Knowledge Graph?

Think of it as a **smart database** that stores information as a network of connections.

```
         ┌──────────┐
         │   CS     │ (Department)
         │Department│
         └────┬─────┘
              │ has faculty
              ▼
         ┌──────────┐          teaches        ┌──────────┐
         │Dr. Smith │─────────────────────────│  CS401   │
         │(Faculty) │                         │(Course)  │
         └──────────┘                         └────┬─────┘
                                                   │ requires
                                                   ▼
                                              ┌──────────┐
                                              │  CS301   │
                                              │(Course)  │
                                              └──────────┘
```

**Why is this useful?**
- We can "walk" through connections to answer complex questions
- "Dr. Smith teaches CS401, which requires CS301" - that's following the graph!

### 🔮 What is Symbolic Reasoning?

Symbolic reasoning means solving problems by applying **clearly defined rules and logical steps**, instead of learning from data.

**Example Rule**:  
*"If a customer is under 21 years old, their credit application must be rejected.  
If the customer is 21 or older and their credit score is above 700, the application can be approved."*

Using symbolic reasoning, the system simply checks these rules step-by-step to reach a decision.

```
Q: What are ALL prerequisites for CS401 (Machine Learning)?

Step 1: CS401 directly requires → [CS301, MATH201, MATH401]
Step 2: CS301 directly requires → [CS201, MATH301]
Step 3: CS201 directly requires → [CS101]
Step 4: MATH201 requires → [MATH101]
... and so on

Final Answer: [CS101, CS201, CS301, MATH101, MATH102, MATH201, MATH301, MATH401]
```

**Benefits**:
- ✅ **Explainable**: You can see exactly WHY an answer was given
- ✅ **Deterministic**: Same question = same answer, every time
- ✅ **Correct**: No "hallucinations" or made-up facts

### 🤖 What is an LLM (Large Language Model)?

An LLM is an AI trained on massive amounts of text that can:
- Understand natural language questions
- Generate human-like responses
- Handle typos, informal phrasing, and ambiguity

**In this project**, the LLM's job is simple: **translate your question into a structured query**.

```
User: "What do I need to take before ML?"

LLM translates to:
{
  "query_type": "GET_ALL_PREREQUISITES",
  "parameters": {"course_code": "CS401"}
}
```

The LLM **does NOT answer the question directly** - that's the symbolic reasoner's job!

---

## ⚙️ How It Works

Here's the complete flow from question to answer:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           YOUR QUESTION                                  │
│         "What are the prerequisites for Machine Learning?"               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 1: LLM INTERFACE                                                   │
│  ─────────────────────                                                   │
│  The LLM understands your question and converts it to a structured       │
│  query that the computer can process.                                    │
│                                                                          │
│  Input:  "What are the prerequisites for Machine Learning?"              │
│  Output: {query_type: GET_ALL_PREREQUISITES, course_code: CS401}        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 2: SYMBOLIC REASONER                                               │
│  ─────────────────────────                                               │
│  The reasoner follows logical rules to find the answer.                  │
│                                                                          │
│  Rule Applied: "Get all prerequisites (transitive)"                      │
│  Steps Taken:                                                            │
│    1. Find CS401 in the graph                                           │
│    2. Get direct prerequisites: [CS301, MATH201, MATH401]               │
│    3. Recursively get prerequisites of those courses                    │
│    4. Collect all unique courses                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 3: ANSWER GENERATION                                               │
│  ─────────────────────────                                               │
│  Raw data is formatted into a human-readable response.                   │
│                                                                          │
│  Output:                                                                 │
│    "All prerequisites (including transitive):                           │
│     - MATH101: Calculus I                                               │
│     - CS101: Introduction to Programming                                │
│     - CS201: Data Structures                                            │
│     - ..."                                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Benefits of This Architecture

| Benefit | Explanation |
|---------|-------------|
| **Accuracy** | The symbolic reasoner uses precise logic - no guessing! |
| **Transparency** | Every reasoning step is recorded and shown to the user |
| **Flexibility** | The LLM handles variations in how questions are asked |
| **Reliability** | The knowledge graph is the single source of truth |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# 1. Navigate to the project directory
cd mi-assignment

# 2. (Recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the Agent

```bash
# Run with the built-in mock LLM (no API key needed!)
python -m src.main
```

You'll see an interactive prompt:

```
╔══════════════════════════════════════════════════════════════════╗
║      Neuro-Symbolic University QA Agent                          ║
╚══════════════════════════════════════════════════════════════════╝

🎓 Your question: 
```

### Example Questions to Try

```
What is CS101?
Who teaches CS401?
What are the prerequisites for Algorithms?
List all CS courses
Can I take CS301 if I've completed CS101 and MATH101?
Compare CS301 and CS401
How many courses are there?
```

### Using a Real LLM (Optional)

If you want to use OpenAI or Google Gemini instead of the mock:

```bash
# 1. Copy the environment template
cp .env.example .env

# 2. Edit .env and add your API key
#    OPENAI_API_KEY=sk-xxxx
#    OR
#    GOOGLE_API_KEY=xxxx

# 3. Run with your chosen provider
LLM_PROVIDER=openai python -m src.main
# OR
LLM_PROVIDER=gemini python -m src.main
```

---

## 📁 Project Structure

```
mi-assignment/
│
├── src/                          # Source code
│   ├── __init__.py
│   ├── knowledge_graph.py        # 🗃️ Graph database operations
│   ├── reasoner.py               # 🧠 Symbolic reasoning engine
│   ├── llm_interface.py          # 🤖 LLM integration
│   └── main.py                   # 🎮 CLI and agent orchestration
│
├── data/
│   └── university_kg.json        # 📊 University data (4 depts, 18 courses)
│
├── tests/
│   ├── test_questions.py         # 🧪 50 QA test cases
│   └── test_knowledge_graph.py   # 🧪 Unit tests for graph
│
├── docs/
│   └── DESIGN_REPORT.md          # 📝 Technical design document
│
├── requirements.txt              # 📦 Python dependencies
├── .env.example                  # 🔑 API key template
└── README.md                     # 📖 You are here!
```

### File Descriptions

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `knowledge_graph.py` | Stores and queries university data | `KnowledgeGraph` class |
| `reasoner.py` | Executes queries using logical rules | `SymbolicReasoner`, `QueryType` |
| `llm_interface.py` | Translates natural language to queries | `LLMInterface`, `MockLLMProvider` |
| `main.py` | Ties everything together | `UniversityQAAgent`, CLI loop |

---

## 🧪 Running Tests

### Full Test Suite (50 Questions)

```bash
python tests/test_questions.py
```

**Sample Output:**
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

### Other Test Commands

```bash
# Run a specific test by ID
python tests/test_questions.py --test 11

# Quiet mode (summary only)
python tests/test_questions.py --quiet

# Unit tests for the knowledge graph
python -m pytest tests/test_knowledge_graph.py -v
```

### Test Categories Explained

| Category | Description | Example |
|----------|-------------|---------|
| **Simple** | Direct lookups | "What is CS101?" |
| **Intermediate** | Single-hop relationships | "Prerequisites for CS201?" |
| **Complex** | Multi-step reasoning | "ALL prerequisites for CS401?" |
| **Tricky** | Informal/ambiguous phrasing | "Dr. Smith's classes" |
| **Multi-step** | Compound queries | "Courses taught by head of CS" |

---

## 🔧 Supported Query Types

The system supports **17 different query types**:

### Entity Lookups
| Query Type | Example Question |
|------------|------------------|
| `GET_COURSE_INFO` | "What is CS101?" |
| `GET_FACULTY_INFO` | "Who is Dr. Smith?" |
| `GET_DEPARTMENT_INFO` | "Tell me about CS department" |

### Relationship Queries
| Query Type | Example Question |
|------------|------------------|
| `GET_PREREQUISITES` | "Prerequisites for CS201?" |
| `GET_ALL_PREREQUISITES` | "All requirements for CS401?" |
| `GET_COURSES_BY_DEPARTMENT` | "List CS courses" |
| `GET_FACULTY_BY_DEPARTMENT` | "Faculty in Math?" |
| `GET_COURSES_TAUGHT_BY` | "What does Dr. Smith teach?" |
| `GET_COURSE_INSTRUCTORS` | "Who teaches CS401?" |
| `GET_DEPARTMENT_HEAD` | "Head of CS department?" |
| `GET_COURSES_REQUIRING` | "Courses that need CS101?" |

### Advanced Queries
| Query Type | Example Question |
|------------|------------------|
| `CAN_TAKE_COURSE` | "Can I take CS301 with CS101 done?" |
| `GET_COURSES_BY_LEVEL` | "Graduate courses?" |
| `GET_FACULTY_BY_RESEARCH` | "Who researches ML?" |
| `SEARCH_COURSES` | "Courses about algorithms?" |
| `COUNT_ENTITIES` | "How many courses?" |
| `COMPARE_COURSES` | "Compare CS301 and CS401" |

---

## 👩‍💻 For Developers

### Extending the Knowledge Graph

To add new data, edit `data/university_kg.json`:

```json
{
  "courses": [
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
    {"course": "cs501", "requires": "cs401"}
  ]
}
```

### Adding New Query Types

1. Add the type to `QueryType` enum in `reasoner.py`
2. Implement the rule as `_rule_your_query_type()`
3. Register it in the `_rules` dictionary
4. Add patterns to `MockLLMProvider` in `llm_interface.py`

### Architecture Diagram

```
                    ┌─────────────────┐
                    │   User Input    │
                    └────────┬────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                    UniversityQAAgent                        │
│  ┌──────────────┐   ┌────────────────┐   ┌──────────────┐  │
│  │ LLMInterface │──▶│SymbolicReasoner│──▶│Answer Format │  │
│  │   (Parse)    │   │   (Execute)    │   │  (Generate)  │  │
│  └──────────────┘   └───────┬────────┘   └──────────────┘  │
└─────────────────────────────┼──────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ KnowledgeGraph  │
                    │   (NetworkX)    │
                    └─────────────────┘
```

---

## ❓ Troubleshooting

### Common Issues

**Q: I get "ModuleNotFoundError"**
```bash
# Make sure you're in the right directory and have installed deps
cd mi-assignment
pip install -r requirements.txt
```

**Q: The mock LLM doesn't understand my question**
- Try rephrasing with course codes (e.g., "CS401" instead of "machine learning")
- Check if your query type is supported (see table above)

**Q: I want to use a real LLM but have no API key**
- The mock LLM works without any API key!
- For real LLMs, get a key from [OpenAI](https://platform.openai.com/) or [Google AI Studio](https://aistudio.google.com/)

**Q: How do I see the reasoning steps?**
- The CLI always shows the reasoning trace
- Look for the "Explanation" section in the output

---

## 📊 Knowledge Graph Statistics

| Entity Type | Count | Examples |
|-------------|-------|----------|
| Departments | 4 | CS, MATH, PHYS, EE |
| Faculty | 7 | Dr. Smith, Dr. Johnson, ... |
| Courses | 18 | CS101, MATH201, PHYS301, ... |
| Prerequisites | 24 | CS401→CS301, CS301→CS201, ... |

---

## 🏆 Test Results

| Category | Pass Rate |
|----------|-----------|
| Simple | 100% (10/10) |
| Intermediate | 100% (10/10) |
| Complex | 100% (10/10) |
| Tricky | 80% (8/10) |
| Multi-step | 100% (10/10) |
| **Overall** | **96% (48/50)** |

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

This project was built as a demonstration of neuro-symbolic AI, combining:
- Large Language Models for natural language understanding
- Knowledge graphs for structured data representation
- Symbolic reasoning for explainable, accurate inference

---

<p align="center">
  <b>Questions? Issues? PRs welcome!</b>
</p>
