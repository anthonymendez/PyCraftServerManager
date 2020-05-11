
class Singleton:
    """
    Singleton Decorator Pattern

    https://medium.com/better-programming/singleton-in-python-5eaa66618e3d
    """
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)