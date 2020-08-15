from flask import Flask
from database import db
from views import auth
from config import DB_URI
from bootstrap import create_default_user_roles, create_default_users


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    app.config["DEBUG"] = True
    db.init_app(app)
    app.register_blueprint(auth, url_prefix='')
    app.app_context().push()
    create_default_user_roles()
    create_default_users()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0")
