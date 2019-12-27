from __future__ import annotations

from functools import reduce, partial
from inspect import signature
from itertools import filterfalse
from typing import Generic, Iterable, Any, Callable, Union, Tuple, Generator

from lambdachain.functions import T, U, fold, unique, unique_by, rebind, foldc
from lambdachain.lambda_identifier import LambdaIdentifier, Lambda as _
from lambdachain.utils import assert_callable, assert_generator


class LambdaChain(Generic[T]):

    def __init__(self, it: Iterable[T]):
        self._it = it

    def __iter__(self):
        return iter(self._it)

    # def map(self, f: Callable[[T], U]) -> LambdaChain[U]:
    def map(self, f):
        """
        Applies a function to each element of the current iterable. Analogous to the builtin function `map`.

        Args:
            f: The function to apply.

        Returns:
            A new `LambdaChain` object with `f` applied.`
        """
        assert_callable(f)
        return LambdaChain(map(f, self._it))

    # def filter(self, f: Callable[[T], Any] = identity) -> LambdaChain[T]:
    def filter(self, f):
        """
        Removes the elements of the current iterable that, when passed into a function, return a value that evaluates
        to `False`. Analogous to the builtin function `filter``.

        Args:
            f: The function to filter with.

        Returns:
            A new `LambdaChain` object filtered by `f`.
        """
        assert_callable(f)
        return LambdaChain(filter(f, self._it))

    # def reject(self, f: Callable[[T], Any] = identity) -> LambdaChain[T]:
    def reject(self, f):
        """
        Removes the elements of the current iterable that, when passed into a function, return a value that evaluates
        to `True`. Analogous to `itertools.filterfalse`.

        Args:
            f: The function to filter with.

        Returns:
            A new `LambdaChain` object filtered by `f`.
        """
        assert_callable(f)
        return LambdaChain(filterfalse(f, self._it))

    # def fold(self, f: Callable[[U, T], U], initial_value: U) -> U:
    def fold(self, f, initial_value):
        """
        Applies a function to an accumulator and successive values of the current iterable, with the accumulator
        storing the value of each application, until the iterable is exhausted. The accumulator is initialised with a
        given value. Analogous to `functools.reduce`.

        Similar to `foldc`, except that `fold` accepts a 2-argument function and an initial value, returning the result
        directly.

        Args:
            f: The function to apply.
            initial_value: The initial value of the accumulator.

        Returns:
            The result of the reduction.

        Examples:

        """
        assert_callable(f)
        return fold(f, self._it, initial_value)

    # def foldc(self, f: Callable[[U], Callable[[T], U]]) -> Callable[[U], U]:
    def foldc(self, f):
        """
        Applies a function to an accumulator and successive values of the current iterable, with the accumulator
        storing the value of each application, until the iterable is exhausted. The accumulator is initialised with a
        given value. Analogous to `functools.reduce`.

        Similar to `fold`, except that `foldc` accepts a 2-argument curried function and returns a function that takes
        an initial value.

        Args:
            f: The function to apply.

        Returns:
            A function that takes an initial value and performs the actual reduction.

        Examples:
            >>> LambdaChain(range(5)).foldc(_ + _)(0)
            10
        """
        assert_callable(f)
        return foldc(uncurry(f), self._it)

    def unique(self, ordered: bool = False) -> LambdaChain[T]:
        """
        Removes repeated elements from the current iterable. If `ordered = True`, the unique elements in the result
        be in the same order as when they first appeared in the original iterable.

        Args:
            ordered: Whether to maintain the original ordering.

        Returns:
            A new `LambdaChain` object with unique elements.
        """
        return LambdaChain(unique(self._it, ordered))

    def unique_by(self, key: Callable[[T], Any], ordered: bool = False) -> LambdaChain[T]:
        """
        Removes elements from the current iterable that compare equal after having `key` applied to them. If
        `ordered = True`, the unique elements in the result will be in the same order as when they first appeared in
        the original iterable.

        Args:
            key: The function to apply to the values in the current iterable before comparing for equality.
            ordered: Whether to maintain the original ordering.

        Returns:
            A new `LambdaChain` object with unique elements.
        """
        assert_callable(key)
        return LambdaChain(unique_by(self._it, key, ordered))

    def zip(self, other: Iterable[U]) -> LambdaChain[Tuple[T, U]]:
        return LambdaChain(zip(self._it, iter(other)))

    def enumerate(self, start: int = 0) -> LambdaChain[Tuple[T, int]]:
        return LambdaChain(enumerate(self._it, start))

    def apply(self, g: Generator[U, None, None]) -> LambdaChain[U]:
        """
        Applies a generator expression to the current iterable. This function effectively allows the use of "bindable"
        generator expressions, with the current iterable replacing the source iterable in the generator expression.
        For clarity, `_` should be used to represent the replaceability of the source iterable, as in
        `(obj for obj in _)`. See the examples for more details.

        Args:
            g: The generator expression to apply.

        Returns:
            A new `LambdaChain` object with the generator expression applied.

        Examples:

        First, create a `LambdaChain`:
        `>>> chain = LambdaChain([0, 2.0, 'str', ['in_list']])`

        Next, apply a generator expression to it:
        `>>> result = chain.apply(x * 2 for x in _)`

        Lastly, convert the contents to a `list`:
        ```
        >>> result.force(list)
        [0, 4.0, 'strstr', ['in_list', 'in_list']]
        ```

        The given generator expression is applied to whatever is contained in the `LambdaChain` at that point. In this
        way, generator expressions can be parametrised in terms of the source iterable.
        """

        # This does not create a new generator, but instead modifies the one that is passed in. For the expected use
        # case (being able to specify "lambda" generator expressions in this method, that shouldn't matter. There is a
        # fair bit of (CPython-dependent) magic here, all in the name of nice-looking syntax. I hope it's worth it.

        assert_generator(g)
        rebind(g, self._it)
        return LambdaChain(g)

    def force(self, f):
        return f(self._it)


