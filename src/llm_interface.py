"""
LLM Interface module for the Neuro-Symbolic University QA Agent.

This module provides the LLMInterface class that translates natural language
questions into structured symbolic queries and generates human-readable
explanations from reasoning results.
"""

import os
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any

from dotenv import load_dotenv

from src.reasoner import QueryType, ReasoningResult


# Load environment variables
load_dotenv()


@dataclass
class ParsedQuery:
    """Represents a parsed natural language query."""
    original_question: str
    query_type: QueryType
    parameters: dict
    confidence: float  # 0.0 to 1.0


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        return self._client
    
    def generate(self, prompt: str) -> str:
        response = self.client.generate_content(prompt)
        return response.text


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider for testing without API calls.
    Uses pattern matching to simulate query parsing.
    """
    
    # Course name to code mapping for natural language references
    COURSE_NAME_MAP = {
        "machine learning": "CS401",
        "natural language processing": "CS402",
        "nlp": "CS402",
        "algorithms": "CS301",
        "data structures": "CS201",
        "programming": "CS101",
        "intro to programming": "CS101",
        "introduction to programming": "CS101",
        "cybersecurity": "CS450",
        "computer networks": "CS350",
        "networks": "CS350",
        "quantum mechanics": "PHYS301",
        "linear algebra": "MATH201",
        "calculus": "MATH101",
        "discrete mathematics": "MATH301",
        "discrete math": "MATH301",
        "probability": "MATH401",
        "physics": "PHYS101",
        "circuits": "EE101",
        "digital logic": "EE201",
        "signal processing": "EE301",
    }
    
    def generate(self, prompt: str) -> str:
        # Extract the question from the prompt
        question_match = re.search(r'Question:\s*"([^"]+)"', prompt)
        if not question_match:
            return json.dumps({
                "query_type": "SEARCH_COURSES",
                "parameters": {"query": ""},
                "confidence": 0.3
            })
        
        question = question_match.group(1).lower()
        
        # Check for course name references and resolve to codes
        resolved_course = None
        for name, code in self.COURSE_NAME_MAP.items():
            if name in question:
                resolved_course = code
                break
        
        # Pattern matching for different query types (ORDER MATTERS - more specific first)
        patterns = [
            # Count entities (specific patterns first)
            (r"how\s+many\s+(course[s]?|facult(?:y|ies)|department[s]?|professor[s]?)", "COUNT_ENTITIES", 
             lambda m: {"entity_type": m.group(1).rstrip('s').replace('ies', 'y')}),
            (r"(?:total\s+)?number\s+of\s+(course[s]?|facult(?:y|ies)|department[s]?)", "COUNT_ENTITIES", 
             lambda m: {"entity_type": m.group(1).rstrip('s').replace('ies', 'y')}),
            
            # Compare courses
            (r"compare\s+(\w+\d+)\s+(?:and|with|to|vs)\s+(\w+\d+)", "COMPARE_COURSES", 
             lambda m: {"course1": m.group(1).upper(), "course2": m.group(2).upper()}),
            (r"difference\s+between\s+(\w+\d+)\s+and\s+(\w+\d+)", "COMPARE_COURSES", 
             lambda m: {"course1": m.group(1).upper(), "course2": m.group(2).upper()}),
            
            # ALL prerequisites (specific - must come before regular prereqs)
            (r"all\s+(?:the\s+)?prerequisite[s]?\s+(?:for|of|to\s+take)\s+(\w+\d+)", "GET_ALL_PREREQUISITES", 
             lambda m: {"course_code": m.group(1).upper()}),
            (r"all\s+(?:the\s+)?prerequisite[s]?.*including\s+transitive", "GET_ALL_PREREQUISITES", 
             lambda m, q=question: {"course_code": self._extract_course_code(q)}),
            (r"(?:what\s+)?prerequisite[s]?\s+do\s+i\s+need\s+to\s+take", "GET_ALL_PREREQUISITES", 
             lambda m, q=question, rc=resolved_course: {"course_code": rc or self._extract_course_code(q)}),
            (r"what\s+(?:do\s+i\s+need|are\s+the\s+requirements)\s+(?:to\s+take|for)", "GET_ALL_PREREQUISITES", 
             lambda m, q=question, rc=resolved_course: {"course_code": rc or self._extract_course_code(q)}),
            (r"prerequisite\s+chain\s+for", "GET_ALL_PREREQUISITES", 
             lambda m, q=question, rc=resolved_course: {"course_code": rc or self._extract_course_code(q)}),
            
            # Direct prerequisites  
            (r"(?:what\s+are\s+)?(?:the\s+)?prerequisite[s]?\s+(?:for|of)\s+(\w+\d+)", "GET_PREREQUISITES", 
             lambda m: {"course_code": m.group(1).upper()}),
            
            # Courses by level (specific patterns)
            (r"(?:list\s+)?(?:all\s+)?(undergraduate|graduate)\s+course[s]?", "GET_COURSES_BY_LEVEL", 
             lambda m: {"level": m.group(1)}),
            (r"(undergraduate|graduate)\s+level\s+course[s]?", "GET_COURSES_BY_LEVEL", 
             lambda m: {"level": m.group(1)}),
            
            # Department head (specific)
            (r"(?:who\s+is\s+)?(?:the\s+)?head\s+of\s+(?:the\s+)?(\w+)(?:\s+department)?", "GET_DEPARTMENT_HEAD", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            (r"(\w+)\s+department\s+head", "GET_DEPARTMENT_HEAD", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            
            # Courses requiring (reverse prerequisite)
            (r"(?:what\s+)?course[s]?\s+require\s+(\w+\d+)", "GET_COURSES_REQUIRING", 
             lambda m: {"course_code": m.group(1).upper()}),
            (r"which\s+course[s]?\s+(?:need|require)\s+(\w+\d+)", "GET_COURSES_REQUIRING", 
             lambda m: {"course_code": m.group(1).upper()}),
            
            # Course instructors
            (r"who\s+teaches?\s+(\w+\d+)", "GET_COURSE_INSTRUCTORS", 
             lambda m: {"course_code": m.group(1).upper()}),
            (r"instructor[s]?\s+(?:for|of)\s+(\w+\d+)", "GET_COURSE_INSTRUCTORS", 
             lambda m: {"course_code": m.group(1).upper()}),
            (r"(\w+\d+)\s+(?:is\s+)?taught\s+by", "GET_COURSE_INSTRUCTORS", 
             lambda m: {"course_code": m.group(1).upper()}),
            
            # Course info
            (r"(?:tell\s+me\s+about|what\s+is|describe|info\s+(?:about|on))\s+(?:the\s+)?(?:course\s+)?(\w+\d+)", "GET_COURSE_INFO", 
             lambda m: {"course_code": m.group(1).upper()}),
            (r"(\w+\d+)\s+(?:course\s+)?(?:info|information|details)", "GET_COURSE_INFO", 
             lambda m: {"course_code": m.group(1).upper()}),
            
            # Department info (specific patterns to avoid faculty match)
            (r"(?:tell\s+me\s+about|what\s+is|describe)\s+(?:the\s+)?(\w+)\s+department", "GET_DEPARTMENT_INFO", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            (r"(?:info|information|details)\s+(?:about|on)\s+(?:the\s+)?(\w+)\s+department", "GET_DEPARTMENT_INFO", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            
            # Courses by department
            (r"(?:what\s+)?course[s]?\s+(?:are\s+)?(?:offered\s+)?(?:in|by)\s+(?:the\s+)?(\w+)\s*(?:department)?", "GET_COURSES_BY_DEPARTMENT", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            (r"list\s+(?:all\s+)?(\w+)\s+course[s]?", "GET_COURSES_BY_DEPARTMENT", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            (r"(\w+)\s+department\s+course[s]?", "GET_COURSES_BY_DEPARTMENT", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            
            # Faculty by department
            (r"(?:who\s+are\s+)?(?:the\s+)?facult(?:y|ies)\s+in\s+(?:the\s+)?(\w+)", "GET_FACULTY_BY_DEPARTMENT", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            (r"professors?\s+in\s+(?:the\s+)?(\w+)", "GET_FACULTY_BY_DEPARTMENT", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            (r"who\s+teaches?\s+(?:in\s+)?(?:the\s+)?(\w+)\s+department", "GET_FACULTY_BY_DEPARTMENT", 
             lambda m: {"code": self._normalize_dept_code(m.group(1))}),
            
            # Courses taught by faculty
            (r"(?:what\s+)?course[s]?\s+(?:does|is)\s+(?:dr\.?|professor)?\s*(\w+(?:\s+\w+)?)\s+teach", "GET_COURSES_TAUGHT_BY", 
             lambda m: {"name": m.group(1)}),
            (r"(?:dr\.?|professor)?\s*(\w+)'?s?\s+course[s]?", "GET_COURSES_TAUGHT_BY", 
             lambda m: {"name": m.group(1)}),
            
            # Faculty by research area
            (r"(?:who\s+)?(?:does\s+)?research\s+(?:on|in|about)\s+(.+)", "GET_FACULTY_BY_RESEARCH", 
             lambda m: {"area": m.group(1).strip()}),
            (r"facult(?:y|ies)\s+(?:working\s+)?(?:on|in)\s+(.+)", "GET_FACULTY_BY_RESEARCH", 
             lambda m: {"area": m.group(1).strip()}),
            (r"(machine\s+learning|ai|artificial\s+intelligence|nlp|data\s+mining)\s+(?:research(?:ers?)?|facult(?:y|ies))", "GET_FACULTY_BY_RESEARCH", 
             lambda m: {"area": m.group(1)}),
            
            # Can take course
            (r"can\s+(?:i|a\s+student)\s+take\s+(\w+\d+)", "CAN_TAKE_COURSE", 
             lambda m: {"course_code": m.group(1).upper(), "completed_courses": self._extract_completed_courses(question)}),
            
            # Faculty info (must come after more specific patterns)
            (r"(?:who\s+is|tell\s+me\s+about)\s+(?:dr\.?|professor)?\s*(\w+(?:\s+\w+)?)", "GET_FACULTY_INFO", 
             lambda m: {"name": m.group(1)}),
            
            # Search courses (catch-all for finding things)
            (r"(?:search|find|look\s+for)\s+(?:course[s]?\s+)?(?:about|on|related\s+to)?\s*(.+)", "SEARCH_COURSES", 
             lambda m: {"query": m.group(1).strip()}),
            (r"(?:are\s+there\s+)?(?:any\s+)?course[s]?\s+(?:about|on|related\s+to)\s+(.+)", "SEARCH_COURSES", 
             lambda m: {"query": m.group(1).strip()}),
            (r"course[s]?\s+(?:with(?:out)?|having)\s+no\s+prerequisite[s]?", "SEARCH_COURSES", 
             lambda m: {"query": "no prerequisites"}),
        ]
        
        for pattern, query_type, param_fn in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                try:
                    params = param_fn(match)
                except TypeError:
                    # Lambda might need the question context
                    params = param_fn(match)
                return json.dumps({
                    "query_type": query_type,
                    "parameters": params,
                    "confidence": 0.85
                })
        
        # Default: search courses
        return json.dumps({
            "query_type": "SEARCH_COURSES",
            "parameters": {"query": question},
            "confidence": 0.5
        })
    
    def _extract_course_code(self, question: str) -> str:
        """Extract course code from a question."""
        match = re.search(r'\b([A-Za-z]+\d+)\b', question)
        if match:
            return match.group(1).upper()
        # Try to find by name
        for name, code in self.COURSE_NAME_MAP.items():
            if name in question.lower():
                return code
        return ""
    
    def _normalize_dept_code(self, dept: str) -> str:
        """Normalize department name/code to standard code."""
        dept_lower = dept.lower()
        dept_map = {
            "computer science": "CS", "computer": "CS", "cs": "CS", "comp": "CS",
            "mathematics": "MATH", "math": "MATH", "maths": "MATH",
            "physics": "PHYS", "phys": "PHYS",
            "electrical engineering": "EE", "electrical": "EE", "ee": "EE",
        }
        return dept_map.get(dept_lower, dept.upper())
    
    def _extract_completed_courses(self, question: str) -> list:
        """Extract completed courses from question."""
        # Look for patterns like "completed CS101 and MATH101" or "only completed CS101"
        courses = re.findall(r'\b([A-Za-z]+\d+)\b', question)
        return [c.upper() for c in courses if c.lower() not in ['cs401', 'take']]


class LLMInterface:
    """
    Interface for translating natural language to symbolic queries and
    generating explanations from reasoning results.
    """
    
    # System prompt for query parsing
    PARSE_SYSTEM_PROMPT = """You are a query parser for a university knowledge base. 
