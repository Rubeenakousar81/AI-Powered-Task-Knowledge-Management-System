# AI Task & Knowledge Management System

This is my project for the intern assignment. I built a full stack app where admin can upload documents and assign tasks, and users can search through those documents using AI search.

Took me around 2-3 days to build this.

---

## Tech Stack

- Python + FastAPI for the backend
- MySQL for the database
- JWT for login/auth
- sentence-transformers + FAISS for the AI search part (runs locally, no external API needed)
- React for the frontend

---

## How to Run It

### 1. Setup MySQL

Just create the database first:

```sql
CREATE DATABASE ai_task_db;
```

Tables get created automatically when backend starts (SQLAlchemy does that).

### 2. Backend

```bash
cd backend

python -m venv venv
source venv/bin/activate    # windows: venv\Scripts\activate

pip install -r requirements.txt
```

Before running, open `app/database.py` and update the MySQL password to yours.

Then:

```bash
uvicorn main:app --reload
```

Backend runs at http://localhost:8000  
API docs at http://localhost:8000/docs (fastapi generates this automatically, very helpful for testing)

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

Opens at http://localhost:3000

---

## What I Built

The app has two roles - admin and user.

**Admin** can upload .txt documents, create tasks and assign them to users.

**User** can see their tasks, mark them done, and search documents.

When a document is uploaded, the text gets split into chunks and each chunk is converted into a vector (embedding) using sentence-transformers. These vectors are stored in FAISS which is a vector database. This is the AI/semantic search part.

When someone searches, the query also becomes a vector and FAISS finds the closest matching document chunks. So its actual semantic search not just keyword matching which i thought was pretty cool.

Admin also has an analytics page showing task completion stats and most searched queries.

---

## Folder Structure

```
backend/
  main.py              
  requirements.txt
  app/
    database.py       # mysql connection setup
    models.py         # all db tables in one file
    auth_helper.py    # jwt + password functions
    ai_search.py      # embedding + faiss search logic
    api/
      auth.py
      tasks.py
      documents.py
      search_analytics.py   # search and analytics combined

frontend/
  src/
    App.js
    api.js            # axios instance
    styles.css
    components/
      Navbar.jsx
    pages/
      Login.jsx
      Register.jsx
      Dashboard.jsx
      Tasks.jsx
      Documents.jsx
      Search.jsx
      Analytics.jsx
```

---

## API Endpoints

| Method | Endpoint | Access |
|--------|----------|--------|
| POST | /auth/register | public |
| POST | /auth/login | public |
| GET | /auth/users | admin |
| GET | /tasks | all (users see only theirs) |
| GET | /tasks?status=pending | filter by status |
| POST | /tasks | admin |
| PATCH | /tasks/{id} | user or admin |
| DELETE | /tasks/{id} | admin |
| GET | /documents | all |
| POST | /documents | admin |
| DELETE | /documents/{id} | admin |
| GET | /search?q=keyword | all |
| GET | /analytics | admin |

---

## Few things to note

- If faiss or sentence-transformers arent installed it falls back to basic keyword search so atleast the app doesnt break
- Uploaded files go into an `uploads/` folder
- FAISS index is saved to disk so it doesnt reset every time you restart
