from scratchwire import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

def NNColumn(*args, **kwargs):
    """
    A non-nullable table column
    """
    return db.Column(*args, nullable = False, **kwargs)

def IDColumn():
    """
    An integer primary key column
    """
    return db.Column(db.Integer, primary_key = True)

def NNForeignID(key):
    """
    An integer foreign key column
    """
    return NNColumn(db.Integer, db.ForeignKey(key))

class User(db.Model):
    """
    A user, pure and simple.
    """
    id = IDColumn()
    email = NNColumn(db.String(120), unique = True)
    pass_salt = NNColumn(db.String(8))
    pass_hash = NNColumn(db.String(32))
    email_verified = NNColumn(db.Boolean())

class VerifyUrl(db.Model):
    """
    A verification URL, used to have users verify their email addresses upon
    registering.
    """
    id = db.Column(db.String(32), primary_key = True)
    user_id = NNForeignID('user.id')
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
    user_id = NNForeignID('user.id')
    date = NNColumn(db.DateTime)
    positive = NNColumn(db.Boolean)

class Noun(db.Model):
    """
    An English noun. Used for random phrase generation
    """
    noun = NNColumn(db.String, primary_key = True)

class Adjective(db.Model):
    """
    An English adjective. Used for random phrase generation
    """
    adjective = NNColumn(db.String, primary_key = True)

class Encounter(db.Model):
    """
    A sexual encounter between multiple users
    """
    id = IDColumn()
    date = NNColumn(db.DateTime)

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
    encounter_id = NNForeignID('encounter.id')
    barrier = NNColumn(db.Boolean)

class Alias(db.Model):
    """
    An alias for a given user. We assign these so users can hook together
    anonymously.
    """
    id = IDColumn()
    user_id = NNForeignID('user.id')
    active = NNColumn(db.DateTime)
    expire = db.Column(db.DateTime)
    name = NNColumn(db.String())
