import urllib.request
import json
import time
import sys

prompt_id = "2b048363-0c24-47bc-a458-2bbe55572539"

print(f"Monitoring ComfyUI job {prompt_id}...")
start_time = time.time()

while True:
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}")
        data = json.loads(req.read().decode('utf-8'))
        if prompt_id in data:
            status = data[prompt_id].get("status", {})
            completed = status.get("completed", False)
            outputs = data[prompt_id].get("outputs", {})
            print(f"Job finished in {time.time() - start_time:.1f}s. Completed: {completed}")
            print("Outputs:", json.dumps(outputs, indent=2))
            break
    except Exception as e:
        print("Polling error:", e)

    time.sleep(5)
