from api.llm_client import call_llm
from engines import generate_with_memory, write_memory_prompt
from memory import load_past_memories, save_in_memory

def generate_chain(topic, num_ideas= 3):
    print(f"\n🎭 Chain of Thought — Topic: '{topic}'")
    saved_metaphor = None

    # Step 1: Metaphor generation loop
    while not saved_metaphor:
        # Construct prompt
        prompt = f"""
Think about '{topic}' and suggest {num_ideas} analogies/metaphors (one per line).
Please write *only the metaphors* — no explanation, no commentary. """
        print(prompt)

        metaphors = call_llm(prompt)
        metaphor_lines = [line.strip("- \n") for line in metaphors.strip().split("\n") if line.strip()]

        print("\n🧠 Generated Metaphors:")
        for i, line in enumerate(metaphor_lines, 1):
            print(f"  [{i}] {line}")

        # Let user choose or regenerate
        picked = input("\nPick one (number), type your own, or 'r' to regenerate: ").strip().lower()
        if picked == 'r':
            continue
        elif picked.isdigit():
            idx = int(picked)
            if 1 <= idx <= len(metaphor_lines):
                saved_metaphor = metaphor_lines[idx - 1]
            else:
                print('You have only 3! I keep the old metaphor! :-()')
        elif picked:
            saved_metaphor = picked.strip()

    print(f"\n✨ Chosen Metaphor: '{saved_metaphor}'")

    # Step 3: Ask if user wants another metaphor round or to generate lyrics
    while True:
        action = input(
            "\nWhat would you like to do next?\n"
            "  [r] Refine this metaphor (generate similar or deeper variations)\n"
            "  [g] Generate poetic lyrics from this metaphor\n"
            "  [q] Quit without generating lyrics\n"
            "Your choice (r/g/q): "
        ).strip().lower()
        
        if action == 'q':
            break
        
        elif action == 'r':
            while True:
                # Step: Generate refined metaphors based on saved metaphor
                refine_prompt = f"""The topic is '{topic}'. 
    Think about the metaphor '{saved_metaphor}' and suggest {num_ideas} analogies/metaphors (one per line), relevant to the given topic.
    Please write *only the metaphors* — no explanation, no commentary."""
                print(refine_prompt)
                refined = call_llm(refine_prompt)
                refined_lines = [line.strip("-• \n") for line in refined.strip().split("\n") if line.strip()]

                print("\n🎨 Next Round Metaphors:")
                for i, line in enumerate(refined_lines, 1):
                    print(f"  [{i}] {line}")

                picked = input("\nChoose one (number), type your own, or 'r' to regenerate: ").strip().lower()

                if picked == 'r':
                    continue  # regenerate inside refinement

                elif picked.isdigit():
                    idx = int(picked)
                    if 1 <= idx <= len(refined_lines):
                        saved_metaphor = refined_lines[idx - 1]
                        break

                elif picked:
                    saved_metaphor = picked.strip()
                    break
                print(f"\n✨ New Chosen Metaphor: '{saved_metaphor}'")

        elif action == 'g':
            break

    # Step 4: Generate lyrics and allow regeneration or saving
    while True:
        final_prompt = f"""- Topic: '{topic}'. \n- Metaphor: '{saved_metaphor}'"""
        lyrics = generate_with_memory(saved_metaphor, only_kept=False, use_memory=True)
        print(f"\n ✨ Lyrics:\n{lyrics}")

        keep = input("\nDo you want to keep this? (y/n): ").strip().lower()
        if keep == 'y':
            save_in_memory(final_prompt, lyrics, keep=True, feedback="final lyrics")
            print("✅ Saved.")
            break
        else:
            fb = input("Optional feedback to help Jane improve: ").strip()
            if fb:
                save_in_memory(final_prompt, lyrics, keep=False, feedback=fb if fb else None)
            print("🔁 Regenerating...")