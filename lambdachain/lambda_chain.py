from __future__ import annotations

from functools import reduce, partial
from inspect import signature
from itertools import filterfalse
from typing import Generic, Iterable, Any, Callable, Tuple, Generator, Union, List

from lambdachain.functions import T, U, fold, unique, unique_by, rebind, foldc, groupby_, enumerate_
from lambdachain.lambda_identifier import Lambda as _, LambdaIdentifier
from lambdachain.utils import assert_callable, assert_genexpr


class LambdaChain(Generic[T]):

    def __init__(self, it: Iterable[T]):
        self._it = it
        self.force = ForceProxy(it)

    def __iter__(self):
        return iter(self._it)

    def map(self, f: Callable[[T], U]) -> LambdaChain[U]:
        """
        Apply a function to each element of the current iterable. Analogous to the builtin function `map`.

        Args:
            f: The function to apply.

        Returns:
            A new `LambdaChain` object with `f` applied.`

        Examples:
        ```python
        >>> LambdaChain([1, 5, 3, 9]).map(_ * 2).force()
        [2, 10, 6, 18]
        ```

        ```python
        >>> LambdaChain(['apple', 'pie', 'surprise']).map(len).force()
        [5, 3, 8]
        ```
        """
        assert_callable(f)
        return LambdaChain(map(f, self._it))

    def filter(self, f: Callable[[T], Any]) -> LambdaChain[T]:
        """
        Remove the elements of the current iterable that, when passed into a function, return a value that evaluates
        to `False`. Analogous to the builtin function `filter``.

        Args:
            f: The function to filter with.

        Returns:
            A new `LambdaChain` object without elements that evaluate to `False` under `f`.

        Examples:

        ```python
        >>> LambdaChain([2, 0, -3, 5, 7]).filter(_ > 0).force()
        [2, 5, 7]
        ```
        """
        assert_callable(f)
        return LambdaChain(filter(f, self._it))

    def reject(self, f: Callable[[T], Any]) -> LambdaChain[T]:
        """
        Remove the elements of the current iterable that, when passed into a function, return a value that evaluates
        to `True`. Analogous to `itertools.filterfalse`.

        Args:
            f: The function to filter with.

        Returns:
            A new `LambdaChain` object without elements that evaluate to `True` under `f`.

        Examples:

        ```python
        >>> LambdaChain([2, 0, -3, 5, 7]).reject(_ > 0).force()
        [0, -3]
        ```
        """
        assert_callable(f)
        return LambdaChain(filterfalse(f, self._it))

    def fold(self, f: Callable[[U, T], U], initial_value: U) -> U:
        """
        Apply a function to an accumulator and successive values of the current iterable, with the accumulator
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

        ```python
        >>> from operator import mul
        >>> LambdaChain([3, 8, -2, 6]).fold(mul, 0)
        -288
        ```
        """
        assert_callable(f)
        return fold(f, self._it, initial_value)

    def foldc(self, f: Callable[[U], Callable[[T], U]]) -> Callable[[U], U]:
        """
        Apply a function to an accumulator and successive values of the current iterable, with the accumulator
        storing the value of each application, until the iterable is exhausted. The accumulator is initialised with a
        given value. Analogous to `functools.reduce`.

        Similar to `fold`, except that `foldc` accepts a 2-argument curried function and returns a function that takes
        an initial value.

        Args:
            f: The function to apply.

        Returns:
            A function that takes an initial value and performs the actual reduction.

        Examples:

        ```python
        >>> LambdaChain(range(5)).foldc(_ + _)(0)
        10
        ```
        """
        assert_callable(f)
        return foldc(uncurry(f), self._it)

    def unique(self, ordered: bool = True) -> LambdaChain[T]:
        """
        Remove repeated elements from the current iterable. If `ordered = True`, the unique elements in the result
        be in the same order as when they first appeared in the original iterable. Does not currently support
        unhashable values.

        Args:
            ordered: Whether to maintain the original ordering.

        Returns:
            A new `LambdaChain` object with unique elements.

        Examples:

        ```python
        # Take unique values without enforcing ordering. The order found in the result is arbitrary.
        >>> LambdaChain([3, 0, 5, 7, 0, 4, 3, 4]).unique(ordered=False).force()
        [0, 3, 4, 5, 7]

        # When passing `ordered=True`, the values in the result will appear in the same order as they did in the input.
        >>> LambdaChain([3, 0, 5, 7, 0, 4, 3, 4]).unique(ordered=True).force()
        [3, 0, 5, 7, 4]
        ```
        """
        return LambdaChain(unique(self._it, ordered))

    def unique_by(self, key: Callable[[T], Any]) -> LambdaChain[T]:
        """
        Remove elements from the current iterable that compare equal after having `key` applied to them. Does not
        currently support unhashable values.

        Args:
            key: The function to apply to the values in the current iterable before comparing for equality.

        Returns:
            A new `LambdaChain` object with elements corresponding to unique values under `key`.

        Examples:

        ```python
        # Take the unique values of a `list` based on their remainder when divided by 3.
        >>> LambdaChain([3, 0, 5, 7, 0, 4, 3, 4]).unique_by(_ % 3).force()
        [3, 5, 7]

        # Take the first string with a given length for each unique length value.
        >>> LambdaChain(['apple', 'scream', 'white', 'bay', 'pea']).unique_by(len).force()
        ['apple', 'scream', 'bay']
        ```
        """
        assert_callable(key)
        return LambdaChain(unique_by(self._it, key))

    def zip(self, other: Iterable[U]) -> LambdaChain[Tuple[T, U]]:
        """
        Combine elements from the current iterable with elements from another iterable in the same order to yield
        tuples of the combination. Analogous to `zip`.

        Args:
            other: The iterable to combine with the current iterable.

        Returns:
            A new `LambdaChain` object with the elements of `other` zipped in.

        Examples:

        ```python
        >>> LambdaChain(['alpha', 'bravo', 'charlie']).zip([True, True, False]).force()
        [('alpha', True), ('bravo', True), ('charlie', False)]
        ```
        """
        return LambdaChain(zip(self._it, iter(other)))

    def enumerate(self, start: int = 0, step: int = 1) -> LambdaChain[Tuple[T, int]]:
        """
        Combine elements from the current iterable with a counter to yield tuples of the combination. Analogous to
        `enumerate`, but with an additional `step` argument controlling the change in the counter's value each
        iteration.

        Args:
            start: The starting value of the counter.
            step: The amount to modify the counter by each iteration.

        Returns:
            A new `LambdaChain` object combined with a counter.

        Examples:

        ```python
        # Combine with a counter that starts at 2 and increments by 2 each iteration.
        >>> LambdaChain(['a', 'b', 'c']).enumerate(start=2, step=2)
        [(2, 'a'), (4, 'b'), (6, 'c')]
        ```
        """
        return LambdaChain(enumerate_(self._it, start, step))

    def groupby(self, key: Callable[[T], Any], combine: bool = True) -> LambdaChain[Tuple[Any, List[T]]]:
        """
        Group elements from the current iterable that compare equal after having `key` applied to them, yielding
        `tuples` where the first element is a unique result of applying `key` and the second is a `list` of all values
        in the current iterable that have that result when `key` is applied to them.

        If `combine` is `True`, all elements which correspond to a particular value under `key` will always be in the
        same group. Otherwise, each run of elements which evaluate to a single unique value under `key` will form a
        single group, analogous to`itertools.groupby`.

        Args:
            key: The function to apply to elements in the current iterable before performing grouping.
            combine: Whether to combine groups corresponding to the same key.

        Returns:
            A new `LambdaChain` object with elements grouped by the result of applying `key`.

        Examples:

        ```python
        # Group by parity (odd/even) and convert to a `list`. Notice that in the output, there are only two groups; one
        for odd numbers and one for even ones.
        >>> chain = LambdaChain([1, 3, 2, 2, 5, 3, 4, 6]).groupby(_ % 2).force()
        [(1, [1, 3, 5, 3]), (0, [2, 2, 4, 6])]

        # Create the same LambdaChain as above; but this time, pass `combine=False`. This time, the output is separated
        into runs of odd and even numbers in the same order as the original.
        >>> LambdaChain([1, 3, 2, 2, 5, 3, 4, 6]).groupby(_ % 2, combine=False).force()
        [(1, [1, 3]), (0, [2, 2]), (1, [5, 3]), (0, [4, 6])]
        ```
        """
        assert_callable(key)
        return LambdaChain(groupby_(self._it, key, combine))

    # noinspection PyUnresolvedReferences
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

        ```python
        # The given generator expression is applied to whatever is contained in the `LambdaChain` at that point. In
        # this way, generator expressions can be parametrised in terms of the source iterable.
        >>> LambdaChain([0, 2.0, 'str', ['in_list']]).apply(x * 2 for x in _).force()
        [0, 4.0, 'strstr', ['in_list', 'in_list']]
        ```
        """

        # This does not create a new generator, but instead modifies the one that is passed in. For the expected use
        # case (being able to specify "lambda" generator expressions in this method, that shouldn't matter.

        assert_genexpr(g)
        rebind(g, self._it)
        return LambdaChain(g)

    def persist(self):
        """
        Convert the current iterable to a `list`, allowing it to be used in multiple operations.

        Returns:
            A new `LambdaChain` object containing the current iterable persisted as a `list`.
        """
        return LambdaChain(list(self._it))


class ForceProxy(Generic[T]):

    def __init__(self, it: Iterable[T]):
        self._it = it

    def __call__(self, f: Callable[[Iterable[T]], Any] = list):
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
