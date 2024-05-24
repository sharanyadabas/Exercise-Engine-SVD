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
    datalist = data["exercises"]

    count = 0
    muscleSet = set()
    equipmentSet = set()
    for exercise in datalist:
        count += 1
        print(exercise["Title"] + " " + str(count) + "/ 214")
        for muscle in exercise["muscle-group"]:
            muscleSet.add(muscle)
        for equipment in exercise["equipment"]:
            equipmentSet.add(equipment)

output_data = {"muscle_groups": list(muscleSet), "equipment": list(equipmentSet)}

# Specify the path for the output JSON file
output_json_file_path = os.path.join(current_directory, "../exercise_info.json")

# Write the output data to the JSON file
with open(output_json_file_path, "w", encoding="utf-8") as output_file:
    json.dump(output_data, output_file, indent=4)
