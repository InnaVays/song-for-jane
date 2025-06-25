
import random
import json
from keybert import KeyBERT
from src.utils.files import load_json, save_json

stanzas = load_json("data/stanzas.json")

# Prompt templates
templates = [
    "Write a romantic folk-style stanza about {}.",
    "Tell a short poetic stanza involving {}.",
    "Create a poem stanza about {} with a gentle rhythm."
]

# Init KeyBERT
kw_model = KeyBERT()

def generate_prompt(stanza):
    keywords = kw_model.extract_keywords(stanza['stanza_text'], top_n=5)
    words = [kw[0] for kw in keywords if len(kw[0]) > 2]

    if len(words) >= 3:
        theme = ', '.join(random.sample(words, 3))
    elif words:
        theme = words[0]
    else:
        theme = "feelings"

    return random.choice(templates).format(theme)

# Generate dataset
prompt_response_data = []
for stanza in stanzas:
    prompt = generate_prompt(stanza)
    prompt_response_data.append({
        "prompt": prompt,
        "response": stanza["stanza_text"].replace("\r\n", "\n")
    })

save_json(prompt_response_data, "love_lyrics_prompts.json")

print("✅ Done! Saved as 'love_lyrics_prompts.json'")
