from flask import render_template

class FormElement(object):
    """
    A single element of a web form.
    """
    def __init__(self, name, label, ftype, content, validate):
        """
        Initialize our Form element.
        """
        self.complaints = []
        self.name = name
        self.label = label
        self.ftype = ftype
        self.content = content
        self.validate = validate
        self.value = None

    def __repr__(self):
        """
        Get a textual debug representation of this object
        """
        data = "%s (%s - %s): %s" % (self.name, self.label, self.ftype,
                self.content)

        if len(self.complaints) > 0:
            data += " (" + ", ".join(self.complaints) + ")"

        return data

    def render(self):
        """
        Render the HTML necessary to draw this form element.
        """
        return render_template("form/field.jinja2", field=self)

class element(object):
    """
    A decorator to turn a method of one of the Form class' descendents into a
    form element.
    """

    def __init__(self, label, ftype, content = ""):
        """
        Store the decorator arguments
        """
        self.label = label
        self.ftype = ftype
        self.content = content

    def __call__(self, validator):
        """
        Decorate a method into a form element. The decorated method performs
        validation.
        """
        return FormElement(validator.__name__, self.label, self.ftype, self.content,
                validator)

class Form(object):
    """
    A web form. Capable of self-validating and of rendering itself as HTML.
    """

    fields = []
    method = "POST"

    def __init__(self, **content):
        """
        Initialize the form from a dict of values.
        """
        for i in self.fields:
            if content.has_key(i.name):
                i.content = content[i.name]

    def validate(self):
        """
        Validate all fields on the form.
        """
        valid = True

        for i in self.fields:
            i.validate(i)

            if len(i.complaints):
                valid = False

        return valid

    def render(self):
        """
        Render the form as HTML
        """
        return render_template("form/main.jinja2", form=self)

    def __repr__(self):
        """
        Get a debug representation of this object
        """
        data = "<form:%s:%s " % (self.method, self.action)
        data += ", ".join([ "( %s " % x for x in self.fields ])
        return data
