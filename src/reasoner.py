"""
Symbolic Reasoner module for the Neuro-Symbolic University QA Agent.

This module provides the SymbolicReasoner class that implements rule-based
reasoning over the knowledge graph to answer complex queries and provide
explanations for the reasoning process.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable
from src.knowledge_graph import KnowledgeGraph


class QueryType(Enum):
    """Types of queries the reasoner can handle."""
    GET_COURSE_INFO = "get_course_info"
    GET_FACULTY_INFO = "get_faculty_info"
    GET_DEPARTMENT_INFO = "get_department_info"
    GET_PREREQUISITES = "get_prerequisites"
    GET_ALL_PREREQUISITES = "get_all_prerequisites"
    GET_COURSES_BY_DEPARTMENT = "get_courses_by_department"
    GET_FACULTY_BY_DEPARTMENT = "get_faculty_by_department"
    GET_COURSES_TAUGHT_BY = "get_courses_taught_by"
    GET_COURSE_INSTRUCTORS = "get_course_instructors"
    GET_DEPARTMENT_HEAD = "get_department_head"
    CAN_TAKE_COURSE = "can_take_course"
    GET_COURSES_REQUIRING = "get_courses_requiring"
    GET_COURSES_BY_LEVEL = "get_courses_by_level"
    GET_FACULTY_BY_RESEARCH = "get_faculty_by_research"
    SEARCH_COURSES = "search_courses"
    COUNT_ENTITIES = "count_entities"
    COMPARE_COURSES = "compare_courses"


@dataclass
class ReasoningStep:
    """A single step in the reasoning chain."""
    rule_name: str
    description: str
    inputs: dict
    outputs: Any
    

@dataclass
class ReasoningResult:
    """Result of a reasoning query with explanation."""
    query_type: QueryType
    answer: Any
    success: bool
    reasoning_chain: list[ReasoningStep] = field(default_factory=list)
    error_message: Optional[str] = None
    
    def get_explanation(self) -> str:
        """Generate a human-readable explanation of the reasoning process."""
        if not self.success:
            return f"Query failed: {self.error_message}"
        
        lines = ["Reasoning Trace:"]
        for i, step in enumerate(self.reasoning_chain, 1):
            lines.append(f"  {i}. [{step.rule_name}] {step.description}")
        
        return "\n".join(lines)


class SymbolicReasoner:
    """
    Symbolic reasoning engine that operates on the knowledge graph.
    
    The reasoner implements a set of rules for answering queries about
    the university domain. Each rule can call knowledge graph methods
    and chain together for complex multi-step reasoning.
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
        "calculus i": "MATH101",
        "calculus ii": "MATH102",
        "discrete mathematics": "MATH301",
        "discrete math": "MATH301",
        "probability": "MATH401",
        "probability and statistics": "MATH401",
        "physics": "PHYS101",
        "physics i": "PHYS101",
        "physics ii": "PHYS201",
        "circuits": "EE101",
        "digital logic": "EE201",
        "digital logic design": "EE201",
        "signal processing": "EE301",
    }
    
    def __init__(self, kg: KnowledgeGraph):
        """
        Initialize the reasoner with a knowledge graph.
        
        Args:
            kg: The KnowledgeGraph instance to reason over
        """
        self.kg = kg
        self._rules: dict[QueryType, Callable] = {
            QueryType.GET_COURSE_INFO: self._rule_get_course_info,
            QueryType.GET_FACULTY_INFO: self._rule_get_faculty_info,
            QueryType.GET_DEPARTMENT_INFO: self._rule_get_department_info,
            QueryType.GET_PREREQUISITES: self._rule_get_prerequisites,
            QueryType.GET_ALL_PREREQUISITES: self._rule_get_all_prerequisites,
            QueryType.GET_COURSES_BY_DEPARTMENT: self._rule_get_courses_by_department,
            QueryType.GET_FACULTY_BY_DEPARTMENT: self._rule_get_faculty_by_department,
            QueryType.GET_COURSES_TAUGHT_BY: self._rule_get_courses_taught_by,
            QueryType.GET_COURSE_INSTRUCTORS: self._rule_get_course_instructors,
            QueryType.GET_DEPARTMENT_HEAD: self._rule_get_department_head,
            QueryType.CAN_TAKE_COURSE: self._rule_can_take_course,
            QueryType.GET_COURSES_REQUIRING: self._rule_get_courses_requiring,
            QueryType.GET_COURSES_BY_LEVEL: self._rule_get_courses_by_level,
            QueryType.GET_FACULTY_BY_RESEARCH: self._rule_get_faculty_by_research,
            QueryType.SEARCH_COURSES: self._rule_search_courses,
            QueryType.COUNT_ENTITIES: self._rule_count_entities,
            QueryType.COMPARE_COURSES: self._rule_compare_courses,
        }
    
    def _resolve_course_name(self, name: str) -> str:
        """Resolve a course name to its code."""
        if not name:
            return name
        name_lower = name.lower().strip()
        return self.COURSE_NAME_MAP.get(name_lower, name)
    
    def _normalize_faculty_name(self, name: str) -> str:
        """Normalize faculty name by removing titles."""
        import re
        if not name:
            return name
        # Remove common prefixes
        name = re.sub(r'^(dr\.?|prof\.?|professor)\s*', '', name, flags=re.IGNORECASE)
        return name.strip()
    
    def execute_query(self, query_type: QueryType, params: dict) -> ReasoningResult:
        """
        Execute a symbolic query with the given parameters.
        
        Args:
            query_type: The type of query to execute
            params: Query-specific parameters
            
        Returns:
            ReasoningResult with answer and explanation
        """
        if query_type not in self._rules:
            return ReasoningResult(
                query_type=query_type,
                answer=None,
                success=False,
                error_message=f"Unknown query type: {query_type}"
            )
        
        try:
            return self._rules[query_type](params)
        except Exception as e:
            return ReasoningResult(
                query_type=query_type,
                answer=None,
                success=False,
                error_message=str(e)
            )
    
    # ========== Rule Implementations ==========
    
    def _rule_get_course_info(self, params: dict) -> ReasoningResult:
        """Get information about a specific course."""
        chain = []
        course_code = params.get('course_code') or params.get('course_id')
        
        chain.append(ReasoningStep(
            rule_name="LOOKUP_COURSE",
            description=f"Looking up course by code: {course_code}",
            inputs={'course_code': course_code},
            outputs=None
        ))
        
        # Try by code first, then by ID
        course = self.kg.get_course_by_code(course_code)
        if not course:
            course = self.kg.get_node(course_code)
        
        if not course:
            return ReasoningResult(
                query_type=QueryType.GET_COURSE_INFO,
                answer=None,
                success=False,
                reasoning_chain=chain,
                error_message=f"Course not found: {course_code}"
            )
        
        chain[-1].outputs = course
        
        # Get additional info
        dept = self.kg.get_course_department(course['id'])
        instructors = self.kg.get_course_instructors(course['id'])
        prereqs = self.kg.get_prerequisites(course['id'])
        
        chain.append(ReasoningStep(
            rule_name="ENRICH_COURSE_DATA",
            description="Retrieving department, instructors, and prerequisites",
            inputs={'course_id': course['id']},
            outputs={'department': dept, 'instructors': instructors, 'prerequisites': prereqs}
        ))
        
        enriched_course = {
            **course,
            'department': dept,
            'instructors': instructors,
            'prerequisites': prereqs
        }
        
        return ReasoningResult(
            query_type=QueryType.GET_COURSE_INFO,
            answer=enriched_course,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_faculty_info(self, params: dict) -> ReasoningResult:
        """Get information about a faculty member."""
        chain = []
        name = params.get('name') or params.get('faculty_id')
        # Normalize name (remove Dr., Prof., etc.)
        normalized_name = self._normalize_faculty_name(name)
        
        chain.append(ReasoningStep(
            rule_name="LOOKUP_FACULTY",
            description=f"Looking up faculty: {name}",
            inputs={'name': name},
            outputs=None
        ))
        
        faculty = self.kg.get_faculty_by_name(normalized_name)
        if not faculty:
            faculty = self.kg.get_node(name)
        
        if not faculty:
            return ReasoningResult(
                query_type=QueryType.GET_FACULTY_INFO,
                answer=None,
                success=False,
                reasoning_chain=chain,
                error_message=f"Faculty not found: {name}"
            )
        
        chain[-1].outputs = faculty
        
        # Enrich with additional data
        dept = self.kg.get_faculty_department(faculty['id'])
        courses = self.kg.get_courses_taught_by(faculty['id'])
        
        chain.append(ReasoningStep(
            rule_name="ENRICH_FACULTY_DATA",
            description="Retrieving department and courses taught",
            inputs={'faculty_id': faculty['id']},
            outputs={'department': dept, 'courses': courses}
        ))
        
        enriched_faculty = {
            **faculty,
            'department': dept,
            'courses_taught': courses
        }
        
        return ReasoningResult(
            query_type=QueryType.GET_FACULTY_INFO,
            answer=enriched_faculty,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_department_info(self, params: dict) -> ReasoningResult:
        """Get information about a department."""
        chain = []
        code = params.get('code') or params.get('dept_id')
        
        chain.append(ReasoningStep(
            rule_name="LOOKUP_DEPARTMENT",
            description=f"Looking up department: {code}",
            inputs={'code': code},
            outputs=None
        ))
        
        dept = self.kg.get_department_by_code(code)
        if not dept:
            dept = self.kg.get_node(code)
        
        if not dept:
            return ReasoningResult(
                query_type=QueryType.GET_DEPARTMENT_INFO,
                answer=None,
                success=False,
                reasoning_chain=chain,
                error_message=f"Department not found: {code}"
            )
        
        chain[-1].outputs = dept
        
        # Enrich with additional data
        head = self.kg.get_department_head(dept['id'])
        faculty = self.kg.get_faculty_by_department(dept['id'])
        courses = self.kg.get_courses_by_department(dept['id'])
        
        chain.append(ReasoningStep(
            rule_name="ENRICH_DEPARTMENT_DATA",
            description="Retrieving head, faculty, and courses",
            inputs={'dept_id': dept['id']},
            outputs={'head': head, 'faculty_count': len(faculty), 'course_count': len(courses)}
        ))
        
        enriched_dept = {
            **dept,
            'head': head,
            'faculty': faculty,
            'courses': courses
        }
        
        return ReasoningResult(
            query_type=QueryType.GET_DEPARTMENT_INFO,
            answer=enriched_dept,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_prerequisites(self, params: dict) -> ReasoningResult:
        """Get direct prerequisites for a course."""
        chain = []
        course_code = params.get('course_code') or params.get('course_id')
        # Try to resolve course name to code
        course_code = self._resolve_course_name(course_code)
        
        # First resolve the course
        course = self.kg.get_course_by_code(course_code)
        if not course:
            course = self.kg.get_node(course_code)
        
        if not course:
            return ReasoningResult(
                query_type=QueryType.GET_PREREQUISITES,
                answer=None,
                success=False,
                error_message=f"Course not found: {course_code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_COURSE",
            description=f"Resolved course code {course_code} to {course['name']}",
            inputs={'course_code': course_code},
            outputs=course
        ))
        
        prereqs = self.kg.get_prerequisites(course['id'])
        
        chain.append(ReasoningStep(
            rule_name="QUERY_PREREQUISITES",
            description=f"Found {len(prereqs)} direct prerequisite(s)",
            inputs={'course_id': course['id']},
            outputs=[p['code'] for p in prereqs]
        ))
        
        return ReasoningResult(
            query_type=QueryType.GET_PREREQUISITES,
            answer=prereqs,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_all_prerequisites(self, params: dict) -> ReasoningResult:
        """Get all prerequisites (transitive) for a course."""
        chain = []
        course_code = params.get('course_code') or params.get('course_id')
        # Try to resolve course name to code
        course_code = self._resolve_course_name(course_code)
        
        course = self.kg.get_course_by_code(course_code)
        if not course:
            course = self.kg.get_node(course_code)
        
        if not course:
            return ReasoningResult(
                query_type=QueryType.GET_ALL_PREREQUISITES,
                answer=None,
                success=False,
                error_message=f"Course not found: {course_code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_COURSE",
            description=f"Resolved course code {course_code} to {course['name']}",
            inputs={'course_code': course_code},
            outputs=course
        ))
        
        # Get direct prereqs first
        direct_prereqs = self.kg.get_prerequisites(course['id'])
        chain.append(ReasoningStep(
            rule_name="QUERY_DIRECT_PREREQUISITES",
            description=f"Found {len(direct_prereqs)} direct prerequisite(s)",
            inputs={'course_id': course['id']},
            outputs=[p['code'] for p in direct_prereqs]
        ))
        
        # Get all transitive prereqs
        all_prereqs = self.kg.get_all_prerequisites(course['id'])
        
        chain.append(ReasoningStep(
            rule_name="COMPUTE_TRANSITIVE_CLOSURE",
            description=f"Computed transitive closure: {len(all_prereqs)} total prerequisite(s)",
            inputs={'direct_prereqs': [p['code'] for p in direct_prereqs]},
            outputs=[p['code'] for p in all_prereqs]
        ))
        
        return ReasoningResult(
            query_type=QueryType.GET_ALL_PREREQUISITES,
            answer=all_prereqs,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_courses_by_department(self, params: dict) -> ReasoningResult:
        """Get all courses offered by a department."""
        chain = []
        code = params.get('code') or params.get('dept_id')
        
        dept = self.kg.get_department_by_code(code)
        if not dept:
            dept = self.kg.get_node(code)
        
        if not dept:
            return ReasoningResult(
                query_type=QueryType.GET_COURSES_BY_DEPARTMENT,
                answer=None,
                success=False,
                error_message=f"Department not found: {code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_DEPARTMENT",
            description=f"Resolved department code {code} to {dept['name']}",
            inputs={'code': code},
            outputs=dept
        ))
        
        courses = self.kg.get_courses_by_department(dept['id'])
        
        chain.append(ReasoningStep(
            rule_name="QUERY_DEPARTMENT_COURSES",
            description=f"Found {len(courses)} course(s) in {dept['name']}",
            inputs={'dept_id': dept['id']},
            outputs=[c['code'] for c in courses]
        ))
        
        return ReasoningResult(
            query_type=QueryType.GET_COURSES_BY_DEPARTMENT,
            answer=courses,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_faculty_by_department(self, params: dict) -> ReasoningResult:
        """Get all faculty in a department."""
        chain = []
        code = params.get('code') or params.get('dept_id')
        
        dept = self.kg.get_department_by_code(code)
        if not dept:
            dept = self.kg.get_node(code)
        
        if not dept:
            return ReasoningResult(
                query_type=QueryType.GET_FACULTY_BY_DEPARTMENT,
                answer=None,
                success=False,
                error_message=f"Department not found: {code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_DEPARTMENT",
            description=f"Resolved department code {code} to {dept['name']}",
            inputs={'code': code},
            outputs=dept
        ))
        
        faculty = self.kg.get_faculty_by_department(dept['id'])
        
        chain.append(ReasoningStep(
            rule_name="QUERY_DEPARTMENT_FACULTY",
            description=f"Found {len(faculty)} faculty member(s) in {dept['name']}",
            inputs={'dept_id': dept['id']},
            outputs=[f['name'] for f in faculty]
        ))
        
        return ReasoningResult(
            query_type=QueryType.GET_FACULTY_BY_DEPARTMENT,
            answer=faculty,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_courses_taught_by(self, params: dict) -> ReasoningResult:
        """Get courses taught by a faculty member."""
        chain = []
        name = params.get('name') or params.get('faculty_id')
        # Normalize name (remove Dr., Prof., etc.)
        normalized_name = self._normalize_faculty_name(name)
        
        faculty = self.kg.get_faculty_by_name(normalized_name)
        if not faculty:
            faculty = self.kg.get_node(name)
        
        if not faculty:
            return ReasoningResult(
                query_type=QueryType.GET_COURSES_TAUGHT_BY,
                answer=None,
                success=False,
                error_message=f"Faculty not found: {name}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_FACULTY",
            description=f"Resolved faculty name to {faculty['name']}",
            inputs={'name': name},
            outputs=faculty
        ))
        
        courses = self.kg.get_courses_taught_by(faculty['id'])
        
        chain.append(ReasoningStep(
            rule_name="QUERY_FACULTY_COURSES",
            description=f"{faculty['name']} teaches {len(courses)} course(s)",
            inputs={'faculty_id': faculty['id']},
            outputs=[c['code'] for c in courses]
        ))
        
        return ReasoningResult(
            query_type=QueryType.GET_COURSES_TAUGHT_BY,
            answer=courses,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_course_instructors(self, params: dict) -> ReasoningResult:
        """Get instructors for a course."""
        chain = []
        course_code = params.get('course_code') or params.get('course_id')
        
        course = self.kg.get_course_by_code(course_code)
        if not course:
            course = self.kg.get_node(course_code)
        
        if not course:
            return ReasoningResult(
                query_type=QueryType.GET_COURSE_INSTRUCTORS,
                answer=None,
                success=False,
                error_message=f"Course not found: {course_code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_COURSE",
            description=f"Resolved course code {course_code} to {course['name']}",
            inputs={'course_code': course_code},
            outputs=course
        ))
        
        instructors = self.kg.get_course_instructors(course['id'])
        
        chain.append(ReasoningStep(
            rule_name="QUERY_COURSE_INSTRUCTORS",
            description=f"{course['name']} is taught by {len(instructors)} instructor(s)",
            inputs={'course_id': course['id']},
            outputs=[i['name'] for i in instructors]
        ))
        
        return ReasoningResult(
            query_type=QueryType.GET_COURSE_INSTRUCTORS,
            answer=instructors,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_department_head(self, params: dict) -> ReasoningResult:
        """Get the head of a department."""
        chain = []
        code = params.get('code') or params.get('dept_id')
        
        dept = self.kg.get_department_by_code(code)
        if not dept:
            dept = self.kg.get_node(code)
        
        if not dept:
            return ReasoningResult(
                query_type=QueryType.GET_DEPARTMENT_HEAD,
                answer=None,
                success=False,
                error_message=f"Department not found: {code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_DEPARTMENT",
            description=f"Resolved department code {code} to {dept['name']}",
            inputs={'code': code},
            outputs=dept
        ))
        
        head = self.kg.get_department_head(dept['id'])
        
        chain.append(ReasoningStep(
            rule_name="QUERY_DEPARTMENT_HEAD",
            description=f"Head of {dept['name']}: {head['name'] if head else 'None'}",
            inputs={'dept_id': dept['id']},
            outputs=head
        ))
        
        return ReasoningResult(
            query_type=QueryType.GET_DEPARTMENT_HEAD,
            answer=head,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_can_take_course(self, params: dict) -> ReasoningResult:
        """Check if a student can take a course given completed courses."""
        chain = []
        course_code = params.get('course_code') or params.get('course_id')
        completed = params.get('completed_courses', [])
        
        course = self.kg.get_course_by_code(course_code)
        if not course:
            course = self.kg.get_node(course_code)
        
        if not course:
            return ReasoningResult(
                query_type=QueryType.CAN_TAKE_COURSE,
                answer=None,
                success=False,
                error_message=f"Course not found: {course_code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_COURSE",
            description=f"Resolved course code {course_code} to {course['name']}",
            inputs={'course_code': course_code},
            outputs=course
        ))
        
        # Normalize completed courses to IDs
        completed_ids = []
        for c in completed:
            resolved = self.kg.get_course_by_code(c)
            if resolved:
                completed_ids.append(resolved['id'])
            elif self.kg.get_node(c):
                completed_ids.append(c)
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_COMPLETED_COURSES",
            description=f"Resolved {len(completed_ids)} completed course(s)",
            inputs={'completed': completed},
            outputs=completed_ids
        ))
        
        can_take, missing = self.kg.can_take_course(course['id'], completed_ids)
        
        chain.append(ReasoningStep(
            rule_name="CHECK_PREREQUISITES",
            description=f"Can take: {can_take}, Missing: {missing}",
            inputs={'course_id': course['id'], 'completed': completed_ids},
            outputs={'can_take': can_take, 'missing': missing}
        ))
        
        return ReasoningResult(
            query_type=QueryType.CAN_TAKE_COURSE,
            answer={'can_take': can_take, 'missing_prerequisites': missing},
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_courses_requiring(self, params: dict) -> ReasoningResult:
        """Get courses that require a given course as prerequisite."""
        chain = []
        course_code = params.get('course_code') or params.get('course_id')
        # Try to resolve course name to code  
        if course_code:
            course_code = self._resolve_course_name(course_code)
        
        course = self.kg.get_course_by_code(course_code) if course_code else None
        if not course:
            course = self.kg.get_node(course_code)
        
        if not course:
            return ReasoningResult(
                query_type=QueryType.GET_COURSES_REQUIRING,
                answer=None,
                success=False,
                error_message=f"Course not found: {course_code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_COURSE",
            description=f"Resolved course code {course_code} to {course['name']}",
            inputs={'course_code': course_code},
            outputs=course
        ))
        
        requiring = self.kg.get_courses_requiring(course['id'])
        
        chain.append(ReasoningStep(
            rule_name="QUERY_DEPENDENT_COURSES",
            description=f"{len(requiring)} course(s) require {course['code']}",
            inputs={'course_id': course['id']},
            outputs=[c['code'] for c in requiring]
        ))
        
        return ReasoningResult(
            query_type=QueryType.GET_COURSES_REQUIRING,
            answer=requiring,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_courses_by_level(self, params: dict) -> ReasoningResult:
        """Get courses by level (undergraduate/graduate)."""
        chain = []
        level = params.get('level', 'undergraduate')
        
        chain.append(ReasoningStep(
            rule_name="FILTER_BY_LEVEL",
            description=f"Filtering courses by level: {level}",
            inputs={'level': level},
            outputs=None
        ))
        
        courses = self.kg.get_courses_by_level(level)
        chain[-1].outputs = [c['code'] for c in courses]
        
        return ReasoningResult(
            query_type=QueryType.GET_COURSES_BY_LEVEL,
            answer=courses,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_get_faculty_by_research(self, params: dict) -> ReasoningResult:
        """Get faculty by research area."""
        chain = []
        area = params.get('area', '')
        
        chain.append(ReasoningStep(
            rule_name="SEARCH_RESEARCH_AREA",
            description=f"Searching for faculty with research area: {area}",
            inputs={'area': area},
            outputs=None
        ))
        
        faculty = self.kg.get_faculty_by_research_area(area)
        chain[-1].outputs = [f['name'] for f in faculty]
        
        return ReasoningResult(
            query_type=QueryType.GET_FACULTY_BY_RESEARCH,
            answer=faculty,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_search_courses(self, params: dict) -> ReasoningResult:
        """Search courses by keyword."""
        chain = []
        query = params.get('query', '')
        
        chain.append(ReasoningStep(
            rule_name="SEARCH_COURSES",
            description=f"Searching for courses matching: {query}",
            inputs={'query': query},
            outputs=None
        ))
        
        courses = self.kg.search_courses(query)
        chain[-1].outputs = [c['code'] for c in courses]
        
        return ReasoningResult(
            query_type=QueryType.SEARCH_COURSES,
            answer=courses,
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_count_entities(self, params: dict) -> ReasoningResult:
        """Count entities of a given type."""
        chain = []
        entity_type = params.get('entity_type', 'course')
        
        stats = self.kg.get_graph_statistics()
        
        count_map = {
            'course': stats.get('courses', 0),
            'courses': stats.get('courses', 0),
            'faculty': stats.get('faculty', 0),
            'department': stats.get('departments', 0),
            'departments': stats.get('departments', 0),
            'prerequisite': stats.get('prerequisites', 0),
            'prerequisites': stats.get('prerequisites', 0),
        }
        
        count = count_map.get(entity_type.lower(), 0)
        
        chain.append(ReasoningStep(
            rule_name="COUNT_ENTITIES",
            description=f"Counting {entity_type}: {count}",
            inputs={'entity_type': entity_type},
            outputs=count
        ))
        
        return ReasoningResult(
            query_type=QueryType.COUNT_ENTITIES,
            answer={'entity_type': entity_type, 'count': count},
            success=True,
            reasoning_chain=chain
        )
    
    def _rule_compare_courses(self, params: dict) -> ReasoningResult:
        """Compare two courses."""
        chain = []
        course1_code = params.get('course1')
        course2_code = params.get('course2')
        
        course1 = self.kg.get_course_by_code(course1_code)
        course2 = self.kg.get_course_by_code(course2_code)
        
        if not course1:
            return ReasoningResult(
                query_type=QueryType.COMPARE_COURSES,
                answer=None,
                success=False,
                error_message=f"Course not found: {course1_code}"
            )
        
        if not course2:
            return ReasoningResult(
                query_type=QueryType.COMPARE_COURSES,
                answer=None,
                success=False,
                error_message=f"Course not found: {course2_code}"
            )
        
        chain.append(ReasoningStep(
            rule_name="RESOLVE_COURSES",
            description=f"Resolved courses: {course1['name']} and {course2['name']}",
            inputs={'course1': course1_code, 'course2': course2_code},
            outputs={'course1': course1, 'course2': course2}
        ))
        
        # Get prerequisites for both
        prereqs1 = set(p['id'] for p in self.kg.get_all_prerequisites(course1['id']))
        prereqs2 = set(p['id'] for p in self.kg.get_all_prerequisites(course2['id']))
        
        common_prereqs = prereqs1 & prereqs2
        
        chain.append(ReasoningStep(
            rule_name="COMPARE_PREREQUISITES",
            description=f"Common prerequisites: {len(common_prereqs)}",
            inputs={'prereqs1': list(prereqs1), 'prereqs2': list(prereqs2)},
            outputs={'common': list(common_prereqs)}
        ))
        
        comparison = {
            'course1': course1,
            'course2': course2,
            'same_department': course1.get('department') == course2.get('department'),
            'same_level': course1.get('level') == course2.get('level'),
            'credits_diff': course1.get('credits', 0) - course2.get('credits', 0),
            'common_prereq_count': len(common_prereqs)
        }
        
        return ReasoningResult(
            query_type=QueryType.COMPARE_COURSES,
            answer=comparison,
            success=True,
            reasoning_chain=chain
        )
