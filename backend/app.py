from sklearn.feature_extraction.text import TfidfVectorizer
import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
import numpy as np

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, "init.json")


# Computes cosine similarity between two exercise descriptions
def get_sim(desc1, desc2, dt_matrix, title_to_index):
    vec1 = dt_matrix[title_to_index[desc1]]
    vec2 = dt_matrix[title_to_index[desc2]]

    dot_product = np.dot(vec1, vec2)

    vec1_norm = np.linalg.norm(vec1)
    vec2_norm = np.linalg.norm(vec2)

    cosine_sim = dot_product / (vec1_norm * vec2_norm)

    return cosine_sim


# Builds a similarity matrix for exercise descriptions.
def build_sim_matrix(n, index_to_title, dt_matrix, title_to_index, sim_method):
    res = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                cosine_sim = sim_method(
                    index_to_title[i], index_to_title[j], dt_matrix, title_to_index
                )

                res[i, j] = cosine_sim

    return res


# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
    exercise_df = pd.DataFrame(data["exercises"])

    num_exercises = len(data["exercises"])

    title_to_index = {
        title: i for i, title in enumerate([e["Title"] for e in data["exercises"]])
    }

    index_to_title = {
        i: title for i, title in enumerate([e["Title"] for e in data["exercises"]])
    }

    # Build Document-Term matrix
    dt_matrix = (
        TfidfVectorizer()
        .fit_transform([e["Desc"] for e in data["exercises"]])
        .toarray()
    )

    # Build similarity matrix
    sim_matrix = build_sim_matrix(
        num_exercises, index_to_title, dt_matrix, title_to_index, get_sim
    )

    # Eliminate unused columns
    filtered = exercise_df[["Title", "Desc", "Rating"]]

app = Flask(__name__)
CORS(app)


# Sample search using json with pandas
def json_search(query):
    # Get query index
    query_idx = title_to_index[query]
    # Get list of cosine similarity values compared to query description
    cos_sim_list = sim_matrix[query_idx]
    # Add list as column to dataframe
    filtered_with_cosine = filtered.assign(Cosine_Similarity=cos_sim_list)
    # Sort dataframe according to column
    sorted_filtered = filtered_with_cosine.sort_values(
        by=["Cosine_Similarity"], ascending=False
    )
    # Turn it back into a json
    filtered_json = sorted_filtered.to_json(orient="records")
    # Return sorted JSON
    return filtered_json


@app.route("/")
def home():
    return render_template("base.html", title="sample html")


@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return json_search(text)


if "DB_NAME" not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5000)
