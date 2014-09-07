from scratchwire import app
from scratchwire.model import db, User, VerifyUrl
from flask import render_template, url_for, request, session, redirect, flash
from flask import abort
from scratchwire.form import Form, element
from scratchwire.mailer import Email
from validate_email import validate_email
from scratchwire.util import monoize_multi, bail_redirect
from datetime import datetime

@app.before_request
def expire_user():
    if session.has_key('User'):
        db.session.add(session['User'])
        db.session.expire(session['User'])

class LoginForm(Form):
    """
    Standard issue login form. Nothing exciting here.
    """
    @element(label="E-Mail", ftype="email")
    def email(self):
        """
        Email address form field. We use this as our primary user identifier.
        """
        if not validate_email(self.content):
            self.complaints.append("You must enter a valid e-mail address")
        else:
            self.value = self.content


    @element(label="Password", ftype="password")
    def password(self):
        """
        Password form field.
        """
        if len(self.content) < 6:
            self.complaints.append("Password must be at least 6 characters")
        else:
            self.value = self.content

    def global_validate(self, valid_so_far):
        """
        Validate the entered user and fetch his database entry
        """
        email = self.fields[0].value
        password = self.fields[1].value

        user = User.query.filter_by(email=email).first()

        if user == None or not user.check_pass(password):
            self.fields[0].complaints.append("Invalid email or password")
        elif not user.email_verified:
            self.fields[0].complaints.append("""You have not yet validated your
                    email address""")

        if valid_so_far and len(self.fields[0].complaints) == 0:
            self.user = user
            return

    def handle_valid(self):
        """
        Handle a valid submission of this form
        """
        session["User"] = self.user
        return bail_redirect()

    fields = [email, password]
    action = 'login'

class RegistrationForm(LoginForm):
    @element(label="Confirm Password", ftype="password")
    def confirm_password(self):
        """
        Confirm password form field.
        """
        self.value = self.content

    def global_validate(self, valid_so_far):
        """
        Validate the user and add him
        """
        email = self.fields[0].value
        password = self.fields[1].value
        confirm_password = self.fields[2].value

        user = User.query.filter_by(email=email).first()

        if user == None and password == confirm_password and valid_so_far:
            user = User()
            user.email = email
            user.set_pass(password)

            self.user = user
            return

        if user != None:
            self.fields[0].complaints.append("E-mail address already in use")

        if password != confirm_password:
            self.fields[1].complaints.append("Passwords do not match")

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

    fields = [LoginForm.email, LoginForm.password, confirm_password]
    action = 'register'

class VerifyForm(LoginForm):
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
        password = self.fields[0].value

        if not valid_so_far:
            return

        if not self.verify.user.check_pass(password):
            self.fields[0].complaints.append("Invalid password")

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

    fields = [LoginForm.password]
    action = 'verify'

LoginForm.route(app, '/login', 'login')
RegistrationForm.route(app, '/register', 'register')
VerifyForm.route(app, '/verify/<verify_id>', 'verify')

@app.route('/')
def home():
    """
    A largely static home page.
    """
    return render_template("home.jinja2")

@app.route('/logout')
def logout():
    if session.has_key("User"):
        del session["User"]
    return bail_redirect()
