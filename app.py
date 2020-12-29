import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
import jwt

from factionpy.logger import log
from factionpy.fastapi import oauth2_scheme
from factionpy.config import FACTION_JWT_SECRET
from factionpy.models import AvailableUserRoles

from bootstrap import create_default_users, create_default_user_roles
from database import SessionLocal
from models.responses import LoginResponse, VerifyResponse, HasuraVerifyResponse, UserResponse
from processing.users import authenticate_user, get_role_by_name, get_user_by_username, create_user
from processing.api_keys import new_api_key, verify_api_key, get_api_key_by_description, disable_key

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# curl -X POST http://localhost:5000/login/ \
# -H 'Content-Type: application/json' -d '{"username": "test2", "password": "test"}'
@app.post('/login/', response_model=LoginResponse)
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)

    if user:
        token = new_api_key(db, "session", user.id)
        user_role = get_role_by_name(user.role_id)
        return LoginResponse.parse_obj({
                "user_id": user.id,
                "username": user.username,
                "user_role": user_role.name,
                "access_key": token['api_key']
            })
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=f"invalid username or password"
        )


# curl http://localhost:5000/verify/ \
# -H 'Authorization: oe0y7pq3xicEEw8u.6rdnbyOJowV9iIFdFtMweTCsi03Tnu4Qqj4T8qUcvKpQwVPh'
@app.get('/verify/', response_model=VerifyResponse)
def verify(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    log(f"Got token: {token}", "debug")
    user_info = verify_api_key(db, token)
    if user_info:
        return VerifyResponse.parse_obj(user_info)
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="invalid API key"
        )


# curl http://localhost:5000/verify/ \
# -H 'Authorization: Bearer oe0y7pq3xicEEw8u.6rdnbyOJowV9iIFdFtMweTCsi03Tnu4Qqj4T8qUcvKpQwVPh'
@app.get('/verify/hasura/', response_model=HasuraVerifyResponse)
def hasura_verify(db: Session = Depends(get_db), token=Depends(oauth2_scheme)):
    user_info = verify_api_key(db, token)
    if user_info:
        return HasuraVerifyResponse.parse_obj(user_info)
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=f"invalid_api_key"
        )


@app.get('/service/', response_model=LoginResponse)
def service_key_request(db: Session = Depends(get_db), token=Depends(oauth2_scheme)):
    try:
        result = jwt.decode(token, FACTION_JWT_SECRET, algorithms="HS256")
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="could not decode JWT. error: {e}"
        )
    key_name = result.get("key_name", None)

    if not key_name:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="JWT does not contain required data"
        )
    else:
        role = get_role_by_name(db, "admin")
        user = get_user_by_username(db, "system")
        log(f"got user: {user.username}", "debug")
        key_description = f"{key_name} (created from JWT)"
        log(f"getting keys with description: {key_description}", "debug")
        existing_keys = get_api_key_by_description(db, key_description)
        for key in existing_keys:
            if key.enabled:
                disable_key(db, key)
        result = new_api_key(db, key_description, user_id=user.id, role_id=role.id)
        return LoginResponse.parse_obj({
                "id": user.id,
                "username": user.username,
                "role_name": role.name,
                "enabled": user.enabled,
                "visible": user.visible,
                "created": user.created,
                "last_login": user.last_login,
                "access_key": result['api_key']
            })


# curl -X POST https://localhost:8443/api/v1/auth/register/ \
# -H 'Content-Type: application/json' -d '{"username": "test2", "password": "test", "user_role": "operator"}'
# TODO: Require actual authentication for this lol
@app.post('/register/', response_model=UserResponse)
def register_user(username: str, password: str, user_role: AvailableUserRoles, db: Session = Depends(get_db)):
    result = create_user(db, username, password, user_role)
    return UserResponse.parse_obj(result)


if __name__ == "__main__":
    create_default_user_roles()
    create_default_users()
    uvicorn.run(app, host="0.0.0.0", port=8000)
