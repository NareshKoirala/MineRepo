import time
import requests

# Set up API details
API_KEY = "b388e2fac8ebcb656ae108ec3c455b5f7813bd8ebd99b664fe7cfd39d67de13da2d300003f2f9189f40889c5e064e7fe1e5a1911c19027b5061f680039c7bc9b"
API_URL_STATUS = "https://api.clipping.software/status"

def check_status(task_id):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    while True:
        response = requests.get(f"{API_URL_STATUS}?taskID={task_id}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print("Status:", data.get("status"))

            if data.get("status") == "COMPLETED":
                print("Clips generated successfully!")
                print("Video URLs:", data.get("videoUrls"))
                break
            elif data.get("status") == "FAILED":
                print("Task failed.")
                break
        else:
            print("Error fetching status:", response.text)
            break

        time.sleep(10)  # Wait before checking again


task_id = input("task id: ")
check_status(task_id)
