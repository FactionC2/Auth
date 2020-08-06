from flask import request, Blueprint
from config import JWT_SECRET
from processing.users import create_user, authenticate_user, get_user_by_username, get_role_name, get_role_id
from processing.api_keys import new_api_key, verify_api_key, get_api_key_by_description, disable_key
import jwt

from logger import log
auth = Blueprint('auth-service', __name__,
                 template_folder='templates',
                 static_folder='static')


# curl -X POST http://localhost:5000/login/ \
# -H 'Content-Type: application/json' -d '{"username": "test2", "password": "test"}'
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
    authorization_header = request.headers.get('Authorization', None)
    token = None
    if authorization_header:
        if authorization_header.index(' ') > 0:
            token = authorization_header.split(' ')[1]
        else:
            token = authorization_header
    if token:
        user_info = verify_api_key(token)
        if user_info:
            return user_info
        else:
            return {"success": False, "message": "invalid api key or secret"}
    else:
        return {"success": False, "message": "missing or incorrectly formatted authorization header"}


# curl http://localhost:5000/verify/ \
# -H 'Authorization: Bearer oe0y7pq3xicEEw8u.6rdnbyOJowV9iIFdFtMweTCsi03Tnu4Qqj4T8qUcvKpQwVPh'
@auth.route('/verify/hasura/', methods=['GET'])
def hasura_verify():
    authorization_header = request.headers.get('Authorization', None)
    token = None
    if authorization_header:
        if authorization_header.index(' ') > 0:
            token = authorization_header.split(' ')[1]
        else:
            token = authorization_header
    if token:
        user_info = verify_api_key(token)

        if user_info:
            return dict({
                "X-Hasura-User-Id": user_info["id"],
                "X-Hasura-Role": user_info["role"]
            })
        else:
            return {"success": "False", "message": "invalid api key or secret"}, 401
    else:
        return {"success": "False", "message": "missing required headers: access_key"}


@auth.route('/service/', methods=['GET'])
def bootstrap():
    authorization_header = request.headers.get('Authorization', None)
    token = None
    if authorization_header:
        if authorization_header.index(' ') > 0:
            token = authorization_header.split(' ')[1]
        else:
            token = authorization_header
    log("auth_service", f"Got token: {token}")
    try:
        result = jwt.decode(token, JWT_SECRET, algorithms="HS256")
    except Exception as e:
        return dict({
            "success": False,
            "message": f"Could not decode JWT. Error: {e}"
        }), 401
    key_name = result.get("key_name", None)

    if not key_name:
        return dict({
            "success": False,
            "message": "JWT does not contain required data."
        }), 401
    else:
        role_id = get_role_id("admin")
        user = get_user_by_username("system")
        key_description = f"{key_name} (created from JWT)"
        existing_keys = get_api_key_by_description(key_description)
        for key in existing_keys:
            disable_key(key)
        result = new_api_key(
            key_description, user_id=user.id, role_id=role_id)
        return dict({
            "success": True,
            "api_key": result['api_key']
        })


# curl -X POST https://localhost:8443/api/v1/auth/register/ \
# -H 'Content-Type: application/json' -d '{"username": "test2", "password": "test", "user_role": "operator"}'
# TODO: Require actual authentication for this lol
@auth.route('/register/', methods=['POST'])
def register_user():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user_role = request.json.get('user_role', None)

    if username and password and user_role:
        result = create_user(username, password, user_role)
        return result
    return {"success": False, "message": "Missing value. Expected values: username, password, user_role"}, 400
