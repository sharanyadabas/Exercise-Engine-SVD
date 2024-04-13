from __future__ import print_function
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from sklearn.preprocessing import normalize
from scipy.sparse.linalg import svds


# Finds the k closest exercises to the given exercise excluding ones without ratings
def closest_projects(documents, count, project_index_in, project_repr_in, k = 10):
    # Performs dot product between project and U to get similarity array
    sims = project_repr_in.dot(project_repr_in[project_index_in,:])
    # Gets index of sorting them according to similarity
    asort = np.argsort(-sims)
    # Excludes all the ones without ratings
    asort = asort[asort >= count][:k+1]
    # Returns in nice dictionary format
    return [{"Title" : documents[i][0], "Desc" : documents[i][1], "Rating" : documents[i][2]} for i in asort[1:]]

# Performs SVD upon the term document matrix, and then finds the top 10 most similar
# documents to the document the given index and returns a dictionary with their Titles,
# Descriptions, and ratings
def svd_search(documents, count, index, td_matrix):
    # Gets U
    docs_compressed, _, _ = svds(td_matrix, k=15)
    # Normalizes
    docs_compressed_normed = normalize(docs_compressed)
    # Sends to function to find top k
    top_10 = closest_projects(documents, count, index, docs_compressed_normed, 10)
    return top_10