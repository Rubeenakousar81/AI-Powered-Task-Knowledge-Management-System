from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ActivityLog, SearchLog, Task, Document, User
from app.auth_helper import get_current_user, admin_only
from app.ai_search import search_docs

# ── Search ────────────────────────────────────────────────────────────────────
search_router = APIRouter()

@search_router.get("/")
def search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    results = search_docs(q, top_k=5)

    # log the search
    db.add(SearchLog(user_id=current_user.id, query=q))
    db.add(ActivityLog(user_id=current_user.id, action="search", detail=q))
    db.commit()

    # format results
    output = []
    for r in results:
        snippet = r["meta"]["chunk"][:300]
        output.append({
            "doc_id":   r["meta"]["doc_id"],
            "title":    r["meta"]["title"],
            "snippet":  snippet,
            "score":    round(r["score"], 3)
        })

    return output


# ── Analytics ─────────────────────────────────────────────────────────────────
analytics_router = APIRouter()

@analytics_router.get("/")
def analytics(db: Session = Depends(get_db), admin = Depends(admin_only)):
    total     = db.query(Task).count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    pending   = db.query(Task).filter(Task.status == "pending").count()
    total_docs  = db.query(Document).count()
    total_users = db.query(User).count()

    # top searched queries
    top_searches = (
        db.query(SearchLog.query, func.count(SearchLog.query).label("count"))
        .group_by(SearchLog.query)
        .order_by(func.count(SearchLog.query).desc())
        .limit(5)
        .all()
    )

    return {
        "total_tasks":     total,
        "completed":       completed,
        "pending":         pending,
        "total_documents": total_docs,
        "total_users":     total_users,
        "top_searches":    [{"query": q, "count": c} for q, c in top_searches]
    }
