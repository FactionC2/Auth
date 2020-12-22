import bcrypt
import secrets

from datetime import datetime

from database import db
from models.api_key import ApiKeys
from models.user import Users
from processing.users import get_role_name
from factionpy.logger import log


def api_key_json(api_key):
    return {
        "id": api_key.id,
        "name": api_key.name,
        "role_id": api_key.role_id,
        "description": api_key.description,
        "enabled": api_key.enabled,
        "visible": api_key.visible
    }


def random_string(length=15):
    import random
    import string
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])


def new_api_key(api_key_description, user_id, role_id=None):
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

    db.session.add(api_key)
    db.session.commit()
    return {
        'success': 'true',
        'id': api_key.id,
        'api_key': key_value
    }


def get_api_key_by_id(api_key_id='all'):
    keys = []
    results = []
    if api_key_id == 'all':
        keys = ApiKeys.query.all()
    else:
        keys.append(ApiKeys.query.get(api_key_id))

    for key in keys:
        results.append(api_key_json(key))

    return {
        'success': 'true',
        'results': results
    }


def get_api_key_by_description(api_key_description):
    keys = None
    try:
        keys = ApiKeys.query.filter(ApiKeys.description == api_key_description)
    except Exception as e:
        log(f"error getting keys: {e}", "error")
    return keys


def disable_key(api_key):
    log(f"Disabling API Key: {api_key.name}")
    api_key.enabled = False
    api_key.visible = False
    db.session.add(api_key)
    db.session.commit()


def verify_api_key(api_key):
    access_key_name, access_secret = api_key.split(".", 1)
    log(f'Got API Key: {access_key_name}')

    api_key = ApiKeys.query.filter_by(name=access_key_name).first()
    if api_key and api_key.enabled:
        log('Returning User with Id: {0}'.format(str(api_key.user_id)))
        user = Users.query.get(api_key.user_id)
        if user.enabled and bcrypt.checkpw(access_secret.encode('utf-8'), api_key.key):
            api_key.last_used = datetime.utcnow()
            db.session.add(api_key)
            user.last_login = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            role_id = user.role_id
            if user.username.lower() == "system":
                role_id = api_key.role_id
            return dict({
                "username": user.username,
                "id": user.id,
                "role": get_role_name(role_id),
                "enabled": str(user.enabled),
                "visible": str(user.visible),
                "created": str(user.created),
                "last_login": str(user.last_login),
                "api_key": api_key.name,
                "api_key_description": api_key.description
            })
    return None
