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

# Sample output:
<img width="1710" height="984" alt="Screenshot 2025-12-17 at 8 43 06 AM" src="https://github.com/user-attachments/assets/83de4127-3bb6-456a-b8ce-be9805bf68d5" />
<img width="1707" height="932" alt="Screenshot 2025-12-17 at 8 43 33 AM" src="https://github.com/user-attachments/assets/1a359325-ba7c-4b5b-90ca-fbcb3cd9e98d" />
