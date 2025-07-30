import argparse
from rename_pipeline.renamer import rename_music_file
from rename_pipeline.drive_handler import download_and_rename_files_from_drive


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", help="Rename a local music file", metavar="FILE")
    parser.add_argument(
        "--output", help="Output directory for renamed file", default="."
    )
    parser.add_argument("--drive", help="Google Drive folder ID to download & rename")

    args = parser.parse_args()

    if args.local:
        renamed = rename_music_file(args.local, args.output)
        print(f"Renamed file: {renamed}")
    elif args.drive:
        download_and_rename_files_from_drive(args.drive, args.output)
    else:
        print("Please provide either --local or --drive argument.")


if __name__ == "__main__":
    main()


# def main():
#    service = authenticate()
#    files = list_music_files(service, SOURCE_FOLDER_ID)
#    for file in files:
#        original_path = file["name"]
#        local_path = f"./{original_path}"
#        download_file(service, file["id"], local_path)

#        metadata = get_metadata(local_path)
#        if metadata:
#            title, artist, bpm = metadata
#            ext = original_path.split(".")[-1]
#            new_name = f"{bpm}__{title}__{artist}.{ext}"
#            new_path = f"./{new_name}"
#            os.rename(local_path, new_path)
#            upload_file(service, new_path, DEST_FOLDER_ID)
#            print(f"Renamed and uploaded: {new_name}")
#        else:
#            print(f"Skipping: {original_path}")