def uncurry(f: Union[LambdaIdentifier, Callable]):
    """
    Uncurries a function, converting it from a function that takes a single argument that

    Args:
        f: The function to uncurry.

    Returns:
        The uncurried form of `f`.

    Examples:
        Consider the function `f` below:

        ```python
        def f(a):
            def g(b):
                def h(c):
                    return a + b + c

                return h

            return g
        ```

        It takes one argument, returns a function that takes one argument, which itself returns another function that
        also takes one argument, and finally returns a result. It would be called in the following way:

        ```python
        >>> curried_result = f(1)(2)(3)
        >>> curried_result == 6
        True
        ```

        `uncurry` can be used to convert it into a function that takes 3 arguments at once:

        ```
        >>> uncurried_f = uncurry(f)
        >>> uncurried_result = uncurried_f(1, 2, 3)
        >>> uncurried_result == 6
        True

        `uncurry` has no effect on functions taking 0 arguments:

        >>> g = lambda: 0
        >>> g == uncurry(g)
        True
        ```
    """
    def uncurried(*args):
        return reduce(lambda next_f, arg: next_f(arg), args, f)

    # noinspection PyProtectedMember
    func = f._f if isinstance(f, LambdaIdentifier) else f
    parameter_count = len(signature(func).parameters)

    # In the case of a 0-arity function, uncurrying should be a no-op (the algorithm below would return a function that
    # returns f)

    if parameter_count == 0:
        return f

    return uncurried


def curry(f):
    def recursive_curry(g, arg_count: int):
        def curried(arg):
            if arg_count > 1:
                return recursive_curry(partial(g, arg), arg_count - 1)

            else:
                return g(arg)

        return curried

    original_arg_count = len(signature(f).parameters)
    if original_arg_count == 0:
        return f

    # Return a series of functions, each of which binds one argument to the base function if more than one unbound
    # argument is left. Otherwise, that is the last argument, and the function taking it should immediately return a
    # result. This works because `partial(partial(f, 1), 2)` is the same as `partial(f, 1, 2)`.

    return recursive_curry(f, original_arg_count)
