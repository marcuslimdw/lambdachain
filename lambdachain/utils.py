from sys import version_info

_major, _minor, *_ = version_info
PY37 = (_major >= 3) and (_minor >= 7)
PY38 = (_major >= 3) and (_minor >= 8)


def assert_callable(f):
    """
    Raise a `TypeError` if an object is not callable.

    Args:
        f: The object to check.
    """
    if not callable(f):
        try:
            addendum = '. Did you mean to use list instead of list(_)?' if len(f) == 0 else ''

        except TypeError:
            addendum = ''

        raise TypeError(f'{f} is not callable{addendum}')


def assert_genexpr(g):
    """
    Raise a `TypeError` if an object is not a generator expression.

    Args:
        g: The object to check.
    """
    if g.__name__ != '<genexpr>':
        raise TypeError(f'{g} is not a generator expression')
