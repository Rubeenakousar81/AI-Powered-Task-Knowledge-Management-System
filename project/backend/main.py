from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.documents import router as docs_router
from app.api.search_analytics import search_router, analytics_router

# create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Task Manager")

# allowing react frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,      prefix="/auth")
app.include_router(tasks_router,     prefix="/tasks")
app.include_router(docs_router,      prefix="/documents")
app.include_router(search_router,    prefix="/search")
app.include_router(analytics_router, prefix="/analytics")

@app.get("/")
def home():
    return {"message": "backend is running!"}
