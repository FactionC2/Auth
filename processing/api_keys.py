import bcrypt
import secrets

from datetime import datetime

from database import db
from models.api_key import ApiKeys
from models.user import Users


def api_key_json(api_key):
    return {
        "id": api_key.id,
        "name": api_key.name,
        "owner_id": api_key.owner_id,
        "type": api_key.type,
        "enabled": api_key.enabled,
        "visible": api_key.visible
    }


def random_string(length=15):
    import random
    import string
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])


def new_api_key(api_key_type, user_id, owner_id=None):
    api_key = ApiKeys()
    api_key.user_id = user_id
    api_key.owner_id = user_id

    # Owner ID is used when an api key is created for another account, for example when a user creates a new transport
    # the api key for the transport is created under the system user (who has no privs)
    if owner_id:
        api_key.owner_id = owner_id
    api_key.type = api_key_type

    token = random_string(48)
    api_key.name = random_string(16)
    api_key.key = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())

    key_value = "{}.{}".format(api_key.name, token)

    db.session.add(api_key)
    db.session.commit()
    return {
        'success': True,
        'id': api_key.id,
        'api_key': key_value
    }


def get_api_key(api_key_id='all'):
    keys = []
    results = []
    if api_key_id == 'all':
        keys = ApiKeys.query.all()
    else:
        keys.append(ApiKeys.query.get(api_key_id))

    for key in keys:
        results.append(api_key_json(key))

    return {
        'Success': True,
        'Results': results
    }


def get_api_key_name(api_key_id):
    key = ApiKeys.query.get(api_key_id)
    return key.name


def verify_api_key(api_key):
    access_key_name, access_secret = api_key.split(".")
    print('Got API KEY: {0}'.format(access_key_name))
    print('Got API Secret: {}'.format(access_secret))

    api_key = ApiKeys.query.filter_by(name=access_key_name).first()
    if api_key and api_key.enabled:
        print('Returning User with Id: {0}'.format(str(api_key.user_id)))
        user = Users.query.get(api_key.user_id)
        if user.enabled and bcrypt.checkpw(access_secret.encode('utf-8'), api_key.key):
            api_key.last_used = datetime.utcnow()
            db.session.add(api_key)
            user.last_login = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            return user
    return None
