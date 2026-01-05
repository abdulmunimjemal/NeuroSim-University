# Neuro-Symbolic University QA Agent

A question-answering agent that combines Large Language Models (LLMs) with symbolic reasoning for university-related queries.

## 🎯 Overview

This project implements a **neuro-symbolic AI system** that:
1. Uses an **LLM** to understand natural language questions
2. Translates questions into **structured symbolic queries**
3. Executes queries using **rule-based reasoning** over a knowledge graph
4. Provides **transparent explanations** of the reasoning process

## 📁 Project Structure

```
mi-assignment/
├── src/
│   ├── __init__.py
│   ├── knowledge_graph.py    # NetworkX-based knowledge graph
│   ├── reasoner.py           # Symbolic reasoning engine
│   ├── llm_interface.py      # LLM integration (OpenAI/Gemini/Mock)
│   └── main.py               # Main agent and CLI
├── data/
│   └── university_kg.json    # University knowledge graph data
├── tests/
│   ├── __init__.py
│   ├── test_knowledge_graph.py  # Unit tests for KG
│   └── test_questions.py        # 25 test questions
├── docs/
│   └── DESIGN_REPORT.md      # Detailed design documentation
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to the project directory
cd mi-assignment

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional - for real LLM)
cp .env.example .env
# Edit .env with your API keys
```

### Running the CLI

```bash
# Run with mock LLM (no API key needed)
python -m src.main

# Run with OpenAI
LLM_PROVIDER=openai python -m src.main

# Run with Gemini
LLM_PROVIDER=gemini python -m src.main
```

### Example Session

```
╔══════════════════════════════════════════════════════════════════╗
║      Neuro-Symbolic University QA Agent                          ║
╚══════════════════════════════════════════════════════════════════╝

🎓 Your question: What are the prerequisites for CS401?

============================================================
Question: What are the prerequisites for CS401?
============================================================

Direct prerequisites:
- CS301: Algorithms
- MATH201: Linear Algebra
- MATH401: Probability and Statistics

────────────────────────────────────────────────────────────
Explanation:
Query Understanding:
  - Interpreted as: get_prerequisites
  - Parameters: {'course_code': 'CS401'}
  - Confidence: 85%

Reasoning Trace:
  1. [RESOLVE_COURSE] Resolved course code CS401 to Machine Learning
  2. [QUERY_PREREQUISITES] Found 3 direct prerequisite(s)
============================================================
```

## 📊 Knowledge Graph

The knowledge graph contains:
- **4 Departments**: CS, MATH, PHYS, EE
- **7 Faculty Members** with research areas
- **18 Courses** across all levels
- **24 Prerequisite Relationships**

### Schema

```
Nodes:
- Department: id, name, code
- Faculty: id, name, title, email, research_areas
- Course: id, code, name, credits, level, description

Edges:
- belongs_to: Faculty/Course → Department
- teaches: Faculty → Course
- prerequisite: Course → Course
- heads: Faculty → Department
```

## 🧪 Running Tests

```bash
# Run the 25-question test suite
python tests/test_questions.py

# Run with quiet mode (summary only)
python tests/test_questions.py --quiet

# Run a specific test
python tests/test_questions.py --test 11

# Run unit tests
python -m pytest tests/test_knowledge_graph.py -v
```

### Test Results (Mock LLM)

| Category      | Pass Rate |
|---------------|-----------|
| Simple        | 100%      |
| Intermediate  | 100%      |
| Complex       | 100%      |
| Tricky        | 80%       |
| Multi-step    | 100%      |
| **Overall**   | **96%**   |

*Note: Using a real LLM (OpenAI/Gemini) can achieve even higher accuracy.*

## 🔧 Query Types Supported

| Query Type | Description | Example |
|------------|-------------|---------|
| `GET_COURSE_INFO` | Course details | "What is CS101?" |
| `GET_FACULTY_INFO` | Faculty details | "Who is Dr. Smith?" |
| `GET_DEPARTMENT_INFO` | Department overview | "Tell me about CS department" |
| `GET_PREREQUISITES` | Direct prereqs | "Prerequisites for CS201?" |
| `GET_ALL_PREREQUISITES` | Transitive prereqs | "All prereqs for CS401?" |
| `GET_COURSES_BY_DEPARTMENT` | Dept courses | "List CS courses" |
| `GET_FACULTY_BY_DEPARTMENT` | Dept faculty | "Faculty in Math?" |
| `GET_COURSES_TAUGHT_BY` | Faculty's courses | "What does Dr. Smith teach?" |
| `GET_COURSE_INSTRUCTORS` | Course teachers | "Who teaches CS401?" |
| `GET_DEPARTMENT_HEAD` | Dept head | "Head of CS department?" |
| `CAN_TAKE_COURSE` | Eligibility check | "Can I take CS301?" |
| `GET_COURSES_REQUIRING` | Reverse prereqs | "Courses requiring CS101?" |
| `GET_COURSES_BY_LEVEL` | Filter by level | "Graduate courses?" |
| `GET_FACULTY_BY_RESEARCH` | By research area | "Who researches ML?" |
| `SEARCH_COURSES` | Keyword search | "Courses about algorithms?" |
| `COUNT_ENTITIES` | Count items | "How many courses?" |
| `COMPARE_COURSES` | Compare two | "Compare CS301 and CS401" |

## 📝 License

MIT License - see LICENSE file for details.
