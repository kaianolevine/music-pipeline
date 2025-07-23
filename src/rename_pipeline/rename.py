import os
import re
import argparse
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3

def sanitize_filename(value):
    # Remove whitespace and special characters
    value = re.sub(r'\s+', '_', value)
    value = re.sub(r'[^a-zA-Z0-9_\-]', '', value)
    return value

def get_metadata(file_path):
    ext = file_path.lower().split('.')[-1]
    try:
        if ext == "mp3":
            audio = MP3(file_path, ID3=EasyID3)
            bpm = audio.get("bpm", ["Unknown"])[0]
        elif ext in ["m4a", "mp4"]:
            audio = MP4(file_path)
            bpm = audio.tags.get("©\xa9tmp", ["Unknown"])[0]
        elif ext == "flac":
            audio = FLAC(file_path)
            bpm = audio.get("bpm", ["Unknown"])[0]
        else:
            return None

        title = audio.get("title", ["Unknown"])[0]
        artist = audio.get("artist", ["Unknown"])[0]

        title = sanitize_filename(title)
        artist = sanitize_filename(artist)

        try:
            bpm = str(round(float(bpm)))
        except:
            bpm = "Unknown"

        return title, artist, bpm
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def rename_music_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.lower().endswith((".mp3", ".m4a", ".mp4", ".flac")):
            metadata = get_metadata(file_path)
            if metadata:
                title, artist, bpm = metadata
                ext = filename.split('.')[-1]
                new_filename = f"{bpm}__{title}__{artist}.{ext}"
                new_filepath = os.path.join(directory, new_filename)
                try:
                    os.rename(file_path, new_filepath)
                    print(f"Renamed: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"Error renaming {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename music files based on metadata.")
    parser.add_argument("-l", "--location", default=".", help="Path to the directory containing music files. Defaults to current directory.")
    args = parser.parse_args()
    rename_music_files(args.location)
