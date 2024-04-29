from sklearn.feature_extraction.text import TfidfVectorizer
import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from sklearn.preprocessing import normalize
from scipy.sparse.linalg import svds
import numpy as np

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, "init.json")

with open(json_file_path, "r", encoding="utf-8") as file:
    # Load necessary data from json file
    data = json.load(file)
    datalist = data["exercises"]
    documents = [
        (x["Title"].upper(), x["all-text"], x.get("Rating"), x.get("YouTubeLink"),
          x.get("BodyPart"), x.get('Equipment'),
          x.get("Level"))
        for x in datalist
        if len(x["all-text"].split()) > 35
    ]

    # Get exercises with no rating or rating of 0.0 to exclude
    no_rating = []
    counter = 0
    for i, e in enumerate(documents):
        if e[2] is None:
            counter += 1
        if e[2] is None or e[2] == "0.0":
            no_rating.append(i)

    # Make term-document matrix
    vectorizer = TfidfVectorizer(stop_words="english", max_df=0.7, min_df=75)
    td_matrix = vectorizer.fit_transform([x[1] for x in documents])
    dt_matrix = vectorizer.fit_transform([x[1] for x in documents]).toarray()

    # Make title to index dictionary and index to title
    title_to_index = {doc[0]: i for i, doc in enumerate(documents)}
    index_to_title = {i : doc[0] for i, doc in enumerate(documents)}
    
    # Make word to index dictionary
    word_to_index = vectorizer.vocabulary_

    # Gets svd
    docs_compressed, s, words_compressed = svds(td_matrix, k=40)

    # Normalizes
    docs_compressed_normed = normalize(docs_compressed)
    words_compressed = words_compressed.transpose()
    words_compressed_normed = normalize(words_compressed, axis=1)

app = Flask(__name__)
CORS(app)

# Global variable for holding the most recent search, used for homepage.
recent_search = []
recent_title = ""
was_AH = False

def closest_docs_from_words(query):
    """
    Given a query of words, finds the 5 closest documents using SVD
    word + doc matrices
    """

    # Transforms query into tfidf vector of words in vocab
    query_tfidf = vectorizer.transform([query]).toarray()
    query_vec = normalize(np.dot(query_tfidf, words_compressed)).squeeze()
    # Performs dot product between vector and U to get similarity array
    sims = docs_compressed_normed.dot(query_vec)
    # Gets index of sorting them according to similarity
    asort = np.argsort(-sims)
    # Excludes all the ones without ratings and itself
    asort = asort[1:]
    asort = asort[np.in1d(asort, no_rating, invert=True)]
    # Returns in nice dictionary format
    return [
        {
            "Title": documents[i][0],
            "Desc": documents[i][1],
            "Rating": documents[i][2],
            "Sim": "{0:.4f}".format(sims[i]),
            "YT_link": documents[i][3],
            "Muscles": documents[i][4],
            "Equipment": documents[i][5],
            "Difficulty": documents[i][6],
        }
        for i in asort
    ]


def closest_docs_from_docs(documents, doc_index, doc_repr_in, no_rating):
    """
    Given a document index, finds the 5 closest documents using SVD
    doc matrix
    """

    # Performs dot product between document and U to get similarity array
    sims = doc_repr_in.dot(doc_repr_in[doc_index, :])
    # Gets index of sorting them according to similarity
    asort = np.argsort(-sims)
    # Excludes all the ones without ratings and itself
    asort = asort[1:]
    asort = asort[np.in1d(asort, no_rating, invert=True)]
    # Returns in nice dictionary format
    return [
        {
            "Title": documents[i][0],
            "Desc": documents[i][1],
            "Rating": documents[i][2],
            "Sim": "{0:.4f}".format(sims[i]),
            "YT_link": documents[i][3],
            "Muscles": documents[i][4], 
            "Equipment": documents[i][5], 
            "Difficulty":  documents[i][6],
        }
        for i in asort
    ]


@app.route("/")
def home():
    # Renders the homepage
    return render_template("homepage.html", title="home html")


@app.route("/results/")
def results():
    # Renders the results
    return render_template("results.html", title="results html")


