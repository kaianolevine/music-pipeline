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

### Run tests and check coverage

```bash
poetry run pytest --cov=rename_pipeline --cov-report=term-missing
```

### Generate HTML coverage report

```bash
poetry run coverage html
open htmlcov/index.html  # macOS
```

---

## 🧼 Code Quality

We use [pre-commit](https://pre-commit.com/) to enforce:

- `black`: auto-formatting
- `flake8`: linting

To run all hooks manually:

```bash
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
