import re

def load_book(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def split_into_songs(text: str):
    pattern = re.compile(r'(No\.\s*\d+\.\n.*?)(?=No\.\s*\d+\.|\Z)', re.DOTALL)
    return pattern.findall(text)

def split_song(song_text: str):
    number_match = re.match(r'No\.\s*(\d+)\.', song_text)
    song_number = number_match.group(1) if number_match else 'Unknown'

    # Get optional title (first non-empty line after No.)
    lines = song_text.split('\n')
    title = next((line.strip() for line in lines[1:] if line.strip()), 'Untitled')

    # Try to find stanzas starting with "1", "2", etc.
    chorus_pattern = re.compile(r'\n\s*(\d+)\n(.*?)(?=\n\s*\d+\n|\Z)', re.DOTALL)
    matches = chorus_pattern.findall(song_text)

    if matches:
        # Format structured choruses
        choruses = [{'chor_number': num, 'text': text.strip()} for num, text in matches]
        return {
            'song_number': song_number,
            'song_title': title,
            'type': 'structured',
            'choruses': choruses
        }
    else:
        # If no structured stanzas, keep full block
        # Clean header lines
        cleaned_lines = [line for line in lines if not line.strip().startswith('No.') and line.strip()]
        return {
            'song_number': song_number,
            'song_title': title,
            'type': 'unstructured',
            'raw_text': '\n'.join(cleaned_lines).strip()
        }
        
# Example usage
if __name__ == "__main__":
    book_text = load_book("songs_of_the_west.txt")
    songs = split_into_songs(book_text)
    parsed_songs = [split_song(song) for song in songs]
