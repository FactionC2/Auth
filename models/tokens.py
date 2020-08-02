from sqlalchemy.dialects.postgresql import UUID
from database import db


class Tokens(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()", unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'))
    description = db.Column(db.String)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    enabled = db.Column(db.Boolean, server_default="TRUE")
    visible = db.Column(db.Boolean, server_default="TRUE")
    expires = db.Column(db.DateTime, nullable=False)
    created = db.Column(db.DateTime, server_default="now()")
    last_used = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'expires': self.expires
        }

    def __repr__(self):
        return '<ApiKey: %s>' % str(self.Id)
