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


# TODO: Optimise this. It can actually be guaranteed, in a singlethreaded scenario, that none of the objects
#  contained herein will be mutated, so regardless of mutability, their hashes will be static (unless for some really
#  weird reason, the `__hash__` method causes mutation)...


def unique(it: Iterable[T], hashable: bool) -> Iterable[T]:
    if hashable:
        yield from {k: None for k in it}

    else:
        result = []
        seen_hashable = set()
        seen_unhashable = []
        for element in it:
            try:
                if element not in seen_hashable:
                    seen_hashable.add(element)
                    yield element

            except:
                if not any(element == seen for seen in seen_unhashable):
                    seen_unhashable.append(element)
                    yield element


def unique_by(it: Iterable[T], key: Callable[[T], U], hashable: bool) -> Iterable[T]:
    uniques_hashable = set()
    if hashable:
        for v in it:
            k = key(v)
            if k not in uniques_hashable:
                uniques_hashable.add(k)
                yield v

    else:
        uniques_unhashable = []
        for v in it:
            k = key(v)
            try:
                if v not in uniques_hashable:
                    uniques_hashable.add(v)
                    yield v

            except TypeError:
                if not any(v == seen for seen in uniques_unhashable):
                    uniques_unhashable.append(v)
                    yield v


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
