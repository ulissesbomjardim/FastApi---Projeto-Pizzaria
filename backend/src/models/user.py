from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    username = Column('username', String(50), unique=True, index=True, nullable=False)
    email = Column('email', String(100), unique=True, index=True, nullable=False)
    hashed_password = Column('hashed_password', String(255), nullable=False)
    is_active = Column('is_active', Boolean, default=True)
    is_admin = Column('is_admin', Boolean, default=False)

    # Relacionamentos
    orders = relationship('Order', back_populates='user')

    def __init__(self, username: str, email: str, hashed_password: str, is_active: bool = True, is_admin: bool = False):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_admin = is_admin
