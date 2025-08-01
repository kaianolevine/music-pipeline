# 🎵 music-pipeline

A Python utility to rename and organize music files using metadata. Designed for DJs, archivists, or enthusiasts maintaining large audio collections.

---

## 🚀 Features

- Renames `.mp3`, `.mp4`, `.m4a`, `.flac` files using embedded metadata.
- Customizable filename templates via `config.json`.
- Cleans special characters and formatting.
- Supports recursive renaming in nested folders.
- Fully tested with `pytest` and `unittest.mock`.
- Pre-commit hooks with `black` and `flake8`.

---

## 🔧 Developer Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/music-pipeline.git
cd music-pipeline
```

### 2. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Then activate the shell:

```bash
poetry shell
```

### 3. Install dependencies

```bash
poetry install
```

### 4. Install pre-commit hooks

```bash
poetry run pre-commit install
```

---

## 🛠️ Usage

### Run the pipeline

```bash
poetry run python -m rename_pipeline.rename_pipeline <input_folder> <output_folder>
```

Example:

```bash
poetry run python -m rename_pipeline.rename_pipeline ./raw_audio ./renamed_audio
```

If no output folder is specified, renamed files will be saved in-place.

---

## 🧪 Testing

### 🧪 Running Tests

```bash
poetry run pytest
```

### With coverage

```bash
poetry run pytest --cov=rename_pipeline --cov-report=html
```

### To erase coverage data:

```bash
poetry run coverage erase
```

---

## 🧼 Code Quality

We use [pre-commit](https://pre-commit.com/) to enforce:

- `black`: auto-formatting
- `flake8`: linting

Install and run all pre-commit hooks:

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

---

## 🧾 Config Example (`config.json`)

```json
{
  "filename_fields": ["bpm", "song", "artist"],
  "include_subdirectories": true
}
```

---

## 💡 Tips

- Only `.mp3`, `.m4a`, `.mp4`, `.flac` files are supported.
- Missing or corrupt metadata will be skipped unless handled explicitly.
- You can mock metadata in tests to simulate edge cases.

---

## 🚀 GitHub Actions Integration for Google Drive Testing

To enable integration testing of Google Drive functionality in CI:

### 🔐 Required Secrets

Go to your GitHub repository → Settings → Secrets and Variables → Actions, and add the following:

#### Option 1 (Raw JSON)

- **Name**: `GOOGLE_SERVICE_ACCOUNT_JSON`
- **Value**: Paste the full raw JSON content of your service account key.

#### Option 2 (Recommended - Base64-encoded)

- **Name**: `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`
- **Value**: Base64-encoded service account JSON (safer for multiline content).

To encode:

```bash
base64 -i credentials.json | pbcopy  # macOS
base64 -w 0 credentials.json | xclip # Linux
```

Then decode it in your script:

```python
import os, json, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

def authenticate():
    encoded = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64")
    if encoded:
        info = json.loads(base64.b64decode(encoded).decode("utf-8"))
    else:
        info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))

    creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=creds)
```

#### (Optional) Google Drive Folder for Tests

- **Name**: `TEST_DRIVE_FOLDER_ID`
- **Value**: A folder ID in Drive that the service account has write access to.

Tests that upload or download files will use this folder if present.

---
