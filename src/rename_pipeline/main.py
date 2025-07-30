import os
from rename_pipeline.renamer import rename_files_in_directory
from rename_pipeline.drive_handler import process_drive_folder


def main():
    mode = os.environ.get("MODE", "local").lower()
    print(f"🚀 Running in {mode.upper()} mode")

    if mode == "ci":
        folder_id = os.environ.get("FOLDER_ID")
        if not folder_id:
            raise ValueError("❌ FOLDER_ID must be set when running in CI mode.")
        process_drive_folder(folder_id)
    else:
        local_dir = os.environ.get("LOCAL_DIR", "./music")
        print(f"🎵 Renaming files in local directory: {local_dir}")
        rename_files_in_directory(local_dir)


if __name__ == "__main__":
    main()
