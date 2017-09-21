from collections import defaultdict


class DependencyError(BaseException):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        super(DependencyError, self).__init__(key)


class DuplicateKeyError(DependencyError):
    def __init__(self, key, old, new, *args, **kwargs):
        self.old = old
        self.new = new
        super(DuplicateKeyError, self).__init__(key, *args, **kwargs)


class UnregisteredDependencyError(DependencyError):
    pass


class CircularDependencyError(DependencyError):
    pass


DNull = object()


class DNode(object):
    def __init__(self, key, value=DNull):
        self.key = key
        self.value = value
        self.dependencies = set()

    def __cmp__(self, other):
        # descending order
        return len(other.dependencies).__cmp__(len(self.dependencies))

    def __lt__(self, other):
        return len(other.dependencies) < len(self.dependencies)

    def __gt__(self, other):
        return len(other.dependencies) > len(self.dependencies)

    def __repr__(self):
        return '{} ({}): {}'.format(self.key, len(self.dependencies), self.value)


class DSolver(object):
    def __init__(self):
        self.__node_map = {}
        self.dependents = defaultdict(list)
        self.unregistered_nodes = set()

    def register(self, key, obj, dependencies=None):
        node = self.__node_map.get(key)
        if node:
            if node.value is DNull:
                node.value = obj
                self.unregistered_nodes.remove(key)
            elif node.value != obj:
                raise DuplicateKeyError(key, node.value, obj)
        else:
            node = self.__node_map[key] = DNode(key, value=obj)

        if dependencies:
            for dependent_key in dependencies:
                dependency = self.__node_map.get(dependent_key)

                if not dependency:
                    dependency = self.__node_map[dependent_key] = DNode(dependent_key)
                    self.unregistered_nodes.add(dependent_key)

                node.dependencies.add(dependency)
                self.dependents[dependency].append(node)

    def resolve(self, func):
        if self.unregistered_nodes:
            raise UnregisteredDependencyError(next(iter(self.unregistered_nodes)))

        nodes = list(self.__node_map.values())

        while nodes:
            nodes.sort()
            node = nodes.pop()
            if node.dependencies:
                raise CircularDependencyError(node.key)

            # resolve
            func(node)

            # then remove from dependencies
            while self.dependents[node]:
                self.dependents[node].pop().dependencies.remove(node)

    def clear(self):
        self.__node_map.clear()
        self.dependents.clear()
        self.unregistered_nodes.clear()
