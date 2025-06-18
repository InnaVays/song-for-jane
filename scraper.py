import re

def load_book(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def split_into_songs(text: str):
    # Match starting from "No. X" and grab until the next one or end of text
    pattern = re.compile(r'(No\.\s*\d+\s+[^\n]+?\n.*?)(?=No\.\s*\d+\s+[^\n]+|\Z)', re.DOTALL)
    return pattern.findall(text)

def split_song_into_chors(song_text: str):
    title_match = re.match(r'No\.\s*(\d+)\s+(.+)', song_text.strip())
    song_number = title_match.group(1) if title_match else 'Unknown'
    song_title = title_match.group(2).split('\n')[0].strip() if title_match else 'Unknown Title'

    # Extract chorus sections
    chorus_pattern = re.compile(r'\n\s*(\d+)\n(.*?)(?=\n\s*\d+\n|\Z)', re.DOTALL)
    choruses = chorus_pattern.findall(song_text)

    structured_chors = [
        {'chor_number': number, 'text': text.strip()}
        for number, text in choruses
    ]

    return {
        'song_number': song_number,
        'song_title': song_title,
        'choruses': structured_chors
    }

# Example usage
if __name__ == "__main__":
    raw_text = load_book("songs_of_the_west.txt")
    songs = split_into_songs(raw_text)

    all_songs_data = [split_song_into_chors(song) for song in songs]

    # Print first example
    import json
    print(json.dumps(all_songs_data[0], indent=2))
