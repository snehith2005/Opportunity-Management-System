import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "mysql://root:mkFbJUcAPgXXBvokNPiOCbUGzWpgjEvw@trolley.proxy.rlwy.net:12876/railway"

    SQLALCHEMY_TRACK_MODIFICATIONS = False