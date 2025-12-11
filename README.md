# Prerequisites:
1. Docker desktop
2. Python

# How to run:
1. Clone the repo by running the following command in terminal 
`git clone https://github.com/joshua-rajj/Chatbot`

2. Cd to the repo
  `cd Chatbot`

3. Install dependencies
   `pip3 install -r requirements.txt`
4. Create a redis vector db:
   `docker run -d \
  --name redis-vector \
  -p 6379:6379 \
  redis/redis-stack:latest`
5. Load data into the vector db
   `python3 load_data.py`

6. Run the chatbot
   `python -m uvicorn rag:app --reload`
