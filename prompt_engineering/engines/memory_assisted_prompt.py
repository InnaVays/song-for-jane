from api.llm_client import call_llm
from memory import load_past_memories
from string import Template

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
    
    return memory_str

def generate_with_memory(
    base_prompt: str,
    task_instruction: str = "Write an output based on the topic.",
    output_format: str = "text only",
    only_kept: bool = False,
    use_memory: bool = True,
    n_memory: int = 10,
):
    """
    Generates a prompt using memory and task-specific instructions, then calls the LLM.

    Parameters:
        base_prompt (str): The main topic or idea.
        task_instruction (str): Instructions for the LLM on what to generate.
        output_format (str): How the output should be formatted (e.g., "text only", "bullet points").
        only_kept (bool): If True, include only previously accepted completions in memory.
        use_memory (bool): Whether to include memory-based context.
        n_memory (int): How many memory items to include.
    """

    memory_str = None
    if use_memory:
        memory_str = write_memory_prompt(n=n_memory, only_kept=only_kept)

    # Use Template for clarity and future extensibility
    prompt_template = Template("""
$memory_section

Now, based on previous past preferences or examples, perform the following task:

Task: $task_instruction  
Topic: $topic

Please output $output_format. Do not include explanations or comments.
""")

    # Memory section formatting
    memory_section = (
        f"Below is a collection of past preferences or examples:\n{memory_str}"
        if memory_str else ""
    )

    final_prompt = prompt_template.substitute(
        memory_section=memory_section.strip(),
        task_instruction=task_instruction.strip(),
        topic=base_prompt.strip(),
        output_format=output_format.strip()
    )

    return call_llm(final_prompt)
