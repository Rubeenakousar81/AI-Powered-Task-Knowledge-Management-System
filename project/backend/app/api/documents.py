import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, ActivityLog
from app.auth_helper import get_current_user, admin_only
from app.ai_search import add_to_index, remove_from_index

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/")
async def upload_doc(
    title: str = Form(...),
    file:  UploadFile = File(...),
    db:    Session = Depends(get_db),
    admin  = Depends(admin_only)
):
    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files allowed")

    # save file to disk
    # storing in uploads folder for now
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # read content for indexing (only txt for now)
    content = ""
    if file.filename.endswith(".txt"):
        with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    # save to db
    doc = Document(
        title       = title,
        filename    = file.filename,
        content     = content[:5000],  # only storing first 5000 chars, full content is in the file
        uploaded_by = admin.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # add to vector index
    if content:
        add_to_index(doc.id, doc.title, content)

    db.add(ActivityLog(user_id=admin.id, action="doc_upload", detail=f"uploaded: {file.filename}"))
    db.commit()

    return {"message": "Document uploaded!", "doc_id": doc.id}


@router.get("/")
def list_docs(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "id":          d.id,
            "title":       d.title,
            "filename":    d.filename,
            "uploaded_by": d.uploaded_by,
            "created_at":  str(d.created_at)
        }
        for d in docs
    ]


@router.delete("/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db), admin = Depends(admin_only)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # remove from vector index too
    remove_from_index(doc_id)

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
