from flask import Flask, session
from flask.ext.session import Session

app = Flask(__name__)

def config_truth(string):
    string = string.lower()

    return (string == 'true' or string == '1')

def config_app(conf):
    """
    Load configuration from the paste INI file into Flask
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = conf['db.uri']

    if conf.has_key('debug') and config_truth(conf['debug']):
        app.debug = True

    app.config['SESSION_TYPE'] = conf['session.type']
    Session(app)
    app.secret_key = conf['session.key']

    app.config['smtp_server'] = conf['email.smtp_server']
    if conf.has_key('email.smtp_port'):
        app.config['smtp_port'] = conf['email.smtp_port']
    if conf.has_key('email.smtp_login'):
        app.config['smtp_login'] = conf['email.smtp_login']
    if conf.has_key('email.smtp_pass'):
        app.config['smtp_pass'] = conf['email.smtp_pass']
    if conf.has_key('email.smtp_tls'):
        app.config['smtp_tls'] = config_truth(conf['email.smtp_tls'])
    else:
        app.config['smtp_tls'] = False

    app.config['default_sender'] = conf['email.default_sender']


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
