# Song for Jane — Personal Songwriting with AI

**Song for Jane** is a DIY AI songwriting tool that helps you write lyrics and generate chord progressions tailored to your unique voice, taste, and emotional world.

This project is part of the **Make It Personal** ( https://makeitpesonal.substack.com/ ) initiative — exploring how AI can be expressive, accessible, and human-centered.

---

## Project Goals

- Let *anyone* train a lyrics model on what they love — even if they’ve never written a song.

- Create a reusable pipeline to turn text into music structure.


## Features
- Scrape Gutenberg public domail folk lyrics
- Fine-tune LoRA on personal prompts
- Generate personalized lyrics
- Evaluate with BLEU, ROUGE, METEOR, embedding similarity

## Getting Started
1. `git clone https://github.com/InnaVays/song-for-jane`
2. `cd song-for-jane`
3. `pip install -r requirements.txt`

## Run Evaluation
```bash
python src/evaluate/evaluate_outputs.py


- **Personal Lyrics Generator**  
  Fine-tunes a small language model using your own texts, poems, diary entries, or favourite songs.

- **Lyrics-to-Chords Mapper**  
  Uses a fine-tuned model to predict chord progressions with rhythm indicators.

- **Fully Customizable** 
  You can swap in your own writing, your own dataset, and even your own genre.
