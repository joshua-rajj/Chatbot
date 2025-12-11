from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
from langchain.chat_models import init_chat_model
from langchain_redis import RedisVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("API")


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


embeddings = HuggingFaceEmbeddings(model_name="Alibaba-NLP/gte-modernbert-base")

vector_store = RedisVectorStore(embeddings, redis_url="redis://localhost:6379", index_name="product_data")
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
llm = init_chat_model("google_genai:gemini-2.5-flash-lite")

# prompt = ChatPromptTemplate.from_template("""
# You are a helpful product expert for an electronics store.
# Use the following product data to answer the user's question accurately.
# If multiple products fit, compare them briefly.
# If no products match, say so clearly.
# === PRODUCT DATA START ===
# {context}
# === PRODUCT DATA END ===

# Question: {question}
# Answer like a friendly salesperson, including model names, specs and prices in rupees.
# When answering use the following template for each product you list:

# Device name
# Description
# Specs: 
#     - CPU
#     - RAM
#     - Storage
#     - Screen size
# Price
# Product link
# produce image url                                    
# """)


# prompt = ChatPromptTemplate.from_template("""
# You are a helpful product expert for an electronics store.
# Use the following product data to answer the user's question accurately.
# If multiple products fit, compare them briefly.
# If no products match, say so clearly.
# === PRODUCT DATA START ===
# {context}
# === PRODUCT DATA END ===

# Question: {question}
# Answer like a friendly salesperson, including model names, specs and prices in rupees.
# When answering use the following template for each product you list:

# Device name
# ![Product](insert image url here)
# Description
# Specs: 
#     - CPU
#     - RAM
#     - Storage
#     - Screen size
# Price
# Product link
# ![Product Image](image_url)
# Make sure the image_url is replaced with the EXACT image url recieved from the context WITH OUT MAKING ANY CHANGES using the Markdown image syntax exactly like:
# ![Product Image](https://example.com/image.jpg)
# """)


prompt = ChatPromptTemplate.from_template("""
You are a helpful product expert for an electronics store.
Use the following product data to answer the user's question accurately.
If multiple products fit, compare them briefly.
If no products match, say so clearly.
=== PRODUCT DATA START ===
{context}
=== PRODUCT DATA END ===

Question: {question}
Answer like a friendly salesperson, including model names, specs and prices in rupees.
When answering use the following template for each product you list:

Device name
Description
Specs: 
    - CPU
    - RAM
    - Storage
    - Screen size
Price
![Product Image](image_url)
Use the image_url EXACTLY as provided in the context — do NOT modify, rewrite, reorder, or reconstruct the URL in any way.
Insert the image using Markdown in this exact format:
![Product Image](https://example.com/image.jpg)
""")


def format_docs(docs):
    formatted = []

    for d in docs:
        meta = d.metadata
        print(meta)
        print(meta.get('product_image'))
        content = f"""
        Product Name: {meta.get('product_name')}
        Description: {meta.get('description')}
        Brand: {meta.get('brand')}
        Price: ₹{meta.get('price')}
        CPU: {meta.get('cpu')}
        GPU: {meta.get('gpu')}
        RAM: {meta.get('ram_gb')} GB
        STORAGE: {meta.get('storage_gb')} GB
        SCREEN SIZE: {meta.get('screen_size_inches')} inches
        SCREEN REFERESH RATE: {meta.get('screen_refresh_rate')} Hz
        Tags: {meta.get('tags')}
        IMAGE URL: {meta.get('image_url')}
        """.strip()
        formatted.append(content)

    print("\n\n---\n\n".join(formatted))
    return "\n".join(formatted)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
)

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.get("/ask")
async def ask(query: str):
    try:
        result = rag_chain.invoke(query)
        print(result)
        return {
            "answer": result.content
        }
    except Exception as e:
        return {
            "error": str(e)
        }

# python -m uvicorn rag:app --reload