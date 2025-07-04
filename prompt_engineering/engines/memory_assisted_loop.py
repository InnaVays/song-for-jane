from engines.memory_assisted_prompt import generate_with_memory
from memory import save_in_memory

def generate_loop(prompt, num_attempts=5, is_kept=True):    
    generations = [generate_with_memory(prompt, is_kept=is_kept) for _ in range(num_attempts)]
    results = []

    for idx, output in enumerate(generations, 1):
        print(f"\n[{idx}] Output:\n{output}\n")

    print("\nPlease respond with:")
    print("  y - to keep")
    print("  n - to reject")
    print("  c - to reject and give feedback")
    print("  (If you give a comment, it will help personalize Jane's style.)")

    for idx, output in enumerate(generations, 1):
        response = input(f"\nDo you want to keep output [{idx}]? (y/n/c): ").strip().lower()

        keep = response == "y"
        feedback = None

        if response == "c":
            feedback = input("Enter your comment: ").strip()
            if feedback == "":
                feedback = None

        # Only save if kept or feedback is provided
        if keep or feedback:
            save_feedback(prompt, output, keep=keep, feedback=feedback)

        results.append((output, keep, feedback))

    return results
