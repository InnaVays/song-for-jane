from engines import generate_with_memory
from memory import save_in_memory

def run_simple():
    
    while True:
        prompt = input("\n ✨ Enter your poetic prompt (or type 'q' or 'exit'): ").strip()
        print("Jane says: "+prompt)


        if prompt.lower() in ["q", "exit"]:
            print(" ✨ Goodbye, Jane.")
            break

        if prompt == '':
            print("\n ✨ You didn't give a topic, Jane! Let me surprise you! ")
            prompt = 'Hippopotamus meets a badger'

        output = generate_with_memory(prompt, is_kept=True)
        print(f"\n ✨ Generated Output:\n{output}")
        print("\n ✨ Please respond with:")
        print("  y - to keep")
        print("  n - to reject")
        print("  c - to reject and give feedback (If you give a comment, it will help to personalize style.)")

        response = input("\nKeep this? (y/n/c): ").strip().lower()
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

            

        
