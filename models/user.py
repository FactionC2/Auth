from sqlalchemy.dialects.postgresql import UUID
import bcrypt
from logger import log
from database import db
import uuid


class Users(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()", unique=True, nullable=False)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.LargeBinary)
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False)
    created = db.Column(db.DateTime, server_default="now()")
    last_login = db.Column(db.DateTime)
    enabled = db.Column(db.Boolean, server_default="TRUE")
    visible = db.Column(db.Boolean, server_default="TRUE")

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


class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    users = db.relationship('Users', backref='user_roles', lazy=True)

    def __repr__(self):
        return '<Role: %s>' % str(self.Id)

