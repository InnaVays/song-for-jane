from engines.memory_assisted_prompt import generate_with_memory
from memory import save_in_memory

def get_user_feedback(output_text, output_idx = 0):
    print(f"\n[{output_idx}] Output:\n{output_text}\n")
    
    # Ask if user wants to keep the output
    keep_response = input("✨ Keep this output? (y/n): ").strip().lower()
    keep = keep_response == "y"

    # Ask for optional feedback
    feedback = input("📝 Leave a comment? (It helps refine your style): ").strip()
    if feedback == "":
        feedback = None

    return keep, feedback

def generate_loop(topic, num_attempts=3):

    base_prompt = f"""
Write a verse of a song, 4 lines, on the following topic:

Topic: {topic}"""

    prompt = base_prompt
    
    while True:
        generations = [generate_with_memory(prompt, only_kept=False) for _ in range(num_attempts)]
        any_kept = False
        refined_feedbacks = []

        for idx, output in enumerate(generations, 1):
            keep, feedback = get_user_feedback(output, idx)
            
            if keep or feedback:
                save_in_memory(prompt, output, keep=keep, feedback=feedback)
                any_kept = True
                print(" ✨ Lyrics saved.")
                
                # Build structured summary for next prompt
                if keep and feedback:
                    refined_feedbacks.append(f"- Output: {output}: Kept — {feedback}")
                elif keep:
                    refined_feedbacks.append(f"- Output {output}: Kept — fits tone/style.")
                elif feedback:
                    refined_feedbacks.append(f"- Output {output}: Rejected — {feedback}")
            else:
                pass

        if not any_kept:
            print("\n ❌ All outputs rejected. Generating new batch...")
            continue

        print("\n ✅ Do you want to iterate again on the same theme?")
        print("  y - yes, continue")
        print("  n - no, stop")

        cont = input(" ✨ Continue? (y/n): ").strip().lower()
        if cont == "n":
            break
        else:
            # Combine feedback into the prompt to refine
            if refined_feedbacks:
                joined_feedback = " ".join(refined_feedbacks)
                prompt = f"\n# Consider the following feedback for improvement: {joined_feedback} \n"+base_prompt
            print("\n 🔁 Running another iteration based on your feedback...\n")

    print(" 📝 Loop completed. Thank you, Jane!")
