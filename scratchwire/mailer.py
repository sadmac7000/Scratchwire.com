from smtplib import SMTP
from email.mime.text import MIMEText
from scratchwire import app

env = app.jinja_env

class Email(object):
    """
    An Email generated from a template.
    """

    def __init__(self, template, subject = "<no subject>", **args):
        self.template = env.get_template("email/%s" % template)
        self.subject = subject
        self.args = args

    def addr_process(self, recipients):
        emails = []
        mimenames = []

        for recipient in recipients:
            if type(recipient) == tuple:
                emails.append(recipient[1])
                mimenames.append("%s <%s>" % recipient)
            else:
                emails.append(recipient)
                mimenames.append(recipient)
        
        return emails, mimenames

    def send(self, sender=None, *recipients):
        if sender == None:
            sender = app.config['default_sender']

        msg = MIMEText(self.template.render(**self.args))

        emails, mimenames = self.addr_process(recipients)

        msg['Subject'] = self.subject
        msg['To'] = ", ".join(mimenames)


        if type(sender) == tuple:
            msg['From'] = "%s <%s>" % sender
            sender = sender[1]
        else:
            msg['From'] = sender

        if app.config.has_key('smtp_port'):
            s = SMTP(app.config['smtp_server'], app.config['smtp_port'])
        else:
            s = SMTP(app.config['smtp_server'])

        if app.config['smtp_tls']:
            s.starttls()
            s.ehlo()

        if app.config.has_key('smtp_pass'):
            s.login(app.config['smtp_login'], app.config['smtp_pass'])

        s.sendmail(sender, emails, msg.as_string())
        s.close()
