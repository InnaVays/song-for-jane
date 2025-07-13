from api.llm_client import call_llm
from engines import write_memory_prompt
from memory import load_past_memories, save_in_memory

def generate_chain(topic, num_ideas):
    print(f"\n🎭 Prompt Chain - Jane's Song Topic: '{topic}'")

    # Step 1: Define the Emotional Core
    prompt_emotion = f"""You are Jane. You want to write a song about "{topic}". 
What emotion is at the heart of this theme? Please, only emotion, no explanation or commentary."""
    print(f"\n🧠 Emotion Identification Prompt:\n{prompt_emotion}")
    emotion = call_llm(prompt_emotion).strip()
    print(f"\n✨ Detected Emotion: {emotion}")

    # Step 2: Generate Metaphors based on Emotion
    prompt_metaphors = f"""Based on the emotion "{emotion}", suggest an analogy or metaphor 
that capture this feeling. Please, only the analogy or metaphor, no explanation or commentary."""
    print(f"\n🧠 Metaphor Generation Prompt:\n{prompt_metaphors}")
    metaphors = call_llm(prompt_metaphors)    
    print(f"\n🎨 Generated Metaphors: {metaphors}")
    
    # Step 3: Generate Verse using Memory + Metaphor
    prompt_verse = f"""Use the following metaphor: "{metaphors}" to generate 4 lines of a verse 
about the topic: "{topic}".
Include subtle emotional texture reflecting: "{emotion}".
"""
    memory_str = write_memory_prompt()
    prompt_verse = f"Below is a collection of Jane's past preferences:\n{memory_str}.\n" + prompt_verse

    print(f"\n🎼 Verse Generation Prompt:\n{prompt_verse}")
    verse = generate_with_memory(saved_metaphor, only_kept=False, use_memory=True)
    print(f"\n🎵 Generated Verse:\n{verse}")

    # Step 4: Critique & Tone Adjustment
    prompt_critique = f"""Here is a verse:\n{verse}\n\nIs the tone aligned with Jane's emotional state "{emotion}" 
and topic "{topic}"? How good it allines with Jane's style?
Suggest how the verse can be improved to make it more stylistically consistent."""
    print(f"\n🔍 Critique Prompt:\n{prompt_critique}")

    critique = call_llm(prompt_critique).strip()
    print(f"\n📝 Critique Suggestion:\n{critique}")

    # Step 5: Final Choice
    keep = input("\nDo you want to keep this verse? (y/n): ").strip().lower()
    if keep == 'y':
        save_in_memory(prompt_verse, verse, keep=True, feedback="final lyrics")
        print("✅ Saved.")
    else:
        fb = input("Optional feedback to help improve styling: ").strip()
        save_in_memory(prompt_verse, verse, keep=False, feedback=fb if fb else None)
        print("🔁 Feedback saved. You can restart the chain or tweak the metaphor.")

    return saved_metaphor, verse, critique, emotion

