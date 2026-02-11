from .base import BaseAgent
from ..schemas import Evaluation

EVALUATOR_PROMPT = """
You are an expert Interview Evaluator. 
Analyze the user's answer based on the question asked.
Provide a structured evaluation in JSON format including:
- technical_score (0-100)
- clarity_score (0-100)
- structure_score (0-100)
- confidence_score (0-100)
- professionalism_score (0-100): Evaluate if the tone and content are appropriate for a professional interview.
- strengths (short summary)
- weaknesses (short summary)
- improvement_plan (actionable steps)

If the answer is completely out of context, rude, or unprofessional, give a low professionalism score and mention it in the weaknesses.
Be objective and critical.
"""

class Evaluator(BaseAgent):
    def __init__(self):
        super().__init__(system_prompt=EVALUATOR_PROMPT)

    def evaluate_answer(self, question: str, answer: str):
        prompt = f"Question: {question}\nUser Answer: {answer}\n\nPlease evaluate this response."
        return self.chat(prompt, response_model=Evaluation)
