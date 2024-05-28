from abc import abstractmethod


def constant_key(func):
    property(classmethod(abstractmethod(func)))
