from collections import defaultdict
from functools import reduce, partial
from itertools import groupby as groupby, count
from typing import TypeVar, Iterable, Callable, Generator, Tuple

T = TypeVar('T')
U = TypeVar('U')


def enumerate_(it: Iterable[T], start: int, step: int) -> Iterable[Tuple[T, int]]:
    if step == 1:
        return enumerate(it, start)

    else:
        return zip(count(start, step), it)


def flatten(it: Iterable[Iterable[T]]) -> Iterable[T]:
    return (element for sub_iterable in it for element in sub_iterable)


# def fold(f: Callable[[U, T], U], it: Iterable[T], initial_value: U) -> U:
def fold(f, it, initial_value):
    return reduce(f, it, initial_value)


# def foldc(f: Callable[[U, T], U], it: Iterable[T]) -> Callable[[U], U]:
def foldc(f, it):
    def inner(u: U) -> U:
        return reduce(f, it, u)

    return inner


def identity(x: T) -> T:
    return x


# def map_(f: Callable[[T], U], it: Iterable[T], *args, **kwargs) -> Iterable[U]:
def map_(f, it, *args, **kwargs):
    return map(partial(f, *args, **kwargs), it)


# def groupby_(it: Iterable[T], key: Callable[[T], U], combine: bool) -> Iterable[Tuple[U, T]]:
def groupby_(it, key, combine):
    if combine:
        d = defaultdict(list)
        for v in it:
            d[key(v)].append(v)

        yield from d.items()

    else:
        yield from ((k, list(g)) for k, g in groupby(it, key))


def rebind(g: Generator[T, None, None], new_source: Iterable):
    try:
        import ctypes
        frame = g.gi_frame
        frame.f_locals.update({'.0': iter(new_source)})
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))

    except ImportError:
        raise NotImplementedError('Rebinding generators is only supported on CPython')


# TODO: Optimise this. It can actually be guaranteed, in a singlethreaded scenario, that none of the objects
#  contained herein will be mutated, so regardless of mutability, their hashes will be static (unless for some really
#  weird reason, the `__hash__` method causes mutation)...or can it be optimised?


def unique(it: Iterable[T], hashable: bool) -> Iterable[T]:
    unique_hashable = set()
    unique_unhashable = []

    if hashable:
        for e in it:
            try:
                if e not in unique_hashable:
                    unique_hashable.add(e)
                    yield e

            except TypeError:
                if e not in unique_unhashable:
                    unique_unhashable.append(e)
                    yield e

    else:
        for e in it:
            if e not in unique_unhashable:
                unique_unhashable.append(e)
                yield e


def unique_by(it: Iterable[T], key: Callable[[T], U], hashable: bool) -> Iterable[T]:
    unique_hashable = set()
    unique_unhashable = []

    if hashable:
        for e in it:
            k = key(e)
            try:
                if k not in unique_hashable:
                    unique_hashable.add(k)
                    yield e

            except TypeError:
                if k not in unique_unhashable:
                    unique_unhashable.append(k)
                    yield e

    else:
        for e in it:
            k = key(e)
            if k not in unique_unhashable:
                unique_unhashable.append(k)
                yield e

def without(it: Iterable[T], other: Iterable[T]) -> Iterable[T]:
    pass
