"""Common collection classes."""


# http://stackoverflow.com/a/14620633/2127762
class AttrDict(dict):
    """Sub-classes dict, and further allows attribute-like access to dictionary items.

    Examples:
        >>> d = AttrDict({'a': 1})
        >>> d.a, d['a'], d.get('a')
        (1, 1, 1)
        >>> d.b = 2
        >>> d.b, d['b']
        (2, 2)
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


