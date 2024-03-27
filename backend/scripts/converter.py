import json

with open("complete_exercises.json", "r", encoding="utf-8") as openfile:
    data = json.load(openfile)
openfile.close()

new_exercise = []
for exercise in data:
    if not exercise["description"].strip():
        continue
    new_exercise.append(exercise)


json_object = json.dumps(new_exercise, indent=2)

with open("newDataset.json", "w") as outfile:
    outfile.write(json_object)
outfile.close()
