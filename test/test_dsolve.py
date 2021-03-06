import unittest
import dsolve
from collections import OrderedDict


class DSolveTest(unittest.TestCase):
    def setUp(self):
        self.__resolver = dsolve.resolver()

    def void(self, *args, **kwargs):
        pass

    @property
    def resolver(self):
        return self.__resolver

    def test_no_dependency(self):
        self.resolver.register('a', 'A')
        self.resolver.register('b', 'B')
        self.resolver.resolve(self.void)

    def test_duplicate_keys(self):
        self.resolver.register('a', 'A')
        with self.assertRaises(dsolve.DuplicateKeyError) as ctx:
            self.resolver.register('a', 'B')

        self.assertEqual('a', ctx.exception.key)
        self.assertEqual('A', ctx.exception.old)
        self.assertEqual('B', ctx.exception.new)

    def test_duplicate_duplicate_dependencies(self):
        self.resolver.register('a', 'A', ['b', 'b'])
        self.resolver.register('b', 'B')

        self.resolver.resolve(self.void)

    def test_circular_dependency(self):
        self.resolver.register('a', 'A', ['b'])
        self.resolver.register('b', 'B', ['a'])

        with self.assertRaises(dsolve.CircularDependencyError):
            self.resolver.resolve(self.void)

    def test_unregistered_dependency(self):
        self.resolver.register('a', 'A', ['b'])
        with self.assertRaises(dsolve.UnregisteredDependencyError) as ctx:
            self.resolver.resolve(self.void)

        self.assertEqual('b', ctx.exception.key)

    def test_single_dependency(self):
        self.resolver.register('a', 'A', ['b'])
        self.resolver.register('b', 'B')
        self.resolver.resolve(self.void)

    def test_multiple_dependencies(self):
        self.resolver.register('a', 'A', ['b', 'c'])
        self.resolver.register('b', 'B', ['c'])
        self.resolver.register('c', 'C')
        self.resolver.resolve(self.void)

    def test_multiple_dependencies_duplicate_key(self):
        self.resolver.register('a', 'A', ['b', 'c'])
        self.resolver.register('b', 'B', ['c'])
        with self.assertRaises(dsolve.DuplicateKeyError) as ctx:
            self.resolver.register('a', 'C')

        self.assertEqual('a', ctx.exception.key)
        self.assertEqual('A', ctx.exception.old)
        self.assertEqual('C', ctx.exception.new)

    def test_multiple_dependencies_unregistered(self):
        self.resolver.register('a', 'A', ['b', 'c'])
        self.resolver.register('b', 'B', ['c'])
        self.resolver.register('c', 'C', ['d'])
        with self.assertRaises(dsolve.UnregisteredDependencyError) as ctx:
            self.resolver.resolve(self.void)

        self.assertEqual('d', ctx.exception.key)

    def test_multiple_dependencies_circular(self):
        self.resolver.register('a', 'A', ['b', 'c'])
        self.resolver.register('b', 'B', ['c'])
        self.resolver.register('c', 'C', ['a'])
        with self.assertRaises(dsolve.CircularDependencyError):
            self.resolver.resolve(self.void)

    def test_use_case_01(self):
        class Node(object):
            def __init__(self, key, dependencies=None):
                self.key = key
                self.dependencies = dependencies

            def resolve(self, key):
                self.dependencies[key] = key

        def resolve(n, d):
            d.resolve(n.key)

        test = Node('a', {'b': '__PLACEHOLDER__'})
        self.resolver.register('a', test, ['b'])
        self.resolver.register('b', Node('b'))
        self.resolver.resolve(resolve)
        self.assertEqual('b', test.dependencies['b'])

    def test_use_case_02(self):

        packages = [
            Package('main', dependencies=['whatever-project', 'awesome-project', 'that-project', 'great-project']),
            Package('whatever-project', dependencies=['great-project', 'that-project']),
            Package('awesome-project', dependencies=['dsolve']),
            Package('that-project', dependencies=['great-project', 'flask']),
            Package('great-project', dependencies=['dsolve', 'flask']),
        ]

        resolved = PackageResolver(packages).resolve()

        self.assertListEqual([
            ('dsolve', ('great-project', 'awesome-project')),
            ('flask', ('great-project', 'that-project')),
            ('awesome-project', ('main',)),
            ('great-project', ('that-project', 'whatever-project', 'main')),
            ('that-project', ('whatever-project', 'main')),
            ('whatever-project', ('main',))
        ], resolved)


class Package(object):
    def __init__(self, name, dependencies=None):
        self.name = name
        self.dependencies = dependencies


class PackageResolver(object):
    def __init__(self, packages):
        self.execution_order = OrderedDict()
        self.resolver = dsolve.resolver()
        for package in packages:
            self.resolver.register(package.name, package, package.dependencies)

    def __resolve(self, resolving, dependent):
        order = self.execution_order.get(resolving.name)
        if not order:
            order = self.execution_order[resolving.name] = []

        order.append(dependent.name)

    def resolve(self):
        # register 3rd party packages
        for key in self.resolver.unregistered_nodes:
            self.resolver.register(key, Package(key))

        self.resolver.resolve(self.__resolve)

        return [(key, tuple(values)) for key, values in self.execution_order.items()]
