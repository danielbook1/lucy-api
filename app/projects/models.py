import uuid
from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    completed_on = Column(DateTime, nullable=True)
    rate = Column(Float, nullable=True)
    hours_worked = Column(Float, nullable=False, default=0.0)
    use_client_rate = Column(Boolean, nullable=False, default=True)
    use_task_hours = Column(Boolean, nullable=False, default=True)

    deadline = Column(DateTime, nullable=True)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    client = relationship("Client", back_populates="projects")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="projects")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    completed_on = Column(DateTime, nullable=True)
    hours_worked = Column(Float, nullable=False, default=0.0)

    deadline = Column(DateTime, nullable=True)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="tasks")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")