@app.route("/create-recent-normal")
def create_recent_normal():
    """
    Route for performing normal doc-doc search and storing results
    in global var recent_search. Needed for switch from homepage to results.
    """
    global recent_search
    global recent_title
    global was_AH
    global muscle_groups
    global equipments
    global difficulties

    was_AH = False
    title = request.args.get("title")
    muscle_groups = request.args.get("muscleFilter")
    equipments = request.args.get("equipmentFilter")
    difficulties = request.args.get("difficultyFilter")
    index = title_to_index[title]
    recent_search = closest_docs_from_docs(documents, index, docs_compressed_normed, no_rating)
    if len(muscle_groups) >= 1:
        recent_search = [search for search in recent_search
        if search["Muscles"].lower() in muscle_groups
    ]
    if len(equipments) >= 1:
        recent_search = [search for search in recent_search
        if search["Equipment"].lower() in equipments
    ]
    if len(difficulties) >= 1:
        recent_search = [search for search in recent_search
                         if search["Difficulty"].lower() in difficulties]
    if len(recent_search) > 5:
        recent_search = recent_search[:5]
    recent_title = title
    return {}


@app.route("/create-recent-AH")
def create_recent_AH():
    """
    Route for performing ad-hoc words-doc search and storing results
    in global var recent_search. Needed for switch from homepage to results.
    """
    global recent_search
    global recent_title
    global was_AH
    global muscle_groups
    global equipments
    global difficulties
    was_AH = True
    title = request.args.get("title")
    muscle_groups = request.args.get("muscleFilter")
    equipments = request.args.get("equipmentFilter")
    difficulties = request.args.get("difficultyFilter")
    recent_search = closest_docs_from_words(title)
    if len(muscle_groups) >= 1:
        recent_search = [search for search in recent_search
        if search["Muscles"].lower() in muscle_groups
    ]
    if len(equipments) >= 1:
        recent_search = [search for search in recent_search
        if search["Equipment"].lower() in equipments
    ]
    if len(difficulties) >= 1:
        recent_search = [search for search in recent_search
                         if search["Difficulty"].lower() in difficulties]
    if len(recent_search) > 5:
        recent_search = recent_search[:5]
    recent_title = title
    return {}


@app.route("/get-recent")
def get_recent():
    # Returns the most recent results
    return recent_search

@app.route("/get-recent-info")
def get_recent_title():
    # Returns the most recent results
    return json.dumps({
        "title" : recent_title,
        "was_AH" : was_AH,
        "muscle_groups": muscle_groups,
        "equipments": equipments,
        "difficulties": difficulties
                       })

@app.route("/get-titles")
def get_titles():
    # Gets the title request, finds the index and returns the svd result
    titles = [
        e[0] for e in documents[214:]
    ]
    titles.sort()
    return {"titles": titles}


@app.route("/normal_search")
def normal_search():
    """
    Route for performing normal doc-doc search and storing results
    in global var recent_search. Gets the title request, finds the index and
    returns the svd result of top 5 in a dictionary with Title, Desc, Rating,
    Sim, and YT_link keys.
    """

    global recent_search
    global recent_title
    global was_AH
    was_AH = False
    title = request.args.get("title")
    recent_title = title
    muscle_groups = request.args.get("muscleFilter")
    equipments = request.args.get("equipmentFilter")
    difficulties = request.args.get("difficultyFilter")
    index = title_to_index[title]
    recent_search = closest_docs_from_docs(documents, index, docs_compressed_normed, no_rating)
    if len(muscle_groups) >= 1:
        recent_search = [search for search in recent_search
        if search["Muscles"].lower() in muscle_groups
    ]
    if len(equipments) >= 1:
        recent_search = [search for search in recent_search
        if search["Equipment"].lower() in equipments
    ]
    if len(difficulties) >= 1:
        recent_search = [search for search in recent_search
                         if search["Difficulty"].lower() in difficulties]
    if len(recent_search) > 5:
        return recent_search[:5]
    return recent_search
    

@app.route("/AH_search")
def AH_search():
    """
    Route for performing ad-hoc words-doc search and storing results
    in global var recent_search. Gets the title request and returns the
    svd result of top 5 in a dictionary with Title, Desc, Rating,
    Sim, and YT_link keys.
    """
    global recent_search
    global was_AH
    global recent_title
    was_AH = True
    title = request.args.get("title")
    recent_title = title
    muscle_groups = request.args.get("muscleFilter")
    equipments = request.args.get("equipmentFilter")
    difficulties = request.args.get("difficultyFilter")
    recent_search = closest_docs_from_words(title)
    if len(muscle_groups) >= 1:
        recent_search = [search for search in recent_search
        if search["Muscles"].lower() in muscle_groups
    ]
    if len(equipments) >= 1:
        recent_search = [search for search in recent_search
        if search["Equipment"].lower() in equipments
    ]
    if len(difficulties) >= 1:
        recent_search = [search for search in recent_search
                         if search["Difficulty"].lower() in difficulties]
    if len(recent_search) > 5:
        return recent_search[:5]
    return recent_search


if "DB_NAME" not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5001)
