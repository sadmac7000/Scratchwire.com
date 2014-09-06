from flask import Flask, session
from flask.ext.session import Session

app = Flask(__name__)

def config_app(conf):
    """
    Load configuration from the paste INI file into Flask
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = conf['db.uri']

    if conf.has_key('debug') and conf['debug'] == "true":
        app.debug = True

    app.config['SESSION_TYPE'] = conf['session.type']
    Session(app)
    app.secret_key = conf['session.key']

def wsgi_factory(global_config, **local_config):
    """
    Get a WSGI-compliant object from our application
    """
    conf = global_config
    conf.update(local_config)
    config_app(conf)
    return app.wsgi_app

import scratchwire.model
import scratchwire.controller
import scratchwire.websetup
