from api.llm_client import call_llm
from memory.memory_store import save_feedback
from memory.memory_retriever import load_past_memories

from engines.step1_memory_prompt import generate_with_memory
from engines.step2_prompt_loop import generate_loop
from engines.step3_chain_of_thought import chain_of_thought_prompt

def main():
    print("🎙️ Welcome to Jane's Lyric Engine 🎙️")
    print("Let's generate something beautiful... or weird... or sad - whatever Jane wants.")
    print("\nChoose a mode:")
    print("  1. simple - one-shot generation using Jane's memory")
    print("  2. loop   - generate multiple outputs and choose what you like")
    print("  3. chain  - think deeply, generate metaphors before writing")

    mode = input("\nEnter mode (simple / loop / chain): ").strip().lower()

    prompt = input("\nWhat should Jane write about today? (e.g. 'falling out of love', 'rain on concrete')\n→ ").strip()

    if mode == "simple":
        output = generate_with_memory(prompt)
        print("\n✨ Jane says:\n", output)

    elif mode == "loop":
        results = generate_loop(prompt, num_attempts=5)
        print("\n🧾 Session complete. Results saved.")

    elif mode == "chain":
        output = chain_of_thought_prompt(prompt)
        print("\n🧠 Jane reflects, then says:\n", output)

    else:
        print("⚠️ Invalid mode. Please restart and choose from: simple, loop, or chain.")

if __name__ == "__main__":
    main()
