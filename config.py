import os

FLASK_SECRET = os.environ.get("FLASK_SECRET")
JWT_SECRET = os.environ.get("JWT_SECRET")
DB_URI = os.environ.get("FACTION_DB_URI")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
SYSTEM_PASSWORD = os.environ.get("SYSTEM_PASSWORD")
