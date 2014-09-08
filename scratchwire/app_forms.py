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

from scratchwire.model import db, User, VerifyUrl, Alias
from flask import session, abort, flash
from scratchwire.form import Form, element
from validate_email import validate_email
from scratchwire.util import bail_redirect
from datetime import datetime

class LoginForm(Form):
    """
    Standard issue login form. Nothing exciting here.
    """
    @element(label="E-Mail", ftype="email")
    def email(self, field):
        """
        Email address form field. We use this as our primary user identifier.
        """
        if not validate_email(field.content):
            field.complaints.append("You must enter a valid e-mail address")
        else:
            field.value = field.content


    @element(label="Password", ftype="password")
    def password(self, field):
        """
        Password form field.
        """
        if len(field.content) < 6:
            field.complaints.append("Password must be at least 6 characters")
        else:
            field.value = field.content

    def global_validate(self, valid_so_far):
        """
        Validate the entered user and fetch his database entry
        """

        if not valid_so_far:
            return

        email = self.email.value
        password = self.password.value

        user = User.query.filter_by(email=email).first()

        if user == None or not user.check_pass(password):
            self.email.complaints.append("Invalid email or password")
        elif not user.email_verified:
            self.password.complaints.append("""You have not yet validated your
                    email address""")

        if len(self.email.complaints) == 0:
            self.user = user
            return

    def handle_valid(self):
        """
        Handle a valid submission of this form
        """
        session["User"] = self.user
        return bail_redirect()

    action = 'login'
    template = 'login'

class RegistrationForm(LoginForm):
    @element(label="Confirm Password", ftype="password")
    def confirm_password(self, field):
        """
        Confirm password form field.
        """
        field.value = field.content

    def global_validate(self, valid_so_far):
        """
        Validate the user and add him
        """
        email = self.email.value
        password = self.password.value
        confirm_password = self.confirm_password.value

        user = User.query.filter_by(email=email).first()

        if user == None and password == confirm_password and valid_so_far:
            user = User()
            user.email = email
            user.set_pass(password)

            self.user = user
            return

        if user != None:
            self.email.complaints.append("E-mail address already in use")

        if password != confirm_password:
            self.password.complaints.append("Passwords do not match")

    def handle_valid(self):
        verify_url = VerifyUrl(self.user)
        db.session.add(self.user)
        db.session.add(verify_url)
        db.session.commit()
        verify_url.send_email()
        flash(
        """We have sent you an email to confirm your email address.
        Please click on the link to confirm your registration.""")
        return bail_redirect()

    action = 'register'
    template = 'register'

class VerifyForm(LoginForm):
    email = None

    def setup(self):
        id = self.action_vars['verify_id']
        self.verify = VerifyUrl.query.filter(VerifyUrl.id == id,
                VerifyUrl.expires > datetime.utcnow()).first()

        if not self.verify:
            abort(404)

    def global_validate(self, valid_so_far):
        """
        Validate the verified user
        """
        password = self.password.value

        if not valid_so_far:
            return

        if not self.verify.user.check_pass(password):
            self.password.complaints.append("Invalid password")

    def handle_valid(self):
        """
        Verify the user
        """
        session['User'] = self.verify.user
        session['User'].email_verified = True

        db.session.add(session['User'])
        db.session.commit()

        flash("Your email address has been verified successfully")

        return bail_redirect()

    action = 'verify'
    template = 'verify'

