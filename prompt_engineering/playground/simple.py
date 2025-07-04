from engines import generate_with_memory
from memory import save_in_memory

def run_simple():
    while True:
        prompt = input("\nEnter your poetic prompt (or type 'q' to exit): ").strip()
        if prompt.lower() in ["q", "exit"]:
            print("Goodbye, Jane.")
            break

        output = generate_with_memory(prompt)
        print(f"\nGenerated Output:\n{output}")

        choice = input("\nKeep this? (y/n): ").strip().lower()
        keep = choice == "y"

        feedback = None
        if not keep:
            feedback = input("Any feedback? (press Enter to skip): ").strip()
            if feedback == "":
                feedback = None

        if keep or feedback:
            save_in_memory(prompt, output, keep=keep, feedback=feedback)
            print("Memory saved.")