import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_redis import RedisVectorStore, RedisConfig


df = pd.read_csv("data2.csv")
embeddings = HuggingFaceEmbeddings(model_name="Alibaba-NLP/gte-modernbert-base")
documents = []


config = RedisConfig(
    index_name="product_data1",
    redis_url="redis://localhost:6379",
    distance_metric="COSINE"
)

vector_store = RedisVectorStore(embeddings, config=config)

for _, row in df.iterrows():
    content = f"""
    Product Name: {row['product_name']}
    Description: {row['description']}
    Brand: {row['brand']}
    Type: {row['product_type']}
    Price: ₹{row['price_rupees']}
    CPU: {row['cpu']}
    GPU: {row['gpu']}
    RAM: {row['ram_gb']} GB
    Storage: {row['storage_gb']} GB
    Screen: {row['screen_size_inches']}" {row['screen_refresh_rate']}Hz
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
        "ram_gb": int(row["ram_gb"]),
        "storage_gb": int(row["storage_gb"]),
        "screen_refresh_rate": int(row["screen_refresh_rate"]),
        "screen_size_inches": float(row["screen_size_inches"]),
        "description": row["description"],
        "image_url": str(row["image_url_1"] if "image_url_1" in row else ""),
        "product_url": row["product_url"],
    }
    doc = Document(page_content=content, metadata=metadata)
    documents.append(doc)


# RedisVectorStore.drop_index(
#     redis_url="redis://localhost:6379",
#     index_name="product_index"
# )

# vectordb = Redis.from_documents(
#     documents=documents,
#     embedding=embedder,
#     redis_url="redis://localhost:6379",
#     index_name="product_index"
# )

vector_store.add_documents(documents)