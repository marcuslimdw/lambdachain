from typing import Callable

from lambdachain.functions import identity


class LambdaIdentifier:

    __slots__ = ['_f']

    def __init__(self, f: Callable):
        self._f = f

    def __iter__(self):
        return iter(())

    def __add__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) + other)

    def __radd__(self, other):
        return LambdaIdentifier(lambda x: other + self._f(x))

    def __sub__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) - other)

    def __rsub__(self, other):
        return LambdaIdentifier(lambda x: other - self._f(x))

    def __mul__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) * other)

    def __rmul__(self, other):
        return LambdaIdentifier(lambda x: other * self._f(x))

    def __truediv__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) / other)

    def __rtruediv__(self, other):
        return LambdaIdentifier(lambda x: other / self._f(x))

    def __floordiv__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) // other)

    def __rfloordiv__(self, other):
        return LambdaIdentifier(lambda x: other // self._f(x))

    def __mod__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) % other)

    def __rmod__(self, other):
        return LambdaIdentifier(lambda x: other % self._f(x))

    def __pow__(self, power, modulo=None):
        return LambdaIdentifier(lambda x: pow(self._f(x) ** power, modulo))

    def __rpow__(self, other):
        return LambdaIdentifier(lambda x: other ** self._f(x))

    def __eq__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) == other)

    def __ge__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) >= other)

    def __gt__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) > other)

    def __le__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) <= other)

    def __lt__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) < other)

    def __ne__(self, other):
        return LambdaIdentifier(lambda x: self._f(x) != other)

    def __getitem__(self, item):
        return LambdaIdentifier(lambda x: self._f(x)[item])

    def __bool__(self):
        raise ValueError("A LambdaIdentifier cannot be converted to a bool; if you wish to apply boolean operators in "
                         "a lambda expression, use '&' for 'and', '|' for 'or' and '~' for 'not' instead")

    # TODO: Think about how to support chaining boolean operators.

    # noinspection PyPep8
    def __and__(self, other):
        return LambdaIdentifier(lambda x: lambda y: self._f(x) and other(y)
                                if isinstance(other, LambdaIdentifier)
                                else lambda z: other and self._f(z))

    # noinspection PyPep8
    def __or__(self, other):
        return LambdaIdentifier(lambda x: lambda y: self._f(x) or other(y)
                                if isinstance(other, LambdaIdentifier)
                                else lambda z: other or self._f(z))

    def __invert__(self):
        return LambdaIdentifier(lambda x: not self._f(x))

    def __getattr__(self, attr):
        return GetattrProxy(self._f, attr)

    def __call__(self, *args, **kwargs):
        return self._f(*args, **kwargs)


class GetattrProxy(LambdaIdentifier):

    def __init__(self, f, attr):
        self._attr = attr
        super().__init__(f)

    def __matmul__(self, args):
        # As it stands, there is no apparent way to distinguish between a GetattrProxy that is being called on an
        # object to access an attribute, and one that is being called to construct a GetattrCallProxy. Accordingly,
        # since matrix multiplication is only used in NumPy (that I know of), which probably would have little use for
        # such lambdas, this operator has been repurposed for the specific case of binding arguments to a GetattrProxy
        # to create a GetattrCallProxy.

        return GetattrCallProxy(self._f, self._attr, args)

    def __call__(self, *args):
        attr = self._attr
        if len(args) != 1:
            message = (f"A GetattrProxy accessing attribute '{attr}' was called with the wrong number of arguments. "
                       f"Did you want to access the method '{attr}' with _.{attr} @ {args} instead?")
            raise ValueError(message)

        arg = args[0]
        try:
            return getattr(self._f(arg), attr)

        except AttributeError as e:
            message = (f"If you meant to access the attribute '{attr}' on {arg}, it does not exist - alternatively, "
                       f"did you want to access the method '{attr}' with _.{attr} @ {arg} instead?")
            raise ValueError(message) from e


class GetattrCallProxy(GetattrProxy):

    def __init__(self, f, attr, arg_or_args):
        self._arg_or_args = arg_or_args
        super().__init__(f, attr)

    def __call__(self, obj):

        # To allow _.method @ 1 instead of _.method @ (1,) in the special case where only 1 argument is provided,
        # there is ambiguity in whether a tuple of arguments (of either length 0 or 2 and above) or a single argument
        # is stored.

        arg_or_args = self._arg_or_args
        call = super().__call__(obj)
        try:
            # To distinguish a TypeError raised by the function itself from one arising from splat failure
            args = iter(arg_or_args)
            return call(*args)

        except TypeError:
            return call(arg_or_args)


Lambda = LambdaIdentifier(identity)


__all__ = ['Lambda', 'LambdaIdentifier']
