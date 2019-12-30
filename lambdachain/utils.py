from inspect import isgenerator


def assert_callable(f):
    """
    Raise a `TypeError` if an object is not callable.

    Args:
        f: The object to check.
    """
    if not callable(f):
        raise TypeError(f'{f} is not callable')


def assert_genexpr(g):
    """
    Raise a `TypeError` if an object is not a generator expression.

    Args:
        g: The object to check.
    """
    if g.__name__ != '<genexpr>':
        raise TypeError(f'{g} is not a generator expression')
