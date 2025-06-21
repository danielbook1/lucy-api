from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.types import JSON
from ..base import Base
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from ..client import Client
    from ..task import Task


class Project(Base):
    __tablename__ = "project"

    # Identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    tags = Column(JSON, default=list)

    # Status
    start_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, default=None)
    is_complete = Column(Boolean, default=False)

    # Client
    client_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("client.id"), nullable=True
    )
    client: Mapped[Optional["Client"]] = relationship(back_populates="projects")

    # Tasks
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="project", lazy="selectin"
    )
