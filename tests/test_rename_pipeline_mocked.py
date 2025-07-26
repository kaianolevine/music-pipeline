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


def test_get_metadata_invalid_extension():
    result = rename_pipeline.get_metadata("song.xyz")
    assert result is None


@patch("rename_pipeline.rename_pipeline.FLAC")
def test_get_metadata_flac(mock_flac):
    mock_audio = MagicMock()
    mock_audio.get.side_effect = lambda key, default=None: {
        "title": ["SongTitle"],
        "artist": ["ArtistName"],
        "bpm": ["125.6"],
    }.get(key, default)
    mock_flac.return_value = mock_audio

    result = rename_pipeline.get_metadata("file.flac")
    assert result == ("SongTitle", "ArtistName", "126")


def test_list_music_files():
    mock_service = MagicMock()
    mock_service.files().list.return_value.execute.return_value = {
        "files": [{"id": "123", "name": "song.mp3"}]
    }

    result = rename_pipeline.list_music_files(mock_service, "folder123")
    assert isinstance(result, list)
    assert result[0]["name"] == "song.mp3"


@patch("rename_pipeline.rename_pipeline.authenticate")
@patch("rename_pipeline.rename_pipeline.list_music_files")
@patch("rename_pipeline.rename_pipeline.download_file")
@patch("rename_pipeline.rename_pipeline.upload_file")
@patch("rename_pipeline.rename_pipeline.get_metadata")
@patch("rename_pipeline.rename_pipeline.os.rename")
def test_main_flow(
    mock_rename,
    mock_get_metadata,
    mock_upload,
    mock_download,
    mock_list_files,
    mock_auth,
):
    mock_auth.return_value = "mock_service"
    mock_list_files.return_value = [{"id": "123", "name": "song.mp3"}]
    mock_get_metadata.return_value = ("Title", "Artist", "128")

    with patch(
        "rename_pipeline.rename_pipeline.os.path.exists", return_value=True
    ), patch("rename_pipeline.rename_pipeline.open", create=True), patch(
        "rename_pipeline.rename_pipeline.os.remove"
    ):

        rename_pipeline.main()

    assert mock_auth.called
    assert mock_list_files.called
    assert mock_download.called
    assert mock_get_metadata.called
    assert mock_rename.called
    assert mock_upload.called
