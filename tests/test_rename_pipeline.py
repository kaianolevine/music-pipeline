import pytest
from rename_pipeline import rename_pipeline

def test_sanitize_filename():
    assert rename_pipeline.sanitize_filename("Song Name (Remix)!") == "Song_Name_Remix"

def test_get_metadata_missing_file():
    result = rename_pipeline.get_metadata("nonexistent_file.mp3")
    assert result is None