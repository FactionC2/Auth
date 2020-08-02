from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims
from datetime import datetime

from database import db
from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import decode_token

from models.tokens import Tokens

# This whole file was largely taken from here: https://github.com/vimalloc/flask-jwt-extended/blob/master/examples/database_blacklist/blacklist_helpers.py


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['roles'] != 'admin':
            return jsonify(success=False, message='You do not have permissions to perform this action'), 403
        else:
            return fn(*args, **kwargs)
    return wrapper


class TokenNotFound(Exception):
    """
    Indicates that a token could not be found in the database
    """
    pass


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def add_token_to_database(encoded_token):
    """
    Adds a new token to the database. It is not revoked when it is added.
    :param identity_claim:
    """
    decoded_token = decode_token(encoded_token)
    user_id = decoded_token['user_id']
    role_id = decoded_token['role_id']
    description = decoded_token['description']
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    expires = _epoch_utc_to_datetime(decoded_token['exp'])

    db_token = Tokens(
        user_id=user_id,
        user_role=role_id,
        description=description,
        jti=jti,
        token_type=token_type,
        expires=expires
    )
    db.session.add(db_token)
    db.session.commit()


def is_token_revoked(decoded_token):
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    jti = decoded_token['jti']
    try:
        token = Tokens.query.filter_by(jti=jti).one()
        return token.enabled
    except NoResultFound:
        return True


def get_user_tokens(user_id):
    """
    Returns all of the tokens, revoked and unrevoked, that are stored for the
    given user
    """
    return Tokens.query.filter_by(user_id=user_id).all()


def disable_token(token_id, user):
    """
    Revokes the given token. Raises a TokenNotFound error if the token does
    not exist in the database
    """
    try:
        token = Tokens.query.filter_by(id=token_id, user_id=user).one()
        token.enabled = False
        db.session.commit()
    except NoResultFound:
        raise TokenNotFound("Could not find the token {}".format(token_id))


def enable_token(token_id, user):
    """
    Disables the given token. Raises a TokenNotFound error if the token does
    not exist in the database
    """
    try:
        token = Tokens.query.filter_by(id=token_id, user_id=user).one()
        token.enabled = True
        db.session.commit()
    except NoResultFound:
        raise TokenNotFound("Could not find the token {}".format(token_id))


def prune_database():
    """
    Delete tokens that have expired from the database.
    How (and if) you call this is entirely up you. You could expose it to an
    endpoint that only administrators could call, you could run it as a cron,
    set it up with flask cli, etc.
    """
    now = datetime.now()
    expired = Tokens.query.filter(Tokens.expires < now).all()
    for token in expired:
        db.session.delete(token)
    db.session.commit()
