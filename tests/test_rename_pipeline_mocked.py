from unittest.mock import patch, MagicMock
from rename_pipeline import rename_pipeline


def test_sanitize_filename():
    assert rename_pipeline.sanitize_filename("Test Song!") == "Test_Song"


@patch("rename_pipeline.rename_pipeline.MediaIoBaseDownload")
def test_download_file(mock_downloader):
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_service.files().get_media.return_value = mock_request
    mock_downloader.return_value.next_chunk.side_effect = [(None, True)]

    with patch("builtins.open", new_callable=MagicMock):
        rename_pipeline.download_file(mock_service, "file123", "dummy_path")
    assert mock_downloader.called


@patch("rename_pipeline.rename_pipeline.MediaFileUpload")
def test_upload_file(mock_upload):
    mock_service = MagicMock()
    mock_service.files().create.return_value.execute.return_value = {"id": "file456"}

    rename_pipeline.upload_file(mock_service, "testfile.mp3", "folder123")
    assert mock_upload.called


def test_get_metadata_invalid_path():
    assert rename_pipeline.get_metadata("nonexistent.mp3") is None
