import os
import openai
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# using local llm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from itertools import islice

import uuid
from datasets import load_dataset
import pandas as pd
import logging
import requests
import json
from dotenv import load_dotenv
import pickle


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

LLM_SERVICE_URL = os.getenv('LOCAL_LLM_SERVICE_URL', 'http://host.docker.internal:8080/')
LLM_TYPE = os.getenv('LLM_TYPE', 'local') # Default to local

# Initialize global variables
# Initialize SentenceTransformer model
encoder = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Qdrant client
qdrant = QdrantClient(path="/webapp/qdrant_storage") # Using In-Memory Storage (location=":memory:") for a quick demo
collection_name = "medqa_collection"

# Function to load dataset and prepare data
def load_data(sample_size=700):
    logger.info("Loading dataset...")
    dataset = load_dataset("qiaojin/PubMedQA", 'pqa_labeled', split="train")
    df = pd.DataFrame(dataset)
    sample = df.sample(sample_size)
    return sample.to_dict('records')

# Function to generate embeddings and load them into the vector database
def initialize_vector_db(data):
    logger.info("Initializing vector database...")

    # Define path to save/load precomputed embeddings
    embeddings_path = "/webapp/embeddings.pkl"

    # Check if embeddings are precomputed
    if os.path.exists(embeddings_path):
        logger.info("Loading precomputed embeddings from disk...")
        with open(embeddings_path, 'rb') as f:
            embeddings = pickle.load(f)
    else:
        # If not, compute embeddings, save them, and use them during the database initialization.
        logger.info("Generating embeddings...")
        embeddings = {doc['question']: encoder.encode(doc["question"]).tolist() for doc in data}
        with open(embeddings_path, 'wb') as f:
            pickle.dump(embeddings, f)
        logger.info(f"Embeddings saved to {embeddings_path}")

    # Create collection if not exists
    if not qdrant.collection_exists(collection_name):
        vector_size = encoder.get_sentence_embedding_dimension()
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        logger.info(f"Collection '{collection_name}' created.")
    else:
        logger.info(f"Collection '{collection_name}' already exists.")

    """Upload points to the collection"""
    logger.info("Uploading embeddings to the vector database...")
    
    """Uploading points individually"""
    # qdrant.upload_points(
    #     collection_name=collection_name,
    #     points=[
    #         models.PointStruct(
    #             id=str(uuid.uuid4()),
    #             vector=encoder.encode(doc["question"]).tolist(),
    #             payload={
    #                 "question": doc["question"],
    #                 "context": doc["context"],
    #                 "long_answer": doc["long_answer"],
    #                 "final_decision": doc["final_decision"]
    #             },
    #         ) for doc in data
    #     ]
    # )

    """Uploading points in batch"""
    def batch(iterable, size):
        it = iter(iterable)
        while True:
            batch_iter = list(islice(it, size))
            if not batch_iter:
                break
            yield batch_iter

    for chunk in batch(data, 100): # Batch size is 100, adjust depend on needs
        points=[
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=encoder.encode(doc["question"]).tolist(),
                payload={
                    "question": doc["question"],
                    "context": doc["context"],
                    "long_answer": doc["long_answer"],
                    "final_decision": doc["final_decision"]
                },
            ) for doc in chunk
        ]
        qdrant.upsert(collection_name=collection_name, points=points)

    logger.info("Embeddings uploaded successfully")

# Function to search locally
def search_local(query):
    logger.info("Searching locally ...")

    # Get the vector for the query
    query_vector = encoder.encode(query).tolist()
    
    # Perform the search in Qdrant
    hits = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=3  # Replace with desired number of top results
    )
    
    # Extract the 'long_answer' content from the most relevant document
    results = [
            {
                "question": hit.payload.get("question", ""),
                "long_answer": hit.payload.get("long_answer", ""),
            } for hit in hits
        ]    
    logger.info(f"Search results: {results}")
    return results


def assist_with_local_llm(query, context):
    url = LLM_SERVICE_URL + "v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-no-key-required",
        "Content-Type": "application/json"
    }
    
    # Integrate search results into the prompt
    messages = [
        {"role": "system", "content": "You are a helpful assistant specialized in medical question answering. Answer based on the relevant research findings provided below."},
        {"role": "user", "content": f"My question is: {query}"},
        {"role": "assistant", "content": "Here are relevant research findings based on your query:"},
    ]

    # Add context safely
    for res in context:
        question = res.get("question", "No question available")
        long_answer = res.get("long_answer", "No answer available")
        messages.append(
            {"role": "assistant", "content": f"Research finding: {question} - {long_answer}"}
        )

    # Add final user query
    messages.append({"role": "user", "content": f"Please answer the question: {query} based on the above findings."})

    
    payload = {
        "model": "Llama-3.2-3B-Instruct.Q6_K",
        "messages": messages,
        "temperature": 0.4
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        completion = response.json()
        return completion['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"


# Create a FastAPI app
app = FastAPI()

# Load data and initialize vector database on app startup
logger.info("Starting application...")
data = load_data(sample_size=700)

# Initialize vector database
initialize_vector_db(data=data)

logger.info("Application initialization complete.")


# Models
class Body(BaseModel):
    query: str


# Routes
@app.get('/')
def root():
    return RedirectResponse(url='/docs', status_code=301)


@app.post('/ask')
def ask(body: Body):
    """
    Process the user's query and interact with the local LLM.
    """
    if LLM_TYPE == 'local':
        # Search in local vector database
        logger.info(f"===Body Query:===\n{body.query}")
        search_results = search_local(body.query)
        # Generate response from local LLM
        chat_bot_response = assist_with_local_llm(body.query, search_results)
    else:
        chat_bot_response = "Unsupported LLM_TYPE."

    return {'response': chat_bot_response}