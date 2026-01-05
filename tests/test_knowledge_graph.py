"""
Unit tests for the Knowledge Graph component.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge_graph import KnowledgeGraph


@pytest.fixture
def kg():
    """Create a KnowledgeGraph instance for testing."""
    return KnowledgeGraph()


class TestKnowledgeGraphBasics:
    """Test basic KnowledgeGraph functionality."""
    
    def test_load_data(self, kg):
        """Test that data is loaded correctly."""
        stats = kg.get_graph_statistics()
        assert stats['total_nodes'] > 0
        assert stats['departments'] > 0
        assert stats['courses'] > 0
        assert stats['faculty'] > 0
    
    def test_get_all_departments(self, kg):
        """Test getting all departments."""
        depts = kg.get_all_departments()
        assert len(depts) == 4  # CS, MATH, PHYS, EE
        assert all(d['type'] == 'department' for d in depts)
    
    def test_get_all_courses(self, kg):
        """Test getting all courses."""
        courses = kg.get_all_courses()
        assert len(courses) >= 18
        assert all(c['type'] == 'course' for c in courses)
    
    def test_get_all_faculty(self, kg):
        """Test getting all faculty."""
        faculty = kg.get_all_faculty()
        assert len(faculty) >= 7
        assert all(f['type'] == 'faculty' for f in faculty)


class TestCourseQueries:
    """Test course-related queries."""
    
    def test_get_course_by_code(self, kg):
        """Test finding a course by code."""
        course = kg.get_course_by_code("CS101")
        assert course is not None
        assert course['code'] == 'CS101'
        assert course['name'] == 'Introduction to Programming'
    
    def test_get_course_by_code_not_found(self, kg):
        """Test course not found case."""
        course = kg.get_course_by_code("XYZ999")
        assert course is None
    
    def test_get_prerequisites(self, kg):
        """Test getting direct prerequisites."""
        prereqs = kg.get_prerequisites("cs201")
        assert len(prereqs) == 1
        assert prereqs[0]['code'] == 'CS101'
    
    def test_get_all_prerequisites(self, kg):
        """Test getting transitive prerequisites."""
        all_prereqs = kg.get_all_prerequisites("cs401")
        prereq_codes = {p['code'] for p in all_prereqs}
        # CS401 requires CS301, MATH201, MATH401
        # CS301 requires CS201, MATH301
        # CS201 requires CS101
        # etc.
        assert 'CS101' in prereq_codes
        assert 'CS201' in prereq_codes
        assert 'CS301' in prereq_codes
    
    def test_get_courses_by_department(self, kg):
        """Test getting courses by department."""
        dept = kg.get_department_by_code("CS")
        courses = kg.get_courses_by_department(dept['id'])
        assert len(courses) >= 7
        assert all('CS' in c['code'] for c in courses)
    
    def test_get_courses_by_level(self, kg):
        """Test filtering courses by level."""
        grad_courses = kg.get_courses_by_level("graduate")
        assert len(grad_courses) > 0
        assert all(c['level'] == 'graduate' for c in grad_courses)


class TestFacultyQueries:
    """Test faculty-related queries."""
    
    def test_get_faculty_by_name(self, kg):
        """Test finding faculty by name."""
        faculty = kg.get_faculty_by_name("Smith")
        assert faculty is not None
        assert "Smith" in faculty['name']
    
    def test_get_faculty_by_department(self, kg):
        """Test getting faculty by department."""
        dept = kg.get_department_by_code("CS")
        faculty = kg.get_faculty_by_department(dept['id'])
        assert len(faculty) >= 2  # Garcia, Lee (Smith is department head)
    
    def test_get_courses_taught_by(self, kg):
        """Test getting courses taught by faculty."""
        faculty = kg.get_faculty_by_name("Smith")
        courses = kg.get_courses_taught_by(faculty['id'])
        assert len(courses) >= 3


class TestRelationships:
    """Test relationship queries."""
    
    def test_get_department_head(self, kg):
        """Test getting department head."""
        dept = kg.get_department_by_code("CS")
        head = kg.get_department_head(dept['id'])
        assert head is not None
        assert "Smith" in head['name']
    
    def test_get_course_instructors(self, kg):
        """Test getting course instructors."""
        course = kg.get_course_by_code("CS401")
        instructors = kg.get_course_instructors(course['id'])
        assert len(instructors) >= 1
    
    def test_get_courses_requiring(self, kg):
        """Test reverse prerequisite lookup."""
        course = kg.get_course_by_code("CS101")
        requiring = kg.get_courses_requiring(course['id'])
        requiring_codes = {c['code'] for c in requiring}
        assert 'CS201' in requiring_codes
    
    def test_can_take_course_satisfied(self, kg):
        """Test prerequisite check when satisfied."""
        can_take, missing = kg.can_take_course("cs201", ["cs101"])
        assert can_take is True
        assert len(missing) == 0
    
    def test_can_take_course_unsatisfied(self, kg):
        """Test prerequisite check when not satisfied."""
        can_take, missing = kg.can_take_course("cs201", [])
        assert can_take is False
        assert "cs101" in missing


class TestSearch:
    """Test search functionality."""
    
    def test_search_courses(self, kg):
        """Test course search."""
        results = kg.search_courses("algorithm")
        assert len(results) >= 1
        assert any("Algorithm" in c['name'] for c in results)
    
    def test_get_faculty_by_research_area(self, kg):
        """Test finding faculty by research area."""
        faculty = kg.get_faculty_by_research_area("Machine Learning")
        assert len(faculty) >= 1
        assert any("Smith" in f['name'] for f in faculty)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
