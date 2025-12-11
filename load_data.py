import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_redis import RedisVectorStore, RedisConfig


df = pd.read_csv("final_data.csv")
embeddings = HuggingFaceEmbeddings(model_name="Alibaba-NLP/gte-modernbert-base")
documents = []


config = RedisConfig(
    index_name="product_data",
    redis_url="redis://localhost:6379",
    distance_metric="COSINE"
)

vector_store = RedisVectorStore(embeddings, config=config)

for _, row in df.iterrows():
    content = f"""
    Product Name: {row['product_name']}
    Description: {row['Description']}
    Brand: {row['brand']}
    Type: {row['product_type']}
    Price: ₹{row['price_rupees']}
    CPU: {row['cpu']}
    GPU: {row['gpu']}
    RAM: {row['ram']} GB
    Storage: {row['product_storage']} GB
    Screen Size: {row['screen_size']}" 
    Screen refresh rate: {row['refresh_rate']}Hz
    Tags: {row['tags']}
    """

    # Structured metadata for filtering
    metadata = {
        "product_id": str(row["product_id"]),
        "product_name": row["product_name"],
        "brand": row["brand"],
        "product_type": row["product_type"],
        "tags": [t.strip() for t in str(row["tags"]).split(",") if t.strip()],
        "price": row["price_rupees"],
        "cpu": row["cpu"],
        "gpu": row["gpu"],
        "ram_gb": int(row["ram"]),
        "storage_gb": int(row["product_storage"]),
        "screen_refresh_rate": int(row["refresh_rate"]),
        "screen_size_inches": float(row["screen_size"]),
        "description": row["Description"],
        "image_url": str(row["product_image"]),
        # "product_url": row["product_url"],
    }
    doc = Document(page_content=content, metadata=metadata)
    print(metadata)
    print("\n\n\n")
    documents.append(doc)



# vectordb = Redis.from_documents(
#     documents=documents,
#     embedding=embedder,
#     redis_url="redis://localhost:6379",
#     index_name="product_index"
# )

vector_store.add_documents(documents)