from scratchwire import app
from scratchwire.model import db, User
from flask import render_template, url_for, request, session, redirect, flash
from scratchwire.form import Form, element
from validate_email import validate_email
from scratchwire.util import monoize_multi, bail_redirect

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

        if valid_so_far and user != None and user.check_pass(password):
            self.user = user
        elif valid_so_far:
            self.fields[0].complaints.append("Invalid email or password")

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
            print user
            self.fields[0].complaints.append("E-mail address already in use")

        if password != confirm_password:
            self.fields[1].complaints.append("Passwords do not match")

    def handle_valid(self):
        db.session.add(self.user)
        db.session.commit()
        flash(
        """We have sent you an email to confirm your email address.
        Please click on the link to confirm your registration.""")
        return bail_redirect()

    fields = [LoginForm.email, LoginForm.password, confirm_password]
    action = 'register'

@app.route('/')
def home():
    """
    A largely static home page.
    """
    return render_template("home.jinja2")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    The login form page.
    """
    return LoginForm.page_handle_request(request)

@app.route('/logout')
def logout():
    del session["User"]
    return bail_redirect()

@app.route('/register', methods=['GET','POST'])
def register():
    """
    The registration form page.
    """
    return RegistrationForm.page_handle_request(request)
