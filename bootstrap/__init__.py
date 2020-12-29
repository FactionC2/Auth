from time import sleep

from sqlalchemy.orm import Session
from factionpy.logger import log

from database import SessionLocal
from processing.users import create_user, create_user_role, get_role_by_name, get_user_by_username
from factionpy.config import FACTION_ADMIN_PASSWORD, FACTION_SYSTEM_PASSWORD
from factionpy.models import AvailableUserRoles

DEFAULT_USERS = [
    {
        "username": "admin",
        "password": FACTION_ADMIN_PASSWORD
    },
    {
        "username": "system",
        "password": FACTION_SYSTEM_PASSWORD
    }
]


def create_default_user_roles():
    running = True
    while running:
        try:
            for role in AvailableUserRoles:
                log(f"checking if role has been created: {role.value}")
                db = SessionLocal()
                result = get_role_by_name(db, role.value)
                if not result:
                    log("creating user role: {}".format(role.value))
                    create_user_role(db, role.value)
                db.close()
            running = False
        except Exception as e:
            log(f"Failed to create default user roles. Sleeping 3 seconds and trying again. Error: {e}", "error")
            sleep(3)


def create_default_users():
    running = True
    while running:
        try:
            for default_user in DEFAULT_USERS:
                db = SessionLocal()
                log(f"checking if {default_user['username']} has been created", "info")
                user = get_user_by_username(db, default_user['username'])
                if not user:
                    log("creating users")
                    create_user(db, default_user['username'], default_user['password'], "admin")
                db.close()
            running = False
        except Exception as e:
            log(f"Failed to create default users. Sleeping 3 seconds and trying again. Error: {e}", "error")
            sleep(3)
