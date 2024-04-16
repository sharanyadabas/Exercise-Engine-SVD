from sklearn.feature_extraction.text import TfidfVectorizer
import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
from svd import svd_search

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
        (x["Title"].upper(), x["all-text"], x.get("Rating"), x.get("YouTubeLink"))
        for x in datalist
        if len(x["all-text"].split()) > 35
    ]

    # Get exercises with no rating or rating of 0.0 to exclude
    no_rating = []
    for i, e in enumerate(documents):
        if e[2] is None or e[2] == "0.0":
            no_rating.append(i)

    # Make term-document matrix
    vectorizer = TfidfVectorizer(stop_words="english", max_df=0.7, min_df=75)
    td_matrix = vectorizer.fit_transform([x[1] for x in documents])

    # Make title to index dictionary
    title_to_index = {
        doc[0]: i for i, doc in enumerate(documents)
    }

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    # Renders the homepage
    return render_template("homepage.html", title="home html")

@app.route("/results")
def results():
    # Renders the results
    return render_template("results.html", title="results html")

@app.route('/create-recent')
def create_recent():
    global recent_search
    title = request.args.get("title")
    index = title_to_index[title]
    recent_search = svd_search(documents, index, td_matrix, no_rating)
    return {}

@app.route("/get-recent")
def get_recent():
    # Renders the results
    global recent_search
    return recent_search


@app.route("/get-titles")
def get_titles():
    # Gets the title request, finds the index and returns the svd result
    titles = [
        e[0] for e in documents[230:]
    ]  # Experimental, excludes webscraped queries
    # titles = [e[0] for e in documents]
    return {"titles": titles}

@app.route("/svd_search")
def search():
    # Gets the title request, finds the index and returns the svd result of top 10
    # in a dictionary with Title, Desc, and Rating keys
    global recent_search
    title = request.args.get("title")
    index = title_to_index[title]
    recent_search = svd_search(documents, index, td_matrix, no_rating)
    return recent_search


if "DB_NAME" not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5001)
