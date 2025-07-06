from api.llm_client import call_llm
from memory import load_past_memories

def generate_with_memory(base_prompt, is_kept=False):
    # Load both kept and meaningful rejected memories
    memories = load_past_memories(n=10, only_kept=is_kept)

    memory_str = ""
    for m in memories:
        if m['keep']:
            memory_str += f"- Jane liked: {m['output']}\n"

    for m in memories:
        if not m['keep'] and m.get('feedback'):
            memory_str += f"- Jane rejected: {m['output']} // Feedback: {m['feedback']}\n"   
    
    #print('----------------------------------------')    
    #print(memory_str)
    #print('----------------------------------------')    

    final_prompt = f"""
Below is a collection of Jane's past memories and stylistic preferences:

{memory_str}

Now, based on these, write a verse of a song, 4 lines, on the following topic:

Topic: {base_prompt}

Please write *only the lyrics* — no explanation, no commentary. Keep it aligned with Jane's tone.
"""

    return call_llm(final_prompt)

# TOPIC EXAMPLE: False pretenses are dinner invitations that turn into unpaid babysitting shifts.