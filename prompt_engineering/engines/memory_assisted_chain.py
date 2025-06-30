from api.llm_client import call_llm
from memory.memory_retriever import load_past_memories

def chain_of_thought_prompt(topic):
    memory = load_past_memories(n=3)
    metaphors = "\n".join([f"- {m['output']}" for m in memory])
    prompt = f"""Past favorites:\n{memory_str}

Think about '{topic}' emotionally. First describe it as a metaphor. Then write two poetic lines using it."""
    return call_llm(prompt)
