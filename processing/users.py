from datetime import datetime
from sqlalchemy import func
import bcrypt

from database import db
from models.user import Users, UserRoles
from factionpy.logger import log


def get_user_by_username(username):
    return Users.query.filter(func.lower(Users.username) == func.lower(username)).first()


def get_role_id(name):
    log("Getting role {0}".format(name))
    role = UserRoles.query.filter_by(name=name.lower()).first()
    if role:
        log("Got role {0}".format(role.id))
        return role.id
    else:
        log("Role not found")
        return None


def get_role_name(role_id):
    log("Getting role name {0}".format(role_id))
    role = UserRoles.query.get(role_id)
    if role:
        log("Got role name {0}".format(role.name))
        return role.name
    else:
        log("Role not found")
        return None


def user_json(user):
    log("Working on user: {0}".format(user), "debug")
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
    log("returning: {0}".format(result), "debug")
    return result


def authenticate_user(username, password):
    log("Checking " + username)
    user = Users.query.filter(func.lower(Users.username) == func.lower(username)).first()

    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user.password):
            log("Login successful")
            return True
    log("username or password no good")
    return False


def create_user(username, password, role_name):
    log(f"Creating user {username}")

    try:
        user = Users()
        user.username = username
        user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user.created = datetime.utcnow()
        user.role_id = get_role_id(role_name)
        user.enabled = True
        user.visible = True
        db.session.add(user)
        db.session.commit()
        return dict({
            "success": "true",
            "message": 'User {0} created successfully'.format(user.username)
        })
    except Exception as e:
        log(f"Error creating user: {e}", "error")
        return dict({
            "success": "false",
            "message": str(e)
        }), 500


def update_user(user_id, username=None, role_id=None, enabled=None, visible=None):
    if user_id < 3:
        return dict({
            "success": "false",
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
    return dict({"success": "true", "result": user_json(user)})


# This is called when an admin changes a users password
def update_password(user_id, new_password):
    user = Users.query.get(user_id)
    if user:
        log("got user: " + user.username, "debug")
        user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        db.session.add(user)
        db.session.commit()
        return dict({
            "success": "true",
            "message": 'Changed password for user: {0}'.format(user.username)
        })
    return dict({
        "success": "false",
        "message": 'Invalid User Id.'
    }), 400


def create_user_role(role_name):
    try:
        user_role = UserRoles()
        user_role.name = role_name
        db.session.add(user_role)
        db.session.commit()
        return dict({
            "success": "true",
            "message": "Role {} created".format(role_name)
        })
    except Exception as e:
        return dict({
            "success": "false",
            "message": str(e)
        }), 500
