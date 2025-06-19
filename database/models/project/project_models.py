from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.types import JSON
from ..base import Base


class Project(Base):
    __tablename__ = "project"

    # Identification
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    tags = Column(JSON, default=list)

    # Dates
    start_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, default=None)

    # Client

    # Tasks
