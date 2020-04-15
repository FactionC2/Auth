from flask import jsonify, request, Blueprint, current_app
from processing.users import create_user, authenticate_user, get_user_by_username, get_role_name
from processing.api_keys import new_api_key, verify_api_key
from itsdangerous import base64_encode
from logger import log
auth = Blueprint('auth', __name__,
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
        token = new_api_key("session", user.id)

        return dict({
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "user_role": get_role_name(user.role_id),
            "access_key": token['api_key']
        })
    else:
        log("login_faction_user", "Username or password no good")
        return dict({
            "success": False,
            "message": 'Invalid Username or Password'
        }), 401


# curl http://localhost:5000/verify/ -H 'x-api-key: oe0y7pq3xicEEw8u.6rdnbyOJowV9iIFdFtMweTCsi03Tnu4Qqj4T8qUcvKpQwVPh'
@auth.route('/verify/', methods=['GET'])
def verify():
    access_key = request.headers.get('x-api-key', None)
    if access_key:
        user = verify_api_key(access_key)
        if user:
            return dict({
                "success": True,
                "username": user.username,
                "id": user.id,
                "role": get_role_name(user.role_id),
                "enabled": user.enabled,
                "visible": user.visible,
                "created": user.created,
                "last_login": user.last_login
            })
        else:
            return {"success": False, "message": "invalid api key or secret"}
    else:
        return {"success": False, "message": "missing required headers: access_key_name or access_secret"}


# curl http://localhost:5000/verify/ -H 'x-api-key: oe0y7pq3xicEEw8u.6rdnbyOJowV9iIFdFtMweTCsi03Tnu4Qqj4T8qUcvKpQwVPh'
@auth.route('/verify/hasura/', methods=['GET'])
def hasura_verify():
    access_key = request.headers.get('x-api-key', None)
    if access_key:
        user = verify_api_key(access_key)
        if user:
            return dict({
                "X-Hasura-User-Id": user.id,
                "X-Hasura-Role": get_role_name(user.role_id)
            })
        else:
            return {"success": False, "message": "invalid api key or secret"}
    else:
        return {"success": False, "message": "missing required headers: access_key_name or access_secret"}


# curl -X POST http://localhost:5000/register/ -H 'Content-Type: application/json' -d '{"username": "test2", "password": "test", "user_role": "operator"}'
@auth.route('/register/', methods=['POST'])
def register_user():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user_role = request.json.get('user_role', None)

    if username and password and user_role:
        result = create_user(username, password, user_role)
        return result
    return {"success": False, "message": "Missing value. Expected values: username, password, user_role"}, 400
