import numpy as np
from scipy.spatial import distance
from operator import itemgetter
import json
import requests
from .models import BabyName as BabyNameModel, Embedding as EmbeddingModel
hf_token = "" # TODO put this in .env file
model_id = "sentence-transformers/all-MiniLM-L6-v2"

api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {hf_token}"}

def query(texts):
    response = requests.post(api_url, headers=headers, json={"inputs": texts, "options": {"wait_for_model":True}})
    return response.json()

def get_embeddings_names():
    names = BabyNameModel.objects.filter(description__isnull=False).all()
    texts = [name.description for name in names]

    output = query(texts)

    for i, name in enumerate(names):
        name.embedding = output[i]
        emb = EmbeddingModel(name=name, embedding=output[i])
        emb.save()


def get_related_names(query_text, n=10):
    query_vector = np.array(query(query_text))
    embeddings = EmbeddingModel.objects.all()

    # converting JSONField to numpy arrays
    embeddings_vectors = np.array([emb.embedding for emb in embeddings])

    # calculating cosine similarity
    similarities = [1 - distance.cosine(query_vector, vec) for vec in embeddings_vectors]

    # getting indices of the most similar names
    indices_similarities = [(i, sim) for i, sim in enumerate(similarities)]
    indices_similarities.sort(key=itemgetter(1), reverse=True)

    # return the indices of the most similar names
    return [(embeddings[i].name, _) for i, _ in indices_similarities[:n]]