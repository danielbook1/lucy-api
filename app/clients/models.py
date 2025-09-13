import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # relationship back to user
    user = relationship("User", back_populates="clients")
