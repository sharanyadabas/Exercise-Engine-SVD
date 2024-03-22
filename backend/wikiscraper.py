import json
import mediawiki
from mediawiki import MediaWiki
import time


wiki = MediaWiki()
start_time = time.time()  # track start time of program
valid_exercises = {}

with open("data/gymDataset.json", "r", encoding="utf-8") as openfile:
    data = json.load(openfile)
openfile.close()

progress = 0
total = len(data)

for exercise in data:
    progress += 1
    print(f"{progress} / {total}")
    exercise_name = exercise["Title"]
    try:
        page = wiki.page(exercise_name)
        print("Relevant article: " + str(exercise["Title"]))
        valid_exercises[exercise_name] = page.summary
        # valid_exercises[exercise_name] = page.content
    except mediawiki.PageError:
        print("No relevant article: " + str(exercise["Title"]))
    except mediawiki.DisambiguationError:
        # suggestion = wikipedia.suggest(exercise_name)
        # if suggestion:
        #     page = wikipedia.page(suggestion)
        #     valid_exercises[exercise_name] = page.summary
        # else:
        print("Ambiguous name: " + str(exercise["Title"]))

json_object = json.dumps(valid_exercises, indent=4)

# Writing to newDataset.json
with open("data/newDataset.json", "w") as outfile:
    outfile.write(json_object)
outfile.close()

with open("data/newDataset.json", "r") as openfile:
    new_data = json.load(openfile)
openfile.close()

end_time = time.time()

duration = round(end_time - start_time, 2)
og_length = len(data)
new_length = len(new_data.keys())
print(f"length of original json file: {og_length}.")
print(f"length of new json file: {new_length}.")
print(f"it took {duration} seconds to run")
