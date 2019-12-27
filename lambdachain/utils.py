from inspect import isgenerator

def assert_callable(f):
    """
    Raise a `TypeError` if an object is not callable.

    Args:
        f: The object to check.
    """
    if not callable(f):
        raise TypeError(f'{f} is not callable')

def assert_generator(g):
    """
    Raise a `TypeError` if an object is not a generator.

    Args:
        f: The object to check.
    """
    if not isgenerator(g):
        raise TypeError(f'{g} is not a generator')
