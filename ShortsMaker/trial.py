import time
import requests

# Set up API details
API_KEY = "b388e2fac8ebcb656ae108ec3c455b5f7813bd8ebd99b664fe7cfd39d67de13da2d300003f2f9189f40889c5e064e7fe1e5a1911c19027b5061f680039c7bc9b"  # Replace with your actual API key
API_URL_GENERATE = "https://api.clipping.software/generate"
API_URL_STATUS = "https://api.clipping.software/status"


def create_clips(youtube_url, num_clips=3, video_type="Vertical", captions=True):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "yt_link": youtube_url,
        "finalVideo_type": "Vertical",
        "numberOfClips": num_clips,
        "captions": captions,
        "captionStyle": {
            "font_size": 22,
            "vertical_position": 100,
            "border_thickness": 2
        }
    }

    response = requests.post(API_URL_GENERATE, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
        return None


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


# Example usage
youtube_url = "https://www.youtube.com/watch?v=G9b7clmSd4g"
response = create_clips(youtube_url)

if response:
    task_id = response.get("taskID")
    print("Task ID:", task_id)
    check_status(task_id)
