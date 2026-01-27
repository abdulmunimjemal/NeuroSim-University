"""
Evaluation script for the Neuro-Symbolic University QA System.

This script runs a benchmark suite of natural language questions against the
agent to measure:
1. Parsing Accuracy: Did the LLM map the question to the correct QueryType?
2. Parameter Extraction: Did the LLM extract the correct entities (e.g., course codes)?
3. Execution Success: Did the symbolic reasoner execute without errors?
4. Latency: How long did processing take?
"""

import time
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.main import UniversityQAAgent
from src.reasoner import QueryType


@dataclass
class TestCase:
    question: str
    expected_type: QueryType
    expected_params: Dict[str, Any]
    description: str


class Evaluator:
    def __init__(self):
        print("Initializing Agent for Evaluation...")
        # We use 'mock' provider for consistent, deterministic evaluation
        # You can switch this to 'openai' or 'gemini' to evaluate real LLM performance
        self.agent = UniversityQAAgent(llm_provider="mock")

    def get_benchmark_suite(self) -> List[TestCase]:
        """Returns a list of ground-truth test cases."""
        return [
            # --- Type: GET_COURSE_INFO ---
            TestCase(
                question="What is CS101?",
                expected_type=QueryType.GET_COURSE_INFO,
                expected_params={"course_code": "CS101"},
                description="Basic course lookup"
            ),

            # --- Type: GET_ALL_PREREQUISITES ---
            TestCase(
                question="What are all the prerequisites for CS401?",
                expected_type=QueryType.GET_ALL_PREREQUISITES,
                expected_params={"course_code": "CS401"},
                description="Transitive prerequisites"
            ),
            TestCase(
                question="What do I need before taking MATH201?",
                expected_type=QueryType.GET_ALL_PREREQUISITES,
                # The mock LLM might extract MATH201.
                # Note: The mock parser pattern for this is: "what (do i need|are the requirements) (to take|for) (\w+)"
                # "What do I need before taking MATH201" might not match perfectly if the regex is strict
                # Let's align with a known working phrasing or one robust enough.
                # Looking at llm_interface.py patterns:
                # (r"(?:what\s+)?prerequisite[s]?\s+do\s+i\s+need\s+to\s+take", "GET_ALL_PREREQUISITES", ...)
                # (r"what\s+(?:do\s+i\s+need|are\s+the\s+requirements)\s+(?:to\s+take|for)", "GET_ALL_PREREQUISITES", ...)
                # Let's try to match the expected behavior.
                expected_params={"course_code": "MATH201"},
                description="Prerequisites phrasing variation"
            ),

            # --- Type: GET_COURSE_INSTRUCTORS ---
            TestCase(
                question="Who teaches CS101?",
                expected_type=QueryType.GET_COURSE_INSTRUCTORS,
                expected_params={"course_code": "CS101"},
                description="Instructor lookup"
            ),

            # --- Type: GET_FACULTY_INFO ---
            TestCase(
                question="Tell me about Dr. Smith",
                expected_type=QueryType.GET_FACULTY_INFO,
                # Normalized name often expected or extracted
                expected_params={"name": "Smith"},
                description="Faculty lookup"
            ),

            # --- Type: GET_COURSES_BY_DEPARTMENT ---
            TestCase(
                question="List all courses in Computer Science",
                expected_type=QueryType.GET_COURSES_BY_DEPARTMENT,
                expected_params={"code": "CS"},
                description="Department courses"
            ),

            # --- Type: CAN_TAKE_COURSE (Reasoning heavy) ---
            TestCase(
                question="Can I take CS401 if I have completed CS101?",
                expected_type=QueryType.CAN_TAKE_COURSE,
                # Pattern: (r"can\s+(?:i|a\s+student)\s+take\s+(\w+\d+)", ...)
                # Extract completed: (r"\b([A-Za-z]+\d+)\b") excluding target
                expected_params={"course_code": "CS401",
                                 "completed_courses": ["CS101"]},
                description="Enrollment eligibility logic"
            ),
        ]

    def run(self):
        suite = self.get_benchmark_suite()
        results = []
        latencies = []

        print(f"\n{'='*60}")
        print(f"STARTING EVALUATION: {len(suite)} Test Cases")
        print(f"{'='*60}\n")

        passed_parse = 0
        passed_exec = 0

        for i, case in enumerate(suite):
            print(f"Case {i+1}: {case.description}")
            print(f"  Q: {case.question}")

            start_time = time.perf_counter()

            # 1. Parsing Step
            try:
                # Accessing internal LLM interface for granular testing
                parsed = self.agent.llm.parse_question(case.question)

                # Check Type
                type_match = (parsed.query_type == case.expected_type)

                # Check Params (Subset match logic)
                params_match = True
                for k, v in case.expected_params.items():
                    if k not in parsed.parameters:
                        # Allow normalizing variations (e.g. name "Smith" vs "Dr. Smith")
                        # But for strict eval, let's log fail first
                        params_match = False
                        break

                    # Simple equality check; for lists, order might matter in real systems
                    if isinstance(v, list):
                        if sorted(parsed.parameters[k]) != sorted(v):
                            params_match = False
                    elif k == 'name':
                        # Loose check for name to handle normalization differences
                        if v not in parsed.parameters[k] and parsed.parameters[k] not in v:
                            params_match = False
                    elif parsed.parameters[k] != v:
                        params_match = False

                parse_success = type_match and params_match
                if parse_success:
                    passed_parse += 1
                else:
                    print(f"  [X] PARSE FAIL")
                    print(
                        f"      Expected: {case.expected_type} ({case.expected_params})")
                    print(
                        f"      Got:      {parsed.query_type} ({parsed.parameters})")

            except Exception as e:
                print(f"  [!] PARSE ERROR: {e}")
                parse_success = False

            # 2. Execution Step
            exec_success = False
            if parse_success:
                try:
                    # Execute reasoning (using execute_query as per reasoner.py)
                    result = self.agent.reasoner.execute_query(
                        parsed.query_type, parsed.parameters)
                    if result.success:
                        exec_success = True
                        passed_exec += 1
                        print("  [✓] Pass")
                    else:
                        print(
                            f"  [X] LOGIC FAIL: Reasoner returned failure: {result.error_message}")
                except Exception as e:
                    print(f"  [!] EXEC ERROR: {e}")

            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000  # ms
            latencies.append(latency)

            print("-" * 40)

        # --- Report ---
        avg_latency = statistics.mean(latencies) if latencies else 0

        print(f"\n{'='*60}")
        print("EVALUATION REPORT")
        print(f"{'='*60}")
        print(f"Total Cases:       {len(suite)}")
        print(
            f"Parsing Accuracy:  {passed_parse}/{len(suite)} ({passed_parse/len(suite)*100:.1f}%)")
        print(
            f"Logic Success:     {passed_exec}/{len(suite)} ({passed_exec/len(suite)*100:.1f}%)")
        print(f"Avg Latency:       {avg_latency:.2f} ms")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.run()
