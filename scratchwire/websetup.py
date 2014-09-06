from scratchwire import app
from scratchwire import config_app
from scratchwire.model import db

def setup_app(command, conf, vars):
    """
    Initialize a fresh install of this application.
    """
    config_app(conf)
    db.create_all()
