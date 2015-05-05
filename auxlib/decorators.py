from functools import wraps
import types

# TODO: spend time filling out functionality and make these more robust


def memoize(func):
    """
    Decorator to cause a function to cache it's results for each combination of
    inputs and return the cached result on subsequent calls.  Does not support
    named arguments or arg values that are not hashable.

    >>> @memoize
    ... def foo(x):
    ...     print 'running function with', x
    ...     return x+3
    ...
    >>> foo(10)
    running function with 10
    13
    >>> foo(10)
    13
    >>> foo(11)
    running function with 11
    14
    >>> @memoize
    ... def range_tuple(limit):
    ...     print 'running function'
    ...     return tuple(i for i in xrange(limit))
    ...
    >>> range_tuple(3)
    running function
    (0, 1, 2)
    >>> range_tuple(3)
    (0, 1, 2)
    >>> @memoize
    ... def range_iter(limit):
    ...     print 'running function'
    ...     return (i for i in xrange(limit))
    ...
    >>> range_iter(3)
    Traceback (most recent call last):
    TypeError: Can't memoize a generator!
    """
    func._result_cache = {}

    @wraps(func)
    def _memoized_func(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in func._result_cache:
            return func._result_cache[key]
        else:
            result = func(*args, **kwargs)
            if isinstance(result, types.GeneratorType):
                raise TypeError("Can't memoize a generator!")
            func._result_cache[key] = result
            return result

    return _memoized_func


def memoizemethod(method):
    """
    Decorator to cause a method to cache it's results in self for each
    combination of inputs and return the cached result on subsequent calls.
    Does not support named arguments or arg values that are not hashable.

    >>> class Foo (object):
    ...   @memoizemethod
    ...   def foo(self, x, y=0):
    ...     print 'running method with', x, y
    ...     return x + y + 3
    ...
    >>> foo1 = Foo()
    >>> foo2 = Foo()
    >>> foo1.foo(10)
    running method with 10 0
    13
    >>> foo1.foo(10)
    13
    >>> foo2.foo(11, y=7)
    running method with 11 7
    21
    >>> foo2.foo(11)
    running method with 11 0
    14
    >>> foo2.foo(11, y=7)
    21
    >>> class Foo (object):
    ...   def __init__(self, lower):
    ...     self.lower = lower
    ...   @memoizemethod
    ...   def range_tuple(self, upper):
    ...     print 'running function'
    ...     return tuple(i for i in xrange(self.lower, upper))
    ...   @memoizemethod
    ...   def range_iter(self, upper):
    ...     print 'running function'
    ...     return (i for i in xrange(self.lower, upper))
    ...
    >>> foo = Foo(3)
    >>> foo.range_tuple(6)
    running function
    (3, 4, 5)
    >>> foo.range_tuple(7)
    running function
    (3, 4, 5, 6)
    >>> foo.range_tuple(6)
    (3, 4, 5)
    >>> foo.range_iter(6)
    Traceback (most recent call last):
    TypeError: Can't memoize a generator!
    """

    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        # NOTE:  a __dict__ check is performed here rather than using the
        # built-in hasattr function because hasattr will look up to an object's
        # class if the attr is not directly found in the object's dict.  That's
        # bad for this if the class itself has a memoized classmethod for
        # example that has been called before the memoized instance method,
        # then the instance method will use the class's result cache, causing
        # its results to be globally stored rather than on a per instance
        # basis.
        if '_memoized_results' not in self.__dict__:
            self._memoized_results = {}
        memoized_results = self._memoized_results

        key = (method.__name__, args, tuple(sorted(kwargs.items())))
        if key in memoized_results:
            return memoized_results[key]
        else:
            result = method(self, *args, **kwargs)
            if isinstance(result, types.GeneratorType):
                raise TypeError("Can't memoize a generator!")
            return memoized_results.setdefault(key, result)

    return _wrapper


def clear_memoized_methods(obj, *method_names):
    """
    Clear the memoized method or @memoizeproperty results for the given
    method names from the given object.

    >>> v = [0]
    >>> def inc():
    ...     v[0] += 1
    ...     return v[0]
    ...
    >>> class Foo(object):
    ...    @memoizemethod
    ...    def foo(self):
    ...        return inc()
    ...    @memoizeproperty
    ...    def g(self):
    ...       return inc()
    ...
    >>> f = Foo()
    >>> f.foo(), f.foo()
    (1, 1)
    >>> clear_memoized_methods(f, 'foo')
    >>> (f.foo(), f.foo(), f.g, f.g)
    (2, 2, 3, 3)
    >>> (f.foo(), f.foo(), f.g, f.g)
    (2, 2, 3, 3)
    >>> clear_memoized_methods(f, 'g', 'no_problem_if_undefined')
    >>> f.g, f.foo(), f.g
    (4, 2, 4)
    >>> f.foo()
    2
    """
    for key in getattr(obj, '_memoized_results', {}).keys():
        # key[0] is the method name
        if key[0] in method_names:
            del obj._memoized_results[key]

    property_dict = obj.__dict__
    for prop in method_names:
        inner_attname = '_%s' % prop
        if inner_attname in property_dict:
            del property_dict[inner_attname]


def memoizeproperty(func):
    """
    Decorator to cause a method to cache it's results in self for each
    combination of inputs and return the cached result on subsequent calls.
    Does not support named arguments or arg values that are not hashable.

    >>> class Foo (object):
    ...   _x = 1
    ...   @memoizeproperty
    ...   def foo(self):
    ...     self._x += 1
    ...     print 'updating and returning %d'% self._x
    ...     return self._x
    ...
    >>> foo1 = Foo()
    >>> foo2 = Foo()
    >>> foo1.foo
    updating and returning 2
    2
    >>> foo1.foo
    2
    >>> foo2.foo
    updating and returning 2
    2
    >>> foo1.foo
    2
    """
    inner_attname = '_%s' % func.__name__

    def new_fget(self):
        self_dict = self.__dict__
        if inner_attname not in self_dict:
            self_dict[inner_attname] = func(self)
        return self_dict[inner_attname]

    return property(new_fget)
