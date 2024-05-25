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
        (
            x["Title"].upper(),
            x["Desc"],
            x["all-text"],
            x["muscle-group"],
            x["equipment"],
        )
        for x in datalist
        if len(x["all-text"].split()) > 35
    ]

    # Make term-document matrix
    vectorizer = TfidfVectorizer(stop_words="english", max_df=0.85, min_df=0.15)
    td_matrix = vectorizer.fit_transform([x[2] for x in documents])
    dt_matrix = vectorizer.fit_transform([x[2] for x in documents]).toarray()

    # Make title to index dictionary and index to title
    title_to_index = {doc[0]: i for i, doc in enumerate(documents)}
    index_to_title = {i: doc[0] for i, doc in enumerate(documents)}

    # Make word to index dictionary
    word_to_index = vectorizer.vocabulary_
    index_to_word = {i: t for t, i in word_to_index.items()}

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
muscle_groups = []
equipment_groups = []


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
    # Excludes all the ones without itself
    asort = asort[1:]
    # Returns in nice dictionary format
    return [
        {
            "Title": documents[i][0],
            "Desc": documents[i][1],
            "all-text": documents[i][2],
            "Sim": "{0:.4f}".format(sims[i]),
            "Muscles": documents[i][3],
            "Equipment": documents[i][4],
        }
        for i in asort
    ]


