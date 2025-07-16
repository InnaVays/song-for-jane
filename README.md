# Song for Jane — Personal Songwriting with AI

**Song for Jane** is a DIY AI songwriting tool that helps you write lyrics and generate chord progressions tailored to your unique voice, taste, and emotional world.

This project is part of the **Make It Personal** ( https://makeitpesonal.substack.com/ ) initiative — exploring how AI can be expressive, accessible, and human-centered.

---

## Project Goals

- Let *anyone* train a lyrics model on what they love — even if they’ve never written a song.

- Create a reusable pipeline to turn text into music structure.


## Features
- Scrape Gutenberg public domail folk songs lyrics
- Fine-tune LoRA on personal prompts
- Generate personalized lyrics
- Evaluate with BLEU, ROUGE, embedding similarity (for now)

## Getting Started
```bash
git clone https://github.com/InnaVays/song-for-jane.git
cd song-for-jane
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader 'punkt'
python -m nltk.downloader 'wordnet'

```

## Run Demo
```bash
python run_demo.py
```

---

## 🧠 Prompt Engineering Module

### Personalised Memory-Assisted Prompting

Memory-Assisted Prompting works by turning past user preferences into active context for future generations.

Every time the user keeps an output (a line, a metaphor, a verse), or rejects it with feedback, that choice is stored in memory. The next time a prompt is submitted, the system includes a short summary of those past preferences — allowing the language model to respond with content that aligns more closely with the user’s voice, style, and emotional direction.

### Available Modes:

- Simple Mode – Generate a single output using memory — including both liked and (optionally) rejected lines. Keep or reject with feedback.

- Loop Mode – Generate multiple outputs at once. Select what resonates, reject what doesn’t, and leave comments to guide Jane’s voice.

- Chain Mode – Chain of Thoughts. Iterative ideation on a chosen topic. Step by step generation.

## Try Chat (openai based)
```bash
python prompt_engineering/main.py
```
