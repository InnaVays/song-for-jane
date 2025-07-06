from engines.memory_assisted_prompt import generate_with_memory
from memory import save_in_memory

def generate_loop(prompt, num_attempts=3, is_kept=False):    
    generations = [generate_with_memory(prompt, is_kept=is_kept) for _ in range(num_attempts)]
    results = []

    for idx, output in enumerate(generations, 1):

        print(f"\n[{idx}] Output:\n{output}\n")

        print("\n ✨ Please respond with:")
        print("  y - to keep")
        print("  c - to reject and give feedback (If you give a comment, it will help to personalize style.)")

        response = input(f"\n ✨ Do you want to keep output [{idx}]? (y/c): ").strip().lower()
        print(response)

        keep = response == "y"
        feedback = None

        if response == "c":
            feedback = input(" ✨ Enter your comment: ").strip()
            print(feedback)
            if feedback == "":
                feedback = None

        # Only save if kept or feedback is provided
        if keep or feedback:
            save_in_memory(prompt, output, keep=keep, feedback=feedback)
            print(' ✨ Lyrics saved.')

        else:
            print(' ✨ Lyrics no saved.')