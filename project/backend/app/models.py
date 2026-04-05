from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100))
    email      = Column(String(150), unique=True, index=True)
    password   = Column(String(255))
    role       = Column(String(20), default="user")  # admin or user
    created_at = Column(DateTime, server_default=func.now())


class Task(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(255))
    description = Column(Text, nullable=True)
    status      = Column(String(20), default="pending")  # pending or completed
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_by  = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime, server_default=func.now())

    # to get user info when fetching tasks
    assignee = relationship("User", foreign_keys=[assigned_to])


class Document(Base):
    __tablename__ = "documents"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(255))
    filename    = Column(String(255))
    content     = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime, server_default=func.now())


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    action     = Column(String(100))   # login, task_update, doc_upload, search
    detail     = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class SearchLog(Base):
    __tablename__ = "search_logs"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    query      = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
