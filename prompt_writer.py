
import random
import json
from keybert import KeyBERT

# Load your data from JSON
with open("stranzas.json", "r") as f:
    stanzas = json.load(f)

stanzas = stanzas[0:10]

# Prompt templates
templates = [
    "Write a romantic folk-style '{}' stanza about {}.",
    "Tell a short poetic story '{}' involving {}.",
    "Create a poem '{}' about {} with a gentle rhythm."
]

# Init KeyBERT
kw_model = KeyBERT()

def generate_prompt(stanza):
    keywords = kw_model.extract_keywords(stanza['stanza_text'], top_n=5)
    words = [kw[0] for kw in keywords if len(kw[0]) > 2]

    if len(words) >= 2:
        theme = ', '.join(random.sample(words, 5))
    elif words:
        theme = words[0]
    else:
        theme = "romantic feelings"

    return random.choice(templates).format(stanza['title'],theme)

# Generate dataset
prompt_response_data = []
for stanza in stanzas:
    prompt = generate_prompt(stanza)
    prompt_response_data.append({
        "prompt": prompt,
        "response": stanza["stanza_text"].replace("\r\n", "\n")
    })

# Save for LoRA finetuning
with open("love_lyrics_prompts.json", "w") as f:
    json.dump(prompt_response_data, f, indent=2)

print("✅ Done! Saved as 'love_lyrics_prompts.json'")
