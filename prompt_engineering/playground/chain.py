from engines. import chain_of_thoughts
from memory import save_feedback

def run_chain():
    print("\n Chain Mode: Guided emotional/metaphoric writing ")
    while True:
        topic = input("\nWhat do you want Jane to write about? (or type 'q' to exit): ").strip()
        if topic.lower() in ["q", "exit"]:
            print("Goodbye, Jane.")
            break

        output = chain_of_thought_prompt(topic)
        print(f"\nGenerated Output:\n{output}")

        choice = input("\nKeep this? (y/n): ").strip().lower()
        keep = choice == "y"

        feedback = None
        if not keep:
            feedback = input("Any feedback? (press Enter to skip): ").strip()
            if feedback == "":
                feedback = None

        if keep or feedback:
            save_feedback(topic, output, keep=keep, feedback=feedback)
            print("Memory saved.")