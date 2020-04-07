from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token, jwt_refresh_token_required,
    get_jwt_identity
)

from config import JWT_SECRET
from user import authenticate_user

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET  # Change this!
jwt = JWTManager(app)


@app.route('/login/', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if authenticate_user(username, password):
        # create_access_token supports an optional 'fresh' argument,
        # which marks the token as fresh or non-fresh accordingly.
        # As we just verified their username and password, we are
        # going to mark the token as fresh here.
        ret = {
            'success': True,
            'access_token': create_access_token(identity=username, fresh=True),
            'refresh_token': create_refresh_token(identity=username)
        }
        return jsonify(ret), 200
    else:
        return jsonify({
            "success": False,
            "message": "Bad username or password"}), 401


# Refresh token endpoint. This will generate a new access token from
# the refresh token, but will mark that access token as non-fresh,
# as we do not actually verify a password in this endpoint.
@app.route('/refresh/', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, fresh=False)
    ret = {
        'success': True,
        'access_token': new_token}
    return jsonify(ret), 200


# Fresh login endpoint. This is designed to be used if we need to
# make a fresh token for a user (by verifying they have the
# correct username and password). Unlike the standard login endpoint,
# this will only return a new access token, so that we don't keep
# generating new refresh tokens, which entirely defeats their point.
@app.route('/login/fresh/', methods=['POST'])
def fresh_login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if authenticate_user(username, password):
        new_token = create_access_token(identity=username, fresh=True)
        ret = {
            'success': True,
            'access_token': new_token}
        return jsonify(ret), 200
    return jsonify({
        "success": False,
        "message": "Bad username or password"}), 401


if __name__ == '__main__':
    app.run()
