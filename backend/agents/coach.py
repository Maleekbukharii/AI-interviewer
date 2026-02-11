from .base import BaseAgent

COACH_PROMPT = """
You are an Interview Coach. 
Based on the evaluator's feedback and the user's performance, provide spoken-style encouragement and a key tip for the next round.
Keep it brief and conversational, as this will be converted to speech.
"""

class Coach(BaseAgent):
    def __init__(self):
        super().__init__(system_prompt=COACH_PROMPT)

    def get_feedback(self, evaluation_summary: str):
        prompt = f"Evaluator Feedback: {evaluation_summary}\n\nProvide a brief coaching tip for the user."
        return self.chat(prompt)
