import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict

# Load list of books from books.json
with open("data/gutenberg_books.json", "r", encoding="utf-8") as f:
    books = json.load(f)

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


def main():
    all_poems = []
    for book in books:
        try:
            html = fetch_html(book['html_url'])
            poems = extract_stanzas_from_html(html, book['title'])
            all_poems.extend(poems)
            print(f"✅ Extracted {len(poems)} poems from '{book['title']}'")
        except Exception as e:
            print(f"❌ Failed to process {book['title']}: {e}")

    # Save to JSON
    with open("extracted_poems.json", "w", encoding="utf-8") as f:
        json.dump(all_poems, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! Extracted {len(all_poems)} total poems.")
    print("Saved to extracted_poems.json")

if __name__ == "__main__":
    main()
