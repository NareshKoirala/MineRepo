from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Define URLs and credentials
base_url = "https://rugame.axonify.com"
username = "chelseanaresh10@gmail.com"
password = "Swiss1925"

try:
    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Navigate to the page
    driver.get(base_url)

    # Wait for elements to be present (timeout after 10 seconds)
    wait = WebDriverWait(driver, 100)

    # Find and fill username
    username_field = wait.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username_field.send_keys(username)

    # Find and fill password
    password_field = wait.until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    password_field.send_keys(password)

    # Optional: Add login button click if needed
    login_button = wait.until(
        EC.element_to_be_clickable((By.ID, "login-bottom"))
    )
    login_button.click()


except TimeoutException:
    print("Error: Elements took too long to load")
except NoSuchElementException:
    print("Error: Could not find username or password fields")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
finally:
    # Uncomment to close browser automatically
    # driver.quit()
    print("Browser closed")