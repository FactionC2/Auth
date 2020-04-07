from datetime import datetime

import bcrypt
from sqlalchemy import func

from logger import log
from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.LargeBinary)
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'), nullable=False)
    created = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    enabled = db.Column(db.Boolean)
    visible = db.Column(db.Boolean)

    def change_password(self, current_password, new_password):
        log("change_password", "Got password change request")
        if bcrypt.checkpw(current_password.encode('utf-8'), self.password) and self.enabled:
            self.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            db.session.add(self)
            db.session.commit()
            log("change_password", "Password changed")
            return dict({
                "success": True,
                "message": 'Changed password for user: {0}'.format(self.username)
            })
        log("change_password", "Current password incorrect")
        return {
            'success': False,
            'message': 'Invalid username or password.'
        }

    def __repr__(self):
        return '<User: %s>' % str(self.username)


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    users = db.relationship('user', backref='user_role', lazy=True)

    def __repr__(self):
        return '<Role: %s>' % str(self.Id)


def get_role_id(name):
    log("get_role_id", "Getting role {0}".format(name))
    role = UserRole.query.filter_by(Name=name.lower()).first()
    if role:
        log("get_role_id", "Got role {0}".format(role.id))
        return role.id
    else:
        log("get_role_id", "Role not found")
        return None


def get_role_name(role_id):
    log("get_role_name", "Getting role name {0}".format(role_id))
    role = UserRole.query.get(role_id)
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
    user = User.query.filter(func.lower(User.username) == func.lower(username)).first()

    if user:
        log("login_user", "Got user: " + user.username)
        if bcrypt.checkpw(password.encode('utf-8'), user.password) and user.Enabled:
            log("login_user", "Login successful")
            return True
    log("login_user", "username or password no good")
    return False


def create_user(username, password, role_name):
    user = User()
    user.username = username
    user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user.created = datetime.utcnow()
    user.role_id = get_role_id(role_name)
    user.enabled = True
    user.visible = True
    print('Creating user %s ' % user.username)
    db.session.add(user)
    db.session.commit()
    return dict({
        "success": True,
        "message": 'User {0} created successfully'.format(user.username)
    })


def update_user(user_id, username=None, role_id=None, enabled=None, visible=None):
    if user_id < 3:
        return dict({
            "success": False,
            "message": 'Can not change the admin or system user'
        })
    user = User.query.get(user_id)

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
    user = User.query.get(user_id)
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
    })
