import requests
import time
import json
from tqdm import tqdm
import os

INPUT_FILE_PATH = "data/prompt_data/query.jsonl"
RESULTS_PATH = "data/test_data/raw_data"
RESULTS_NAME = "sambanova_dev2_gptoss_data"
MAX_RETRIES = 5
TIMEOUT = 1200 # 20 min
SLEEP_BETWEEN_REQUESTS = 0
RETRY_SLEEP = 20

data_list = []
api_key = os.getenv("SAMBANOVA_API_KEY", None)

if not api_key:
    raise ValueError(f"SAMBANOVA_API_KEY value not set")

base_url = "http://127.0.0.1:8000/api/" #"https://aiskagents-dev.cloud.snova.ai/api/"  #"https://aiskagents.cloud.snova.ai/api/"  # Replace with your agents backend base URL

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"  #required headers
}

with open(INPUT_FILE_PATH, "r", encoding="utf-8") as file:
    for line in file:
        data_list.append(json.loads(line))

timestamp = time.time()

for idx, data in enumerate(tqdm(data_list)):  # Wrap iterable with tqdm
    result = None
    count=0
    while result is None and count <= MAX_RETRIES:
        count+=1
        time_taken = time.time()
        prompt = data['prompt']
        data_id = data['id']
        language = data['language']
        json_data = {
            "prompt": prompt
        }
        print(f"prompt: {json_data}")
        try:
            with requests.Session() as session:
                with session.post(
                    f"{base_url}agent/deepresearch",
                    headers=headers,
                    json=json_data,
                    timeout=TIMEOUT
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
                "article": result['result'],
                "time_taken": time_taken,
                "language": language
            }
            with open(f'{RESULTS_PATH}/{RESULTS_NAME}_{timestamp}.jsonl', 'a') as f:
                json.dump(api_result, f)
                f.write('\n')
        except TypeError:
            print(f"Not result error retrying prompt {idx} for {count} time")
            result=None
            time.sleep(RETRY_SLEEP)
    time.sleep(SLEEP_BETWEEN_REQUESTS)