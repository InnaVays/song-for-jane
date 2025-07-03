from api.llm_client import call_llm
from memory import load_past_memories

def generate_with_memory(base_prompt, is_kept=True, n=5):
    # Load both kept and meaningful rejected memories
    memories = load_past_memories(n, only_kept=is_kept, include_rejected_with_feedback=False)

    memory_str = ""
    for m in memories:
        if m['keep']:
            memory_str += f"- Jane liked: {m['output']}\n"
        elif m.get('feedback'):
            memory_str += f"- Jane rejected: {m['output']} // Feedback: {m['feedback']}\n"

    final_prompt = f"Past memory context:\n{memory_str}\nNow write a new response:\n{base_prompt}"
    
    return call_llm(final_prompt)