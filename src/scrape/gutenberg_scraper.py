import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
from src.utils.files import load_json, save_json

def fetch_html(url: str) -> str:
    print(f"Fetching {url} ...")
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response.text

def extract_stanzas_from_html(html: str, source_book: str) -> List[Dict]:
    soup = BeautifulSoup(html, 'html.parser')
    stanzas_data = []
    current_title = None
    current_poem = []

    for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p']):
        if elem.name in ['h1', 'h2', 'h3', 'h4']:
            # Save previous poem (if stanza count is valid)
            if current_title and 3 <= len(current_poem) <= 20:
                for i, stanza in enumerate(current_poem, start=1):
                    stanzas_data.append({
                        "title": current_title.strip(),
                        "source_book": source_book,
                        "stanza_number": i,
                        "stanza_text": stanza.strip()
                    })
            # Start new poem
            current_title = elem.get_text()
            current_poem = []
        elif elem.name == 'p':
            text = elem.get_text().strip()
            if text and len(text.split()) > 3:
                current_poem.append(text)

    # Handle the final poem
    if current_title and 3 <= len(current_poem) <= 20:
        for i, stanza in enumerate(current_poem, start=1):
            stanzas_data.append({
                "title": current_title.strip(),
                "source_book": source_book,
                "stanza_number": i,
                "stanza_text": stanza.strip()
            })

    return stanzas_data

def scrape_gutenberg_sources(source_list: str, output_file: str):
    books = load_json(source_list)
    all_poems = []

    for book in books:
        try:
            html = fetch_html(book['html_url'])
            poems = extract_stanzas_from_html(html, book['title'])
            all_poems.extend(poems)
            print(f"✅ Extracted {len(poems)} poems from '{book['title']}'")
        except Exception as e:
            print(f"❌ Failed to process {book['title']}: {e}")

    save_json(all_poems, output_file)

    print(f"\n✅ Done! Extracted {len(all_poems)} total poems.")
    print(f"Saved to {output_file}")

def main():
    scrape_gutenberg_sources(
        source_list="data/sources.json",
        output_file="data/extracted_poems.json",
    )

if __name__ == "__main__":
    main()
