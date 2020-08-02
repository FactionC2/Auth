import os
from flask import Flask
from flask_jwt_extended import JWTManager
from database import db
from processing.tokens import is_token_revoked
from processing.users import get_role_name
from views import auth
from config import DB_URI, JWT_SECRET
from bootstrap import create_default_user_roles, create_default_users


app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
print(f"Using connection string: {DB_URI} ")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["DEBUG"] = True
app.config["JWT_SECRET_KEY"] = JWT_SECRET
app.config["JWT_ERROR_MESSAGE_KEY"] = "message"
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)
db.init_app(app)
app.register_blueprint(auth, url_prefix='')
#app.app_context().push()
create_default_user_roles()
create_default_users()


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    role_name = get_role_name(user.role_id)
    return {
        "user_id": user.id,
        "username": user.username,
        "user_role": role_name,
        "X-Hasura-User-Id": user.id,
        "X-Hasura-Role": role_name
    }


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
