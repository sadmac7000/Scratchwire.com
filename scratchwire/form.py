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

from flask import render_template, session, redirect, url_for, request, Markup
from copy import copy
from scratchwire.util import monoize_multi, decamel
from jinja2.exceptions import TemplateNotFound

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
        data = "<%s (%s - %s): %s>" % (self.name, self.label, self.ftype,
                self.content)

        if len(self.complaints) > 0:
            data += " (" + ", ".join(self.complaints) + ")"

        return data

    def __get__(self, instance, owner):
        if not instance:
            return self

        ret = copy(self)
        ret.validate = ret.validate.__get__(instance, owner)

        return ret

    def __call__(self):
        """
        Render the HTML necessary to draw this form element.
        """
        return Markup(render_template("form/field.html", field=self))

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

    def __init__(self, action_vars = {}, content = {}):
        """
        Initialize the form from a dict of values.
        """

        self.action_vars = action_vars

        self.fields = [ getattr(self, x) for x in self.fields ]
        for i in self.fields:
            i.complaints = []
            if content.has_key(i.name):
                i.content = content[i.name]

        self.setup()

    def setup(self):
        pass

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
        self.fields = [ getattr(self, x) for x in self.__class__.fields ]
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
        try:
            return Markup(render_template("form/%s.html" % \
                    decamel(self.__class__.__name__), form=self))
        except TemplateNotFound:
            return Markup(render_template("form/_default.html", form=self))

    def __repr__(self):
        """
        Get a debug representation of this object
        """
        data = "<form:%s:%s " % (self.method, self.action)
        data += ", ".join([ "( %s )" % x for x in self.fields ])
        data += ">"
        return data

    @classmethod
    def page_handle_request(klass, **action_vars):
        """
        Handle a request object.
        """
        if request.method == 'POST':
            reqvars = monoize_multi(request.form)
            form = klass(action_vars, reqvars)

            if form.validate():
                return form.handle_valid()
            else:
                session[klass.__name__] = form
                return redirect(url_for(klass.action, **action_vars))
        elif session.has_key(klass.__name__):
            form = session[klass.__name__]
            del session[klass.__name__]
        else:
            form = klass(action_vars)

        return render_template("form.html", form=form)

    @classmethod
    def route(klass, app, rule, endpoint):
        app.add_url_rule(rule=rule, endpoint=endpoint, \
                view_func=klass.page_handle_request, methods=['GET', 'POST'])
