# this is a decorator that will make a class a singleton
# usage:
# @singleton
# class MyClass:
#     pass
#
def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances or "recreate_singleton" in kwargs:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance
