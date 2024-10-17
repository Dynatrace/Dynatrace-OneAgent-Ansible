from abc import abstractmethod


def constant_key(func) -> None:
    property(classmethod(abstractmethod(func)))
