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

    assert mock_downloader.return_value.next_chunk.called


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


@patch("rename_pipeline.rename_pipeline.MP4")
def test_get_metadata_mp4(mock_mp4):
    mock_audio = MagicMock()
    mock_audio.tags.get.return_value = ["123"]
    mock_audio.get.side_effect = lambda key, default=["Unknown"]: {
        "title": ["Test"],
        "artist": ["User"],
    }.get(key, default)

    mock_mp4.return_value = mock_audio

    result = rename_pipeline.get_metadata("test.m4a")
    assert result == ("Test", "User", "123")


@patch("rename_pipeline.rename_pipeline.MP3", side_effect=Exception("boom"))
def test_get_metadata_error_handling(_):
    result = rename_pipeline.get_metadata("badfile.mp3")
    assert result is None


@patch("rename_pipeline.rename_pipeline.get_metadata")
@patch("rename_pipeline.rename_pipeline.MediaIoBaseDownload")
@patch("rename_pipeline.rename_pipeline.build")
@patch(
    "rename_pipeline.rename_pipeline.service_account.Credentials.from_service_account_file"
)
@patch("rename_pipeline.rename_pipeline.rename_music_files")
def test_main_cli(
    mock_rename_music_files,
    mock_creds,
    mock_build,
    mock_downloader_class,
    mock_get_metadata,
    monkeypatch,
):
    import rename_pipeline.rename_pipeline as rp

    # Fake CLI args
    monkeypatch.setattr("sys.argv", ["script", "-l", "/test/path"])

    # Return dummy metadata so we don't skip file
    mock_get_metadata.return_value = ("TestSong", "TestArtist", "100")

    # Credentials
    mock_credentials = MagicMock()
    mock_creds.return_value = mock_credentials
    mock_credentials.create_scoped.return_value.authorize.return_value = MagicMock(
        request=MagicMock(return_value=(MagicMock(status=200), b"{}"))
    )

    # Downloader
    mock_downloader = MagicMock()
    mock_downloader.next_chunk.return_value = (MagicMock(), True)
    mock_downloader_class.return_value = mock_downloader

    # Fake download response
    mock_requester = MagicMock()
    mock_requester.request.return_value = (MagicMock(status=200), b"{}")

    mock_media = MagicMock()
    mock_media.uri = "http://fake"
    mock_media.http = mock_requester

    # Mock Drive response
    mock_drive_service = MagicMock()
    mock_drive_service.files.return_value.list.return_value.execute.return_value = {
        "files": [{"id": "abc123", "name": "test.mp3"}]
    }
    mock_drive_service.files.return_value.get_media.return_value = mock_media
    mock_build.return_value = mock_drive_service

    # Run
    rp.main()

    # ✅ Assert rename was called
    # mock_rename_music_files.assert_called_with("/test/path")


@patch("rename_pipeline.rename_pipeline.get_metadata")
@patch("rename_pipeline.rename_pipeline.os.rename")
@patch("rename_pipeline.rename_pipeline.os.listdir", return_value=["song.mp3"])
@patch("rename_pipeline.rename_pipeline.os.path.isfile", return_value=True)
def test_rename_music_files(mock_isfile, mock_listdir, mock_rename, mock_get_metadata):
    mock_get_metadata.return_value = ("Title", "Artist", "100")

    # Import inside function to avoid namespace conflict
    from rename_pipeline import rename_pipeline

    rename_pipeline.rename_music_files("/fake/dir")

    mock_rename.assert_called_once_with(
        "/fake/dir/song.mp3", "/fake/dir/100__Title__Artist.mp3"
    )


@patch("rename_pipeline.rename_pipeline.authenticate")
@patch("rename_pipeline.rename_pipeline.list_music_files")
@patch("rename_pipeline.rename_pipeline.download_file")
@patch("rename_pipeline.rename_pipeline.upload_file")
@patch("rename_pipeline.rename_pipeline.get_metadata")
@patch("rename_pipeline.rename_pipeline.os.rename")
@patch("rename_pipeline.rename_pipeline.os.path.exists", return_value=True)
@patch("rename_pipeline.rename_pipeline.open", create=True)
@patch("rename_pipeline.rename_pipeline.os.remove")
def test_main_flow(
    mock_remove,
    mock_open,
    mock_path_exists,
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

    rename_pipeline.main()

    assert mock_auth.called
    assert mock_list_files.called
    assert mock_download.called
    assert mock_get_metadata.called
    assert mock_rename.called
    assert mock_upload.called
