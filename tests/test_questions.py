"""
Test suite for the Neuro-Symbolic University QA Agent.

This module contains 20+ test questions covering simple, intermediate,
and complex multi-step queries to validate the agent's capabilities.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import UniversityQAAgent


# Test questions organized by complexity
TEST_QUESTIONS = [
    # ========== Simple Queries (Direct lookups) ==========
    {
        "id": 1,
        "question": "What is CS101?",
        "category": "simple",
        "expected_type": "GET_COURSE_INFO",
        "description": "Basic course lookup"
    },
    {
        "id": 2,
        "question": "Who is Dr. Smith?",
        "category": "simple",
        "expected_type": "GET_FACULTY_INFO",
        "description": "Faculty lookup by name"
    },
    {
        "id": 3,
        "question": "Tell me about the Computer Science department",
        "category": "simple",
        "expected_type": "GET_DEPARTMENT_INFO",
        "description": "Department information"
    },
    {
        "id": 4,
        "question": "Who teaches CS401?",
        "category": "simple",
        "expected_type": "GET_COURSE_INSTRUCTORS",
        "description": "Find course instructors"
    },
    {
        "id": 5,
        "question": "How many courses are there?",
        "category": "simple",
        "expected_type": "COUNT_ENTITIES",
        "description": "Count entities"
    },
    
    # ========== Intermediate Queries (Single-hop relationships) ==========
    {
        "id": 6,
        "question": "What are the prerequisites for CS201?",
        "category": "intermediate",
        "expected_type": "GET_PREREQUISITES",
        "description": "Direct prerequisites"
    },
    {
        "id": 7,
        "question": "What courses does Dr. Garcia teach?",
        "category": "intermediate",
        "expected_type": "GET_COURSES_TAUGHT_BY",
        "description": "Courses by instructor"
    },
    {
        "id": 8,
        "question": "List all CS courses",
        "category": "intermediate",
        "expected_type": "GET_COURSES_BY_DEPARTMENT",
        "description": "Courses by department"
    },
    {
        "id": 9,
        "question": "Who is the head of the Mathematics department?",
        "category": "intermediate",
        "expected_type": "GET_DEPARTMENT_HEAD",
        "description": "Department head lookup"
    },
    {
        "id": 10,
        "question": "What courses require CS101?",
        "category": "intermediate",
        "expected_type": "GET_COURSES_REQUIRING",
        "description": "Reverse prerequisite lookup"
    },
    
    # ========== Complex Queries (Multi-step reasoning) ==========
    {
        "id": 11,
        "question": "What are ALL the prerequisites for CS401 including transitive ones?",
        "category": "complex",
        "expected_type": "GET_ALL_PREREQUISITES",
        "description": "Transitive prerequisite chain"
    },
    {
        "id": 12,
        "question": "List all graduate courses",
        "category": "complex",
        "expected_type": "GET_COURSES_BY_LEVEL",
        "description": "Filter by course level"
    },
    {
        "id": 13,
        "question": "Who does research in Machine Learning?",
        "category": "complex",
        "expected_type": "GET_FACULTY_BY_RESEARCH",
        "description": "Faculty by research area"
    },
    {
        "id": 14,
        "question": "Compare CS301 and CS401",
        "category": "complex",
        "expected_type": "COMPARE_COURSES",
        "description": "Course comparison"
    },
    {
        "id": 15,
        "question": "Find courses about algorithms",
        "category": "complex",
        "expected_type": "SEARCH_COURSES",
        "description": "Semantic search"
    },
    
    # ========== Tricky Queries (Edge cases, ambiguity) ==========
    {
        "id": 16,
        "question": "What prerequisites do I need to take Machine Learning?",
        "category": "tricky",
        "expected_type": "GET_ALL_PREREQUISITES",
        "alternative_types": ["GET_PREREQUISITES"],  # Both provide useful answers
        "description": "Informal course reference"
    },
    {
        "id": 17,
        "question": "Professor Lee's courses",
        "category": "tricky",
        "expected_type": "GET_COURSES_TAUGHT_BY",
        "description": "Incomplete question"
    },
    {
        "id": 18,
        "question": "EE department faculty",
        "category": "tricky",
        "expected_type": "GET_FACULTY_BY_DEPARTMENT",
        "description": "Abbreviated query"
    },
    {
        "id": 19,
        "question": "What's the prerequisite chain for NLP?",
        "category": "tricky",
        "expected_type": "GET_ALL_PREREQUISITES",
        "description": "Course by topic name"
    },
    {
        "id": 20,
        "question": "Which courses have no prerequisites?",
        "category": "tricky",
        "expected_type": "SEARCH_COURSES",
        "alternative_types": ["GET_COURSES_BY_LEVEL"],  # Level filtering also valid approach
        "description": "Negative condition query"
    },
    
    # ========== Multi-step Reasoning Queries ==========
    {
        "id": 21,
        "question": "How many prerequisites does Quantum Mechanics have?",
        "category": "multi-step",
        "expected_type": "GET_ALL_PREREQUISITES",
        "alternative_types": ["GET_PREREQUISITES"],  # Count of direct prereqs is also valid
        "description": "Count after lookup"
    },
    {
        "id": 22,
        "question": "Can I take CS401 if I've only completed CS101 and MATH101?",
        "category": "multi-step",
        "expected_type": "CAN_TAKE_COURSE",
        "description": "Eligibility check with given history"
    },
    {
        "id": 23,
        "question": "Who teaches courses in the Physics department?",
        "category": "multi-step",
        "expected_type": "GET_FACULTY_BY_DEPARTMENT",
        "description": "Faculty through department"
    },
    {
        "id": 24,
        "question": "What courses are taught by faculty researching AI?",
        "category": "multi-step",
        "expected_type": "GET_FACULTY_BY_RESEARCH",
        "description": "Courses through research area"
    },
    {
        "id": 25,
        "question": "Are there any courses about cybersecurity?",
        "category": "multi-step",
        "expected_type": "SEARCH_COURSES",
        "description": "Existence check"
    },
    
    # ========== NEW TESTS (Expanded Coverage) ==========
    
    # New Simple Queries
    {
        "id": 26,
        "question": "What is MATH101?",
        "category": "simple",
        "expected_type": "GET_COURSE_INFO",
        "description": "Course lookup - Mathematics"
    },
    {
        "id": 27,
        "question": "Who is Prof. Taylor?",
        "category": "simple",
        "expected_type": "GET_FACULTY_INFO",
        "description": "Faculty lookup - Mathematics"
    },
    {
        "id": 28,
        "question": "Tell me about the Physics department",
        "category": "simple",
        "expected_type": "GET_DEPARTMENT_INFO",
        "description": "Department lookup - Physics"
    },
    {
        "id": 29,
        "question": "Who teaches EE101?",
        "category": "simple",
        "expected_type": "GET_COURSE_INSTRUCTORS",
        "description": "Course instructor lookup"
    },
    {
        "id": 30,
        "question": "How many faculty members are there?",
        "category": "simple",
        "expected_type": "COUNT_ENTITIES",
        "description": "Count faculty"
    },
    
    # New Intermediate Queries
    {
        "id": 31,
        "question": "What are the prerequisites for MATH201?",
        "category": "intermediate",
        "expected_type": "GET_PREREQUISITES",
        "description": "Math prerequisites"
    },
    {
        "id": 32,
        "question": "List all Physics courses",
        "category": "intermediate",
        "expected_type": "GET_COURSES_BY_DEPARTMENT",
        "description": "Courses by department - Physics"
    },
    {
        "id": 33,
        "question": "Who teaches in the EE department?",
        "category": "intermediate",
        "expected_type": "GET_FACULTY_BY_DEPARTMENT",
        "description": "Faculty by department - EE"
    },
    {
        "id": 34,
        "question": "What courses does Dr. Chen teach?",
        "category": "intermediate",
        "expected_type": "GET_COURSES_TAUGHT_BY",
        "description": "Courses by instructor - Dr. Chen"
    },
    {
        "id": 35,
        "question": "What courses require MATH101?",
        "category": "intermediate",
        "expected_type": "GET_COURSES_REQUIRING",
        "description": "Reverse prereq - MATH101"
    },
    
    # New Complex Queries
    {
        "id": 36,
        "question": "What are ALL preconditions for CS402 including transitive ones?",
        "category": "complex",
        "expected_type": "GET_ALL_PREREQUISITES",
        "description": "Transitive prereqs - CS402 (deep chain)"
    },
    {
        "id": 37,
        "question": "List all undergraduate courses",
        "category": "complex",
        "expected_type": "GET_COURSES_BY_LEVEL",
        "description": "Filter by level - Undergraduate"
    },
    {
        "id": 38,
        "question": "Who works on Quantum Mechanics?",
        "category": "complex",
        "expected_type": "GET_FACULTY_BY_RESEARCH",
        "description": "Research area lookup - Quantum"
    },
    {
        "id": 39,
        "question": "Compare MATH101 and MATH102",
        "category": "complex",
        "expected_type": "COMPARE_COURSES",
        "description": "Compare related courses"
    },
    {
        "id": 40,
        "question": "Find courses related to signals",
        "category": "complex",
        "expected_type": "SEARCH_COURSES",
        "description": "Keyword search - signals"
    },
    
    # New Tricky Queries
    {
        "id": 41,
        "question": "What do I need for Signal Processing?",
        "category": "tricky",
        "expected_type": "GET_ALL_PREREQUISITES",
        "alternative_types": ["GET_PREREQUISITES"],
        "description": "Informal name + 'need'"
    },
    {
        "id": 42,
        "question": "Dr. Johnson's classes",
        "category": "tricky",
        "expected_type": "GET_COURSES_TAUGHT_BY",
        "description": "Possessive informal query"
    },
    {
        "id": 43,
        "question": "Math department professors",
        "category": "tricky",
        "expected_type": "GET_FACULTY_BY_DEPARTMENT",
        "description": "Informal department name"
    },
    {
        "id": 44,
        "question": "Prereqs for Algorithms",
        "category": "tricky",
        "expected_type": "GET_PREREQUISITES",
        "alternative_types": ["GET_ALL_PREREQUISITES"],
        "description": "Very short informal query"
    },
    {
        "id": 45,
        "question": "Any courses on logic?",
        "category": "tricky",
        "expected_type": "SEARCH_COURSES",
        "description": "Existence check informal"
    },
    
    # New Multi-step Queries
    {
        "id": 46,
        "question": "How many courses require Calculus I?",
        "category": "multi-step",
        "expected_type": "GET_COURSES_REQUIRING",
        "description": "Count of reverse prereqs"
    },
    {
        "id": 47,
        "question": "Can I take CS402 if I only know python?",
        "category": "multi-step",
        "expected_type": "CAN_TAKE_COURSE",
        "description": "Eligibility with vague skills (should likely fail or default to basic check)"
    },
    {
        "id": 48,
        "question": "Who is the head of the department that offers CS101?",
        "category": "multi-step",
        "expected_type": "GET_DEPARTMENT_HEAD",
        "description": "Head of department via course"
    },
    {
        "id": 49,
        "question": "List courses taught by the head of CS",
        "category": "multi-step",
        "expected_type": "GET_COURSES_TAUGHT_BY",
        "description": "Courses by dept head"
    },
    {
        "id": 50,
        "question": "Are there incomplete prerequisites for CS401 if I took CS101?",
        "category": "multi-step",
        "expected_type": "CAN_TAKE_COURSE",
        "description": "Missing prereqs check"
    },
]


def run_test_suite(verbose: bool = True) -> dict:
    """
    Run all test questions and collect results.
    
    Args:
        verbose: If True, print detailed output for each question
        
    Returns:
        Dictionary with test results summary
    """
    agent = UniversityQAAgent()
    
    results = {
        "total": len(TEST_QUESTIONS),
        "passed": 0,
        "failed": 0,
        "by_category": {},
        "details": []
    }
    
    print("\n" + "="*70)
    print("NEURO-SYMBOLIC UNIVERSITY QA AGENT - TEST SUITE")
    print("="*70 + "\n")
    
    for test in TEST_QUESTIONS:
        category = test["category"]
        if category not in results["by_category"]:
            results["by_category"][category] = {"passed": 0, "total": 0}
        results["by_category"][category]["total"] += 1
        
        try:
            response = agent.ask(test["question"])
            
            # Check if query type matches expected (flexible matching)
            actual_type = response.parsed_query.query_type.value
            expected_type = test["expected_type"]
            alternative_types = test.get("alternative_types", [])
            type_match = (actual_type.upper() == expected_type.upper() or 
                          actual_type.upper() in [t.upper() for t in alternative_types])
            
            # Check if we got a successful result
            success = response.reasoning_result.success
            
            passed = type_match and success
            
            if passed:
                results["passed"] += 1
                results["by_category"][category]["passed"] += 1
                status = "✅ PASS"
            else:
                results["failed"] += 1
                status = "❌ FAIL"
            
            test_result = {
                "id": test["id"],
                "question": test["question"],
                "category": category,
                "passed": passed,
                "expected_type": expected_type,
                "actual_type": actual_type,
                "confidence": response.parsed_query.confidence,
                "answer_preview": response.answer[:200] if response.answer else "No answer"
            }
            results["details"].append(test_result)
            
            if verbose:
                print(f"[{test['id']:02d}] {status} | {test['category'].upper():12s} | {test['description']}")
                print(f"     Q: {test['question']}")
                print(f"     Expected: {expected_type}, Got: {actual_type}")
                if not passed:
                    print(f"     Answer: {response.answer[:100]}...")
                print()
                
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "id": test["id"],
                "question": test["question"],
                "category": category,
                "passed": False,
                "error": str(e)
            })
            if verbose:
                print(f"[{test['id']:02d}] ❌ ERROR | {test['category'].upper():12s} | {test['description']}")
                print(f"     Error: {e}")
                print()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nTotal: {results['total']} | Passed: {results['passed']} | Failed: {results['failed']}")
    print(f"Success Rate: {results['passed']/results['total']*100:.1f}%\n")
    
    print("By Category:")
    for category, stats in results["by_category"].items():
        rate = stats['passed']/stats['total']*100 if stats['total'] > 0 else 0
        print(f"  {category.upper():15s}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")
    
    print("\n" + "="*70)
    
    return results


def run_single_test(question_id: int, verbose: bool = True):
    """Run a single test by ID."""
    agent = UniversityQAAgent()
    
    test = next((t for t in TEST_QUESTIONS if t["id"] == question_id), None)
    if not test:
        print(f"Test with ID {question_id} not found.")
        return
    
    print(f"\n{'='*60}")
    print(f"Test #{test['id']}: {test['description']}")
    print(f"Category: {test['category']}")
    print(f"{'='*60}\n")
    
    response = agent.ask(test["question"])
    print(response)
    
    print(f"\nExpected Query Type: {test['expected_type']}")
    print(f"Actual Query Type: {response.parsed_query.query_type.value}")
    print(f"Match: {'✅ Yes' if response.parsed_query.query_type.value.upper() == test['expected_type'].upper() else '❌ No'}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run QA Agent Test Suite")
    parser.add_argument("--test", "-t", type=int, help="Run a specific test by ID")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (summary only)")
    
    args = parser.parse_args()
    
    if args.test:
        run_single_test(args.test)
    else:
        run_test_suite(verbose=not args.quiet)
