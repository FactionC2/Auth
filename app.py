from flask import Flask

from database import db
from config import DB_URI
from views import auth

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["DEBUG"] = True
db.init_app(app)
app.register_blueprint(auth, url_prefix='')


if __name__ == '__main__':
    app.run(host="0.0.0.0")
