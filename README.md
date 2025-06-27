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
- Evaluate with BLEU, ROUGE, METEOR, embedding similarity (for now)

## Getting Started
```bash
git clone https://github.com/InnaVays/song-for-jane.git
cd song-for-jane
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
import nltk
nltk.download('wordnet')
nltk.download('punkt')
```

## Run Demo
```bash
python run_demo.py
```

- **Personal Lyrics Generator**  
  LoRa Fine-tunes a small language model using your own texts, poems, diary entries, or favourite songs.

- **Lyrics-to-Chords Mapper**  
  Uses a fine-tuned model to predict chord progressions with rhythm indicators.

- **Fully Customizable** 
  You can swap in your own writing, your own dataset