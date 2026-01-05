"""
University QA Agent - Main Application

This module provides the main agent that combines the LLM interface with
the symbolic reasoning engine to answer natural language questions about
the university knowledge graph.
"""

from dataclasses import dataclass
from typing import Optional

from src.knowledge_graph import KnowledgeGraph
from src.reasoner import SymbolicReasoner, ReasoningResult
from src.llm_interface import LLMInterface, ParsedQuery


@dataclass
class AgentResponse:
    """Complete response from the QA agent."""
    question: str
    answer: str
    parsed_query: ParsedQuery
    reasoning_result: ReasoningResult
    explanation: str
    
    def __str__(self) -> str:
        return f"""
{'='*60}
Question: {self.question}
{'='*60}

{self.answer}

{'─'*60}
Explanation:
{self.explanation}
{'='*60}
"""


class UniversityQAAgent:
    """
    Neuro-Symbolic QA Agent for university-related queries.
    
    This agent combines:
    1. LLM-based natural language understanding (parsing questions)
    2. Symbolic reasoning over a knowledge graph
    3. Explanation generation for transparency
    """
    
    def __init__(
        self,
        kg_path: Optional[str] = None,
        llm_provider: Optional[str] = None
    ):
        """
        Initialize the QA agent.
        
        Args:
            kg_path: Path to the knowledge graph JSON file
            llm_provider: LLM provider to use ('openai', 'gemini', 'mock')
        """
        # Initialize knowledge graph
        self.kg = KnowledgeGraph(kg_path)
        
        # Initialize symbolic reasoner
        self.reasoner = SymbolicReasoner(self.kg)
        
        # Initialize LLM interface
        if llm_provider:
            import os
            os.environ["LLM_PROVIDER"] = llm_provider
        self.llm = LLMInterface()
    
    def ask(self, question: str) -> AgentResponse:
        """
        Process a natural language question and return a complete response.
        
        Args:
            question: Natural language question about the university
            
        Returns:
            AgentResponse with answer and explanation
        """
        # Step 1: Parse the question using LLM
        parsed = self.llm.parse_question(question)
        
        # Step 2: Execute symbolic reasoning
        result = self.reasoner.execute_query(parsed.query_type, parsed.parameters)
        
        # Step 3: Generate natural language answer
        answer = self.llm.generate_answer(question, result)
        
        # Step 4: Generate reasoning explanation
        explanation = self._generate_explanation(parsed, result)
        
        return AgentResponse(
            question=question,
            answer=answer,
            parsed_query=parsed,
            reasoning_result=result,
            explanation=explanation
        )
    
    def _generate_explanation(self, parsed: ParsedQuery, result: ReasoningResult) -> str:
        """Generate a detailed explanation of the reasoning process."""
        lines = [
            "Query Understanding:",
            f"  - Interpreted as: {parsed.query_type.value}",
            f"  - Parameters: {parsed.parameters}",
            f"  - Confidence: {parsed.confidence:.0%}",
            "",
            result.get_explanation()
        ]
        return "\n".join(lines)
    
    def get_graph_stats(self) -> dict:
        """Get statistics about the knowledge graph."""
        return self.kg.get_graph_statistics()


def run_cli():
    """Run the interactive CLI interface."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║      Neuro-Symbolic University QA Agent                          ║
║      ─────────────────────────────────                          ║
║      Ask questions about courses, faculty, and departments       ║
║      Type 'help' for example questions, 'quit' to exit           ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    agent = UniversityQAAgent()
    
    stats = agent.get_graph_stats()
    print(f"Knowledge Graph loaded: {stats['courses']} courses, "
          f"{stats['faculty']} faculty, {stats['departments']} departments\n")
    
    example_questions = [
        "What are the prerequisites for CS401?",
        "Who teaches Machine Learning?",
        "List all Computer Science courses",
        "Tell me about Dr. Smith",
        "What courses require CS201?",
        "How many graduate courses are there?",
        "Compare CS301 and CS401",
        "Who is the head of the Math department?",
    ]
    
    while True:
        try:
            question = input("\n🎓 Your question: ").strip()
            
            if not question:
                continue
            
            if question.lower() == 'quit':
                print("\nGoodbye! 👋")
                break
            
            if question.lower() == 'help':
                print("\nExample questions you can ask:")
                for i, q in enumerate(example_questions, 1):
                    print(f"  {i}. {q}")
                continue
            
            if question.lower() == 'stats':
                stats = agent.get_graph_stats()
                print(f"\nKnowledge Graph Statistics:")
                for key, value in stats.items():
                    print(f"  - {key}: {value}")
                continue
            
            # Process the question
            response = agent.ask(question)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    run_cli()
