from unittest.mock import patch, MagicMock
from rename_pipeline import renamer
from rename_pipeline import drive_handler


def test_sanitize_filename():
    assert renamer.sanitize_filename("Test Song!") == "Test_Song"


@patch("rename_pipeline.drive_handler.MediaIoBaseDownload")
def test_download_file(mock_downloader):
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_service.files().get_media.return_value = mock_request
    mock_downloader.return_value.next_chunk.side_effect = [(None, True)]

    with patch("builtins.open", new_callable=MagicMock):
        drive_handler.download_file(mock_service, "file123", "dummy_path")

    assert mock_downloader.return_value.next_chunk.called


@patch("rename_pipeline.drive_handler.MediaFileUpload")
def test_upload_file(mock_upload):
    mock_service = MagicMock()
    mock_service.files().create.return_value.execute.return_value = {"id": "file456"}

    drive_handler.upload_file(mock_service, "testfile.mp3", "folder123")
    assert mock_upload.called


def test_get_metadata_invalid_path():
    assert renamer.get_metadata("nonexistent.mp3") is None


def test_get_metadata_invalid_extension():
    result = renamer.get_metadata("song.xyz")
    assert result is None


@patch("rename_pipeline.renamer.FLAC")
def test_get_metadata_flac(mock_flac):
    mock_audio = MagicMock()
    mock_audio.get.side_effect = lambda key, default=None: {
        "title": ["SongTitle"],
        "artist": ["ArtistName"],
        "bpm": ["125.6"],
    }.get(key, default)
    mock_flac.return_value = mock_audio

    result = renamer.get_metadata("file.flac")
    assert result == ("SongTitle", "ArtistName", "126")


def test_list_music_files():
    mock_service = MagicMock()
    mock_service.files().list.return_value.execute.return_value = {
        "files": [{"id": "123", "name": "song.mp3"}]
    }

    result = drive_handler.list_music_files(mock_service, "folder123")
    assert isinstance(result, list)
    assert result[0]["name"] == "song.mp3"


@patch("rename_pipeline.renamer.MP4")
def test_get_metadata_mp4(mock_mp4):
    mock_audio = MagicMock()
    mock_audio.tags.get.return_value = ["123"]
    mock_audio.get.side_effect = lambda key, default=["Unknown"]: {
        "title": ["Test"],
        "artist": ["User"],
    }.get(key, default)

    mock_mp4.return_value = mock_audio

    result = renamer.get_metadata("test.m4a")
    assert result == ("Test", "User", "123")


@patch("rename_pipeline.renamer.MP3", side_effect=Exception("boom"))
def test_get_metadata_error_handling(_):
    result = renamer.get_metadata("badfile.mp3")
    assert result is None


@patch("rename_pipeline.renamer.get_metadata")
@patch("rename_pipeline.drive_handler.os.rename")
@patch("rename_pipeline.drive_handler.os.listdir", return_value=["song.mp3"])
@patch("rename_pipeline.drive_handler.os.path.isfile", return_value=True)
def test_rename_music_files(mock_isfile, mock_listdir, mock_rename, mock_get_metadata):
    mock_get_metadata.return_value = ("Title", "Artist", "100")

    # Import inside function to avoid namespace conflict
    # from rename_pipeline import renamer

    renamer.rename_music_files("/fake/dir")

    mock_rename.assert_called_once_with(
        "/fake/dir/song.mp3", "/fake/dir/100__Title__Artist.mp3"
    )
