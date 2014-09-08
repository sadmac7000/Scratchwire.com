from scratchwire import app
from scratchwire.mailer import Email
from flask.ext.sqlalchemy import SQLAlchemy
from hashlib import sha224
from base64 import b64encode
from datetime import datetime, timedelta
import os

db = SQLAlchemy(app)

def NNColumn(*args, **kwargs):
    """
    A non-nullable table column
    """
    return db.Column(*args, nullable = False, **kwargs)

def IDColumn(*args, **kwargs):
    """
    An integer primary key column
    """
    return db.Column(db.Integer, *args, primary_key = True, **kwargs)

def NNForeignID(key, *args, **kwargs):
    """
    An integer foreign key column
    """
    return NNColumn(db.Integer, db.ForeignKey(key), *args, **kwargs)

class User(db.Model):
    """
    A user, pure and simple.
    """
    id = IDColumn()
    email = NNColumn(db.String(120), unique = True)
    pass_salt = NNColumn(db.String(8))
    pass_hash = NNColumn(db.String(40))
    email_verified = NNColumn(db.Boolean())

    def __init__(self):
        """
        Blank out this user
        """
        self.email = ""
        self.pass_salt = ""
        self.pass_hash = ""
        self.email_verified = False

    def hash_pass(self, password):
        """
        Perform our salted hashing algorithm and get the resulting digest
        """
        return b64encode(sha224(self.pass_salt + password).digest())

    def check_pass(self, password):
        """
        Check whether a given password is this users'
        """
        return self.hash_pass(password) == self.pass_hash

    def set_salt(self):
        """
        Set a new salt for this user
        """
        self.pass_salt = b64encode(os.urandom(7))[0:8]

    def set_pass(self, password):
        """
        Set a new password for this user
        """
        self.set_salt()
        self.pass_hash = self.hash_pass(password)

class VerifyUrl(db.Model):
    """
    A verification URL, used to have users verify their email addresses upon
    registering.
    """

    def __init__(self, user_id):
        """
        Create a new randomized verification URL
        """
        if user_id.__class__ == User:
            self.user = user_id
        else:
            self.user_id = user_id

        self.user_id = user_id
        self.id = b64encode(os.urandom(24), ['-', '_'])
        self.expires = datetime.utcnow() + timedelta(days= \
                app.config['verify']['expires_days'])

    def send_email(self):
        Email("verification.jinja2", "Welcome to scratchwire.com", \
                verify_id=self.id).send(None, self.user.email)

    id = db.Column(db.String(32), primary_key = True)
    user_id = NNForeignID('user.id')
    user = db.relationship('User', backref='verify_urls')
    expires = NNColumn(db.DateTime())

class Disease(db.Model):
    """
    A sexually transmitted disease
    """
    id = IDColumn()
    name = db.Column(db.String, unique = True, nullable = False)

class Test(db.Model):
    """
    A test the user has had performed to check for a given disease
    """
    __tablename__ = 'test'
    __table_args__ = (db.PrimaryKeyConstraint('disease_id', 'user_id', 'date'),)

    disease_id = NNForeignID('disease.id')
    diseases = db.relationship('Disease', backref='tests')
    user_id = NNForeignID('user.id')
    user = db.relationship('User', backref='tests')
    date = NNColumn(db.DateTime)
    positive = NNColumn(db.Boolean)

class Noun(db.Model):
    """
    An English noun. Used for random phrase generation
    """
    def __init__(self, word):
        self.noun = word

    noun = NNColumn(db.String, primary_key = True)

class Adjective(db.Model):
    """
    An English adjective. Used for random phrase generation
    """
    def __init__(self, word):
        self.adjective = word

    adjective = NNColumn(db.String, primary_key = True)

class Encounter(db.Model):
    """
    A sexual encounter between multiple users
    """
    id = IDColumn()
    date = NNColumn(db.DateTime)
    participants = db.relationship('User', secondary='participation', \
            backref='encounters')

class Participation(db.Model):
    """
    A link indicating one user participated in an encouter
    """
    __tablename__ = 'participation'
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'encounter_id'),)

    user_id = NNForeignID('user.id')
    encounter_id = NNForeignID('encounter.id')

class Activity(db.Model):
    """
    An activity that may occur during a sexual encounter
    """
    id = IDColumn()
    name = NNColumn(db.String())

class Occurrence(db.Model):
    """
    A link indicating an activity occurred during a sexual encounter
    """
    __tablename__ = 'occurrence'
    __table_args__ = (db.PrimaryKeyConstraint('activity_id', 'encounter_id'),)

    activity_id = NNForeignID('activity.id')
    activity = db.relationship('Activity', backref='occurences')
    encounter_id = NNForeignID('encounter.id')
    encounter = db.relationship('Encounter', backref='occurences')
    barrier = NNColumn(db.Boolean)

class Alias(db.Model):
    """
    An alias for a given user. We assign these so users can hook together
    anonymously.
    """

    def __init__(self, user):
        adjective = Adjective.query.order_by('random()').first()
        noun = Noun.query.order_by('random()').first()
        adjective = adjective.adjective.lower()
        noun = noun.noun.lower()
        adjective = adjective[0:1].upper() + adjective[1:]
        noun = noun[0:1].upper() + noun[1:]
        self.name = adjective + noun
        self.active = datetime.utcnow()
        self.expire = self.active + timedelta(days= \
                app.config['alias']['expires_days'])
        self.user = user


    user_id = NNForeignID('user.id')
    user = db.relationship('User', backref='aliases')
    active = NNColumn(db.DateTime)
    expire = db.Column(db.DateTime)
    name = NNColumn(db.String(), primary_key=True)
