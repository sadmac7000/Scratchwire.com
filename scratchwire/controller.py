# -*- coding: utf-8 -*-
# Copyright © 2014 Casey Dahlin
#
# this file is part of foobar.
#
# foobar is free software: you can redistribute it and/or modify
# it under the terms of the gnu general public license as published by
# the free software foundation, either version 3 of the license, or
# (at your option) any later version.
#
# foobar is distributed in the hope that it will be useful,
# but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose.  see the
# gnu general public license for more details.
#
# you should have received a copy of the gnu general public license
# along with foobar.  if not, see <http://www.gnu.org/licenses/>.

from scratchwire import app
from scratchwire.model import db, Alias
from flask import render_template, session, request
from scratchwire.util import requires_login, bail_redirect
from scratchwire.app_forms import LoginForm, RegistrationForm, VerifyForm

@app.before_request
def expire_user():
    if not session.has_key('User'):
        return

    db.session.add(session['User'])
    db.session.expire(session['User'])

    # FIXME: This is pretty ridiculous
    from sqlalchemy.orm.exc import ObjectDeletedError
    try:
        if session['User'].id == None:
            del session['User']
    except ObjectDeletedError:
        del session['User']

@app.before_request
def map_method():
    if not request.method == 'POST':
        return
    if not request.form.has_key('_method'):
        return

    request.method = request.form['_method']
    del request.form['_method']

LoginForm.route(app, '/login', 'login')
RegistrationForm.route(app, '/register', 'register')
VerifyForm.route(app, '/verify/<verify_id>', 'verify')

@app.route('/')
def home():
    """
    A largely static home page.
    """
    return render_template("home.html")

@app.route('/logout')
def logout():
    if session.has_key("User"):
        del session["User"]
    return bail_redirect()

@app.route('/aliases')
@requires_login
def aliases():
    aliases = session["User"].populate_aliases()

    return render_template("aliases.html", aliases=aliases)