Your task is to analyze natural language questions and extract structured query information.

The knowledge base contains information about:
- Departments (CS, MATH, PHYS, EE)
- Faculty members and their research areas
- Courses with codes like CS101, MATH201, etc.
- Prerequisites relationships between courses

Available query types:
- GET_COURSE_INFO: Get details about a specific course
- GET_FACULTY_INFO: Get details about a faculty member
- GET_DEPARTMENT_INFO: Get details about a department
- GET_PREREQUISITES: Get direct prerequisites for a course
- GET_ALL_PREREQUISITES: Get ALL prerequisites (including transitive) for a course
- GET_COURSES_BY_DEPARTMENT: List courses in a department
- GET_FACULTY_BY_DEPARTMENT: List faculty in a department
- GET_COURSES_TAUGHT_BY: List courses taught by a faculty member
- GET_COURSE_INSTRUCTORS: Get who teaches a course
- GET_DEPARTMENT_HEAD: Get the head of a department
- CAN_TAKE_COURSE: Check if prerequisites are met (needs completed_courses list)
- GET_COURSES_REQUIRING: Find courses that require a given course
- GET_COURSES_BY_LEVEL: List undergraduate or graduate courses
- GET_FACULTY_BY_RESEARCH: Find faculty by research area
- SEARCH_COURSES: Search courses by keyword
- COUNT_ENTITIES: Count courses, faculty, etc.
- COMPARE_COURSES: Compare two courses

