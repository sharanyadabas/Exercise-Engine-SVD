import json

with open("./backend/init.json", "r", encoding="utf-8") as openfile:
    data1 = json.load(openfile)
openfile.close()

with open("./data/gymDataset.json", "r", encoding="utf-8") as openfile:
    data2 = json.load(openfile)
openfile.close()

exercise_list1 = data1['exercises']
exercise_list2 = data2['exercises']
final_data = []

for exercise1 in exercise_list1:
    for exercise2 in exercise_list2:
        if exercise1['Title'].lower() == exercise2['Title'].lower():
            exercise1['Rating'] = exercise2['Rating']
            final_data.append(exercise2)

json_object = json.dumps(final_data, indent=2)

with open("overlapping.json", "w") as outfile:
    outfile.write(json_object)
outfile.close()