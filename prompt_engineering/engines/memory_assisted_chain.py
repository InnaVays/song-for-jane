from api.llm_client import call_llm
from engines import write_memory_prompt, generate_with_memory
from memory import load_past_memories, save_in_memory

def generate_chain(topic, num_ideas=3):
    print(f"\n🎭 Prompt Chain - Jane's Song Topic: '{topic}'")

    chat_history = []

    # Step 1: Define the Emotional Core
    prompt_emotion = f"""You are Jane. You want to write a song about "{topic}".
    LET'S THINK STEP BY STEP
    STEP 1. What emotion is at the heart of this theme?"""
    emotion = call_llm(prompt_emotion, chat_history)
    print(f"\n✅ Detected Emotion: {emotion}")

    # Step 2: Generate Metaphors based on Emotion
    prompt_metaphors = f"""STEP 2. Based on the emotions uncovered, suggest {num_ideas} analogies or metaphors 
that captures this feeling and topic"""
    metaphors = call_llm(prompt_metaphors, chat_history)
    print(f"\n✅ Generated Metaphors: {metaphors}")

    while True:
        # Step 3: Generate Verse using Memory + Metaphor
        memory_str = write_memory_prompt()
        prompt_verse = f"""STEP 3. Below is a collection of Jane's past preferences:\n{memory_str}.\n
Use the metaphors created in STEP 2 to generate 4 lines of a verse about the topic.
Include subtle emotional texture reflecting emotions from STEP 1.
"""
        verse = call_llm(prompt_verse, chat_history)
        print(f"\n✅ Generated Verse:\n{verse}")

        # Step 4: Critique & Tone Adjustment
        prompt_critique = f"""Is the tone aligned with Jane's emotional state and topic? 
How well does it match Jane's style?
Suggest how the verse can be improved to make it more stylistically consistent."""
        critique = call_llm(prompt_critique, chat_history)
        print(f"\n✅ Critique Suggestion:\n{critique}")

        # Step 5: Final Choice
        keep = input("\nDo you want to keep this verse? (y/n): ").strip().lower()
        if keep == 'y':
            save_in_memory(prompt_verse, verse, keep=True, feedback="final lyrics")
            print("✅ Saved.")
        else:
            fb = input("Optional feedback to help improve styling: ").strip()
            save_in_memory(prompt_verse, verse, keep=False, feedback=fb if fb else None)
            print("✅ Feedback saved.")

        # Step 6: Loop Options
        next_step = input(
            "\nWhat would you like to do next?\n"
            "[1] Create new verse using critique\n"
            "[2] Regenerate verse with same metaphor\n"
            "[q] Exit\n"
            "Enter choice: "
        ).strip()

        if next_step == '1':
            print("\n✅ Using critique to generate a new verse...")
            improved_prompt = f"""Based on the critique:\n{critique}\n and previous feedback: \n{fb} \nGenerate a new version of the verse 
about topic "{topic}", keeping the emotion "{emotion}" and using the metaphor: "{metaphors}". 
Stay consistent with Jane's preferred lyrical style."""
            improved_prompt = f"Below is Jane’s memory:\n{memory_str}.\n" + improved_prompt
            verse = call_llm(improved_prompt, chat_history)
            print(f"\n✅ New Verse:\n{verse}")
        elif next_step == '2':
            print("\n✅ Repeating Step 3 with same metaphor...")
            continue
        else:
            print("\n✅ Exiting the chain. Thank you!")
            break