from flask import request, Blueprint
from processing.users import create_user, authenticate_user, get_user_by_username, get_role_name, get_role_id
from processing.api_keys import new_api_key, verify_api_key
import jwt

from factionpy.logger import log
from factionpy.config import get_config_value

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
    access_key = request.headers.get('x-faction-api-key', None)
    if access_key:
        user_info = verify_api_key(access_key)
        if user_info:
            return user_info
        else:
            return {"success": False, "message": "invalid api key or secret"}
    else:
        return {"success": False, "message": "missing required headers: access_key_name or access_secret"}


# curl http://localhost:5000/verify/ -H 'x-api-key: oe0y7pq3xicEEw8u.6rdnbyOJowV9iIFdFtMweTCsi03Tnu4Qqj4T8qUcvKpQwVPh'
@auth.route('/verify/hasura/', methods=['GET'])
def hasura_verify():
    access_key = request.headers.get('x-faction-api-key', None)
    if access_key:
        user_info = verify_api_key(access_key)

        if user_info:
            return dict({
                "X-Hasura-User-Id": user_info["id"],
                "X-Hasura-Role": user_info["role"]
            })
        else:
            return {"success": "False", "message": "invalid api key or secret"}, 401
    else:
        return {"success": "False", "message": "missing required headers: access_key"}


@auth.route('/auth/service/', methods=['GET'])
def bootstrap():
    token = request.headers.get('X-Faction-Service-Auth')
    faction_key = get_config_value('FACTION_SERVICE_SECRET')
    try:
        result = jwt.decode(token, faction_key)
    except Exception as e:
        return dict({
            "success": False,
            "message": f"Could not decode JWT. Error: {e}"
        }), 401
    service_name = result.get("service_name", None)
    role = result.get("role", None)

    if not service_name or not role:
        return dict({
            "success": False,
            "message": "JWT does not contain required data."
        }), 401
    else:
        role_id = get_role_id(role)
        user = get_user_by_username("system")
        result = new_api_key(f"[service] {service_name}", user_id=user.id, role_id=role_id)
        return dict({
            "success": True,
            "api_key": result['api_key']
        })


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
