"""
Knowledge Graph module for the Neuro-Symbolic University QA Agent.

This module provides the KnowledgeGraph class that loads university data
from a JSON file and provides methods for querying entities and relationships.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Union
import networkx as nx


class KnowledgeGraph:
    """
    A knowledge graph implementation using NetworkX for university data.
    
    The graph contains nodes for:
    - Departments (type: 'department')
    - Faculty members (type: 'faculty')
    - Courses (type: 'course')
    
    And edges representing relationships:
    - 'belongs_to': faculty/course -> department
    - 'teaches': faculty -> course
    - 'prerequisite': course -> course (required before)
    - 'heads': faculty -> department
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the knowledge graph.
        
        Args:
            data_path: Path to the JSON file containing university data.
                      If None, uses the default path in data/university_kg.json
        """
        self.graph = nx.DiGraph()
        self._data: dict = {}
        
        if data_path is None:
            # Default to the data directory relative to this file
            data_path = Path(__file__).parent.parent / "data" / "university_kg.json"
        
        self.load_data(data_path)
    
    def load_data(self, path: str | Path) -> None:
        """
        Load university data from a JSON file and build the graph.
        
        Args:
            path: Path to the JSON file
        """
        with open(path, 'r') as f:
            self._data = json.load(f)
        
        self._build_graph()
    
    def _build_graph(self) -> None:
        """Build the NetworkX graph from loaded data."""
        # Add department nodes
        for dept in self._data.get('departments', []):
            self.graph.add_node(
                dept['id'],
                type='department',
                name=dept['name'],
                code=dept['code']
            )
        
        # Add faculty nodes
        for faculty in self._data.get('faculty', []):
            self.graph.add_node(
                faculty['id'],
                type='faculty',
                name=faculty['name'],
                title=faculty['title'],
                email=faculty.get('email', ''),
                research_areas=faculty.get('research_areas', [])
            )
            # Add belongs_to edge (faculty -> department)
            self.graph.add_edge(
                faculty['id'],
                faculty['department'],
                relation='belongs_to'
            )
            
        # Add department head edges
        for dept in self._data.get('departments', []):
            if 'faculty_head' in dept:
                self.graph.add_edge(
                    dept['faculty_head'],
                    dept['id'],
                    relation='heads'
                )
        
        # Add course nodes
        for course in self._data.get('courses', []):
            self.graph.add_node(
                course['id'],
                type='course',
                code=course['code'],
                name=course['name'],
                credits=course['credits'],
                level=course['level'],
                description=course.get('description', '')
            )
            # Add belongs_to edge (course -> department)
            self.graph.add_edge(
                course['id'],
                course['department'],
                relation='belongs_to'
            )
            # Add teaches edges (faculty -> course)
            for instructor_id in course.get('taught_by', []):
                self.graph.add_edge(
                    instructor_id,
                    course['id'],
                    relation='teaches'
                )
        
        # Add prerequisite edges
        for prereq in self._data.get('prerequisites', []):
            self.graph.add_edge(
                prereq['course'],
                prereq['requires'],
                relation='prerequisite'
            )
    
    # ========== Basic Query Methods ==========
    
    def get_node(self, node_id: str) -> Optional[dict]:
        """
        Get a node by its ID with all attributes.
        
        Args:
            node_id: The unique identifier of the node
            
        Returns:
            Dict with node attributes or None if not found
        """
        if node_id in self.graph.nodes:
            return {'id': node_id, **self.graph.nodes[node_id]}
        return None
    
    def get_all_nodes_by_type(self, node_type: str) -> list[dict]:
        """
        Get all nodes of a specific type.
        
        Args:
            node_type: One of 'department', 'faculty', 'course'
            
        Returns:
            List of node dictionaries
        """
        return [
            {'id': node_id, **attrs}
            for node_id, attrs in self.graph.nodes(data=True)
            if attrs.get('type') == node_type
        ]
    
    def get_all_departments(self) -> list[dict]:
        """Get all departments."""
        return self.get_all_nodes_by_type('department')
    
    def get_all_faculty(self) -> list[dict]:
        """Get all faculty members."""
        return self.get_all_nodes_by_type('faculty')
    
    def get_all_courses(self) -> list[dict]:
        """Get all courses."""
        return self.get_all_nodes_by_type('course')
    
    # ========== Relationship Query Methods ==========
    
    def get_course_by_code(self, code: str) -> Optional[dict]:
        """
        Find a course by its code (e.g., 'CS101').
        
        Args:
            code: The course code
            
        Returns:
            Course dictionary or None
        """
        for course in self.get_all_courses():
            if course.get('code', '').upper() == code.upper():
                return course
        return None
    
    def get_faculty_by_name(self, name: str) -> Optional[dict]:
        """
        Find a faculty member by name (partial match).
        
        Args:
            name: Full or partial name to search
            
        Returns:
            Faculty dictionary or None
        """
        name_lower = name.lower()
        for faculty in self.get_all_faculty():
            if name_lower in faculty.get('name', '').lower():
                return faculty
        return None
    
    def get_department_by_code(self, code: str) -> Optional[dict]:
        """
        Find a department by its code (e.g., 'CS').
        
        Args:
            code: The department code
            
        Returns:
            Department dictionary or None
        """
        for dept in self.get_all_departments():
            if dept.get('code', '').upper() == code.upper():
                return dept
        return None
    
    def get_prerequisites(self, course_id: str) -> list[dict]:
        """
        Get the direct prerequisites for a course.
        
        Args:
            course_id: The course ID
            
        Returns:
            List of prerequisite course dictionaries
        """
        prereqs = []
        for _, target, data in self.graph.out_edges(course_id, data=True):
            if data.get('relation') == 'prerequisite':
                prereq_node = self.get_node(target)
                if prereq_node:
                    prereqs.append(prereq_node)
        return prereqs
    
    def get_all_prerequisites(self, course_id: str) -> list[dict]:
        """
        Get all prerequisites for a course (including transitive prerequisites).
        
        Args:
            course_id: The course ID
            
        Returns:
            List of all prerequisite course dictionaries (in topological order)
        """
        all_prereqs = set()
        queue = [course_id]
        
        while queue:
            current = queue.pop(0)
            for _, target, data in self.graph.out_edges(current, data=True):
                if data.get('relation') == 'prerequisite' and target not in all_prereqs:
                    all_prereqs.add(target)
                    queue.append(target)
        
        # Return as list of course dictionaries
        return [self.get_node(prereq_id) for prereq_id in all_prereqs if self.get_node(prereq_id)]
    
    def get_courses_by_department(self, dept_id: str) -> list[dict]:
        """
        Get all courses offered by a department.
        
        Args:
            dept_id: The department ID
            
        Returns:
            List of course dictionaries
        """
        courses = []
        for source, target, data in self.graph.in_edges(dept_id, data=True):
            if data.get('relation') == 'belongs_to':
                node = self.get_node(source)
                if node and node.get('type') == 'course':
                    courses.append(node)
        return courses
    
    def get_faculty_by_department(self, dept_id: str) -> list[dict]:
        """
        Get all faculty members in a department.
        
        Args:
            dept_id: The department ID
            
        Returns:
            List of faculty dictionaries
        """
        faculty = []
        for source, target, data in self.graph.in_edges(dept_id, data=True):
            if data.get('relation') == 'belongs_to':
                node = self.get_node(source)
                if node and node.get('type') == 'faculty':
                    faculty.append(node)
        return faculty
    
    def get_department_head(self, dept_id: str) -> Optional[dict]:
        """
        Get the head of a department.
        
        Args:
            dept_id: The department ID
            
        Returns:
            Faculty dictionary or None
        """
        for source, target, data in self.graph.in_edges(dept_id, data=True):
            if data.get('relation') == 'heads':
                return self.get_node(source)
        return None
    
    def get_courses_taught_by(self, faculty_id: str) -> list[dict]:
        """
        Get all courses taught by a faculty member.
        
        Args:
            faculty_id: The faculty ID
            
        Returns:
            List of course dictionaries
        """
        courses = []
        for _, target, data in self.graph.out_edges(faculty_id, data=True):
            if data.get('relation') == 'teaches':
                course = self.get_node(target)
                if course:
                    courses.append(course)
        return courses
    
    def get_course_instructors(self, course_id: str) -> list[dict]:
        """
        Get all faculty who teach a specific course.
        
        Args:
            course_id: The course ID
            
        Returns:
            List of faculty dictionaries
        """
        instructors = []
        for source, _, data in self.graph.in_edges(course_id, data=True):
            if data.get('relation') == 'teaches':
                faculty = self.get_node(source)
                if faculty:
                    instructors.append(faculty)
        return instructors
    
    def get_faculty_department(self, faculty_id: str) -> Optional[dict]:
        """
        Get the department a faculty member belongs to.
        
        Args:
            faculty_id: The faculty ID
            
        Returns:
            Department dictionary or None
        """
        for _, target, data in self.graph.out_edges(faculty_id, data=True):
            if data.get('relation') == 'belongs_to':
                return self.get_node(target)
        return None
    
    def get_course_department(self, course_id: str) -> Optional[dict]:
        """
        Get the department a course belongs to.
        
        Args:
            course_id: The course ID
            
        Returns:
            Department dictionary or None
        """
        for _, target, data in self.graph.out_edges(course_id, data=True):
            if data.get('relation') == 'belongs_to':
                return self.get_node(target)
        return None
    
    # ========== Advanced Query Methods ==========
    
    def get_courses_by_level(self, level: str) -> list[dict]:
        """
        Get all courses at a specific level.
        
        Args:
            level: 'undergraduate' or 'graduate'
            
        Returns:
            List of course dictionaries
        """
        return [
            course for course in self.get_all_courses()
            if course.get('level', '').lower() == level.lower()
        ]
    
    def get_faculty_by_research_area(self, area: str) -> list[dict]:
        """
        Find faculty members by research area.
        
        Args:
            area: Research area to search (partial match)
            
        Returns:
            List of faculty dictionaries
        """
        area_lower = area.lower()
        return [
            faculty for faculty in self.get_all_faculty()
            if any(area_lower in ra.lower() for ra in faculty.get('research_areas', []))
        ]
    
    def get_prerequisite_chain(self, course_id: str) -> list[list[dict]]:
        """
        Get all possible prerequisite chains (paths) to take a course.
        
        Args:
            course_id: The target course ID
            
        Returns:
            List of prerequisite chains (each chain is a list of courses)
        """
        def find_paths(current_id: str, visited: set) -> list[list[dict]]:
            prereqs = self.get_prerequisites(current_id)
            if not prereqs:
                return [[]]
            
            all_paths = []
            for prereq in prereqs:
                if prereq['id'] not in visited:
                    sub_paths = find_paths(prereq['id'], visited | {prereq['id']})
                    for path in sub_paths:
                        all_paths.append(path + [prereq])
            
            return all_paths if all_paths else [[]]
        
        paths = find_paths(course_id, {course_id})
        # Remove empty paths and duplicates
        return [path for path in paths if path]
    
    def can_take_course(self, course_id: str, completed_courses: list[str]) -> tuple[bool, list[str]]:
        """
        Check if a student can take a course given their completed courses.
        
        Args:
            course_id: The course to check
            completed_courses: List of completed course IDs
            
        Returns:
            Tuple of (can_take: bool, missing_prerequisites: list)
        """
        prereqs = self.get_prerequisites(course_id)
        missing = [
            prereq['id'] for prereq in prereqs
            if prereq['id'] not in completed_courses
        ]
        return (len(missing) == 0, missing)
    
    def get_courses_requiring(self, course_id: str) -> list[dict]:
        """
        Get all courses that have this course as a prerequisite.
        
        Args:
            course_id: The prerequisite course ID
            
        Returns:
            List of course dictionaries
        """
        courses = []
        for source, target, data in self.graph.in_edges(course_id, data=True):
            if data.get('relation') == 'prerequisite':
                course = self.get_node(source)
                if course:
                    courses.append(course)
        return courses
    
    def search_courses(self, query: str) -> list[dict]:
        """
        Search courses by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching course dictionaries
        """
        query_lower = query.lower()
        return [
            course for course in self.get_all_courses()
            if query_lower in course.get('name', '').lower()
            or query_lower in course.get('description', '').lower()
        ]
    
    def get_graph_statistics(self) -> dict:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dictionary with counts of nodes and edges by type
        """
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'departments': len(self.get_all_departments()),
            'faculty': len(self.get_all_faculty()),
            'courses': len(self.get_all_courses()),
            'prerequisites': sum(
                1 for _, _, d in self.graph.edges(data=True)
                if d.get('relation') == 'prerequisite'
            )
        }
        return stats
