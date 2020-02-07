from typing import Type, Tuple, Union, Any, Dict

from lambdachain.lambda_identifier import LambdaIdentifier
from lambdachain.utils import PY38

# TODO: Hook other builtins like bytes

# TODO: Think about whether hooking types is actually necessary/desirable

_old_bool = bool
_old_int = int
_old_float = float
_old_str = str
_old_isinstance = isinstance
_old_len = len
_old_type = type

_EMPTY_OBJECT_OR_NAME = object()
_EMPTY_BASES = object()
_EMPTY_ATTR_DICT = object()


# noinspection PyShadowingBuiltins
def bool(x):
    return LambdaIdentifier(_old_bool) if isinstance(x, LambdaIdentifier) else _old_bool(x)


# noinspection PyShadowingBuiltins
def int(x):
    return LambdaIdentifier(_old_int) if isinstance(x, LambdaIdentifier) else _old_int(x)


# noinspection PyShadowingBuiltins
def float(x):
    return LambdaIdentifier(_old_float) if isinstance(x, LambdaIdentifier) else _old_float(x)


# noinspection PyShadowingBuiltins
def str(x):
    return LambdaIdentifier(_old_str) if isinstance(x, LambdaIdentifier) else _old_str(x)


_NEW_TYPE_MAP = {
    bool: _old_bool,
    int: _old_int,
    float: _old_float,
    str: _old_str
}


# noinspection PyShadowingBuiltins
def len(x: Union[LambdaIdentifier, Any]):
    return LambdaIdentifier(lambda y: _old_len(x._f(y))) if isinstance(x, LambdaIdentifier) else _old_len(x)


# noinspection PyShadowingBuiltins
def isinstance(obj, types):
    if _old_isinstance(types, tuple):
        return _old_isinstance(obj, tuple(_NEW_TYPE_MAP[t] for t in types if t in _NEW_TYPE_MAP))

    else:
        return _old_isinstance(obj, _NEW_TYPE_MAP.get(types, types))


def _type(object_or_name, bases: Union[None, Tuple[Type]] = None, attr_dict: Union[None, Dict[str, Any]] = None):
    if object_or_name is _EMPTY_OBJECT_OR_NAME:
        raise TypeError('type() takes 1 or 3 arguments')

    if isinstance(object_or_name, LambdaIdentifier):
        return LambdaIdentifier(lambda x: type(x))

    elif bases is _EMPTY_BASES and attr_dict is _EMPTY_ATTR_DICT:
        type_result = _old_type(object_or_name)
        return _NEW_TYPE_MAP.get(type_result, type_result)

    elif bases is not _EMPTY_BASES and attr_dict is not _EMPTY_ATTR_DICT:
        return _old_type(object_or_name, bases, attr_dict)

    else:
        raise TypeError('type() takes 1 or 3 arguments')


if PY38:

    # This is, unfortunately, a SyntaxError in earlier versions...

    exec('''def type(object_or_name: Any = _EMPTY_OBJECT_OR_NAME, 
                     bases: Union[object, Tuple[Type]] = _EMPTY_BASES, 
                     attr_dict: Union[object, Dict[str, Any]] = _EMPTY_ATTR_DICT, /):
        return _type(object_or_name, bases, attr_dict)''')

else:
    # noinspection PyShadowingBuiltins
    def type(object_or_name: Any = _EMPTY_OBJECT_OR_NAME,
             bases: Union[object, Tuple[Type]] = _EMPTY_BASES,
             attr_dict: Union[object, Dict[str, Any]] = _EMPTY_ATTR_DICT):
        return _type(object_or_name, bases, attr_dict)


__all__ = ['bool', 'int', 'float', 'str', 'len', 'isinstance', 'type']
