# Task Manager API with Flask and PostgreSQL

This is a RESTful API for a task management system. The project is built with Python, Flask, and connects to a PostgreSQL database.

## Features
-   Full CRUD (Create, Read, Update, Delete) for tasks.
-   User registration and login system.
-   Authentication via JWT (JSON Web Tokens).
-   Ownership-based authorization (a user can only manage their own tasks).
-   Password hashing with `passlib` and `bcrypt`.

## How to Run

1.  **Prerequisites:** Docker, Python 3.11+.
2.  **Start the Database:**
    ```bash
    docker run --name pg-gerenciador-tarefas -e POSTGRES_USER=user_tarefas -e POSTGRES_PASSWORD=pass_tarefas -e POSTGRES_DB=db_tarefas -p 5432:5432 -d postgres
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
5.  **Create the Tables:** Connect to the `db_tarefas` database with a DB client (like DBeaver) and run the `CREATE TABLE` scripts for `usuarios` and `tarefas`.
6.  **Start the Application:**
    ```bash
    python app.py
    ```
The API will be running on `http://localhost:5000`.