Output JSON with:
{
  "query_type": "<QUERY_TYPE>",
  "parameters": {<relevant parameters>},
  "confidence": <0.0 to 1.0>
}

Parameter examples:
- course_code: "CS101", "MATH201"
- name: "Smith", "Alice Smith"
- code: "CS", "MATH" (department code)
- level: "undergraduate" or "graduate"
- area: "Machine Learning", "AI"
- completed_courses: ["CS101", "MATH101"]
- query: "programming" (search term)
- course1, course2: for comparing courses
"""

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        """
        Initialize the LLM interface.
        
        Args:
            provider: LLM provider to use. If None, selects based on LLM_PROVIDER env var.
        """
        if provider is not None:
            self.provider = provider
        else:
            llm_provider = os.getenv("LLM_PROVIDER", "mock").lower()
            if llm_provider == "openai":
                self.provider = OpenAIProvider()
            elif llm_provider == "gemini":
                self.provider = GeminiProvider()
            else:
                # Default to mock for testing
                self.provider = MockLLMProvider()
    
    def parse_question(self, question: str) -> ParsedQuery:
        """
        Parse a natural language question into a structured query.
        
        Args:
            question: The natural language question
            
        Returns:
            ParsedQuery object with query type and parameters
        """
        prompt = f"""{self.PARSE_SYSTEM_PROMPT}

