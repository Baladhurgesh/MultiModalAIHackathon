import deeplake
from deeplake import types
import openai
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
# Define dataset path (store locally or in the cloud)

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
def embedding_function(texts, model="text-embedding-3-small"):
    if isinstance(texts, str):
        texts = [texts]

    texts = [t.replace("\n", " ") for t in texts]
    return [data.embedding for data in openai.embeddings.create(input = texts, model=model).data]

def create_embeddings(review, product_name):
    # Create embeddings
    batch_size = 50
    embeddings_review = []
    reviews = []
    for i in range(0, len(review), batch_size):
        print(review[i : i + batch_size])
        embeddings_review += embedding_function(review[i : i + batch_size])

        reviews += [review[i : i + batch_size]]

        print("Yay")
    print(reviews)
    org_id = "baladhurgesh97"
    dataset_name_vs = "review_db_final"
    vector_search = deeplake.create(f"al://{org_id}/{dataset_name_vs}")
    # Add columns to the dataset
    vector_search.add_column(name="embedding", dtype=types.Embedding(1536))
    vector_search.add_column(name="product_name", dtype=types.Text(index_type=types.BM25))
    vector_search.add_column(name="review_context", dtype=types.Text(index_type=types.BM25))
    for i in range(len(embeddings_review)):
        # print(embeddings_review[i])
        
        vector_search.append({"embedding": np.array(embeddings_review[i]).reshape(1, -1), "product_name": [product_name], "review_context": [reviews[i]]})
    vector_search.commit()
    print("Text data successfully ingested into Deep Lake!")

def query_vector_search(query):
    query = "How many stars does this product have?"
    
    embed_query = embedding_function(query)[0]
    embedding_string = ",".join(str(c) for c in embed_query)
    org_id = "baladhurgesh97"
    dataset_name_vs = "review_db_final"
    vector_search = deeplake.open(f"al://{org_id}/{dataset_name_vs}")
    tql_vs = f"""
    SELECT *, cosine_similarity(embedding, ARRAY[{embedding_string}]) as score
    FROM (
        SELECT *, ROW_NUMBER() AS row_id
    )
    ORDER BY cosine_similarity(embedding, ARRAY[{embedding_string}]) DESC 
    LIMIT 5
"""
    
    vs_results = vector_search.query(tql_vs)
    print(vs_results)
    print(vs_results["review_context"])
    for row in vs_results:
        print(row["review_context"])
    return vs_results

if __name__ == "__main__":
    # Create or load a Deep Lake dataset
    

    # Add columns to the dataset
    # vector_search.add_column(name="embedding", dtype=types.Embedding(3072))
    # vector_search.add_column(name="product_name", dtype=types.Text(index_type=types.BM25))
    # vector_search.add_column(name="review_context", dtype=types.Text(index_type=types.BM25))

    # vector_search.commit()
    
    review= "The AuraGlow Sleep Mask is a reliable option for minimizing light disruption during sleep. Its contoured design, particularly around the nose bridge, effectively reduces ambient light, even in brighter environments. The adjustable strap ensures a comfortable and secure fit, accommodating various head sizes without slippage.  The mask is made from a soft modal blend, which breathes well and prevents overheating—a common complaint with some sleep masks.  The stitching appears durable, and after several weeks of use, there are no signs of wear. While it doesn't offer noise cancellation, its light-blocking and comfort make it a worthwhile choice for improving sleep quality. 4/5 stars."
    create_embeddings(review, product_name="AuraGlow Sleep Mask")
    query_vector_search("How many stars does this product have?")

