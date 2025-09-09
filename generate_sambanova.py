import requests
import time
import json
from tqdm import tqdm  # Import the tqdm library
import os

file_path = "data/prompt_data/query.jsonl"
data_list = []
api_key = os.getenv("SN_API_KEY", None)
if not api_key:
    raise ValueError(f"SN_API_KEY value not set")

with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        data_list.append(json.loads(line))

base_url = "https://aiskagents.cloud.snova.ai/api/"  # Replace with your base URL
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"  # Add any required headers
}

timestamp = time.time()

for idx, data in enumerate(tqdm(data_list)):  # Wrap your iterable with tqdm
    # Your existing loop code here
    # if idx >= sample:
    #     break
    result = None
    time_taken = time.time()
    prompt = data['prompt']
    data_id = data['id']
    language = data['language']
    json_data = {
        "prompt": prompt
    }
    try:
        with requests.Session() as session:
            with session.post(
                f"{base_url}agent/deepresearch",
                headers=headers,
                json=json_data,
                timeout=1200  # 1200 seconds (20 minutes) timeout
            ) as response:
                response.raise_for_status()  # Raises an HTTPError for bad responses
                result = response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    time_taken = time.time() - time_taken

    api_result = {
        "id": data_id, 
        "prompt": prompt, 
        "article": result['result'],
        "time_taken": time_taken,
        "language": language
    }
    with open(f'generate_sambanova_data_{timestamp}.jsonl', 'a') as f:
        json.dump(api_result, f)
        f.write('\n')