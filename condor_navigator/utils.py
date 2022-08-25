
class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)

def _value_or_default(value, default):
    return value if value is not None else default
