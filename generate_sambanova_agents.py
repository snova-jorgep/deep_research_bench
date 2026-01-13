import requests
import time
import json
from tqdm import tqdm  # Import the tqdm library
import os

file_path = "data/prompt_data/query.jsonl"
data_list = []
api_key = os.getenv("SN_API_KEY", None)
print(api_key)
if not api_key:
    raise ValueError(f"SN_API_KEY value not set")

with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        data_list.append(json.loads(line))

base_url = "http://127.0.0.1:8000/api/" #"https://aiskagents-dev.cloud.snova.ai/api/"  #"https://aiskagents.cloud.snova.ai/api/"  # Replace with your base URL

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
    count=0
    while result is None and count <= 5: # 5 retries
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
                    timeout=1200  # 1200 seconds (20 minutes) timeout
                ) as response:
                    response.raise_for_status()  # Raises an HTTPError for bad responses
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
            with open(f'generate_sambanova_dec_22_data_{timestamp}.jsonl', 'a') as f:
                json.dump(api_result, f)
                f.write('\n')
        except TypeError:
            print(f"Not result error retrying prompt {idx} for {count} time")
            result=None
            time.sleep(20)