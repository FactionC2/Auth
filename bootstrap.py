from logger import log
from models.user import Users, UserRoles
from processing.users import create_user, create_user_role
from config import ADMIN_PASSWORD, SYSTEM_PASSWORD

AUTH_ROLES = ["admin", "agent", "operator", "read_only", "transport", "nobody"]


def create_default_user_roles():
    log("create_default_user_roles", "checking if user roles exist")
    roles = UserRoles.query.all()
    if len(roles) == 0:
        for role in AUTH_ROLES:
            log("create_default_user_roles", "creating user role: {}".format(role))
            create_user_role(role)


def create_default_users():
    log("create_default_users", "checking if users exist")
    users = Users.query.all()
    if len(users) == 0:
        log("create_default_users", "creating users")
        create_user("system", SYSTEM_PASSWORD, "nobody")
        create_user("admin", ADMIN_PASSWORD, "admin")

