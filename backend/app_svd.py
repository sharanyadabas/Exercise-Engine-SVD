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
    documents = [(x['Title'], x['Desc'])
                 for x in datalist
                 if len(x['Desc'].split()) > 50]


vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, min_df = 75)
td_matrix = vectorizer.fit_transform([x[1] for x in documents])


docs_compressed, s, words_compressed = svds(td_matrix, k=10)
words_compressed = words_compressed.transpose()


word_to_index = vectorizer.vocabulary_
index_to_word = {i:t for t,i in word_to_index.items()}


words_compressed_normed = normalize(words_compressed, axis = 1)

def closest_words(word_in, words_representation_in, k = 20):
    if word_in not in word_to_index: return "Not in vocab."
    sims = words_representation_in.dot(words_representation_in[word_to_index[word_in],:])
    asort = np.argsort(-sims)[:k+1]
    return [(index_to_word[i],sims[i]) for i in asort[1:]]

td_matrix_np = td_matrix.transpose().toarray()
td_matrix_np = normalize(td_matrix_np)

word = 'strength'
print("Using SVD:")
for w, sim in closest_words(word, words_compressed_normed):
  try:
    print("{}, {:.3f}".format(w, sim))
  except:
    print("word not found")
print()

docs_compressed_normed = normalize(docs_compressed)

def closest_projects(project_index_in, project_repr_in, k = 5):
    sims = project_repr_in.dot(project_repr_in[project_index_in,:])
    asort = np.argsort(-sims)[:k+1]
    return [(documents[i][0],sims[i]) for i in asort[1:]]

for i in range(10):
    print("INPUT PROJECT: "+documents[i][0])
    print("CLOSEST PROJECTS:")
    print("Using SVD:")
    for title, score in closest_projects(i, docs_compressed_normed):
        print("{}:{:.3f}".format(title, score))
    print()
    print("Not using SVD (using directly term-document matrix):")
    for title, score in closest_projects(i, td_matrix_np):
        print("{}:{:.3f}".format(title, score))
    print("--------------------------------------------------------\n")