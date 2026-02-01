# Evaluation Report — Neuro-Symbolic University QA Agent

Evaluation summary, test results, and limitations. Last updated from test run and project docs.

---

## 1. Executive Summary

| Metric | Value |
|--------|--------|
| **Unit tests (Knowledge Graph)** | 20 / 20 passed (100%) |
| **QA integration tests** | 50 questions; expected ~96% pass rate (requires `OPENAI_API_KEY`) |
| **Test framework** | pytest (unit), custom runner (QA) |

The symbolic layer (knowledge graph and reasoner) is fully covered by unit tests. End-to-end QA tests depend on the LLM provider (OpenAI or Gemini) and require an API key; pass rates can vary with model and prompt changes.

---

## 2. Test Execution Summary

### 2.1 Unit Tests — Knowledge Graph

**Command:** `python -m pytest tests/test_knowledge_graph.py -v`

**Result:** All 20 tests passed.

| Test class | Tests | Status |
|------------|-------|--------|
| TestKnowledgeGraphBasics | 4 | Passed |
| TestCourseQueries | 6 | Passed |
| TestFacultyQueries | 3 | Passed |
| TestRelationships | 5 | Passed |
| TestSearch | 2 | Passed |

**Coverage:** Load data, departments/courses/faculty lookups, prerequisites (direct and transitive), courses by department/level, faculty by name/department/research, department head, course instructors, courses requiring a course, eligibility (`can_take_course`), search.

### 2.2 QA Integration Tests — Question Answering

**Command:** `python tests/test_questions.py` (verbose) or `python tests/test_questions.py --quiet` (summary only)

**Prerequisites:**

- Dependencies installed: `pip install -r requirements.txt`
- **QA tests require an LLM API:** set `OPENAI_API_KEY` in `.env` (or use `LLM_PROVIDER=gemini` and `GOOGLE_API_KEY`). Without a valid key, parsing will fail or hang on API errors.
- No mock LLM is shipped; the suite uses the configured provider (OpenAI by default).

**Expected results (from project README / 07-TESTING):**

| Category | Tests | Expected pass rate | Notes |
|----------|-------|--------------------|--------|
| Simple | 10 | 100% | Direct lookups (course, faculty, department, count) |
| Intermediate | 10 | 100% | Single-hop (prerequisites, courses by dept, instructors, etc.) |
| Complex | 10 | 100% | Multi-step (transitive prerequisites, compare, level, research) |
| Tricky | 10 | ~80% | Informal phrasing, “ML”, “Dr. Smith’s classes”, edge cases |
| Multi-step | 10 | 100% | Compound (head of dept → courses, eligibility) |
| **Total** | **50** | **~96%** | Failures typically in Tricky category |

**Pass criteria per question:**

1. Parsed `query_type` matches `expected_type` (or is in `alternative_types`).
2. `reasoning_result.success` is `True`.

---

## 3. Evaluation by Component

| Component | Tested by | Result |
|-----------|-----------|--------|
| **KnowledgeGraph** | `test_knowledge_graph.py` | 20/20 passed |
| **SymbolicReasoner** | Indirectly via KG + QA tests | All supported query types exercised by QA suite |
| **LLMInterface** | QA tests only | Depends on API; parsing and answer formatting validated end-to-end |
| **UniversityQAAgent** | QA tests only | Full pipeline (parse → reason → answer) |

---

## 4. Limitations

### 4.1 Testing and Environment

- **QA tests require API key:** No in-repo mock LLM; `test_questions.py` calls the live provider (OpenAI or Gemini). Running the full QA suite incurs API cost and requires network.
- **Non-determinism:** LLM parsing can vary by model version and prompt. QA results are not fully reproducible across runs or environments.
- **No gold answer check:** QA tests assert query type and reasoning success, not the exact text or exact set of entities in the answer. Semantic correctness of answers is not automatically validated.
- **Single data set:** All tests use `data/university_kg.json`. Coverage is for one schema and one graph size; different or larger graphs are untested.

### 4.2 System and Design

- **Single query per turn:** Only one query type is executed per user question. Multi-intent questions (“Who teaches ML and what are its prerequisites?”) are not split or fully answered.
- **Fixed query types:** Support is limited to the defined `QueryType` set. New question types require code changes (enum, rule, parsing, formatting).
- **Name resolution:** Course/faculty/department name → ID logic is duplicated (LLM post-processing and reasoner). Incomplete or inconsistent mappings can cause wrong or “not found” results.
- **Explanation is trace-only:** The system explains “what was done” (reasoning steps), not “why this query type or these parameters were chosen.” Users cannot see the rationale for the LLM’s parsing.
- **Error messages:** Reasoner errors (e.g. “Course not found: XYZ”) are technical. No built-in natural-language suggestions or “Did you mean …?” from the KG.
- **Scale:** In-memory NetworkX graph and single JSON file are suitable for small/medium data only. No benchmarking for large graphs or concurrent load.

### 4.3 Operational

- **Cost and latency:** Every question triggers at least one LLM call (parsing); answer generation may add more. Cost and response time grow with usage.
- **No caching:** Identical or near-identical questions are not cached; each run calls the LLM and reasoner again.
- **No monitoring:** No built-in metrics or logging of query types, confidence, failures, or latency for production use.

---

## 5. How to Reproduce

### Unit tests (no API key)

```bash
cd mi-assignment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests/test_knowledge_graph.py -v
```

### QA tests (requires API key)

```bash
# Ensure .env has OPENAI_API_KEY (or use Gemini and GOOGLE_API_KEY)
python tests/test_questions.py
# Summary only:
python tests/test_questions.py --quiet
# Single test (e.g. ID 11):
python tests/test_questions.py --test 11
```

### Expected output (unit)

```
============================== 20 passed in <1s ==============================
```

### Expected output (QA, typical)

```
Total: 50 | Passed: 48 | Failed: 2
Success Rate: 96.0%

By Category:
  SIMPLE         : 10/10 (100%)
  INTERMEDIATE   : 10/10 (100%)
  COMPLEX        : 10/10 (100%)
  TRICKY         : 8/10 (80%)
  MULTI-STEP     : 10/10 (100%)
```

---

## 6. References

- [Testing Guide](./07-TESTING.md) — Test categories, structure, and adding tests
- [Main README](../README.md) — Quick start and run instructions
