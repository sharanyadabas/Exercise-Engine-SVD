import json

with open("../backend/init.json", "r", encoding="utf-8") as openfile:
    data = json.load(openfile)
openfile.close()

for exercise in data["exercises"]:
    exercise["Rating"] = str(float(exercise["Rating"]))

json_object = json.dumps(data, indent=2)

with open("newDataset.json", "w") as outfile:
    outfile.write(json_object)
outfile.close()
