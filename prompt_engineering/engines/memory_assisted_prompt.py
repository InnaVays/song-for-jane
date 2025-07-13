from api.llm_client import call_llm
from memory import load_past_memories

def write_memory_prompt(n=10, only_kept=False):
    # Load both kept and meaningful rejected memories
    memories = load_past_memories(n=n, only_kept=only_kept)

    memory_str = ""
    for m in memories:
        if m['keep']:
            memory_str += f"- Jane liked: {m['output']}\n"

    for m in memories:
        if not m['keep'] and m.get('feedback'):
            memory_str += f"- Jane rejected: {m['output']} // Feedback: {m['feedback']}\n"   
    
    print('----------------------------------------')    
    #print(memory_str)
    #print('----------------------------------------')

    return memory_str

def generate_with_memory(bases_prompt, only_kept=False, use_memory=True):
    
    memory_str = None
    
    if use_memory: 
        memory_str = write_memory_prompt(n=10, only_kept=only_kept)
    
    prompt = f"""
{f"Below is a collection of Jane's past preferences:\n{memory_str}" if memory_str else ""}
Now, based on these, write a verse of a song, 4 lines, on the following topic:

Topic: {base_prompt}

Please write *only the lyrics* — no explanation, no commentary. Keep it aligned with Jane's tone.
"""

    return call_llm(prompt)

# TOPIC EXAMPLE: False pretenses are dinner invitations that turn into unpaid babysitting shifts.