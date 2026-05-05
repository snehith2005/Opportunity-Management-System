import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/admin_portal"
    SQLALCHEMY_TRACK_MODIFICATIONS = False