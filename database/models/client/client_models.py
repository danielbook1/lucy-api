from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List
from ..base import Base


class Client(Base):
    # Identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # Prokects
    # projects: Mapped[List[Project]] = relationship(
    #     back_populates="client", lazy="selectin"
    # )
