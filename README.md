
<h1>LambdaChain</h1>

A Python library intended to inject a little functional programming goodness into the language.

---

## Why use `lambdachain`?

Imagine you have a list of names, and you want to group and sort names longer than 4 characters by their first letter. You could do this in vanilla Python:

```python
>>> names = ['John', 'Emily', 'Aaron', 'Keith', 'Mary', 'Samantha', 'Luke', 'Joash', 'Sean', 'Ken', 'Amelia', 'Joanne', 'Melissa']
>>> result = {}
>>> for name in names:
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
>>> dict((k, sorted(g)) for k, g in groupby(sorted(filter(lambda name: len(name) > 4, names), key=lambda name: name[0]), key=lambda name: name[0]))
{'A': ['Aaron', 'Amelia'], 'E': ['Emily'], 'J': ['Joanne', 'Joash'], 'K': ['Keith'], 'M': ['Melissa'], 'S': ['Samantha']}
```

There's a lot going on in that one line. What `lambdachain` brings you is the ability to chain computations together in a functional way, as well as express lambda functions compactly, without losing clarity (the outer parentheses are only for method chaining, and are not necessarily for functionality):

```python
>>> from lambdachain import LambdaChain, _
>>> from lambdachain.builtin_hooks import *
>>> (LambdaChain(names)
...     .filter(len(_) > 4)
...     .groupby(_[0])
...     .apply((k, sorted(g)) for k, g in _)
...     .force(dict))
{'E': ['Emily'], 'A': ['Aaron', 'Amelia'], 'K': ['Keith'], 'S': ['Samantha'], 'J': ['Joanne', 'Joash'], 'M': ['Melissa']}
```

The above operations can be read like a list of steps:

1. Keep only everything with a length more than 4
2. Group what remains by the first element (the key)
3. Sort the "group" part of each key-group pair

What about step 4?

In `lambdachain`, all *non-forcing* operations are *lazy*, which means that they are not performed until you actually need them. Therefore, an additional `force` step is needed to convert the result of step 3 into a `dict`. Since all the `lambdachain` operations do not change the data you pass in, there's no need to perform calculations until you actually need their results.

---

## Cool stuff



