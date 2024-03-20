import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
import numpy as np

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'init.json')


def cos_sim(query_desc_vec, title_to_vec_list):
    """
    Returns a list of cosine similarity values between the 
    query description and the exercise descriptions corresponding 
    to the order that each description appears in the given list.
    """
    pass

def vectorize_description(desc):
    """
    Turns a given description into a vector.
    """
    pass        

def create_title_to_vec(data):
    """
    Creates a dictionary where the keys are the titles of exercises
    and the values are their corresponding vectors.
    """
    result = {}
    for exercise in data["exercises"]:
        desc_vec = vectorize_description(exercise["Desc"])
        result[exercise["Title"]] = desc_vec
    return result


# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)
    exercise_df = pd.DataFrame(data['exercises'])
    # Create dictionary mapping titles to description vectors
    title_to_vec = create_title_to_vec(data)
    title_to_vec_list = title_to_vec.values()
    # Eliminate unused columns
    filtered = exercise_df[['Title', 'Desc', 'Rating']]

app = Flask(__name__)
CORS(app)

# Sample search using json with pandas
def json_search(query):
    # Retrive query description vector
    query_desc_vec = title_to_vec[query]
    # Get list of cosine similarity values compared to query description
    cos_sim_list = cos_sim(query_desc_vec, title_to_vec_list)
    # Add list as column to dataframe
    filtered = filtered.assign(Cosine_Similarity=cos_sim_list)
    # Sort dataframe according to column
    filtered.sort_values(by=["Cosine_Similarity"], ascending=False)
    # Turn it back into a json
    filtered_json = filtered.to_json(orient='records')
    # Return it
    return filtered_json

@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return json_search(text)

if 'DB_NAME' not in os.environ:
    app.run(debug=True,host="0.0.0.0",port=5000)