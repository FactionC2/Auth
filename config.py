import os

FLASK_SECRET = os.environ.get("FACTION_FLASK_SECRET")
JWT_SECRET = os.environ.get("FACTION_JWT_SECRET")
DB_URI = os.environ.get("FACTION_DB_URI")
ADMIN_PASSWORD = os.environ.get("FACTION_ADMIN_PASSWORD")
SYSTEM_PASSWORD = os.environ.get("FACTION_SYSTEM_PASSWORD")
