import os
import re
from typing import Dict
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3


def new_sanitize_filename(value):
    value = re.sub(r"[\(\[]", "_", value)
    value = re.sub(r"[\)\]]", "", value)
    value = re.sub(r"\s+", "", value)
    value = re.sub(r"[^a-zA-Z0-9_]", "", value)
    return value


def sanitize_filename(value):
    value = re.sub(r"\s+", "_", value)
    return re.sub(r"[^a-zA-Z0-9_\-]", "", value)


def new_get_metadata(file_path):
    ext = file_path.lower().split(".")[-1]
    audio = None
    if ext == "mp3":
        audio = MP3(file_path, ID3=EasyID3)
    elif ext == "flac":
        audio = FLAC(file_path)
    elif ext in ("m4a", "mp4"):
        audio = MP4(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    tags = audio.tags or {}
    artist = tags.get("artist", ["Unknown"])[0]
    title = tags.get("title", ["Unknown"])[0]
    bpm = tags.get("bpm", [""])[0]
    comment = tags.get("comment", [""])[0]

    return {
        "artist": artist,
        "title": title,
        "bpm": str(bpm),
        "comment": str(comment),
    }


def get_metadata(file_path):
    ext = file_path.lower().split(".")[-1]
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
        except (ValueError, TypeError):
            bpm = "Unknown"

        return title, artist, bpm
    except Exception as e:
        print(f"Metadata error: {e}")
        return None


def rename_music_file(file_path, output_dir):
    metadata = get_metadata(file_path)
    filename_parts = [
        metadata["bpm"],
        metadata["title"],
        metadata["artist"],
        metadata["comment"],
    ]
    cleaned_parts = [sanitize_filename(p) for p in filename_parts if p]
    new_filename = "__".join(cleaned_parts) + os.path.splitext(file_path)[1]
    new_path = os.path.join(output_dir, new_filename)
    os.rename(file_path, new_path)
    return new_path


def rename_music_files(directory):
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            metadata = get_metadata(full_path)
            if metadata:
                title, artist, bpm = metadata
                new_name = f"{bpm}__{sanitize_filename(title)}__{sanitize_filename(artist)}.mp3"
                new_path = os.path.join(directory, new_name)
                os.rename(full_path, new_path)


def rename_files_in_directory(directory: str, config: Dict) -> None:
    # logger.info(f"Scanning directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            try:
                full_path = os.path.join(root, file)
                if not os.path.isfile(full_path):
                    continue
                metadata = get_metadata(full_path)
                new_name = generate_filename(metadata, config)
                if not new_name:
                    # logger.warning(f"Skipping file due to missing metadata: {file}")
                    continue
                new_path = os.path.join(root, new_name)
                if new_path != full_path:
                    os.rename(full_path, new_path)
                    # logger.info(f"Renamed: {file} -> {new_name}")
            except Exception:  # as e:
                pass
                # logger.error(f"Failed to rename file: {file}. Error: {e}")


def generate_filename(metadata: Dict[str, str], config: Dict) -> str:
    """
    Generate a sanitized filename based on selected metadata fields and config-defined order.

    Args:
        metadata: A dictionary with keys like 'bpm', 'title', 'artist', 'comment'.
        config: A dictionary with a key 'order' specifying the field order for filenames.

    Returns:
        A string filename with sanitized fields, joined by '__', or None if required fields are missing.
    """
    filename_parts = []
    for field in config.get("order", []):
        value = metadata.get(field, "")
        if not value and field in config.get("required_fields", []):
            return None  # skip if a required field is missing
        sanitized = sanitize_filename(value)
        if sanitized:
            filename_parts.append(sanitized)
    if not filename_parts:
        return None
    return "__".join(filename_parts) + config.get("extension", ".mp3")
