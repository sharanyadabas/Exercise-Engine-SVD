from __future__ import print_function
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from sklearn.preprocessing import normalize
from scipy.sparse.linalg import svds

os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, "init.json")

with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
    datalist = data['exercises']
    documents = [(x['Title'], x['all-text'])
                 for x in datalist
                 if len(x['all-text'].split()) > 50]

count = 0
for exercise in documents:
    if exercise[0].upper() == exercise[0]:
        count += 1
print(count)

vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, min_df = 75)
td_matrix = vectorizer.fit_transform([x[1] for x in documents])

docs_compressed, s, words_compressed = svds(td_matrix, k=15)

docs_compressed_normed = normalize(docs_compressed)

def closest_projects(project_index_in, project_repr_in, k = 10):
    sims = project_repr_in.dot(project_repr_in[project_index_in,:])
    asort = np.argsort(-sims)
    asort = asort[asort >= count][:k+1]
    return [(documents[i][0],sims[i]) for i in asort[1:]]

for i in range(10):
    print("INPUT PROJECT: "+documents[i][0])
    print("CLOSEST PROJECTS:")
    print("Using SVD:")
    for title, score in closest_projects(i, docs_compressed_normed):
        print("{}:{:.3f}".format(title, score))
    print()