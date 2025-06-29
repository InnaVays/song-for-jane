from api.llm_client import call_llm
from memory.memory_store import save_feedback
from memory.memory_retriever import load_past_memories

def run_interactive_session():
    print("🎤 INVENTING JANE: INTERACTIVE PROMPTING")
    prompt = input("What would you like to ask Jane to write about?\n> ")

    # Load recent memory context
    past = load_past_memories(n=10, only_kept=True)
    if past:
        print("\n📓 Jane's previous favorites:")
        for i, m in enumerate(past):
            print(f"{i+1}. {m['output'][:]}...")

    while True:
        # Compose final prompt
        memory_context = "\n".join([f"- {m['output']}" for m in past])
        full_prompt = f"""Jane's previous poetic outputs she liked:
{memory_context}

Keeping in memory Jane's style, write song verse based on this prompt:
{prompt}
"""
        print("\n🤖 Generating...")
        response = call_llm(full_prompt)
        print("\n📝 LLM Response:\n")
        print(response)

        # Ask user to keep or not
        decision = input("\n💾 Do you want to KEEP this? (y/n): ").strip().lower()

        if decision == "y":
            save_feedback(prompt, response, feedback=None, keep=True)
            print("\n✅ Saved to memory log.")
            break

        elif decision == "n":
            feedback = input("🗨️ Why not? (You can write feedback or ideas to improve):\n> ")
            save_feedback(prompt, response, feedback=feedback, keep=False)
            print("\n Saved as rejected with feedback.")
            rerun = input("\n🔁 Want to try a different version? (y/n): ").strip().lower()
            if rerun != "y":
                break  # Exit the loop if not rerunning

        else:
            print("⚠️ I didn't understand. Please type 'y' to keep, or 'n' to reject and give feedback.")


if __name__ == "__main__":
    while True:
        run_interactive_session()
        again = input("\n🔁 Try another? (y/n): ").lower()
        if again != "y":
            break
