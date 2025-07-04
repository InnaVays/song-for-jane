from api.llm_client import call_llm
from memory import load_past_memories, save_in_memory

def generate_chain(topic, num_ideas = 3):
    saved_metaphors = []
    while True:
        # Step 1: Get Jane’s memory
        memories = load_past_memories(n=10, only_kept=True, include_rejected_with_feedback=True)
        memory_str = ""
        for m in memories:
            if m['keep']:
                memory_str += f"- Jane liked: {m['output']}\n"
            elif m.get('feedback'):
                memory_str += f"- Jane rejected: {m['output']} // Feedback: {m['feedback']}\n"

        # Step 2: Generate N metaphors
        prompt = f"""{memory_str}
Think about '{topic}' emotionally. Suggest {num_ideas} metaphors (one per line)."""
        metaphors = call_llm(prompt)
        metaphor_lines = [line.strip("- \n") for line in metaphors.strip().split("\n") if line.strip()]

        print("\nGenerated Metaphors:")
        for i, line in enumerate(metaphor_lines, 1):
            print(f"  [{i}] {line}")

        # Step 3: User chooses one or more
        picked = input("\nEnter the numbers of metaphor you like the best! 'r' to regenerate: ").strip().lower()
        if picked == 'r':
            continue

        #kept_indexes = [int(x.strip()) for x in picked.split() if x.isdigit()]
        kept_indexes = [picked]
        kept_metaphors = [metaphor_lines[i - 1] for i in kept_indexes if 0 < i <= len(metaphor_lines)]

        if not kept_metaphors:
            print("No metaphors chosen. Let's try again.")
            continue

        # Store picked metaphors
        for metaphor in kept_metaphors:
            save_in_memory(topic, metaphor, keep=True, feedback="kept metaphor")

        saved_metaphors.extend(kept_metaphors)

        # Step 4: Choose to continue or write lyrics
        next_action = input("\nType 'write' to generate poetic lines using saved metaphors,\n"
                            "'more' to explore more metaphors,\n"
                            "or 'q' to exit: ").strip().lower()

        if next_action == 'more':
            continue
        elif next_action == 'write':
            for metaphor in saved_metaphors:
                final_prompt = f"Use this metaphor: '{metaphor}'. Write {num_ideas} poetic lines that reflect it emotionally."
                output = call_llm(final_prompt)
                print(f"\n Metaphor: {metaphor}\n {output}")
                save_in_memory(final_prompt, output, keep=True, feedback="from metaphor")
        break

