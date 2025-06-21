from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped
from typing import List, TYPE_CHECKING
from ..base import Base

if TYPE_CHECKING:
    from ..project import Project


class Client(Base):
    __tablename__ = "client"

    # Identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # Projects
    projects: Mapped[List["Project"]] = relationship(
        back_populates="client", lazy="selectin"
    )
