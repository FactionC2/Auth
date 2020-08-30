from models.user import Users, UserRoles
from processing.users import create_user, create_user_role
from config import ADMIN_PASSWORD, SYSTEM_PASSWORD
from factionpy.logger import log

AUTH_ROLES = ["admin", "service", "super-user", "user", "transport", "read-only", "nobody"]


def create_default_user_roles():
    log("checking if user_roles exist")
    roles = UserRoles.query.all()
    if len(roles) == 0:
        for role in AUTH_ROLES:
            log("creating user role: {}".format(role))
            create_user_role(role)


def create_default_users():
    log("checking if users exist", "info")
    users = Users.query.all()
    if len(users) == 0:
        log("creating users")
        create_user("admin", ADMIN_PASSWORD, "admin")
        create_user("system", SYSTEM_PASSWORD, "admin")
