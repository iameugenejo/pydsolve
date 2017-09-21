from .dsolve import DependencyError, DuplicateKeyError, UnregisteredDependencyError, CircularDependencyError, DSolver


def resolver():
    return DSolver()
