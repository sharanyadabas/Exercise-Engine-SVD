import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)  # Setting up WebDriverWait

# Load JSON data
with open("../practice.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Filter for exercises that have ratings
rated_exercises = [exercise for exercise in data["exercises"] if "Rating" in exercise]

# Find YouTube links for each rated exercise
for exercise in rated_exercises:
    search_query = exercise["Title"]
    driver.get(
        "https://www.youtube.com/results?search_query=bodybuilding.com " + search_query
    )

    try:
        link_webelement = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a#video-title"))
        )
        exercise["YouTubeLink"] = link_webelement.get_attribute("href")
    except Exception as e:
        print(f"Error finding video for '{search_query}': {e}")
        exercise["YouTubeLink"] = None  # Append None if no link found

# Save updated data back to JSON file
with open("../updated_init.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=1)

driver.quit()  # Make sure to close the driver