def closest_docs_from_docs(documents, doc_index, doc_repr_in):
    """
    Given a document index, finds the 5 closest documents using SVD
    doc matrix
    """

    # Performs dot product between document and U to get similarity array
    sims = doc_repr_in.dot(doc_repr_in[doc_index, :])
    # Gets index of sorting them according to similarity
    asort = np.argsort(-sims)
    # Excludes all the ones without itself
    asort = asort[1:]
    # Returns in nice dictionary format
    return [
        {
            "Title": documents[i][0],
            "Desc": documents[i][1],
            "all-text": documents[i][2],
            "Sim": "{0:.4f}".format(sims[i]),
            "Muscles": documents[i][3],
            "Equipment": documents[i][4],
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


muscle_dict = {
    "chest": [
        "Pectoralis M. (Sternal-Clavicular)",
        "Pectoralis",
        "Pectoralis Clavicular Head",
        "Pectoralis major, Minor",
        "Pectoralis Major",
        "Pectoralis Minor",
        "Pectoralis Major, Clavicular",
        "Pectoralis Major, Sternal-Lower",
        "Pectoralis Major, Sternal",
    ],
    "shoulders": [
        "Deltoids",
        "Deltoids (Lateral)",
        "Deltoid, Anterior",
        "Lateral and Posterior Deltoid",
        "Anterior Deltoid",
        "Deltoids (Posterior, Lateral)",
        "Posterior Deltoid",
        "Lateral Deltoid",
        "Front and Posterior Deltoid",
    ],
    "upper back": [
        "Rhomboid",
        "Rhomboids",
        "Upper Trapezius",
        "Trapezius (Lower, Middle)",
        "Trapezius, Middle",
        "Levator Scapula",
        "Latissimus dorsi",
        "Splenius Cervitis",
        "Middle Scalene",
        "Back",
    ],
    "lower back": [
        "Lower Trapezius",
        "Lower Back",
        "Lower Back (Erector Spinae)",
        "Quadratus Lumborum",
        "Quadratus lumborum",
        "Erector Spinae",
        "Multifidus",
        "Spinalis Cervicis",
        "Iliocastalis lumborum",
        "Iliocastalis thoracis",
    ],
    "biceps": ["Biceps Brachii", "Biceps", "Forearms, Biceps", "Brachialis"],
    "triceps": [
        "Triceps, Long Head",
        "Triceps (Long Head)",
        "Triceps Brachii",
        "Dynamic Stabilizers Triceps, Long Head",
    ],
    "forearms": [
        "Wrist Flexors",
        "Wrist Extensors",
        "Extensor Carpi Radialis",
        "Flexor Carpi Radialis",
        "Wrist and Forearm",
        "Forearm Flexors",
        "Wrist Flexor",
        "Forearms",
        "Forearms and Wrists",
    ],
    "core": [
        "Rectus Abdominis",
        "Transverse Abdominis",
        "Stabilizers- Rectus Abdominis",
        "Abdominal muscles",
        "Internal oblique",
        "Abdominals",
        "Rectus abdominis",
        "Obliques",
        "Core Muscles",
        "External oblique",
        "Abdominal",
        "Transverse abdominis",
        "Abs",
        "Abdominals (Core Muscles)",
    ],
    "quadriceps": [
        "Quadriceps",
        "Rectus Femoris",
        "Sartorius",
        "Tensor Fasciae Latae",
        "Tensor fasciae latae",
        "Leg",
    ],
    "glutes": [
        "Glutes",
        "Gluteus Medius and Minimus",
        "Gluteus Maximus, Lower Fibers",
        "Gluteus Maximus",
        "Gluteus Medius",
        "Gluteus Medius, Minius",
        "Gluteus Minimus",
        "Gluteus medius",
        "Gluteal Muscles",
        "Hip Abductors",
    ],
    "hamstrings": ["Hamstring", "Hamstrings"],
    "adductors": [
        "Hip Adductors",
        "Adductors (Inner Thigh Muscles)",
        "Adductor Magnus",
        "Adductor longus",
        "Adductor Longus",
        "Adductor Brevis",
        "Hip Adductors/Abductors",
        "Hip Adductors and Abductors",
        "Hip, Adductors",
        "Obturator externus",
        "Hip Adductors and Abductors",
    ],
    "calves": [
        "Calves",
        "Calf Muscles",
        "Soleus",
        "Gastrocnemius",
        "Tibialis Anterior",
        "Plantar Flexion",
        "Ankle Stabilizers",
    ],
    "neck": [
        "Sternocleidomastoideus",
        "Platysma",
        "Longus colli",
        "Longissimus Capitis",
        "Sternocleidomastoid",
        "Longissimus Cervicis",
        "Scalene",
        "Scalene Muscles",
        "Splenius Cervicis",
        "Splenius Capitis",
        "Anterior Scalene",
        "Omohyoid",
    ],
    "rotator cuff": [
        "Teres Major",
        "Teres Minor",
        "Subscapularis",
        "Supraspinatus",
        "Infraspinatus",
        "Rotator Cuff",
    ],
    "spine": [
        "Spinalis Cervicis",
        "Erectos Spinae",
        "Spinalis Capitis",
        "Iliocastalis lumborum",
        "Iliocastalis thoracis",
        "Longissimus Cervicis",
        "Longissimus Capitis",
    ],
    "other": [
        "Diaphragm",
        "Pelvic floor",
        "Stabilizers -Upper Trapezius",
        "Splenius",
        "Levatos Scapula",
        "Clavicular",
        "Pectoralis Major, (Clavicular)",
        "Omohyoid",
        "Scapula",
    ],
}


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
    global equipment_groups
    global difficulties
    global muscle_dict

    was_AH = False
    title = request.args.get("title")
    index = title_to_index[title]
    recent_search = closest_docs_from_docs(documents, index, docs_compressed_normed)

    muscle_list = request.args.get("muscleFilter")
    muscle_groups = muscle_list.split(",") if (muscle_list != "") else []

    equipment_list = request.args.get("equipmentFilter")
    equipment_groups = equipment_list.split(",") if (equipment_list != "") else []

    if len(muscle_groups) >= 1:
        new_search = []
        for search in recent_search:
            for filter_muscle in muscle_groups:
                for exercise_muscle in search["Muscles"]:
                    if exercise_muscle in muscle_dict[filter_muscle]:
                        new_search.append(search)
        recent_search = new_search

    if len(equipment_groups) >= 1:
        new_search = []
        for search in recent_search:
            for equipment in search["Equipment"]:
                if equipment.lower() in equipment_groups:
                    new_search.append(search)
        recent_search = new_search

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
    global equipment_groups
    global difficulties
    global muscle_dict

    was_AH = True
    title = request.args.get("title")
    recent_search = closest_docs_from_words(title)

    muscle_list = request.args.get("muscleFilter")
    muscle_groups = muscle_list.split(",") if (muscle_list != "") else []

    equipment_list = request.args.get("equipmentFilter")
    equipment_groups = equipment_list.split(",") if (equipment_list != "") else []

    if len(muscle_groups) >= 1:
        new_search = []
        for search in recent_search:
            for filter_muscle in muscle_groups:
                for exercise_muscle in search["Muscles"]:
                    if exercise_muscle in muscle_dict[filter_muscle]:
                        new_search.append(search)
        recent_search = new_search

    if len(equipment_groups) >= 1:
        new_search = []
        for search in recent_search:
            for equipment in search["Equipment"]:
                if equipment.lower() in equipment_groups:
                    new_search.append(search)
        recent_search = new_search

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
    return json.dumps(
        {
            "title": recent_title,
            "was_AH": was_AH,
            "muscle_groups": muscle_groups,
            "equipments": equipment_groups,
        }
    )


@app.route("/get-titles")
def get_titles():
    # Gets the title request, finds the index and returns the svd result
    titles = [e[0] for e in documents]
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
    global muscle_dict
    global muscle_groups
    global equipment_groups

    was_AH = False
    title = request.args.get("title")
    recent_title = title
    index = title_to_index[title]
    recent_search = closest_docs_from_docs(documents, index, docs_compressed_normed)

    muscle_list = request.args.get("muscleFilter")
    muscle_groups = muscle_list.split(",") if (muscle_list != "") else []

    equipment_list = request.args.get("equipmentFilter")
    equipment_groups = equipment_list.split(",") if (equipment_list != "") else []

    if len(muscle_groups) >= 1:
        new_search = []
        for search in recent_search:
            for filter_muscle in muscle_groups:
                for exercise_muscle in search["Muscles"]:
                    if exercise_muscle in muscle_dict[filter_muscle]:
                        new_search.append(search)
        recent_search = new_search

    if len(equipment_groups) >= 1:
        new_search = []
        for search in recent_search:
            for equipment in search["Equipment"]:
                if equipment.lower() in equipment_groups:
                    new_search.append(search)
        recent_search = new_search

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
    global muscle_dict
    global muscle_groups
    global equipment_groups

    was_AH = True
    title = request.args.get("title")
    recent_title = title
    recent_search = closest_docs_from_words(title)

    muscle_list = request.args.get("muscleFilter")
    muscle_groups = muscle_list.split(",") if (muscle_list != "") else []

    equipment_list = request.args.get("equipmentFilter")
    equipment_groups = equipment_list.split(",") if (equipment_list != "") else []

    if len(muscle_groups) >= 1:
        new_search = []
        for search in recent_search:
            for filter_muscle in muscle_groups:
                for exercise_muscle in search["Muscles"]:
                    if exercise_muscle in muscle_dict[filter_muscle]:
                        new_search.append(search)
        recent_search = new_search

    if len(equipment_groups) >= 1:
        new_search = []
        for search in recent_search:
            for equipment in search["Equipment"]:
                if equipment.lower() in equipment_groups:
                    new_search.append(search)
        recent_search = new_search

    if len(recent_search) > 5:
        return recent_search[:5]
    return recent_search


if "DB_NAME" not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5001)
