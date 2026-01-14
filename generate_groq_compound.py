import requests
import time
import json
from tqdm import tqdm  # Import the tqdm library
import os

INPUT_FILE_PATH = "data/prompt_data/query.jsonl"
RESULTS_PATH = "data/test_data/raw_data"
RESULTS_NAME = "groq_compound_data"
MAX_RETRIES = 5
TIMEOUT = 1200  # 20 min
SLEEP_BETWEEN_REQUESTS = 30
RETRY_SLEEP = 20

data_list = []

with open(INPUT_FILE_PATH, "r", encoding="utf-8") as file:
    for line in file:
        data_list.append(json.loads(line))

api_key = os.getenv("GROQ_API_KEY", None)
if not api_key:
    raise ValueError(f"GROQ_API_KEY value not set")

base_url = "https://api.groq.com/openai/v1/"  # Replace with your base URL
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"  # Add any required headers
}

timestamp = time.time()

os.makedirs(RESULTS_PATH, exist_ok=True)

citation_prompt = "\n\nMake sure to add a citations page at the end."

for idx, data in enumerate(tqdm(data_list)):  # Wrap your iterable with tqdm
    result = None
    count = 0
    while result is None and count <= MAX_RETRIES:
        count += 1
        time_taken = time.time()
        prompt = data["prompt"]
        data_id = data["id"]
        language = data["language"]
        json_data = {
            "model": "compound-beta",
            "messages": [{"role": "user", "content": prompt + citation_prompt}],
        }
        print(f"prompt: {json_data}")
        try:
            with requests.Session() as session:
                with session.post(
                    f"{base_url}chat/completions",
                    headers=headers,
                    json=json_data,
                    timeout=TIMEOUT,
                ) as response:
                    response.raise_for_status()
                    result = response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

        time_taken = time.time() - time_taken

        try:
            api_result = {
                "id": data_id,
                "prompt": prompt,
                "article": result["choices"][0]["message"]["content"],
                "time_taken": time_taken,
                "language": language,
            }
            with open(f"{RESULTS_PATH}/{RESULTS_NAME}_{timestamp}.jsonl", "a") as f:
                json.dump(api_result, f)
                f.write("\n")
        except (TypeError, KeyError, IndexError):
            print(f"Not result error retrying prompt {idx} for {count} time")
            result = None
            time.sleep(RETRY_SLEEP)

    time.sleep(SLEEP_BETWEEN_REQUESTS)
