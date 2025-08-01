import os
import pytest
from rename_pipeline import drive_handler


@pytest.fixture(scope="module")
def drive_service():
    return drive_handler.authenticate()


def test_connection(drive_service):
    files = drive_service.files().list(pageSize=1).execute()
    assert "files" in files


def test_upload_and_download_file(drive_service, tmp_path):
    test_folder_id = os.getenv("TEST_DRIVE_FOLDER_ID")
    if not test_folder_id:
        pytest.skip("TEST_DRIVE_FOLDER_ID not set")

    # Create a dummy file
    test_file_path = tmp_path / "test_file.txt"
    test_file_path.write_text("Hello, Drive!")

    # Upload file
    uploaded = drive_handler.upload_file(
        drive_service, str(test_file_path), test_folder_id
    )
    assert "id" in uploaded

    # Download file
    download_path = tmp_path / "downloaded.txt"
    drive_handler.download_file(drive_service, uploaded["id"], str(download_path))

    # Verify contents
    content = download_path.read_text()
    assert content == "Hello, Drive!"

    # Clean up
    drive_service.files().delete(fileId=uploaded["id"]).execute()


def test_list_music_files(drive_service):
    test_folder_id = os.getenv("TEST_DRIVE_FOLDER_ID")
    if not test_folder_id:
        pytest.skip("TEST_DRIVE_FOLDER_ID not set")

    files = drive_handler.list_music_files(drive_service, test_folder_id)
    assert isinstance(files, list)
