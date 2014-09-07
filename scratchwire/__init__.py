from flask import Flask, session
from flask.ext.session import Session

app = Flask(__name__)

def config_truth(string):
    string = string.lower()

    return (string == 'true' or string == '1')

def config_type(name, type, default=None):
    target = app.config

    keylets = name.split('.')

    while len(keylets) > 1:
        if not target.has_key(keylets[0]):
            if default != None:
                target[keylets[0]] = {}
            else:
                return
        target = target[keylets[0]]
        keylets.pop(0)

    name = keylets[0]

    if not target.has_key(name):
        if default != None:
            target[name] = default
        return

    if type == 'int':
        target[name] = int(target[name])
    if type == 'boolean':
        target[name] = target[name].lower() in ['true', '1']

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

    scratchwire_conf = {}

    for key in conf.keys():
        keylets = key.split('.')
        if keylets[0] != 'scratchwire':
            continue

        keylets.pop(0)

        location = scratchwire_conf

        while len(keylets) > 1:
            if not location.has_key(keylets[0]):
                location[keylets[0]] = {}
            location = location[keylets[0]]
            keylets.pop(0)

        location[keylets[0]] = conf[key]

    app.config.update(scratchwire_conf)
    config_type('verify_expires_days', 'int', 7)
    config_type('alias_expires_days', 'int', 7)
    config_type('alias_count', 'int', 3)
    config_type('email.smtp_tls', 'boolean', False)


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
