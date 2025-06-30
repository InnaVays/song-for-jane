from engines.memory_assisted_prompt import generate_with_memory

def generate_loop(prompt, num_attempts=5,is_kept=True):
    results = []
    for _ in range(num_attempts):
        output = generate_with_memory(prompt)
        print(f"\nOutput:\n{output}")
        user_input = input("Keep this? (y/n): ")
        feedback = input("Any comment? ") if user_input.lower() == 'n' else None
        from memory.memory_store import save_feedback
        save_feedback(prompt, output, feedback, keep=(user_input.lower() == 'y'))
        results.append((output, user_input, feedback))
    return results