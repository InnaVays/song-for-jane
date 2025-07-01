from api.llm_client import call_llm
from memory.memory_retriever import load_past_memories

def chain_of_thought_prompt(topic):
    memories = load_past_memories(n=3, only_kept=True, include_rejected_with_feedback=True)

    memory_str = ""
    for m in memories:
        if m['keep']:
            memory_str += f"- Jane liked: {m['output']}\n"
        elif m.get('feedback'):
            memory_str += f"- Jane rejected: {m['output']} // Feedback: {m['feedback']}\n"

    prompt = f"""{memory_str}
Think about '{topic}' emotionally. First describe it as a metaphor. Then write two poetic lines using that metaphor."""
    
    return call_llm(prompt)
