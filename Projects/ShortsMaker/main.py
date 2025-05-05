from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import random
import time
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_random_video(strs: str = "JasonTheWeen"):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background (commented for debugging)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    print("Using webdriver-manager to install ChromeDriver")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Go to YouTube and search for streams
        driver.get(f"https://www.youtube.com/results?search_query={strs}+30+minutes")

        # Handle consent page if present
        try:
            consent_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Accept')]"))
            )
            consent_button.click()
            time.sleep(1)  # Wait for page to reload after consent
        except:
            pass  # No consent page found, proceed

        # Wait for search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )

        # Find all video elements in search results
        video_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer a#thumbnail")

        # Filter out invalid elements and get hrefs
        video_links = [elem.get_attribute("href") for elem in video_elements
                       if elem.get_attribute("href") and
                       "watch?v=" in elem.get_attribute("href")]

        if not video_links:
            return "No stream videos found in search results"

        # Pick a random video link
        random_video = random.choice(video_links)
        return random_video

    except Exception as e:
        return f"An error occurred while fetching video: {str(e)}"

    finally:
        # Clean up
        driver.quit()

# Set up API details
API_KEY = "b388e2fac8ebcb656ae108ec3c455b5f7813bd8ebd99b664fe7cfd39d67de13da2d300003f2f9189f40889c5e064e7fe1e5a1911c19027b5061f680039c7bc9b"
API_URL_GENERATE = "https://api.clipping.software/generate"
API_URL_STATUS = "https://api.clipping.software/status"

def create_clips(youtube_url, num_clips=3, video_type="Wide", captions=True):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Debug: Print headers to confirm they are set correctly
    print(f"Request headers: {headers}")

    payload = {
        "yt_link": youtube_url,
        "finalVideo_type": "Vertical",
        "numberOfClips": num_clips,
        "captions": captions,
        "captionStyle": {
            "font_size": 26,
            "vertical_position": 30,
            "border_thickness": 2
        }
    }

    # Set up retry strategy
    session = requests.Session()
    retries = Retry(total=3,  # Retry 3 times
                    backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
                    status_forcelist=[429, 500, 502, 503, 504])  # Retry on these status codes
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        print("Submitting clip generation request to Clipping.software...")
        response = session.post(API_URL_GENERATE, json=payload, headers=headers, timeout=60)  # Increased timeout to 60 seconds
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.Timeout as e:
        return f"Request timed out after 60 seconds: {str(e)}"
    except requests.exceptions.HTTPError as e:
        return f"An error occurred while generating clips: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"An error occurred while generating clips: {str(e)}"
    finally:
        session.close()

def check_status(task_id):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Debug: Print headers for status request
    print(f"Status request headers: {headers}")

    max_attempts = 100  # Maximum number of polling attempts
    polling_interval = 10  # Seconds between polling attempts

    # Set up retry strategy for status checks
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    for attempt in range(max_attempts):
        print(f"Checking task status (attempt {attempt + 1}/{max_attempts})...")
        try:
            response = session.get(f"{API_URL_STATUS}?taskID={task_id}", headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            print("Status:", data.get("status"))

            if data.get("status") == "COMPLETED":
                print("Clips generated successfully!")
                clip_urls = data.get("videoUrls", [])
                if not clip_urls:
                    return "Task completed, but no clips were generated"
                return clip_urls
            elif data.get("status") in ["FAILED", "ERROR"]:
                return f"Task failed with status: {data.get('status')}"
        except requests.exceptions.RequestException as e:
            return f"Error fetching status: {str(e)}"

        time.sleep(polling_interval)

    return "Task did not complete within the maximum number of attempts"

def download_clips(clip_urls):
    # Create a directory to store the downloaded clips
    if not os.path.exists("clips"):
        os.makedirs("clips")

    for i, clip_url in enumerate(clip_urls, 1):
        try:
            print(f"Downloading clip {i} from {clip_url}...")
            response = requests.get(clip_url, stream=True, timeout=30)
            response.raise_for_status()

            # Extract the filename from the URL or use a default name
            filename = clip_url.split("/")[-1] if "/" in clip_url else f"clip_{i}.mp4"
            filepath = os.path.join("clips", filename)

            # Download the clip
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Clip {i} downloaded successfully to {filepath}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading clip {i}: {str(e)}")

def automate_youtube_to_clips():
    # Step 1: Get a random stream video link
    search_query = input("Which One: ")
    video_link = get_random_video(search_query)
    if "error" in video_link.lower() or "no jasontheween" in video_link.lower():
        return video_link  # Return the error message if fetching fails

    print(f"Random stream video link: {video_link}")

    # Step 2: Generate clips using Clipping.software API
    response = create_clips(video_link)

    if isinstance(response, str) and "error" in response.lower():
        return response  # Return the error message if clip generation fails

    task_id = response.get("taskID")
    if not task_id:
        return "No taskID returned by the API"
    print(f"Task ID: {task_id}")

    # Step 3: Wait for the task to complete and get clip URLs
    clip_urls = check_status(task_id)
    if isinstance(clip_urls, str) and ("error" in clip_urls.lower() or "failed" in clip_urls.lower()):
        return clip_urls  # Return the error message if status checking fails

    # Step 4: Download the generated clips
    print("Generated clips:")
    for i, clip_url in enumerate(clip_urls, 1):
        print(f"Clip {i}: {clip_url}")

    download_clips(clip_urls)
    return clip_urls

if __name__ == "__main__":
    result = automate_youtube_to_clips()
    if isinstance(result, str) and "error" in result.lower():
        print(result)  # Print error message if something went wrong