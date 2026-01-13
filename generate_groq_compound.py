import requests
import time
import json
from tqdm import tqdm  # Import the tqdm library
import time
import os

file_path = "data/prompt_data/query.jsonl"
data_list = []

with open(file_path, "r", encoding="utf-8") as file:
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

#sample = 1

citation_prompt = "\n\nMake sure to add a citations page at the end."

for idx, data in enumerate(tqdm(data_list)):  # Wrap your iterable with tqdm
    # Your existing loop code here
    #if idx >= sample:
    #    break
    result = None
    time_taken = time.time()
    prompt = data['prompt']
    data_id = data['id']
    language = data['language']
    json_data = {
        "model": "compound-beta",
        "messages": [
        {
            "role": "user",
            "content": prompt + citation_prompt
        }
        ]
    }
    try:
        with requests.Session() as session:
            with session.post(
                f"{base_url}chat/completions",
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
        "article": result['choices'][0]['message']['content'],
        "time_taken": time_taken,
        "language": language
    }
    with open(f'generate_groq_data_{timestamp}.jsonl', 'a') as f:
        json.dump(api_result, f)
        f.write('\n')
    time.sleep(30)
