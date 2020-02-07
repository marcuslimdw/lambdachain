
<h1>LambdaChain 0.1</h1>

A Python library intended to inject a little functional programming goodness into the language.

---

## Quickstart

`lambdachain` is on [PyPI](https://pypi.org/), so you can just install it through `pip`:

`pip install lambdachain`

Note that `lambdachain` requires Python >= 3.6. There are no other dependencies. However, if you want to run the unit tests, you'll have to install `pytest`.

That's it! You'll generally only need three imports to use `lambdachain`: the `LC` object to allow you to chain operations, the `_` object (which is an instance of `LambdaIdentifier`) to create lambdas quickly, and the `builtin_hooks` module, if you intend to do stuff like `int(_)` or `type(_)` - the builtin hooks replace the builtin versions of functions with ones that can handle `LambdaIdentifiers`.

```python
from lambdachain import LC, _
from builtin_hooks import *
```

Note that if you're using IPython, the shell tends to overwrite `_` with the result of the last expression. Therefore, you might want to import `_` under another name, such as with `from lambdachain import _ as Y` (which kind of looks like an upside down λ).

---

## Why use `lambdachain`?

Imagine you have a list of names, and you want to remove duplicates, and then group and sort names longer than 4 characters by their first letter. You could do this in vanilla Python:

```python
>>> names = ['John', 'Emily', 'Aaron', 'Keith', 'Aaron', 'Mary', 'Samantha', 'John', 'Aaron', 'Luke', 'Joash', 'Joanne', 'Sean', 'Ken', 'Amelia', 'Joanne', 'Melissa', 'Emily']
>>> result = {}
>>> unique_names = set(names)
>>> for name in unique_names:
...     if len(name) > 4:
...         starting_char = name[0]
...         if starting_char in result:
...                 result[starting_char].append(name)
...         else:
...                 result[starting_char] = [name]
...
>>> for group_names in result.values():
...     group_names.sort()
...
>>> result
{'E': ['Emily'], 'A': ['Aaron', 'Amelia'], 'K': ['Keith'], 'S': ['Samantha'], 'J': ['Joanne', 'Joash'], 'M': ['Melissa']}
```

This works, but is a bit imperative and lengthy. You could use `itertools.groupby` or a `defaultdict`, but you would end up with something like this:

```python
>>> from itertools import groupby
>>> {k: sorted(g) for k, g in groupby(sorted(filter(lambda name: len(name) > 4, set(names)), key=lambda name: name[0]), key=lambda name: name[0])}
{'A': ['Aaron', 'Amelia'], 'E': ['Emily'], 'J': ['Joanne', 'Joash'], 'K': ['Keith'], 'M': ['Melissa'], 'S': ['Samantha']}
```

There's a lot going on in that one line. Also, the fact that some operations extend to the left and some to the right makes it difficult to read.

What `lambdachain` brings you is the ability to chain computations together in a functional way, as well as express lambda functions compactly, without losing clarity (the outer parentheses are only for method chaining, and are not necessarily for functionality):

```python
>>> from lambdachain import LC, _
>>> from lambdachain.builtin_hooks import *
>>> LC(names)
...     .unique()
...     .filter(len(_) > 4)
...     .groupby(_[0])
...     .apply((k, sorted(g)) for k, g in _)
...     .force(dict))
{'E': ['Emily'], 'A': ['Aaron', 'Amelia'], 'K': ['Keith'], 'S': ['Samantha'], 'J': ['Joanne', 'Joash'], 'M': ['Melissa']}
```

The above operations can be read like a list of steps:

1. Filter out duplicates
2. Keep only everything with a length more than 4
3. Group what remains by the first element (the key)
4. Sort the "group" part of each key-group pair

What about the `force`?

In `lambdachain`, all *non-forcing* operations are *lazy*, which means that they are not performed until you actually need them. Therefore, an additional `force` step is needed to convert the result of step 3 into a `dict`. Since all the `lambdachain` operations do not change the data you pass in, there's no need to perform caLCulations until you actually need their results.

For completeness, the equivalent Scala code:

```scala
scala> val names = List("John", "Emily", "Aaron", "Keith", "Aaron", "Mary", "Samantha", "John", "Aaron", "Luke", "Joash", "Joanne", "Sean", "Ken", "Amelia", "Joanne", "Melissa", "Emily")
scala> names.toSet.filter(_.length > 4).groupBy(_(0)).map{case (k, g) => (k, g.toSeq.sorted)}.toMap
res1: scala.collection.immutable.Map[Char,Seq[String]] = Map(E -> ArrayBuffer(Emily), J -> ArrayBuffer(Joanne, Joash), A -> ArrayBuffer(Aaron, Amelia), M -> ArrayBuffer(Melissa), K -> ArrayBuffer(Keith), S -> ArrayBuffer(Samantha))
```

---

## Cool stuff

### Simple lambda functions like Scala or Haskell

Tired of writing `lambda x: x + 1` or `from operator import itemgetter`? Just use `lambdachain`:

```python
>>> f = _ + 1  # Instead of lambda x: x + 1
>>> f(1)
2
>>> g = len(_[2])  # Instead of lambda x: len(x[2])
>>> g(['lambda', 'chain', 'fun'])
3
```

### Map over both attributes and methods

Take the real parts of complex numbers:

```python
>>> LC([1.0 + 2.0j, -3.0 - 1.0j, 6.0 - 3.0j, 2.0]).map(_.real).force()
[1.0, -3.0, 6.0, 2.0]
```

Strip strings:

```python
>>> LC(['   spaces  ', ' alligator.. ..  ', 'thing', ' help    ']).map(_.strip @ ()).force()
['spaces', 'alligator.. ..', 'thing', 'help']
```

Note that when you're calling a *method*, as opposed to accessing an *attribute*, you need an additional `@` between the method name and the argument list. This is to help `lambdachain` distinguish the two (after all, we're just using reflection magic, not stuff built into the language's sytax).

### Rebindable generators

Through a bit of poking around in CPython (yes, that means this might not work on Jython or PyPy), the idea of a *lambda generator* is possible with the `LC.apply` method. Basically, you can define arbitrary generator expressions and then apply them to a `LC` object, which "inserts" the iterable it's holding into the source iterable for the generator:

```python
>>> g = (i * 3 for i in _ if i % 2 == 0)
>>> LC([1, 2, 3, 4, 5]).apply(g).sum()
18
```

This is the equivalent to the following:

```python
>>> data = [1, 2, 3, 4, 5]
>>> sum(i * 3 for i in data if i % 2 == 0)
18
```

The advantage of `lambdachain` is that you can have multiple `apply` calls in a data pipeline. This is particularly helpful after a stage that converts individual elements to collections, such as `groupby`. 

## Other Examples

The [Sock Merchant problem](https://www.hackerrank.com/challenges/sock-merchant/problem) involves finding the number of pairs of each unique value in a collection, ignoring remainders. So, for example, `[1, 2, 1, 2, 1, 3, 2]` has 2 pairs and 3 odd ones out.

Two possible solutions:

```python
>>> LC([1, 2, 1, 2, 1, 3, 2]).groupby(_).apply(len(g) // 2 for k, g in _).force.sum()
2
>>> LC([1, 2, 1, 2, 1, 3, 2]).groupby(_).map(len(_[1]) // 2).force.sum()
2
```

Explanation:

1. Group the input values by the identity function, placing all the instances of each unique value into their own group
2. Take the length of each group and floor divide by 2
3. Evaluate the previous steps by taking the sum

---

## FAQ

Q: Why do I get `TypeError` when I do things like `len(_)` or `int(_)`?

A: You need to import a set of functions that replace the builtins so they'll play nice with `lambdachain`. Execute `from lambdachain.builtin_hooks import *`.

Q: I still get problems with stuff like `bytes`!

A: I haven't implemented those yet. Sorry.

---

## Future plans

* Add static methods for iterators like `range`, `cycle` and `repeat`
* More operations like `take`, `takewhile`, `compact` and `partition`
* Proper separate documentation (I couldn't really get Sphinx to work well with the complex type signatures)

If you have any suggestions/find any bugs, feel free to email me at marcuslimdw@gmail.com.
