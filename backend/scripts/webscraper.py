from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time

driver = webdriver.Chrome()
all_exercise_data = []
complete_exercise_data = []
num_pages = 80
counter = 1
total_exercises = 1200

try:
    for page in range(1, num_pages):
        url = (
            "https://fitnessprogramer.com/exercises/"
            if page == 1
            else f"https://fitnessprogramer.com/exercises/page/{page}/"
        )
        driver.get(url)
        time.sleep(2)  # Wait for page to load

        exercises = driver.find_elements(By.CSS_SELECTOR, ".exercise_list article")
        exercise_urls = [
            exercise.find_element(
                By.CSS_SELECTOR, ".main_info h2.title a"
            ).get_attribute("href")
            for exercise in exercises
        ]

        for exercise_url in exercise_urls:
            driver.get(exercise_url)
            time.sleep(2)  # Wait for page to load

            # Description
            description_elements = driver.find_elements(
                By.CSS_SELECTOR, ".wpb_wrapper p"
            )
            description = (
                " ".join([p.text for p in description_elements])
                if description_elements
                else None
            )

            # Page Text
            body_element = driver.find_element(By.TAG_NAME, "body")
            page_text = (
                body_element.text.replace("\n", " ")
                .replace("\r", " ")
                .replace("\t", " ")
                .replace("\u2019", "'")
                if body_element
                else None
            )

            # Title
            title_element = driver.find_element(By.CSS_SELECTOR, "h1.page_title")
            title = title_element.text if title_element else None

            # Instructions
            ordered_lists = driver.find_elements(By.CSS_SELECTOR, "ol")
            instruction_elements = (
                ordered_lists[0].find_elements(By.TAG_NAME, "li")
                if len(ordered_lists) > 0
                else None
            )
            instructions = (
                {
                    index + 1: element.text
                    for index, element in enumerate(instruction_elements)
                }
                if instruction_elements
                else None
            )

            # Primary Muscles
            muscle_elements = driver.find_elements(By.CSS_SELECTOR, ".vc_label")
            primary_muscles = (
                [muscle.text for muscle in muscle_elements] if muscle_elements else None
            )
            if primary_muscles:
                primary_muscles = [
                    item.split(" - ")[1] if " - " in item else item
                    for item in primary_muscles
                ]

            # Equipment
            ul_element = driver.find_element(
                By.CSS_SELECTOR, ".spec_group.equipments .group-content ul"
            )
            li_elements = (
                ul_element.find_elements(By.TAG_NAME, "li") if ul_element else None
            )
            equipment = (
                [li.find_element(By.TAG_NAME, "span").text for li in li_elements]
                if li_elements
                else None
            )

            # Images
            image_elements = driver.find_elements(By.TAG_NAME, "img")
            second_image_url = (
                image_elements[1].get_attribute("src")
                if len(image_elements) >= 2
                else None
            )
            third_image_url = (
                image_elements[2].get_attribute("src")
                if len(image_elements) >= 3
                else None
            )

            exercise_data = {
                "title": title,
                "description": description,
                "instructions": instructions,
                "muscle-group": primary_muscles,
                "equipment": equipment,
                "exercise_image_url": second_image_url,
                "muscle_image_url": third_image_url,
                "all-text": page_text,
            }
            if description is not None:
                complete_exercise_data.append(exercise_data)
            all_exercise_data.append(exercise_data)
            print(f"{title} ({description is not None}): {counter} / {total_exercises}")
            counter += 1


finally:
    driver.quit()

# Output and JSON Conversion
print(
    "number of exercises in complete_exercises_data: "
    + str(len(complete_exercise_data))
)
print("number of exercises in all_exercises_data: " + str(len(all_exercise_data)))

all_json_data = json.dumps(all_exercise_data, indent=4)
with open("all_exercises.json", "w") as file:
    file.write(all_json_data)

complete_json_data = json.dumps(complete_exercise_data, indent=4)
with open("complete_exercises.json", "w") as file:
    file.write(complete_json_data)
