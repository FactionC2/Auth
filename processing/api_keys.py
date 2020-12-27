from typing import List

import bcrypt
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session, Query
from processing.users import get_role_by_id, get_user_by_id
from factionpy.logger import log

from database.models import ApiKeys, UserRoles


def random_string(length=15):
    import random
    import string
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])


def new_api_key(db: Session, api_key_description: str, user_id: UUID, role_id: UUID = None):
    api_key = ApiKeys()
    api_key.user_id = user_id

    # Role ID is used for API keys created by Faction (for services, transports, etc)
    if role_id:
        api_key.role_id = role_id
    api_key.description = api_key_description

    token = random_string(48)
    api_key.name = random_string(16)
    api_key.key = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())

    key_value = "{}.{}".format(api_key.name, token)

    db.add(api_key)
    db.commit()
    return {
        'id': api_key.id,
        'api_key': key_value
    }


def get_api_key_by_id(db: Session, api_key_id: UUID):
    return db.query(ApiKeys).get(api_key_id).first()


def get_api_key_by_name(db: Session, api_key_name: str):
    return db.query(ApiKeys).fir_by(name=api_key_name).first()


def get_api_key_by_description(db: Session, api_key_description: str) -> List[Query]:
    return db.query(ApiKeys).filter(ApiKeys.description == api_key_description)


def disable_key(db: Session, api_key: ApiKeys) -> None:
    log(f"Disabling API Key: {api_key.name}")
    api_key.enabled = False
    api_key.visible = False
    db.add(api_key)
    db.commit()


def verify_api_key(db: Session, api_key):
    access_key_name, access_secret = api_key.split(".", 1)
    log(f'Got API Key: {access_key_name}')

    api_key = get_api_key_by_name(db, access_key_name)
    if api_key and api_key.enabled:
        log('Returning User with Id: {0}'.format(str(api_key.user_id)))
        user = get_user_by_id(api_key.user_id)
        if user.enabled and bcrypt.checkpw(access_secret.encode('utf-8'), api_key.key):
            api_key.last_used = datetime.utcnow()
            db.add(api_key)
            user.last_login = datetime.utcnow()
            db.add(user)
            db.commit()
            role_id = user.role_id
            return dict({
                "username": user.username,
                "id": user.id,
                "role_name": get_role_by_id(db, role_id).name,
                "enabled": user.enabled,
                "visible": user.visible,
                "created": user.created,
                "last_login": user.last_login,
                "api_key_name": api_key.name,
                "api_key_description": api_key.description
            })
    return None
