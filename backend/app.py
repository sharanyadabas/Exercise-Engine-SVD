from sklearn.feature_extraction.text import TfidfVectorizer
import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
import numpy as np
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
    datalist = data['exercises']
    documents = [(x['Title'], x['all-text'], x.get('Rating'))
                 for x in datalist
                 if len(x['all-text'].split()) > 50 and (x.get('Rating') is None or x.get('Rating') != "0.0")]
                                                        # This is used to get rid of 0 rated exercises, could remove

    # Find index of first exercise with rating
    count = 0
    for exercise in documents:
        if exercise[0].upper() == exercise[0]:
            count += 1
    
    # Make term-document matrix
    vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, min_df = 75)
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
    return render_template("base.html", title="sample html")

@app.route("/get-titles")
def get_titles():
    # Gets the title request, finds the index and returns the svd result
    titles = [e["Title"].upper() for e in data["exercises"]]
    return {"titles": titles}

@app.route("/episodes")
def episodes_search():
    # Gets the title request, finds the index and returns the svd result of top 10
    # in a dictionary with Title, Desc, and Rating keys
    title = request.args.get("title")
    index = title_to_index[title]
    return svd_search(documents, count, index, td_matrix)


if "DB_NAME" not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5001)