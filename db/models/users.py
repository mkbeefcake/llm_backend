from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    passwd = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    socials = relationship("Social", back_populates="owner")

class Social(Base):
    __tablename__ = "socials"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="socials")