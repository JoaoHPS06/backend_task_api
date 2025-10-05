# Task Manager API with Flask and MongoDB

This is a re-implementation of the task management API, exploring the NoSQL paradigm with MongoDB.

## Features
-   Full CRUD for tasks using a document-based database.
-   Flexible data modeling.
-   Built with Python, Flask, and `pymongo`.

## How to Run

1.  **Prerequisites:** Docker, Python 3.11+.
2.  **Start the Database:**
    ```bash
    docker run --name mongo-tarefas -e MONGO_INITDB_ROOT_USERNAME=user_tarefas -e MONGO_INITDB_ROOT_PASSWORD=pass_tarefas -p 27017:27017 -d mongo
    ```
3.  **Create the Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Start the Application:**
    ```bash
    python app_mongo.py
    ```
The API will be running on `http://localhost:5001`.
