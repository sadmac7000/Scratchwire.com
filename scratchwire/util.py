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
