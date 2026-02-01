"""
FastAPI backend for the Knowledge Base Visualizer.

Provides REST endpoints for:
- Knowledge graph data (nodes/edges for Cytoscape.js)
- Query processing with step-by-step reasoning
- Graph statistics
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from src.knowledge_graph import KnowledgeGraph
from src.reasoner import SymbolicReasoner, QueryType
from src.llm_interface import LLMInterface
from src.main import UniversityQAAgent


# Initialize FastAPI app
app = FastAPI(
    title="Neuro-Symbolic University QA Visualizer",
    description="Interactive knowledge graph and reasoning trace visualization",
    version="1.0.0"
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
kg = KnowledgeGraph()
llm_provider = os.getenv("LLM_PROVIDER", "openai")  # Default to real LLM
agent = UniversityQAAgent(llm_provider=llm_provider)


# Request/Response models
class QueryRequest(BaseModel):
    question: str


class ReasoningStep(BaseModel):
    step_number: int
    rule_name: str
    description: str
    inputs: dict
    outputs: Optional[dict] = None


class QueryResponse(BaseModel):
    success: bool
    query_type: str
    answer: str
    reasoning_steps: list[ReasoningStep]
    highlighted_entities: list[str] = []  # Entity IDs to highlight in graph
    highlighted_edges: list[str] = []  # Edge IDs to highlight (source_relation_target format)
    error: Optional[str] = None


# API Endpoints
@app.get("/api/graph")
def get_graph():
    """
    Get the full knowledge graph in Cytoscape.js format.
    
    Returns nodes and edges with styling metadata.
    """
    nodes = []
    edges = []
    
    # Add department nodes
    for dept in kg.get_all_departments():
        nodes.append({
            "data": {
                "id": dept["id"],
                "label": dept["name"],
                "code": dept["code"],
                "type": "department"
            }
        })
    
    # Add faculty nodes
    for faculty in kg.get_all_faculty():
        dept = kg.get_faculty_department(faculty["id"])
        nodes.append({
            "data": {
                "id": faculty["id"],
                "label": faculty["name"],
                "title": faculty.get("title", ""),
                "email": faculty.get("email", ""),
                "research_areas": faculty.get("research_areas", []),
                "department_id": dept["id"] if dept else None,
                "type": "faculty"
            }
        })
        # Add belongs_to edge
        if dept:
            edges.append({
                "data": {
                    "id": f"{faculty['id']}_belongs_to_{dept['id']}",
                    "source": faculty["id"],
                    "target": dept["id"],
                    "relation": "belongs_to"
                }
            })
    
    # Add course nodes
    for course in kg.get_all_courses():
        dept = kg.get_course_department(course["id"])
        nodes.append({
            "data": {
                "id": course["id"],
                "label": f"{course['code']}: {course['name']}",
                "code": course["code"],
                "name": course["name"],
                "credits": course.get("credits", 0),
                "level": course.get("level", ""),
                "description": course.get("description", ""),
                "department_id": dept["id"] if dept else None,
                "type": "course"
            }
        })
        # Add belongs_to edge
        if dept:
            edges.append({
                "data": {
                    "id": f"{course['id']}_belongs_to_{dept['id']}",
                    "source": course["id"],
                    "target": dept["id"],
                    "relation": "belongs_to"
                }
            })
    
    # Add teaches edges
    for faculty in kg.get_all_faculty():
        courses = kg.get_courses_taught_by(faculty["id"])
        for course in courses:
            edges.append({
                "data": {
                    "id": f"{faculty['id']}_teaches_{course['id']}",
                    "source": faculty["id"],
                    "target": course["id"],
                    "relation": "teaches"
                }
            })
    
    # Add prerequisite edges
    for course in kg.get_all_courses():
        prereqs = kg.get_prerequisites(course["id"])
        for prereq in prereqs:
            edges.append({
                "data": {
                    "id": f"{course['id']}_requires_{prereq['id']}",
                    "source": course["id"],
                    "target": prereq["id"],
                    "relation": "prerequisite"
                }
            })
    
    # Add heads edges
    for dept in kg.get_all_departments():
        head = kg.get_department_head(dept["id"])
        if head:
            edges.append({
                "data": {
                    "id": f"{head['id']}_heads_{dept['id']}",
                    "source": head["id"],
                    "target": dept["id"],
                    "relation": "heads"
                }
            })
    
    return {"nodes": nodes, "edges": edges}


@app.post("/api/query", response_model=QueryResponse)
def process_query(request: QueryRequest):
    """
    Process a natural language question and return reasoning trace.
    """
    try:
        response = agent.ask(request.question)
        
        # Format reasoning steps and extract entity IDs
        steps = []
        highlighted_entities = set()
        highlighted_edges = set()
        
        for i, step in enumerate(response.reasoning_result.reasoning_chain):
            outputs = step.outputs
            
            # Extract entity IDs from outputs
            _extract_entity_ids(outputs, highlighted_entities, highlighted_edges)
            
            # Convert outputs to dict if needed
            if hasattr(outputs, '__dict__'):
                outputs = outputs.__dict__
            elif isinstance(outputs, list):
                outputs = {"items": [str(o) for o in outputs[:5]]}  # Limit for display
            elif not isinstance(outputs, dict):
                outputs = {"value": str(outputs)}
            
            steps.append(ReasoningStep(
                step_number=i + 1,
                rule_name=step.rule_name,
                description=step.description,
                inputs=step.inputs or {},
                outputs=outputs
            ))
        
        # Also extract from final answer
        _extract_entity_ids(response.reasoning_result.answer, highlighted_entities, highlighted_edges)
        
        return QueryResponse(
            success=response.reasoning_result.success,
            query_type=response.reasoning_result.query_type.value,
            answer=response.answer,
            reasoning_steps=steps,
            highlighted_entities=list(highlighted_entities),
            highlighted_edges=list(highlighted_edges),
            error=response.reasoning_result.error_message
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            query_type="UNKNOWN",
            answer="",
            reasoning_steps=[],
            highlighted_entities=[],
            highlighted_edges=[],
            error=str(e)
        )


def _extract_entity_ids(data, entities: set, edges: set):
    """Recursively extract entity IDs from reasoning outputs."""
    if data is None:
        return
    
    if isinstance(data, dict):
        # Check for entity with 'id' field
        if 'id' in data:
            entities.add(data['id'])
        
        # Get course from nested 'course' field
        course_id = None
        if 'course' in data and isinstance(data['course'], dict):
            course_id = data['course'].get('id')
            if course_id:
                entities.add(course_id)
        elif 'id' in data:
            course_id = data.get('id')
        
        # Check for prerequisite relationships
        prereqs_key = 'prerequisites' if 'prerequisites' in data else 'all_prerequisites'
        if prereqs_key in data and isinstance(data[prereqs_key], list):
            for prereq in data[prereqs_key]:
                if isinstance(prereq, dict) and 'id' in prereq:
                    entities.add(prereq['id'])
                    if course_id:
                        edges.add(f"{course_id}_requires_{prereq['id']}")
        
        # Check for instructors
        if 'instructors' in data and isinstance(data['instructors'], list):
            for instructor in data['instructors']:
                if isinstance(instructor, dict) and 'id' in instructor:
                    entities.add(instructor['id'])
                    if course_id:
                        edges.add(f"{instructor['id']}_teaches_{course_id}")
        
        # Check for courses list (e.g., courses by department, courses taught by)
        if 'courses' in data and isinstance(data['courses'], list):
            for course in data['courses']:
                if isinstance(course, dict) and 'id' in course:
                    entities.add(course['id'])
        
        # Check for faculty list
        if 'faculty' in data and isinstance(data['faculty'], list):
            for fac in data['faculty']:
                if isinstance(fac, dict) and 'id' in fac:
                    entities.add(fac['id'])
        
        # Check for department
        if 'department' in data and isinstance(data['department'], dict):
            dept = data['department']
            if 'id' in dept:
                entities.add(dept['id'])
                # Add belongs_to edges for entities in this result
                if 'id' in data:
                    edges.add(f"{data['id']}_belongs_to_{dept['id']}")
        
        # Recurse into nested dicts (but skip already processed keys)
        skip_keys = {'course', 'courses', 'faculty', 'instructors', 'prerequisites', 
                     'all_prerequisites', 'department'}
        for key, value in data.items():
            if key not in skip_keys:
                _extract_entity_ids(value, entities, edges)
    
    elif isinstance(data, list):
        for item in data:
            _extract_entity_ids(item, entities, edges)


@app.get("/api/stats")
def get_stats():
    """Get knowledge graph statistics."""
    return kg.get_graph_statistics()


@app.get("/api/examples")
def get_example_questions():
    """Get example questions for the UI."""
    return {
        "examples": [
            {"category": "Simple", "question": "What is CS101?"},
            {"category": "Simple", "question": "Who is Dr. Smith?"},
            {"category": "Intermediate", "question": "What are the prerequisites for CS301?"},
            {"category": "Intermediate", "question": "Who teaches CS401?"},
            {"category": "Complex", "question": "What are ALL prerequisites for CS401?"},
            {"category": "Complex", "question": "Compare CS301 and CS401"},
            {"category": "Multi-step", "question": "Can I take CS301 if I've completed CS101?"},
            {"category": "Multi-step", "question": "List courses taught by the head of CS"},
        ]
    }


# Serve static files (visualizer frontend)
visualizer_path = os.path.join(os.path.dirname(__file__), "..", "visualizer")


@app.get("/")
def serve_frontend():
    """Serve the main visualizer page."""
    index_path = os.path.join(visualizer_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Visualizer not found. Run from project root."}


# Mount static files at root (must be after all other routes)
if os.path.exists(visualizer_path):
    app.mount("/", StaticFiles(directory=visualizer_path), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
