from sqlalchemy.dialects.postgresql import UUID
from database import db
import uuid


class ApiKeys(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()", unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'))
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    key = db.Column(db.LargeBinary)
    created = db.Column(db.DateTime, server_default="now()")
    last_used = db.Column(db.DateTime)
    enabled = db.Column(db.Boolean, server_default="TRUE")
    visible = db.Column(db.Boolean, server_default="TRUE")

    def __repr__(self):
        return '<ApiKey: %s>' % str(self.Id)


