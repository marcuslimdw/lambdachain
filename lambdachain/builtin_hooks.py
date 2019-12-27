from lambdachain.lambda_identifier import LambdaIdentifier

_old_bool = bool
_old_int = int
_old_float = float
_old_str = str
_old_isinstance = isinstance


# noinspection PyShadowingBuiltins
def bool(x):
    return _old_bool if isinstance(x, LambdaIdentifier) else _old_bool(x)


# noinspection PyShadowingBuiltins
def int(x):
    return _old_int if isinstance(x, LambdaIdentifier) else _old_int(x)


# noinspection PyShadowingBuiltins
def float(x):
    return _old_float if isinstance(x, LambdaIdentifier) else _old_float(x)


# noinspection PyShadowingBuiltins
def str(x):
    return _old_str if isinstance(x, LambdaIdentifier) else _old_str(x)


NEW_TYPE_MAP = {
    bool: _old_bool,
    int: _old_int,
    float: _old_float,
    str: _old_str
}


# noinspection PyShadowingBuiltins
def isinstance(obj, types):
    if _old_isinstance(types, tuple):
        return _old_isinstance(obj, tuple(NEW_TYPE_MAP[type] for type in types if type in NEW_TYPE_MAP))

    else:
        return _old_isinstance(obj, NEW_TYPE_MAP.get(types, types))


__all__ = ['bool', 'int', 'float', 'str', 'isinstance']
