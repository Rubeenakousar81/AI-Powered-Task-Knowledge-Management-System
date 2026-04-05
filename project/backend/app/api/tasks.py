from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Task, User, ActivityLog
from app.auth_helper import get_current_user, admin_only

router = APIRouter()

class TaskBody(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: int

class StatusBody(BaseModel):
    status: str  # pending or completed


@router.post("/")
def create_task(body: TaskBody, db: Session = Depends(get_db), admin = Depends(admin_only)):
    # make sure user exists
    user = db.query(User).filter(User.id == body.assigned_to).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task = Task(
        title       = body.title,
        description = body.description,
        assigned_to = body.assigned_to,
        created_by  = admin.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    db.add(ActivityLog(user_id=admin.id, action="task_create", detail=f"created task: {task.title}"))
    db.commit()

    return {"message": "Task created", "task_id": task.id}


@router.get("/")
def get_tasks(
    status:      Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task)

    # users can only see their own tasks
    # admins can see everyone's tasks
    if current_user.role != "admin":
        query = query.filter(Task.assigned_to == current_user.id)
    elif assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.created_at.desc()).all()

    result = []
    for t in tasks:
        assignee = db.query(User).filter(User.id == t.assigned_to).first()
        result.append({
            "id":          t.id,
            "title":       t.title,
            "description": t.description,
            "status":      t.status,
            "assigned_to": t.assigned_to,
            "assignee_name": assignee.name if assignee else "",
            "created_at":  str(t.created_at)
        })
    return result


@router.patch("/{task_id}")
def update_status(task_id: int, body: StatusBody, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # only the assigned user or admin can update
    if current_user.role != "admin" and task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not your task")

    task.status = body.status
    db.commit()

    db.add(ActivityLog(user_id=current_user.id, action="task_update", detail=f"task {task_id} -> {body.status}"))
    db.commit()

    return {"message": "Task updated", "status": body.status}


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), admin = Depends(admin_only)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
