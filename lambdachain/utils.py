from sys import version_info

_major, _minor, *_ = version_info
PY36 = (_major >= 3) and (_minor >= 6)
PY37 = (_major >= 3) and (_minor >= 7)
PY38 = (_major >= 3) and (_minor >= 8)


def assert_callable(f):
    """
    Raise a `TypeError` if an object is not callable.

    Args:
        f: The object to check.
    """
    if not callable(f):
        raise TypeError(f"'{type(f)}' object is not callable")


def assert_genexpr(g):
    """
    Raise a `TypeError` if an object is not a generator expression.

    Args:
        g: The object to check.
    """
    if g.__name__ != '<genexpr>':
        raise TypeError(f"'{type(g)}' object is not a generator expression")
