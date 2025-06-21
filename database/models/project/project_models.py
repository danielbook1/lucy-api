from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.types import JSON
from ..base import Base
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Client


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
    client_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("client.id"), nullable=True
    )
    client: Mapped[Optional["Client"]] = relationship(back_populates="projects")

    # Tasks
