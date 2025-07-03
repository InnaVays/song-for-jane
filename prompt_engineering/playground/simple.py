from engines import generate_with_memory
from memory.memory_store import save_feedback

def run_simple():
    prompt = input("Enter your poetic prompt or topic: ")
    output = generate_with_memory(prompt)

    print(f"\n Generated Output:\n{output}")

    choice = input("\nKeep this? (y/n): ").strip().lower()
    keep = choice == "y"

    feedback = None
    if not keep:
        feedback = input("Any feedback? (press Enter to skip): ").strip()
        if feedback == "":
            feedback = None

    if keep or feedback:
        save_feedback(prompt, output, keep=keep, feedback=feedback)
        print("Memory saved.")