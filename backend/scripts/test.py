import json
import os

# This file checks how many exercises with ratings have a 0.0 rating

os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, "../init.json")

with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
    datalist = data['exercises']

    count = 0
    count1 = 0
    for exercise in datalist:
      if exercise.get('Desc') is None:
        count1 += 1
        if exercise['Rating'] == '0.0':
          count += 1
    print(count1)
    print(count)