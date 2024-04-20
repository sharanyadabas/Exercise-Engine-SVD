from __future__ import print_function
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from sklearn.preprocessing import normalize
from scipy.sparse.linalg import svds


# Finds the k closest exercises to the given exercise excluding ones without ratings
def closest_projects(documents, project_index_in, project_repr_in, no_rating, k=10):
    # Performs dot product between project and U to get similarity array
    sims = project_repr_in.dot(project_repr_in[project_index_in, :])
    # Gets index of sorting them according to similarity
    asort = np.argsort(-sims)
    # Excludes all the ones without ratings
    asort = asort[np.in1d(asort, no_rating, invert=True)][: k + 1]
    # Returns in nice dictionary format
    return [
        {
            "Title": documents[i][0],
            "Desc": documents[i][1],
            "Rating": documents[i][2],
            "Sim": "{0:.4f}".format(sims[i]),
            "YT_link": documents[i][3],
        }
        for i in asort[1:]
    ]


# Performs SVD upon the term document matrix, and then finds the top 10 most similar
# documents to the document the given index and returns a dictionary with their Titles,
# Descriptions, and ratings
def svd_search(documents, index, td_matrix, no_rating):
    # Gets svd
    docs_compressed, s, words_compressed = svds(td_matrix, k=40)
    # Normalizes
    docs_compressed_normed = normalize(docs_compressed)
    # Sends to function to find top k
    top_10 = closest_projects(documents, index, docs_compressed_normed, no_rating, 10)
    return top_10