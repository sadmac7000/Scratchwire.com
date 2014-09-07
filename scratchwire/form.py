from flask import render_template
from copy import copy

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

    def __call__(self):
        """
        Validate us
        """
        self.validate(self)

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

        self.fields = [ copy(x) for x in self.fields ]
        for i in self.fields:
            i.complaints = []
            if content.has_key(i.name):
                i.content = content[i.name]

    def __getstate__(self):
        """
        Clean out the function references from the elements before we
        serialize, otherwise we'll error out.
        """
        data = copy(self.__dict__)

        data['fields'] = [ x.__dict__ for x in self.fields ]

        for i in data['fields']:
            del i['validate']

        return data

    def __setstate__(self, state):
        """
        Restore our slightly mutilated pickle state. We do this since there's
        function references in FormElement that can't be pickled, so we have to
        chop them out before pickling.
        """
        self.__dict__.update(state)

        fields_data = self.fields
        self.fields = [ copy(x) for x in self.__class__.fields ]
        for i in range(0, len(self.fields)):
            self.fields[i].__dict__.update(fields_data[i])

    def validate(self):
        """
        Validate all fields on the form.
        """
        valid = True

        for i in self.fields:
            i.validate(i)
            if len(i.complaints):
                valid = False

        self.global_validate(valid)

        for i in self.fields:
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
