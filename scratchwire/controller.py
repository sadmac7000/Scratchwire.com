from scratchwire import app
from flask import render_template, url_for, request, session, redirect
from scratchwire.form import Form, element

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
        pass

    @element(label="Password", ftype="password")
    def password(self):
        """
        Password form field.
        """
        if len(self.content) < 6:
            self.complaints.append("Password must be at least 6 characters")

    fields = [email, password]
    action = 'login_submit'

@app.route('/')
def home():
    """
    A largely static home page.
    """
    return render_template("home.jinja2")

@app.route('/login')
def login():
    """
    The login form page.
    """
    form = LoginForm()

    return render_template("form.jinja2", form=form)

@app.route('/login/submit', methods=['POST'])
def login_submit():
    """
    POST target for the login form.
    """
    reqvars = monoize_multi(request.form)
    form = LoginForm(**reqvars)
    form.validate()

    session["LoginForm"] = form

    return redirect(url_for('login'))

@app.route('/register')
def register():
    """
    Registration page.
    """
    return render_template("register.jinja2")
