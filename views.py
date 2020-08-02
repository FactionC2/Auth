from flask import request, Blueprint, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, \
    jwt_required, fresh_jwt_required
from processing.users import create_user, authenticate_user, get_user_by_username, get_role_name, get_role_id
from processing.tokens import admin_required, add_token_to_database

from logger import log
auth = Blueprint('auth-service', __name__,
                 template_folder='templates',
                 static_folder='static')


# curl -X POST http://localhost:5000/login/ -H 'Content-Type: application/json' -d '{"username": "test2", "password": "test"}'
@auth.route('/login/', methods=['POST'])
def login():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
    except:
        return {"success": False, "message": "invalid request"}, 401

    if authenticate_user(username, password):
        user = get_user_by_username(username)
        token = create_access_token(identity=user, fresh=True)
        refresh_token = create_refresh_token(user)

        add_token_to_database(token)
        add_token_to_database(refresh_token)

        return jsonify({
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "user_role": get_role_name(user.role_id),
            "access_token": token,
            "refresh_token": refresh_token
        }), 200
    else:
        log("login_faction_user", "Username or password no good")
        return jsonify({
            "success": False,
            "message": 'Invalid Username or Password'
        }), 401


@auth.route('/refresh/', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user, fresh=True)
    add_token_to_database(access_token)
    ret = {
        'success': True,
        'access_token': access_token
    }
    return jsonify(ret), 200


@auth.route('/revoke/<token_id>', methods=['PUT'])
@jwt_required
def revoke_token(token_id):
    user_identity = get_jwt_identity()
    try:
        revoke_token(token_id, user_identity)
        return jsonify({'success': True, 'message': f'Token revoked: {token_id}'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Token could not be revoked: {e}'})


# curl -X POST https://localhost:8443/api/v1/auth/register/ -H 'Content-Type: application/json' -d '{"username": "test2", "password": "test", "user_role": "operator"}'
@auth.route('/register/', methods=['POST'])
@fresh_jwt_required
@admin_required
def register_user():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user_role = request.json.get('user_role', None)
    if username and password and user_role:
        result = create_user(username, password, user_role)
        return jsonify(result)
    return jsonify(dict({
        "success": "False",
        "message": "Missing value. Expected values: username, password, user_role"
    }), 400)
