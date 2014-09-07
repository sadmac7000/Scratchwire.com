from scratchwire import app
from scratchwire.model import db, User
from flask import render_template, url_for, request, session, redirect, flash
from scratchwire.form import Form, element
from validate_email import validate_email

def monoize_multi(multidict):
    """
    Multidicts turn into lists of dicts when you cast them. We run into them
    in a few places. This will flatten them in cases where multidicts weren't
    necessary in the first place.

    MultiDicts are sort of weird anyway, so this is pretty much our SOP
    anywhere we have to touch them.
    """
    singledict = dict(multidict)

    for i in singledict.keys():
        if len(singledict[i]) > 1:
            raise "Too many items in multidict"

        singledict[i] = singledict[i][0]

    return singledict

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
        email = self.fields[0].value
        password = self.fields[1].value

        user = User.query.filter_by(email=email).first()

        if valid_so_far and user != None and user.check_pass(password):
            self.user = user
        elif valid_so_far:
            self.fields[0].complaints.append("Invalid email or password")

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

    fields = [LoginForm.email, LoginForm.password, confirm_password]
    action = 'register'

def bail_redirect():
    """
    We were redirected on a detour, such as being prompted to log in, and now
    we can go back to where we were. This will give us the appropriate
    redirect.
    """

    # FIXME: make this do something more ornate
    return redirect(url_for('home'))

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
    if request.method == 'POST':
        reqvars = monoize_multi(request.form)
        form = LoginForm(**reqvars)

        if form.validate():
            session["User"] = form.user
            return bail_redirect()
        else:
            session["LoginForm"] = form
            return redirect(url_for('login'))
    elif session.has_key("LoginForm"):
        form = session["LoginForm"]
        del session["LoginForm"]
    else:
        form = LoginForm()

    return render_template("form.jinja2", form=form)

@app.route('/logout')
def logout():
    del session["User"]
    return bail_redirect()

@app.route('/register', methods=['GET','POST'])
def register():
    """
    The registration form page.
    """
    if request.method == 'POST':
        reqvars = monoize_multi(request.form)
        form = RegistrationForm(**reqvars)

        if form.validate():
            db.session.add(form.user)
            db.session.commit()
            flash(
            """We have sent you an email to confirm your email address.
            Please click on the link to confirm your registration""")
            return bail_redirect()
        else:
            session["RegistrationForm"] = form
            return redirect(url_for('register'))
    elif session.has_key("RegistrationForm"):
        form = session["RegistrationForm"]
        del session["RegistrationForm"]
    else:
        form = RegistrationForm()

    return render_template("form.jinja2", form=form)
