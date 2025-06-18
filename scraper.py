import re

def load_book(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_songs(raw_text):
    pattern = re.compile(r"(No\.\s*\d+\.*\s*(.*?)\n.*?)(?=No\.\s*\d+|\Z)", re.DOTALL)
    matches = pattern.findall(raw_text)
    songs = []
    for full, title in matches:
        title = title.strip() if title else "Untitled"
        songs.append({
            "title": title,
            "raw_text": full.strip()
        })
    return songs

# Function to split song into numbered choruses
def extract_chors(song_text):
    chorus_pattern = re.compile(r"\n\s*(\d+)\s*\n(.*?)(?=\n\s*\d+\s*\n|\Z)", re.DOTALL)
    matches = chorus_pattern.findall(song_text)
    return [{"chor_number": int(num), "text": stanza.strip()} for num, stanza in matches]

        }
        
# Example usage
if __name__ == "__main__":
    book_text = load_book("songs_of_the_west.txt")
    songs = split_into_songs(book_text)
    parsed_songs = [split_song(song) for song in songs]
