import os
import re
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_PATH = "credentials.json"
SOURCE_FOLDER_ID = "YOUR_SOURCE_FOLDER_ID"
DEST_FOLDER_ID = "YOUR_DEST_FOLDER_ID"


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


def sanitize_filename(value):
    value = re.sub(r"\s+", "_", value)
    return re.sub(r"[^a-zA-Z0-9_\-]", "", value)


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


def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def list_music_files(service, folder_id):
    query = f"'{folder_id}' in parents and mimeType contains 'audio'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])


def download_file(service, file_id, dest_path):
    request = service.files().get_media(fileId=file_id)
    with open(dest_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()


def upload_file(service, filepath, folder_id):
    file_metadata = {"name": os.path.basename(filepath), "parents": [folder_id]}
    media = MediaFileUpload(filepath, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()


def main():
    service = authenticate()
    files = list_music_files(service, SOURCE_FOLDER_ID)
    for file in files:
        original_path = file["name"]
        local_path = f"./{original_path}"
        download_file(service, file["id"], local_path)

        metadata = get_metadata(local_path)
        if metadata:
            title, artist, bpm = metadata
            ext = original_path.split(".")[-1]
            new_name = f"{bpm}__{title}__{artist}.{ext}"
            new_path = f"./{new_name}"
            os.rename(local_path, new_path)
            upload_file(service, new_path, DEST_FOLDER_ID)
            print(f"Renamed and uploaded: {new_name}")
        else:
            print(f"Skipping: {original_path}")


if __name__ == "__main__":
    main()
