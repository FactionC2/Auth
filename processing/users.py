from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func
import bcrypt

from models import User, UserRole
from database.models import Users, UserRoles
from factionpy.logger import log


def get_user_by_id(db: Session, user_id: UUID):
    return db.query(Users).get(user_id)


def get_user_by_username(db: Session, username: str):
    return db.query(Users).filter(func.lower(Users.username) == func.lower(username)).first()


def get_role_by_id(db: Session, role_id: UUID):
    log("Getting role name {0}".format(role_id))
    return db.query(UserRoles).get(role_id)


def get_role_by_name(db: Session, role_name: str):
    return db.query(UserRoles).filter(func.lower(UserRoles.name) == func.lower(role_name)).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    log("Checking " + username)
    user = get_user_by_username(db, username)

    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user.password):
            log("Login successful")
            return User.parse_obj(user)
    log("username or password no good")
    return None


def create_user(db: Session, username: str, password: str, role_name: str) -> User:
    log(f"Creating user {username}")

    user = Users()
    user.username = username
    user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user.created = datetime.utcnow()
    user.role_id = get_role_by_name(db, role_name).id
    user.enabled = True
    user.visible = True
    db.add(user)
    db.commit()
    return User.parse_obj(user)


def update_user(db: Session, user_id, username=None, role_id=None, enabled=None, visible=None) -> User:
    user = get_user_by_id(db, user_id)

    if username is not None:
        user.username = username

    if role_id is not None:
        user.role_id = role_id

    if enabled is not None:
        user.enabled = enabled

    if visible is not None:
        user.visible = visible

    db.add(user)
    db.commit()
    return User.parse_obj(user)


# This is called when an admin changes a users password
def update_password(db: Session, user_id: UUID, new_password: str):
    user = get_user_by_id(db, user_id)
    log("got user: " + user.username, "debug")
    user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    db.add(user)
    db.commit()
    return User.parse_obj(user)


def create_user_role(db: Session, role_name: str):
    user_role = UserRoles()
    user_role.name = role_name
    db.add(user_role)
    db.commit()
    return UserRole.parse_obj(user_role)
