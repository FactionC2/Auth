from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import bcrypt
from database import Base
from factionpy.logger import log


class ApiKeys(Base):
    __tablename__ = "api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()", unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    role_id = Column(Integer, ForeignKey('user_roles.id'))
    name = Column(String, unique=True)
    description = Column(String)
    key = Column(LargeBinary)
    created = Column(DateTime, server_default="now()")
    last_used = Column(DateTime)
    enabled = Column(Boolean, server_default="TRUE")
    visible = Column(Boolean, server_default="TRUE")

    def __repr__(self):
        return '<ApiKey: %s>' % str(self.id)


class Users(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()",
                   unique=True, nullable=False)
    username = Column(String, unique=True)
    password = Column(LargeBinary)
    role_id = Column(Integer, ForeignKey('user_roles.id'), nullable=False)
    created = Column(DateTime, server_default="now()")
    last_login = Column(DateTime)
    enabled = Column(Boolean, server_default="TRUE")
    visible = Column(Boolean, server_default="TRUE")

    def __repr__(self):
        return '<User: %s>' % str(self.username)


class UserRoles(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    users = relationship('Users', backref='user_roles', lazy=True)

    def __repr__(self):
        return '<Role: %s>' % str(self.id)
