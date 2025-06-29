from api.llm_client import call_llm
from memory import load_past_memories

def generate_with_memory(base_prompt):
    past = load_past_memories()
    memory_str = "\n".join([f"- Jane liked: {m['output']}" for m in past])
    final_prompt = f"Past favorites:\n{memory_str}\n\nNew Prompt:\n{base_prompt}"
    return call_llm(final_prompt)