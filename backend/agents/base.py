import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if openrouter_key:
        print("Using OpenRouter API...")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
        )
    elif api_key:
        print("Using OpenAI API...")
        return OpenAI(api_key=api_key)
    else:
        print("Warning: No API key found in environment.")
        return None

client = None
DEFAULT_MODEL = os.getenv("NVIDIA_MODEL_NAME", "nvidia/nemotron-3-nano-30b-a3b:free")

class BaseAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        global client
        if client is None:
            client = get_openai_client()

    def chat(self, user_input: str, response_model=None):
        if client is None:
            return "Error: API client not initialized. Please set OPENAI_API_KEY or OPENROUTER_API_KEY in .env"
        
        if response_model:
            try:
                # Try structured output first
                completion = client.beta.chat.completions.parse(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    response_format=response_model,
                )
                return completion.choices[0].message.parsed
            except Exception as e:
                print(f"Structured output error: {e}. Falling back to manual JSON parsing.")
                # Fallback: regular completion + manual parse
                completion = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    response_format={"type": "json_object"}
                )
                import json
                content = completion.choices[0].message.content
                return response_model.model_validate_json(content)
        else:
            completion = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )
            return completion.choices[0].message.content
