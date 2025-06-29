from api.llm_client import call_llm
from memory.memory_store import save_feedback
from memory.memory_retriever import load_past_memories

def run_interactive_session():
    print("🎤 INVENTING JANE: INTERACTIVE PROMPTING")
    prompt = input("What would you like to ask Jane to write about?\n> ")

    # Load recent memory context
    past = load_past_memories(n=3)
    if past:
        print("\n📓 Past outputs Jane liked:")
        for i, m in enumerate(past):
            print(f"{i+1}. {m['output'][:80]}...")

    # Compose final prompt
    memory_context = "\n".join([f"- {m['output']}" for m in past])
    full_prompt = f"""Jane's previous poetic outputs she liked:
{memory_context}

Now, write something new based on this prompt:
{prompt}
"""
    print("\n🤖 Generating...")
    response = call_llm(full_prompt)
    print("\n📝 LLM Response:\n")
    print(response)

    # Ask user to keep or not
    decision = input("\n💾 Do you want to KEEP this? (y/n): ").lower()
    keep = decision == "y"

    feedback = None
    if not keep:
        feedback = input("🗨️ Why not? (Optional feedback): ")

    save_feedback(prompt, response, feedback=feedback, keep=keep)

    print("\n✅ Saved to memory log.")

if __name__ == "__main__":
    while True:
        run_interactive_session()
        again = input("\n🔁 Try another? (y/n): ").lower()
        if again != "y":
            break
