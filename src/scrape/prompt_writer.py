
import random
import json
from keybert import KeyBERT
from src.utils.files import load_json, save_json

def generate_prompt(stanza_text: str, kw_model: KeyBERT, templates: list) -> str:
    keywords = kw_model.extract_keywords(stanza_text, top_n=5)
    words = [kw[0] for kw in keywords if len(kw[0]) > 2]

    if len(words) >= 3:
        theme = ', '.join(random.sample(words, 3))
    elif words:
        theme = words[0]
    else:
        theme = "feelings"

    return random.choice(templates).format(theme)

def create_prompts_from_stanzas(input_file: str, output_file: str):
    stanzas = load_json(input_file)

    # Prompt templates
    templates = [
        "Write a romantic folk-style stanza about {}.",
        "Tell a short poetic stanza involving {}.",
        "Create a poem stanza about {} with a gentle rhythm."
    ]

    # Init KeyBERT
    kw_model = KeyBERT()

    # Generate dataset
    prompt_response_data = []
    for stanza in stanzas:
        prompt = generate_prompt(stanza['stanza_text'], kw_model, templates)
        prompt_response_data.append({
            "prompt": prompt,
            "response": stanza["stanza_text"].replace("\r\n", "\n")
        })

    save_json(prompt_response_data, output_file)
    print(f"✅ Done! Saved {len(prompt_response_data)} prompts to '{output_file}'")

def main():
    create_prompts_from_stanzas(
        input_file="data/stanzas.json",
        output_file="data/love_lyrics_prompts.json",
    )

if __name__ == "__main__":
    main()