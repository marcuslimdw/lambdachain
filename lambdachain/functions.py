from itertools import groupby as groupby, count
from collections import defaultdict
from functools import reduce
from typing import TypeVar, Iterable, Callable, Any, Generator, Tuple, Hashable

T = TypeVar('T')
U = TypeVar('U')


def identity(x: T) -> T:
    return x


def fold(f: Callable[[U, T], U], it: Iterable[T], initial_value: U) -> U:
    return reduce(f, it, initial_value)


def foldc(f: Callable[[U, T], U], it: Iterable[T]) -> Callable[[U], U]:
    def inner(u: U) -> U:
        return reduce(f, it, u)

    return inner


def rebind(g: Generator[T, None, None], new_source: Iterable):
    try:
        import ctypes
        frame = g.gi_frame
        frame.f_locals.update({'.0': iter(new_source)})
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))

    except ImportError:
        raise NotImplementedError('Rebinding generators is only supported on CPython')


# TODO: Support unique and unique_by for unhashable items


def unique(it: Iterable[T], ordered: bool) -> Iterable[T]:
    if ordered:
        yield from {k: None for k in it}

    else:
        yield from set(it)


def unique_by(it: Iterable[T], key: Callable[[T], Hashable]) -> Iterable[T]:
    uniques = set()
    result = []
    for v in it:
        k = key(v)
        if k not in uniques:
            uniques.add(k)
            result.append(v)

    yield from result


def groupby_(it: Iterable[T], key: Callable[[T], U], combine: bool) -> Iterable[Tuple[U, T]]:
    if combine:
        d = defaultdict(list)
        for v in it:
            d[key(v)].append(v)

        yield from d.items()

    else:
        yield from ((k, list(g)) for k, g in groupby(it, key))


def enumerate_(it: Iterable[T], start: int, step: int) -> Iterable[Tuple[T, int]]:
    if step == 1:
        return enumerate(it, start)

    else:
        return zip(count(start, step), it)
