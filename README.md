
# 📄 Document Similarity Checker with Ollama AI 🤖

## 📌 Overview

This Python script automates the identification of similar documents within a Paperless NGX environment using the Ollama AI service. It fetches documents from the API, evaluates their similarity using Ollama AI, and tags duplicates accordingly. Key features include batch processing, caching, logging, and progress tracking to efficiently handle large datasets.

## ✨ Features

- **Batch Processing**: Processes documents in batches to optimize performance and reduce memory usage.
- **Caching**: Caches results of document similarity checks to avoid redundant API calls and speed up future checks.
- **Logging**: Comprehensive logging to track progress and any errors encountered during the process.
- **Progress Tracking**: Tracks progress and can resume from where it left off in case of interruptions.
- **Tagging**: Automatically tags documents as duplicates based on the similarity check results.

## 📋 Requirements

- Python 3.x
- `requests` library
- `tqdm` library

## 🛠️ Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/hendkai/paperless_find_duplicates_ollama.git
    cd paperless_find_duplicates_ollama
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## 🔧 Configuration

Before running the script, ensure you have the following configuration set up in the script:

- `API_URL`: The URL of the Paperless NGX API.
- `API_TOKEN`: Your API token for authentication.
- `OLLAMA_URL`: The URL of the Ollama AI service.
- `OLLAMA_ENDPOINT`: The endpoint for the Ollama AI similarity check.
- `DUPLICATE_TAG_ID`: The tag ID used to mark duplicate documents.
- `MODEL_NAME`: The model name to be used for the Ollama AI similarity check.

## 🚀 Usage

1. Update the configuration variables in the script with your specific values.
2. Run the script:
    ```sh
    python main.py
    ```
3. Follow the prompts to decide whether to ignore already tagged documents and confirm the processing of documents.

## 📜 Logging

The script logs important information and errors to a file named `processing.log`. Check this file for detailed logs of the processing.

## 🗃️ Caching

The script caches the results of the Ollama AI similarity checks in a file named `document_cache.json`. This helps speed up the process for documents that have already been checked.

## 📊 Progress Tracking

The script tracks its progress in a file named `progress.json`. This allows the script to resume from where it left off in case of interruptions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any improvements or bug fixes.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/hendkai/paperless_find_duplicates_ollama?tab=MIT-1-ov-file) file for details.
