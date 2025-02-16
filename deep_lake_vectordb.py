import deeplake
from deeplake import types
import openai
# Define dataset path (store locally or in the cloud)
openai.api_key = OPENAI_API_KEY
dataset_path = "/Users/bala/Documents/MultiModalAIHackathon"

import openai

def embedding_function(texts, model="text-embedding-3-large"):
    if isinstance(texts, str):
        texts = [texts]
    print("Iam here at embedding function")
    texts = [t.replace("\n", " ") for t in texts]
    print("Iam here at embedding function 2")
    return [data.embedding for data in openai.embeddings.create(input = texts, model=model).data]

if __name__ == "__main__":
    # Create or load a Deep Lake dataset
    org_id = "baladhurgesh97"
    dataset_name_vs = "sample_db"
    vector_search = deeplake.open(f"al://{org_id}/{dataset_name_vs}")

    # Add columns to the dataset
    # vector_search.add_column(name="embedding", dtype=types.Embedding(3072))
    # vector_search.add_column(name="product_name", dtype=types.Text(index_type=types.BM25))
    # vector_search.add_column(name="review_context", dtype=types.Text(index_type=types.BM25))

    # vector_search.commit()
     
    review= "The AuraGlow Sleep Mask is a reliable option for minimizing light disruption during sleep. Its contoured design, particularly around the nose bridge, effectively reduces ambient light, even in brighter environments. The adjustable strap ensures a comfortable and secure fit, accommodating various head sizes without slippage.  The mask is made from a soft modal blend, which breathes well and prevents overheating—a common complaint with some sleep masks.  The stitching appears durable, and after several weeks of use, there are no signs of wear. While it doesn't offer noise cancellation, its light-blocking and comfort make it a worthwhile choice for improving sleep quality. 4/5 stars."
    # Create embeddings
    batch_size = 50
    embeddings_review = []
    print("Iam here")
    for i in range(0, len(review), batch_size):
        embeddings_review += embedding_function(review[i : i + batch_size])
        print("Yay")

    vector_search.append({"embedding": embeddings_review, "product_name": "AuraGlow Sleep Mask", "review_context": review})
    vector_search.commit()
    print("Text data successfully ingested into Deep Lake!")