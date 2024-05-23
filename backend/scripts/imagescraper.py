import os
import requests
import json


# Function to download an image from a URL
def download_image(url, folder_path, file_name):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        with open(os.path.join(folder_path, file_name), "wb") as file:
            file.write(response.content)
        print(f"Successfully downloaded {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_name}: {e}")


# Function to download images from a list of URLs in a JSON file
def download_images_from_json(json_file_path, folder_path):
    with open(json_file_path, "r") as file:
        data = json.load(file)

    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    for exercise in data["exercises"]:
        # Download exercise image
        exercise_image_url = exercise.get("exercise_image_url")
        if exercise_image_url:
            file_name = f"{exercise['Title'].replace(' ', '_')}.gif"
            download_image(exercise_image_url, folder_path, file_name)


# Example usage
json_file_path = "backend/init.json"  # Replace with the path to your JSON file
folder_path = (
    "backend/static/images/exercises"  # Replace with the path to your download folder
)

download_images_from_json(json_file_path, folder_path)
