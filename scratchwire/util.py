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

from flask import redirect, url_for, request, session
from decorator import decorator

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

def bail_redirect():
    """
    We were redirected on a detour, such as being prompted to log in, and now
    we can go back to where we were. This will give us the appropriate
    redirect.
    """


    if session.has_key('bail_point'):
        target = session['bail_point'][0]
        args = session['bail_point'][1]

        del session['bail_point']

        return redirect(url_for(target, **args))

    return redirect(url_for('home'))

def set_bail_point(target=None, **args):
    session['bail_point'] = (request.endpoint, request.view_args)

    if target != None:
        return redirect(url_for(target, **args))

def clear_bail_point():
    if session.has_key['bail_point']:
        del session['bail_point']

@decorator
def requires_login(f, *args, **kwargs):
    if session.has_key('User'):
        return f(*args, **kwargs)

    return set_bail_point('login')
