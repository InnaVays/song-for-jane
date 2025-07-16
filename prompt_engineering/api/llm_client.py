import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)

def call_llm(prompt, chat_history=[], model="gpt-4.1-nano", temperature=0.9, max_tokens=200):
    # Append user prompt
    chat_history.append({"role": "user", "content": prompt})
    
    # Call model with full conversation
    response = client.chat.completions.create(
        model=model,
        messages=chat_history,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # Get model reply
    reply = response.choices[0].message.content.strip()
    
    # Append model response to history
    chat_history.append({"role": "assistant", "content": reply})

    return reply