import requests
from datetime import datetime
from tqdm import tqdm
import json
import os
import logging

# Configuration
API_URL = 'http://YOURPAPERLESSNGXSERVERHERE:8777/api'
API_TOKEN = 'YOURPAPERLESSNGXTOKENHERE'
OLLAMA_URL = 'http://YOUROLLAMASERVER:11434'
OLLAMA_ENDPOINT = '/api/generate'
PROMPT_DEFINITION = """
Please review the following document content and determine if it is similar to the previous document.
Respond strictly with "similar" or "not similar".
Content:
"""
DUPLICATE_TAG_ID = 26  # Replace with the actual tag ID for duplicates
MODEL_NAME = 'llama3'  # Replace with the actual model name to be used
CACHE_FILE = 'document_cache.json'
PROGRESS_FILE = 'progress.json'
BATCH_SIZE = 10

logging.basicConfig(filename='processing.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_documents_with_content(api_url, api_token):
    headers = {'Authorization': f'Token {api_token}'}
    params = {'page_size': 100}
    documents = []

    while True:
        response = requests.get(f'{api_url}/documents/', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        new_docs = data.get('results', [])
        documents.extend([doc for doc in new_docs if doc.get('content', '').strip()])

        if not data.get('next'):
            break
        else:
            next_page = data['next'].split('page=')[1].split('&')[0]
            params['page'] = next_page

    return documents

def get_csrf_token(session, api_url, api_token):
    headers = {'Authorization': f'Token {api_token}'}
    response = session.get(api_url, headers=headers)
    response.raise_for_status()
    csrf_token = response.cookies.get('csrftoken')
    logging.info(f"CSRF Token: {csrf_token}")
    return csrf_token

def send_to_ollama(content, ollama_url, endpoint, prompt, model):
    url = f"{ollama_url}{endpoint}"
    payload = {"model": model, "prompt": f"{prompt}{content}"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        responses = response.text.strip().split("\n")
        full_response = ""
        for res in responses:
            try:
                res_json = json.loads(res)
                if 'response' in res_json:
                    full_response += res_json['response']
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON object: {e}")
                logging.error(f"Response text: {res}")
        if "similar" in full_response.lower():
            return "similar"
        elif "not similar" in full_response.lower():
            return "not similar"
        else:
            return ''
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending request to Ollama: {e}")
        return ''

def tag_document(document_id, api_url, api_token, tag_id, csrf_token):
    headers = {
        'Authorization': f'Token {api_token}',
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    url = f'{api_url}/documents/{document_id}/'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    existing_tags = response.json().get('tags', [])
    
    if tag_id not in existing_tags:
        payload = {"tags": existing_tags + [tag_id]}
        response = requests.patch(url, json=payload, headers=headers)
        logging.info(f"Tagging Response: {response.status_code} - {response.text}")
        response.raise_for_status()
    else:
        logging.info(f"Document {document_id} already has the selected tag.")

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"last_processed_index": -1}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def process_documents_in_batches(documents, api_url, api_token, ignore_already_tagged):
    session = requests.Session()
    csrf_token = get_csrf_token(session, api_url, api_token)
    cache = load_cache()
    progress = load_progress()
    last_processed_index = progress["last_processed_index"]

    for i in tqdm(range(last_processed_index + 1, len(documents), BATCH_SIZE), desc="Processing batches", unit="batch"):
        batch = documents[i:i + BATCH_SIZE]
        for doc1 in batch:
            if ignore_already_tagged and doc1.get('tags'):
                logging.info(f"Skipping Document ID {doc1['id']} as it is already tagged.")
                continue
            for doc2 in documents[i + 1:]:
                doc_pair_key = f"{doc1['id']}-{doc2['id']}"
                if doc_pair_key in cache:
                    similarity_response = cache[doc_pair_key]
                else:
                    similarity_response = send_to_ollama(doc2['content'], OLLAMA_URL, OLLAMA_ENDPOINT, PROMPT_DEFINITION, MODEL_NAME)
                    cache[doc_pair_key] = similarity_response
                    save_cache(cache)
                logging.info(f"Ollama Response for Document ID {doc2['id']}: {similarity_response}")
                if similarity_response.lower() == 'similar':
                    try:
                        tag_document(doc2['id'], api_url, api_token, DUPLICATE_TAG_ID, csrf_token)
                        logging.info(f"Document ID {doc2['id']} tagged as duplicate.")
                    except requests.exceptions.HTTPError as e:
                        logging.error(f"Failed to tag document ID {doc2['id']} as duplicate: {e}")
        progress["last_processed_index"] = i
        save_progress(progress)

def main():
    print("Searching for documents with content...")
    documents = fetch_documents_with_content(API_URL, API_TOKEN)

    if documents:
        print(f"Found {len(documents)} documents with content.")
        for doc in documents:
            print(f"Document ID: {doc['id']}, Title: {doc['title']}")

        ignore_already_tagged = input("Do you want to ignore already tagged documents? (yes/no): ").lower() == 'yes'
        
        confirm = input("Do you want to process these documents? (yes/no): ").lower()
        
        if confirm == "yes":
            process_documents_in_batches(documents, API_URL, API_TOKEN, ignore_already_tagged)
            print("Processing completed.")
        else:
            print("Processing canceled.")
    else:
        print("No documents with content found.")

if __name__ == "__main__":
    main()
