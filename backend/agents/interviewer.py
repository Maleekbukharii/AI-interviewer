from .base import BaseAgent

INTERVIEWER_PROMPT = """
You are Jon, a professional technical and HR interviewer. 
Your goal is to conduct a realistic mock interview.
- Ask one question at a time.
- Keep your questions short and concise. Avoid long preambles.
- Be professional, encouraging, but rigorous.
- Follow up on the user's previous answers if necessary.
- Adapt to the company and position provided.

Start by introducing yourself briefly as Jon and asking the first question.
"""

class Interviewer(BaseAgent):
    def __init__(self):
        super().__init__(system_prompt=INTERVIEWER_PROMPT)

    def get_next_question(self, history: str, context: str):
        prompt = f"Context: {context}\n\nInterview History:\n{history}\n\nProvide the next interview question."
        return self.chat(prompt)
