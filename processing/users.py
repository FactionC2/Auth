from datetime import datetime
from sqlalchemy import func
import bcrypt

from database import db
from models.user import Users, UserRoles
from logger import log


def get_user_by_username(username):
    return Users.query.filter(func.lower(Users.username) == func.lower(username)).first()


def get_role_id(name):
    log("get_role_id", "Getting role {0}".format(name))
    role = UserRoles.query.filter_by(name=name.lower()).first()
    if role:
        log("get_role_id", "Got role {0}".format(role.id))
        return role.id
    else:
        log("get_role_id", "Role not found")
        return None


def get_role_name(role_id):
    log("get_role_name", "Getting role name {0}".format(role_id))
    role = UserRoles.query.get(role_id)
    if role:
        log("get_role_name", "Got role name {0}".format(role.name))
        return role.name
    else:
        log("get_role_name", "Role not found")
        return None


def user_json(user):
    log("user_json", "Working on user: {0}".format(user))
    last_login = None
    if user.LastLogin:
        last_login = user.LastLogin.isoformat()
    result = {
        'id': user.Id,
        'username': user.username,
        'role': get_role_name(user.role_id),
        'last_login': last_login,
        'created': user.created.isoformat(),
        'enabled': user.enabled,
        'visible': user.visible
    }
    log("user_json", "returning: {0}".format(result))
    return result


def authenticate_user(username, password):
    log("login_user", "Checking " + username)
    user = Users.query.filter(func.lower(Users.username) == func.lower(username)).first()

    if user:
        log("login_user", "Got user: " + user.username)
        if bcrypt.checkpw(password.encode('utf-8'), user.password) and user.enabled:
            log("login_user", "Login successful")
            return True
    log("login_user", "username or password no good")
    return False


def create_user(username, password, role_name):
    try:
        user = Users()
        user.username = username
        user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user.created = datetime.utcnow()
        user.role_id = get_role_id(role_name)
        user.enabled = True
        user.visible = True
        log("create_user", "Creating user: {}".format(username))
        db.session.add(user)
        db.session.commit()
        return dict({
            "success": True,
            "message": 'User {0} created successfully'.format(user.username)
        })
    except Exception as e:
        return dict({
            "success": False,
            "message": str(e)
        }), 500


def update_user(user_id, username=None, role_id=None, enabled=None, visible=None):
    if user_id < 3:
        return dict({
            "success": False,
            "message": 'Can not change the admin or system user'
        })
    user = Users.query.get(user_id)

    if username is not None:
        user.username = username

    if role_id is not None:
        user.role_id = role_id

    if enabled is not None:
        user.enabled = enabled

    if visible is not None:
        user.visible = visible

    db.session.add(user)
    db.session.commit()
    return dict({"success": True, "result": user_json(user)})


# This is called when an admin changes a users password
def update_password(user_id, new_password):
    user = Users.query.get(user_id)
    if user:
        log("update_password", "got user: " + user.username)
        user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        db.session.add(user)
        db.session.commit()
        return dict({
            "success": True,
            "message": 'Changed password for user: {0}'.format(user.username)
        })
    return dict({
        "success": False,
        "message": 'Invalid User Id.'
    }), 400


def create_user_role(role_name):
    try:
        user_role = UserRoles()
        user_role.name = role_name
        db.session.add(user_role)
        db.session.commit()
        return dict({
            "success": True,
            "message": "Role {} created".format(role_name)
        })
    except Exception as e:
        return dict({
            "success": False,
            "message": str(e)
        }), 500
