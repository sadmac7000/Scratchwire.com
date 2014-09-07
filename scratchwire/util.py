from flask import redirect, url_for

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

    # FIXME: make this do something more ornate
    return redirect(url_for('home'))

