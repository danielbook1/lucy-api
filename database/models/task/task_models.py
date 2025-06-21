from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING
from ..base import Base

if TYPE_CHECKING:
    from ..project import Project


class Task(Base):
    __tablename__ = "task"

    # Identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # Status
    start_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, default=None)
    is_complete = Column(Boolean, default=False)

    # Metrics
    estimated_hours = Column(Float, default=None)
    actual_hours = Column(Float, default=None)

    # Project
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("project.id"), nullable=True
    )
    project: Mapped[Optional["Project"]] = relationship(back_populates="tasks")