Question: "{question}"

Respond with only the JSON object, no additional text."""
        
        response = self.provider.generate(prompt)
        
        # Parse the JSON response
        try:
            # Clean up response - sometimes LLMs wrap in code blocks
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"```(?:json)?\n?", "", cleaned)
                cleaned = cleaned.rstrip("`").strip()
            
            parsed = json.loads(cleaned)
            
            query_type_str = parsed.get("query_type", "SEARCH_COURSES")
            try:
                query_type = QueryType[query_type_str]
            except KeyError:
                query_type = QueryType.SEARCH_COURSES
            
            return ParsedQuery(
                original_question=question,
                query_type=query_type,
                parameters=parsed.get("parameters", {}),
                confidence=parsed.get("confidence", 0.5)
            )
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to search
            return ParsedQuery(
                original_question=question,
                query_type=QueryType.SEARCH_COURSES,
                parameters={"query": question},
                confidence=0.3
            )
    
    def generate_answer(self, question: str, result: ReasoningResult) -> str:
        """
        Generate a natural language answer from a reasoning result.
        
        Args:
            question: The original question
            result: The ReasoningResult from the symbolic reasoner
            
        Returns:
            Human-readable answer string
        """
        if not result.success:
            return f"I couldn't find an answer to your question. {result.error_message}"
        
        # Format the answer based on query type
        answer = result.answer
        
        if result.query_type == QueryType.GET_COURSE_INFO:
            return self._format_course_info(answer)
        
        elif result.query_type == QueryType.GET_FACULTY_INFO:
            return self._format_faculty_info(answer)
        
        elif result.query_type == QueryType.GET_DEPARTMENT_INFO:
            return self._format_department_info(answer)
        
        elif result.query_type in (QueryType.GET_PREREQUISITES, QueryType.GET_ALL_PREREQUISITES):
            return self._format_prerequisites(answer, result.query_type == QueryType.GET_ALL_PREREQUISITES)
        
        elif result.query_type == QueryType.GET_COURSES_BY_DEPARTMENT:
            return self._format_course_list(answer, "in this department")
        
        elif result.query_type == QueryType.GET_FACULTY_BY_DEPARTMENT:
            return self._format_faculty_list(answer, "in this department")
        
        elif result.query_type == QueryType.GET_COURSES_TAUGHT_BY:
            return self._format_course_list(answer, "taught by this faculty member")
        
        elif result.query_type == QueryType.GET_COURSE_INSTRUCTORS:
            return self._format_instructor_list(answer)
        
        elif result.query_type == QueryType.GET_DEPARTMENT_HEAD:
            if answer:
                return f"The department head is {answer.get('name', 'Unknown')} ({answer.get('title', '')})."
            return "No department head found."
        
        elif result.query_type == QueryType.CAN_TAKE_COURSE:
            return self._format_can_take(answer)
        
        elif result.query_type == QueryType.GET_COURSES_REQUIRING:
            return self._format_course_list(answer, "that require this course")
        
        elif result.query_type == QueryType.GET_COURSES_BY_LEVEL:
            return self._format_course_list(answer, "at this level")
        
        elif result.query_type == QueryType.GET_FACULTY_BY_RESEARCH:
            return self._format_faculty_list(answer, "working in this research area")
        
        elif result.query_type == QueryType.SEARCH_COURSES:
            return self._format_course_list(answer, "matching your search")
        
        elif result.query_type == QueryType.COUNT_ENTITIES:
            return f"There are {answer.get('count', 0)} {answer.get('entity_type', 'entities')}."
        
        elif result.query_type == QueryType.COMPARE_COURSES:
            return self._format_comparison(answer)
        
        else:
            return f"Result: {answer}"
    
    def _format_course_info(self, course: dict) -> str:
        lines = [
            f"**{course.get('code', 'Unknown')} - {course.get('name', 'Unknown Course')}**",
            f"- Credits: {course.get('credits', 'N/A')}",
            f"- Level: {course.get('level', 'N/A').title()}",
            f"- Description: {course.get('description', 'No description available')}",
        ]
        
        if course.get('department'):
            lines.append(f"- Department: {course['department'].get('name', 'Unknown')}")
        
        if course.get('instructors'):
            instructors = ", ".join(i.get('name', '') for i in course['instructors'])
            lines.append(f"- Instructors: {instructors}")
        
        if course.get('prerequisites'):
            prereqs = ", ".join(p.get('code', '') for p in course['prerequisites'])
            lines.append(f"- Prerequisites: {prereqs}")
        else:
            lines.append("- Prerequisites: None")
        
        return "\n".join(lines)
    
    def _format_faculty_info(self, faculty: dict) -> str:
        lines = [
            f"**{faculty.get('name', 'Unknown')}**",
            f"- Title: {faculty.get('title', 'N/A')}",
            f"- Email: {faculty.get('email', 'N/A')}",
        ]
        
        if faculty.get('department'):
            lines.append(f"- Department: {faculty['department'].get('name', 'Unknown')}")
        
        if faculty.get('research_areas'):
            areas = ", ".join(faculty['research_areas'])
            lines.append(f"- Research Areas: {areas}")
        
        if faculty.get('courses_taught'):
            courses = ", ".join(c.get('code', '') for c in faculty['courses_taught'])
            lines.append(f"- Courses Taught: {courses}")
        
        return "\n".join(lines)
    
    def _format_department_info(self, dept: dict) -> str:
        lines = [
            f"**{dept.get('name', 'Unknown Department')} ({dept.get('code', '')})**",
        ]
        
        if dept.get('head'):
            lines.append(f"- Head: {dept['head'].get('name', 'Unknown')}")
        
        if dept.get('faculty'):
            lines.append(f"- Faculty Members: {len(dept['faculty'])}")
            for f in dept['faculty'][:5]:  # Show first 5
                lines.append(f"  - {f.get('name', '')}")
            if len(dept['faculty']) > 5:
                lines.append(f"  ... and {len(dept['faculty']) - 5} more")
        
        if dept.get('courses'):
            lines.append(f"- Courses Offered: {len(dept['courses'])}")
            for c in dept['courses'][:5]:  # Show first 5
                lines.append(f"  - {c.get('code', '')}: {c.get('name', '')}")
            if len(dept['courses']) > 5:
                lines.append(f"  ... and {len(dept['courses']) - 5} more")
        
        return "\n".join(lines)
    
    def _format_prerequisites(self, prereqs: list, is_all: bool) -> str:
        if not prereqs:
            return "This course has no prerequisites."
        
        prefix = "All prerequisites (including transitive)" if is_all else "Direct prerequisites"
        lines = [f"{prefix}:"]
        for p in prereqs:
            lines.append(f"- {p.get('code', '')}: {p.get('name', '')}")
        
        return "\n".join(lines)
    
    def _format_course_list(self, courses: list, context: str) -> str:
        if not courses:
            return f"No courses found {context}."
        
        lines = [f"Found {len(courses)} course(s) {context}:"]
        for c in courses:
            lines.append(f"- {c.get('code', '')}: {c.get('name', '')} ({c.get('credits', '?')} credits)")
        
        return "\n".join(lines)
    
    def _format_faculty_list(self, faculty: list, context: str) -> str:
        if not faculty:
            return f"No faculty found {context}."
        
        lines = [f"Found {len(faculty)} faculty member(s) {context}:"]
        for f in faculty:
            lines.append(f"- {f.get('name', '')} ({f.get('title', '')})")
        
        return "\n".join(lines)
    
    def _format_instructor_list(self, instructors: list) -> str:
        if not instructors:
            return "No instructors found for this course."
        
        if len(instructors) == 1:
            return f"This course is taught by {instructors[0].get('name', 'Unknown')}."
        
        names = ", ".join(i.get('name', '') for i in instructors)
        return f"This course is taught by: {names}"
    
    def _format_can_take(self, result: dict) -> str:
        if result.get('can_take'):
            return "Yes, you can take this course! All prerequisites are satisfied."
        
        missing = result.get('missing_prerequisites', [])
        if missing:
            missing_str = ", ".join(missing)
            return f"No, you cannot take this course yet. Missing prerequisites: {missing_str}"
        
        return "Unable to determine if you can take this course."
    
    def _format_comparison(self, comparison: dict) -> str:
        c1 = comparison.get('course1', {})
        c2 = comparison.get('course2', {})
        
        lines = [
            f"**Comparing {c1.get('code', '')} and {c2.get('code', '')}:**",
            "",
            f"| Aspect | {c1.get('code', '')} | {c2.get('code', '')} |",
            "|--------|---------|---------|",
            f"| Name | {c1.get('name', '')} | {c2.get('name', '')} |",
            f"| Credits | {c1.get('credits', 'N/A')} | {c2.get('credits', 'N/A')} |",
            f"| Level | {c1.get('level', 'N/A')} | {c2.get('level', 'N/A')} |",
            "",
            f"- Same Department: {'Yes' if comparison.get('same_department') else 'No'}",
            f"- Same Level: {'Yes' if comparison.get('same_level') else 'No'}",
            f"- Common Prerequisites: {comparison.get('common_prereq_count', 0)}",
        ]
        
        return "\n".join(lines)
